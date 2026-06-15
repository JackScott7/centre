import argparse
from .core import Centre
from .utilities import Utilities


def main() -> None:
    parser = argparse.ArgumentParser(prog="centre", description='Centre is A lightweight Windows tool'
                                    ' for consistent app placement, sizing, and desktop layout control.')

    parser.add_argument('-s', '--start', action='store_true', help='Start Centre as background process')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--list', action='store_true', help='List Window Title, Size and Position')
    group.add_argument('-c', '--read-config', action='store_true', help='Read config file and print out')
    group.add_argument('-v', '--version', action='version', version=f'centre {Utilities.get_package_version()}')

    args = parser.parse_args()

    ctr = Centre()
    if args.list:
        titles = Utilities.list_window_titles()
        print(titles)
    elif args.read_config:
        print(ctr.config)
    elif args.start:
        ctr.listen()


if __name__ == '__main__':
    main()
