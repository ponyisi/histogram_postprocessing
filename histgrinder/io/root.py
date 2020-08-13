from ..interfaces import InputModule, OutputModule
from ..HistObject import HistObject
from typing import Union, Iterable

class ROOTInputModule(InputModule):
    def __init__(self):
        self.source = None
        import ROOT
        ROOT.TH1.AddDirectory(ROOT.kFALSE)

    def configure(self, options):
        if 'source' not in options:
            raise ValueError("Must specify 'source' as an option to ROOTInputModule")
        self.source = options['source']
        # print('prefix?', options)
        self.prefix = options.get('prefix', '/')
        self.classwarnings = set()
        self.selectors = None

    def setSelectors(self, selectors):
        """ Do more later """
        self.selectors = selectors

    def iterate(self):
        """ Open ROOT file; iterate over all histograms; close ROOT file """
        import ROOT
        import os.path
        from collections import deque
        infile = ROOT.TFile.Open(self.source)
        if not infile:
            raise ValueError(f"Unable to open input file {self.source}")
        dirqueue = deque([''])
        while dirqueue:
            dirname = dirqueue.popleft()
            indir = infile.GetDirectory(os.path.join(self.prefix, dirname))
            # print(self.prefix + dirname)
            if not indir:
                print(f"Access to invalid directory. This shouldn't happen ... dirname {dirname}") 
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
                    if classname in self.classwarnings:
                        continue
                    else:
                        self.classwarnings.add(classname)
                        print(f"{k.GetName()} is of type {classname} and cannot be considered, for now")
                        print(f"Future warnings for type {classname} will be suppressed")
                        continue
                objname = os.path.join(dirname, k.GetName())
                if self.selectors is not None:
                    if not any(_.match(objname) for _ in self.selectors):
                        continue
                obj = k.ReadObj()
                if hasattr(obj, 'SetDirectory'):
                    obj.SetDirectory(0)
                # print('yielding', os.path.join(dirname, k.GetName()))
                yield HistObject(os.path.join(dirname, k.GetName()), obj)
        infile.Close()

    def __iter__(self):
        return self.iterate()
        
class ROOTOutputModule(OutputModule):
    def __init__(self):
        self.target = None

    def configure(self, options) -> None:
        if 'target' not in options:
            raise ValueError("Must specify 'target' as an option to ROOTInputModule")
        self.target = options['target']
        self.overwrite = bool(options.get('overwrite', True))
        self.prefix = options.get('prefix', '/')
        self.delay = bool(options.get('delay', False))
        self.queue = set()

    def publish(self, obj: Union[HistObject, Iterable[HistObject]]) -> None:
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
        if not self.queue: return # Nothing to do
        outfile = ROOT.TFile.Open(self.target, 'UPDATE')
        for o in self.queue:
            # print("publishing", o)
            fulltargetname = os.path.join(self.prefix, o.name)
            dirtargetname = os.path.dirname(fulltargetname)
            if isinstance(o.hist, ROOT.TObject):
                if not outfile.GetDirectory(dirtargetname):
                    # print("Trying to create", dirtargetname)
                    outfile.mkdir(dirtargetname if dirtargetname[0] != '/'
                                  else dirtargetname[1:])
                d = outfile.GetDirectory(dirtargetname)
                # d.cd()
                # print(d)
                # o.hist.SetName(os.path.basename(fulltargetname))
                # o.hist.Write()#,
#                                ROOT.TObject.kWriteDelete if self.overwrite else 0)
                # outfile.cd()
                # o.hist.SetName(os.path.basename(fulltargetname))
                # d.Append(o.hist, True)
                # d.Write()
                d.WriteTObject(o.hist, os.path.basename(fulltargetname),
                               "WriteDelete" if self.overwrite else "")
                # outfile.WriteTObject(o.hist, o.name, "WriteDelete" if self.overwrite else "")
            else:
                print("Unsupported object type", type(o.hist).__name__)
        outfile.Close()

    def finalize(self) -> None:
        self._write()

if __name__ == '__main__':
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