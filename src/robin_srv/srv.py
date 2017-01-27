# vim: set et ts=4 sw=4 tw=80 :
"""
Copyright (C) Linode LLC, Inc - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Robert DeRose <rderose@linode.com>,  2016
"""

import logging
import re

from datetime import datetime, timedelta
from itertools import groupby
from random import randint

from dns.resolver import get_default_resolver
from dns.exception import DNSException


class SRV(object):
    """
    A wrapper around DNS lookup for SRV records for a service, designed to be
    iterable for client-side load balancing.
    """

    class SRVIter(object):
        """
        The iter object for SRV objects
        """

        def __init__(self, groups):
            self.groups = groups
            self.current_group = (0, [])
            self.log = logging.getLogger(__name__)

        def __iter__(self):
            return self

        def _choose_server(self, total_weight, priority_group):
            """
            Given the total weight and a list of server, return a random server.

            The algorithm used here is defined in
            [RFC 2782](https://tools.ietf.org/html/rfc2782).
            Basically, it tries to pick a server randomly, but still taking into
            account its weight. Those with higher weights, should be selected
            more often.

            There is a special case, when there are servers with a weight of
            zero, they should be used last, only after all servers with a weight
            have been used first.
            """

            self.log.debug("total weight: %d", total_weight)
            choice = None
            size = len(priority_group)
            # Only Zero weighted servers remain
            if size > 0 and total_weight <= 0:
                choice = randint(0, size-1)
                self.log.debug("Zero weights, choice: %d", choice)
            # Use servers with Weights first
            else:
                random_weight = randint(1, total_weight)
                sum_weight = 0
                for i in range(size):
                    server = priority_group[i]
                    sum_weight += server.weight
                    self.log.debug("index %d, random weight: %d, current_sum: "
                                   "%d, server weight: %d", i, random_weight,
                                   sum_weight, server.weight)
                    if sum_weight >= random_weight:
                        choice = i
                        break
                self.log.debug("Non-zero weights, choice: %d", choice)

            if choice is not None:
                chosen = priority_group.pop(choice)
                self.log.debug("Selected server: %s", chosen)
                return chosen, (total_weight - chosen.weight, priority_group)

            # We should never get here, but if we do, want to to know
            self.log.error("Error selecting a server. This is probably a bug")
            raise StopIteration()

        def next(self):
            """
            Will return the next available SRV record based on it being randomly
            selected based on weight in the current priority group.
            """
            size = len(self.groups)
            if not self.current_group[1] and size > 0:
                self.current_group = self.groups.pop(0)

            if len(self.current_group[1]) <= 0:
                raise StopIteration()

            self.log.debug("size: %d, Current group: %s", size,
                           self.current_group)
            chosen, self.current_group = self._choose_server(
                self.current_group[0], self.current_group[1])
            return chosen

        # Python3 compatibility
        __next__ = next

    def __init__(self, service, domain, protocol="tcp", trusted=None,
                 resolver=None, swallow_errors=True):
        """
        Will return an object that will be able to iterate over the results of
        performing a DNS Query for the SRV records for the requested service.
        The iterable object will return items based on Priority first, then by
        Weight in each Priority group.

        Since there is randomness involved, iterating over the object multiple
        times will never result in the same order twice.

        Args:
            service (str): The service to lookup SRV records for
            domain (str): The domain the service is associated with
            protocol (str): Either `tcp` and `udp`, defaults to `tcp`
            trusted (re):  A Regular Expression used to ensure records
                returned are from a trusted domain
            resolver (obj): An instance of DNS Python Resolver to point
                to a custom resolver for DNS queries.
            swallow_errors (bool): Catch exceptions and swallow them,
                default is True

        Example:
            RobinSRV("jabber", "gmail")

        Will result in a RobinSRV object for `_jabber._tcp.gmail.com`.
        """

        self.service = "_{}._{}.{}".format(service, protocol, domain)
        self.trusted = trusted
        self.resolver = resolver if resolver else get_default_resolver()
        self.swallow_errors = swallow_errors
        self.ttl = datetime(1, 1, 1)
        self.groups = []
        self.log = logging.getLogger(__name__)

    def _format_name(self, record):
        """
        Format SRV record server name
        """
        return record.target.to_text(True)

    def _lookup_srv(self):
        """
        Get the servers associated with a service by looking up it's SRV record.

        Returns:
            list:
                On success, is a list of tuples, where the first value in the
                tuple is the total weight of that priority group, and the second
                value is the list of servers in that priority group. The list is
                grouped by priority and each server in their respective list is
                sorted by their weight.

                On failure, an empty list if no result are found.

        Raises:
            DNSException: This results when an issue occurs trying to get the
                          SRV records from DNS, unless `swallow_errors = True`.
        """
        if self.ttl > datetime.now() and self.groups:
            return self.groups

        try:
            self.log.debug("Searching for SRV records for %s", self.service)
            answer = self.resolver.query(self.service, "SRV")
        except DNSException as error:
            self.log.exception("Unable to get SRV records")
            if self.swallow_errors:
                return []
            raise error

        records = sorted(answer.rrset.items,
                         key=lambda r: (r.priority,
                                        r.weight,
                                        self._format_name(r)))
        if self.trusted is not None:
            domain_regex = re.compile(self.trusted)
            found_bad = False
            for srv in records:
                if not domain_regex.match(self._format_name(srv)):
                    self.log.critical("An untrusted SRV record was founf: %s",
                                      srv)
                    found_bad = True
            if found_bad:
                self.log.critical("The SRV records cannot be trusted")
                return []

        for _, value in groupby(records, key=lambda k: k.priority):
            tmp = []
            self.groups.append(
                (sum([(x.weight, tmp.append(x))[0] for x in value]), tmp))
        #self.log.debug("Located the follow SRV records: %s", self.groups)

        self.ttl = datetime.now() + timedelta(seconds=answer.rrset.ttl)
        return self.groups

    def __iter__(self):
        """
        A generator that will continue to return servers based first on
        priority, then by randomly choosing from the priority group based on
        their weight until the list is exhausted.
        """
        return self.SRVIter(self._lookup_srv())
