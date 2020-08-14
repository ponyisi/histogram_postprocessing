from .config import TransformationConfiguration, lookup_name
from .HistObject import HistObject
from typing import Optional, List


class Transformer(object):
    def __init__(self, tc: TransformationConfiguration):
        import re
        self.tc = tc
        # the number of histograms needed for a match
        self.inlength = len(tc.input)
        # regexes of input
        self.inregexes = [re.compile(_) for _ in tc.input]
        # info for pattern matching
        self.regexgroups = [_.groupindex for _ in self.inregexes]
        # check that all regex group keys are subsets of the first pattern
        for regexgroup in self.regexgroups[1:]:
            if not regexgroup.keys() <= self.regexgroups[1].keys():
                raise ValueError("Pattern specification problem: all named "
                                 "groups must given in the first pattern")
        self.regextupnames = [tuple(_) for _ in self.regexgroups]
        # one dictionary for each input slot
        self.hits = [{} for _ in range(len(self.inregexes))]
        try:
            self.transform_function = lookup_name(tc.function)
            if not callable(self.transform_function):
                raise ValueError(f"{tc.function} does not appear "
                                 "to be callable")
        except Exception as e:
            raise ValueError(f"Unable to instantiate transformer because: {e}")

    def consider(self, obj: HistObject) -> Optional[List[HistObject]]:
        """ Emit a new plot if we get a full match, otherwise None """
        from itertools import product
        match = None
        for ire, regex in enumerate(self.inregexes):
            match = regex.match(obj.name)
            if match:
                self.hits[ire][match.groups()] = obj
                break
        if match is None:
            return None
        # Return value list
        rv = []
        # Given a match, what first position histograms match?
        firstmatches = self._getMatchingFirstHists(match)
        # finally, figure out all matching patterns across
        # multiple input positions
        for tup in firstmatches:
            matchdict = dict(zip(self.regextupnames[0], tup))
            matchlist = [[tup]]
            for idx in range(1, self.inlength):
                matchlist.append([])
                for tup2 in self.hits[idx]:
                    if all(v == tup[self.regexgroups[0][self.regextupnames[idx][i]]-1]  # noqa: E501
                           for i, v in enumerate(tup2)):
                        matchlist[-1].append(tup2)
            for arg in product(*matchlist):
                olist = self.transform_function([self.hits[i][v].hist
                                                 for i, v in enumerate(arg)],
                                                self.tc.parameters,
                                                matchdict)
                for i, ohist in enumerate(olist):
                    rv.append(HistObject(self.tc.output[i].format(**matchdict),
                                         ohist))
        return rv

    def _getMatchingFirstHists(self, match):
        firstmatches = []
        for tup in self.hits[0]:
            # does the tuple match in all spots where the pattern name matches?
            # correct for 1-indexing of regex matches
            if all(tup[self.regexgroups[0][_[0]]-1] == _[1]
                   for _ in match.groupdict().items()):
                firstmatches.append(tup)
        return firstmatches
