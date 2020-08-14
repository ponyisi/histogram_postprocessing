def go():
    """ Application entry point """
    import logging

    from histgrinder.config import read_configuration, lookup_name
    from histgrinder.transform import Transformer

    # set up arguments
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Histogram postprocessing script")
    parser.add_argument('-c', '--configfile', nargs='+',
                        help='YAML configuration file(s)')
    parser.add_argument('source', help='Input source, e.g. ROOT file')
    parser.add_argument('target', help='Output target, e.g. ROOT file')
    parser.add_argument('--inmodule',
                        default='histgrinder.io.root.ROOTInputModule',
                        help='Python class which implements an input module')
    parser.add_argument('--outmodule',
                        default='histgrinder.io.root.ROOTOutputModule',
                        help='Python class which implements an output module')
    parser.add_argument('--prefix',
                        help='Prefix to ignore in histogram locations')
    parser.add_argument('--loglevel', help='Set the logging level',
                        choices=['DEBUG', 'INFO', 'WARNING',
                                 'ERROR', 'CRITICAL'],
                        default='INFO')
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel,
                        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')  # noqa: E501
    log = logging.getLogger(__name__)
    log.info("Histgrinder: histogram postprocessor")

    # read configuration & set up transformations
    transformers = []
    for configfile in args.configfile:
        config = read_configuration(configfile)
        transformers += [Transformer(_) for _ in config]
    selectors = set()
    for transform in transformers:
        selectors.update(transform.inregexes)

    # Configure input
    im = lookup_name(args.inmodule)()
    in_configuration = {'source': args.source}
    if args.prefix:
        in_configuration['prefix'] = args.prefix
    im.configure(in_configuration)
    im.setSelectors(selectors)

    # Configure output
    om = lookup_name(args.outmodule)()
    out_configuration = {'target': args.target}
    if args.prefix:
        out_configuration['prefix'] = args.prefix
    om.configure(out_configuration)

    # Event loop
    log.info("Beginning loop")
    for obj in im:
        for _ in transformers:
            v = _.consider(obj)
            if v:
                om.publish(v)

    log.info("Complete")


if __name__ == '__main__':
    go()
