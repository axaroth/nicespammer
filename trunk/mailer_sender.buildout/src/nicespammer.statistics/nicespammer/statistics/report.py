#! /usr/bin/env python

import sys
from optparse import OptionParser

from nicespammer.statistics import stats


class Reports(object):

    def __init__(self, path):
        self.s = stats.Stats(path)

    def newsletters(self):
        """ newsletter name, total number of subscribed users, user having read """

        self.s.cursor.execute('''
            select newsletter_id, count(email_id)
            from bindings
            group by newsletter_id''')
        subscribers = dict(self.s.cursor.fetchall())

        self.s.cursor.execute('''
            select newsletter_id, count(email_id)
            from clicks
            group by newsletter_id''')
        readers = dict(self.s.cursor.fetchall())
        stats = []
        for newsletter_id in subscribers.keys():
            newsletter_name = self.s.getNewsletter(newsletter_id)
            stats.append((newsletter_name, subscribers[newsletter_id], readers.get(newsletter_id,0)))

        return stats

    def emails(self):
        """ email, newsletters sent, number of read newsletters """

        self.s.cursor.execute('''
            select email_id
            from emails''')
        email_ids = [r[0] for r in self.s.cursor.fetchall()]

        subscribtion = {}
        for email_id in email_ids:
            self.s.cursor.execute('''
                select count(newsletter_id)
                from bindings
                where email_id=?
                group by email_id''',
                (email_id,))
            subscribtion[email_id] = self.s.cursor.fetchone()[0]

        sent = {}
        for email_id in email_ids:
            self.s.cursor.execute('''
                select count(newsletter_id)
                from clicks
                where email_id=?
                group by email_id''',
                (email_id,))       # and date not none!
            result = self.s.cursor.fetchone()
            if result is not None:
                sent[email_id] = result[0]

        stats = []
        for email_id in subscribtion.keys():
            email = self.s.getEmail(email_id)
            stats.append((email, subscribtion[email_id], sent.get(email_id,0)))

        return stats

    def email_newsletters(self):
        """ for each email in clicks returns the list of read newsletters """
        email_ids = {}
        self.s.cursor.execute('''
            select distinct email_id
            from clicks''')
        results = self.s.cursor.fetchall()
        if results is not None:
            for r in results:
                email_ids[r[0]] = []

        emails = {}
        for id in email_ids.keys():
            self.s.cursor.execute('''
                select newsletter_id
                from clicks
                where email_id=?''',
                (id,))
            results = self.s.cursor.fetchall()
            if results is not None:
                email = self.s.getEmail(id)
                emails[email] = []
                for r in results:
                    name = self.s.getNewsletter(r[0])
                    emails[email].append(name)

        return emails

    def newsletter_emails(self):
        """ for each newsletter in clicks return the list of email having read """
        newsletter_ids = {}
        self.s.cursor.execute('''
            select distinct newsletter_id
            from clicks''')
        results = self.s.cursor.fetchall()
        if results is not None:
            for r in results:
                newsletter_ids[r[0]] = []

        newsletters = {}
        for id in newsletter_ids.keys():
            self.s.cursor.execute('''
                select email_id
                from clicks
                where newsletter_id=?''',
                (id,))
            results = self.s.cursor.fetchall()
            if results is not None:
                name = self.s.getNewsletter(id)
                newsletters[name] = []
                for r in results:
                    email = self.s.getEmail(r[0])
                    newsletters[name].append(email)

        return newsletters


class CommandGenerator(object):
    """ """
    description = "NiceSpammer reports."

    def run(self):
        """ """
        parser = OptionParser()
        parser.add_option("-n",
                          "--newsletters",
                          dest="newsletters",
                          action="store_true",
                          default=False,
                          help="Stats about newsletters",)
        parser.add_option("-e",
                          "--emails",
                          dest="emails",
                          action="store_true",
                          default=False,
                          help="Stats about emails",)
        parser.add_option("-r",
                          "--read-newsletters",
                          dest="read_newsletter",
                          action="store_true",
                          default=False,
                          help="For each email in clicks returns the list of read newsletters",)
        parser.add_option("-s",
                          "--newsletters-emails",
                          dest="newsletter_emails",
                          action="store_true",
                          default=False,
                          help="For each newsletter in clicks return the list of email having read",)
        # missing the option for output format: csv, json, ...
        # for now only json but use the library for correct conversion

        (options, args) = parser.parse_args()
        #print options, args

        if len(args) < 1:
            parser.error('missing file')
            return -1

        r = Reports(args[0])
        if options.newsletters == True:
            return r.newsletters()
        elif options.emails == True:
            return r.emails()
        elif options.read_newsletter == True:
            return r.email_newsletters()
        elif options.newsletter_emails == True:
            return r.newsletter_emails()

        return 0


def main():
    """Entry point for setuptools.
    """
    sys.exit(CommandGenerator().run())

if __name__ == '__main__':
    main()
