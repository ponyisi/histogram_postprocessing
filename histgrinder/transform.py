from .config import TransformationConfiguration, lookup_name
from .HistObject import HistObject
from typing import Optional, List


class Transformer(object):
    def __init__(self, tc: TransformationConfiguration):
        import re
        import string
        self.tc = tc
        # the number of histograms needed for a match
        self.inlength = len(tc.input)
        # regexes of input
        self.inregexes = [re.compile(_) for _ in tc.input]
        # info for pattern matching
        self.regexgroups = [_.groupindex for _ in self.inregexes]
        # check that all regex group keys are subsets of the first pattern
        for regexgroup in self.regexgroups[1:]:
            if not regexgroup.keys() <= self.regexgroups[0].keys():
                raise ValueError("Pattern specification problem: all named "
                                 "groups must be given in the first pattern")
        self.regextupnames = [tuple(_) for _ in self.regexgroups]

        # group names that appear in outputs
        self.outputnames = set().union(*[[_[1] for _ in string.Formatter().parse(output)]
                                         for output in self.tc.output])

        # one dictionary for each input slot
        self.hits = [{} for _ in range(len(self.inregexes))]
        try:
            self.transform_function = lookup_name(tc.function)
            if not callable(self.transform_function):
                raise ValueError(f"{tc.function} does not appear "
                                 "to be callable")
        except Exception as e:
            raise ValueError(f"Unable to instantiate transformer because: {e}")

    def consider(self, obj: HistObject, dryrun: bool = False) -> Optional[List[HistObject]]:
        """ Emit a new plot if we get a full match, otherwise None """
        import logging
        log = logging.getLogger(__name__)
        log.debug(self.tc.description)
        match = None
        for ire, regex in enumerate(self.inregexes):
            imatch = regex.match(obj.name)
            if imatch:
                self.hits[ire][imatch.groups()] = obj
                match = imatch
        if match is None:
            return None
        # Return value list
        rv = []

        # Given a match, what first position histograms are relevant?
        firstmatches = self._getMatchingFirstHists(match)

        # Group the first position matches by integration variables
        groupedfirstmatches = self._groupMatches(firstmatches)

        # construct iterables & call functions
        for tuplist in groupedfirstmatches.values():
            hci = HistCombinationIterable(self, tuplist)
            if _fullyvalid(hci):
                olist = self.transform_function(hci, **self.tc.parameters)
                for i, ohist in enumerate(olist):
                    oname = self.tc.output[i].format(**dict(zip(self.regextupnames[0], tuplist[0])))
                    rv.append(HistObject(oname, ohist))

        return rv

    def _getMatchingFirstHists(self, match):
        firstmatches = []
        for tup in self.hits[0]:
            # does the tuple match in all spots where the pattern name matches, and
            # where the variable is significant (we would output a different plot)?
            # make sure we handle the 1-indexing of regex matches
            if all(tup[self.regexgroups[0][_[0]]-1] == _[1]
                   for _ in match.groupdict().items()
                   if _[0] in self.outputnames):
                firstmatches.append(tup)
        return firstmatches

    def _groupMatches(self, firstmatches):
        # group matches by self.outputnames
        import collections
        rv = collections.defaultdict(list)
        for tup in firstmatches:
            reducedtup = tuple(v for i, v in enumerate(tup)
                               if self.regextupnames[0][i] in self.outputnames)
            rv[reducedtup].append(tup)
        return rv


class HistCombinationIterable(object):
    def __init__(self, transformer: Transformer, tuples):
        self.transform = transformer
        # tuple of matching first-position objects.
        # corresponds to each iteration step.
        self.tuples = tuples

    def __iter__(self):
        # logic: every tuple (first position object) should correspond to
        # exactly one histogram in each other slot. Find the full set and
        # yield as a tuple ({matches}, [histograms])
        for tup in self.tuples:
            rv = self._getpair(tup)
            if rv is None:
                continue
            yield rv

    def _getpair(self, tup):
        t = self.transform
        matchdict = dict(zip(t.regextupnames[0], tup))
        matchlist = [[tup]]
        for idx in range(1, t.inlength):
            matchlist.append([])
            for tup2 in t.hits[idx]:
                if all(v == tup[t.regexgroups[0][t.regextupnames[idx][i]]-1]  # noqa: E501
                        for i, v in enumerate(tup2)):
                    matchlist[-1].append(tup2)
        if any(not _ for _ in matchlist):
            return None
        return (matchdict, [t.hits[i][v[0]].hist for i, v in enumerate(matchlist)])

    def __getitem__(self, idx):
        return self._getpair(self.tuples[idx])

    def __len__(self):
        return len(self.tuples)


def _fullyvalid(hci: HistCombinationIterable) -> bool:
    hasany = False  # return false if there are no valid combinations
    for o in hci:
        hasany = True
        if any(_ is None for _ in o[1]):
            return False
    return hasany
