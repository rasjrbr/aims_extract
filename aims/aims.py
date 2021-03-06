#!/usr/bin/python3
import argparse
from getpass import getpass
import json
import requests
import sys

from aims import access, parse, process
from aims import roster_format, logbook_format, ical_format, droster_format
from aims.mytypes import *

def _args():
    parser = argparse.ArgumentParser(
        description='Access AIMS data from easyJet servers.')
    parser.add_argument('format',
                        choices=['roster', 'logbook', 'ical',
                                 'changes', 'json', 'droster'])
    parser.add_argument('username')
    parser.add_argument('--future', type=int)
    parser.add_argument('--past', type=int)
    parser.add_argument('--quiet', "-q", action='store_true')
    parser.add_argument('--last_ics', "-l")
    parser.add_argument('--force', '-f', action='store_true')
    parser.add_argument('--portal', '-p', action='store_true')
    return parser.parse_args()


def report_requests_failures(e: requests.RequestException) -> None:
    print("\n", e.__doc__, "\n", e.request.url, file=sys.stderr)


def report_aims_failures(e: AIMSException) -> None:
    print("\n", e.__doc__, "\n", e.str_, file=sys.stderr)


def main() -> int:
    args = _args()
    if args.quiet: access.fprint = lambda x: None
    try:
        if args.portal:
            access.connect_via_portal(args.username, getpass())
        else:
            access.connect_via_ecrew(args.username, getpass())
        access.fprint("Checking for changes ")
        index_page = access.get_index_page()
        access.fprint(" Done\n")
        no_changes_marker = '\r\nvar notification = Trim("");\r\n'
        changes = False
        if index_page.find(no_changes_marker) == -1:
            changes = True
        elif args.format != "changes":
            offset = 0
            if args.future: offset = args.future
            elif args.past: offset = -args.past
            html = access.get_brief_roster(offset)
            brief_roster = parse.parse_brief_roster(html)
            dutylist = process.process_roster_entries(brief_roster, args.force)
    except requests.RequestException as e:
        report_requests_failures(e)
        return -1
    except AIMSException as e:
        report_aims_failures(e)
        return -2
    finally:
        access.logout()
    if changes:
        output = sys.stdout if args.format == "changes" else sys.stderr
        print("You have changes.", file=output)
    elif args.format == "changes":
        print("No changes")
    elif args.format == "roster":
        print(roster_format.dump(dutylist))
    elif args.format == "logbook":
        print(logbook_format.dump(dutylist))
    elif args.format == "ical":
        print(ical_format.dump(dutylist, args.last_ics))
    elif args.format == "json":
        print(json.dumps(dutylist, sort_keys=True, indent=4,
              default=lambda x: x.__str__()))
    elif args.format == "droster":
        print(droster_format.dump(dutylist))
    return 0


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
