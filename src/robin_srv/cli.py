# vim: set et ts=4 sw=4 tw=80 :
"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mrobin_srv` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``robin_srv.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``robin_srv.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse

from robin_srv import SRV

parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument('-s', '--service', metavar='SERVICE', required=True,
                    help="The service to lookup")
parser.add_argument('-d', '--domain', metavar='DOMAIN', required=True,
                    help="The domain the service is associated with")
parser.add_argument('-p', '--protocol', metavar='PROTOCOL', default="tcp",
                    help="The protocol the service is running on: [tcp|udp]")


def main(args=None):
    args = parser.parse_args(args=args)
    srvs = SRV(args.service, args.domain, args.protocol)
    for s in srvs:
      print(s)
