from ..interfaces import InputModule, OutputModule
from ..HistObject import HistObject
from typing import (Union, Iterable, Mapping, Any, Collection,
                    Pattern, Generator)
import logging


def readobj(k, dryrun):
    if not dryrun:
        obj = k.ReadObj()
        if hasattr(obj, 'SetDirectory'):
            obj.SetDirectory(0)
    else:
        obj = None
    return obj


class ROOTInputModule(InputModule):
    def __init__(self):
        self.source = None
        import ROOT
        # allow for us to close the input file and keep the histograms live
        ROOT.TH1.AddDirectory(ROOT.kFALSE)
        self.classwarnings = set()
        self.selectors = None

    def configure(self, options: Mapping[str, Any]) -> None:
        """
        Configure this module. Potential elements of "options":
        source: should be a ROOT-openable filename or URL.
        prefix: directory path to search under. Returned histogram names
            will not include this.
        """
        if 'source' not in options:
            raise ValueError("Must specify 'source' as an "
                             "option to ROOTInputModule")
        self.source = options['source']
        self.prefix = options.get('prefix', '/')

    def setSelectors(self, selectors: Collection[Pattern]) -> None:
        """ Do more later """
        self.selectors = selectors

    def iterate(self, dryrun) -> Generator[HistObject, None, None]:
        """ Open ROOT file; iterate over all histograms; close ROOT file """
        import ROOT
        import os.path
        from collections import deque
        log = logging.getLogger(__name__)
        infile = ROOT.TFile.Open(self.source)  # failure to open will raise OSError
        dirqueue = deque([''])
        while dirqueue:
            dirname = dirqueue.popleft()
            indir = infile.GetDirectory(os.path.join(self.prefix, dirname))
            if not indir:
                log.critical("Access to invalid directory. "
                             f"This shouldn't happen ... dirname {dirname}")
                continue
            for k in indir.GetListOfKeys():
                classname = k.GetClassName()
                if classname.startswith('TDirectory'):
                    dirqueue.append(os.path.join(dirname, k.GetName()))
                    continue
                klass = ROOT.TClass.GetClass(classname)
                if not (klass.InheritsFrom('TH1')
                        or klass.InheritsFrom('TGraph')
                        or klass.InheritsFrom('TEfficiency')):
                    self._classwarning(k, classname, log)
                    continue
                objname = os.path.join(dirname, k.GetName())
                if self.selectors is not None:
                    if not any(_.fullmatch(objname) for _ in self.selectors):
                        continue
                obj = readobj(k, dryrun)
                log.debug('ROOT input read '
                          f'{os.path.join(dirname, k.GetName())}')
                yield HistObject(os.path.join(dirname, k.GetName()), obj)
        infile.Close()

    def _classwarning(self, key, classname, log) -> None:
        """ Log warning for unhandled class """
        if classname not in self.classwarnings:
            self.classwarnings.add(classname)
            log.warning(f"{key.GetName()} is of type {classname} "
                        "and cannot be considered, for now")
            log.warning(f"Future warnings for type {classname} "
                        "will be suppressed")

    def __iter__(self) -> Iterable[HistObject]:
        return self.iterate(dryrun=False)

    def warmup(self) -> Iterable[HistObject]:
        return self.iterate(dryrun=True)


class ROOTOutputModule(OutputModule):
    def __init__(self):
        self.target = None

    def configure(self, options: Mapping[str, Any]) -> None:
        """
        Configure this module. Potential elements of "options":
        target: should be a ROOT-openable filename or URL which
            can be opened for writing.
        prefix: directory path to place results under.
        overwrite: boolean to indicate whether results should overwrite
            existing histograms in the file.
        delay: only write histograms in finalize() (not during publish()).
        """
        if 'target' not in options:
            raise ValueError("Must specify 'target' as an option "
                             "to ROOTOutputModule")
        self.target = options['target']
        self.overwrite = bool(options.get('overwrite', True))
        self.prefix = options.get('prefix', '/')
        self.delay = bool(options.get('delay', False))
        self.queue = set()

    def publish(self, obj: Union[HistObject, Iterable[HistObject]]) -> None:
        """ Accepts a HistObject containing a ROOT object to write to file """
        if isinstance(obj, HistObject):
            obj = [obj]
        if self.delay:
            self.queue.update(obj)
        else:
            self.queue = obj
            self._write()
            self.queue = None

    def _write(self) -> None:
        """ Open ROOT file; write obj; close ROOT file """
        import ROOT
        import os.path
        if not self.queue:
            return  # Nothing to do
        log = logging.getLogger(__name__)
        outfile = ROOT.TFile.Open(self.target, 'UPDATE')
        for o in self.queue:
            log.debug(f"ROOT output: publishing {o}")
            fulltargetname = os.path.join(self.prefix, o.name)
            dirtargetname = os.path.dirname(fulltargetname)
            if isinstance(o.hist, ROOT.TObject):
                if not outfile.GetDirectory(dirtargetname):
                    outfile.mkdir(dirtargetname if dirtargetname[0] != '/'
                                  else dirtargetname[1:])
                d = outfile.GetDirectory(dirtargetname)
                d.WriteTObject(o.hist, os.path.basename(fulltargetname),
                               "WriteDelete" if self.overwrite else "")
            else:
                log.error("ROOT output: unsupported object type "
                          f"{type(o.hist).__name__}")
        outfile.Close()

    def finalize(self) -> None:
        """ Writes outstanding HistObjects to file """
        self._write()


if __name__ == '__main__':  # pragma: no cover
    import sys
    if len(sys.argv) != 3:
        print("Provide two arguments (input and output files)")
        sys.exit(1)
    im = ROOTInputModule()
    im.configure({'source': sys.argv[1]})
    om = ROOTOutputModule()
    om.configure({'target': sys.argv[2]})
    for o in im:
        print(o, o.hist.GetMean())
        om.publish(o)
