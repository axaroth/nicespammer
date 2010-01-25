#! /usr/bin/env python

import sys, os, shutil
from optparse import  OptionParser

from nicespammer.mailgenerator import MailGenerator

def empty_mails(src):
    f = open(src, 'w')
    f.write('mail\n')
    f.close()

class CommandGenerator(object):
    """ """

    description = "Generate mails."

    def run(self):
        """ """
        usage = "usage: %prog [options] directory"
        parser = OptionParser(usage=usage, description=self.description)
        parser.add_option(
                  "-p",
                  "--purge",
                  action="store_true",
                  dest="purge",
                  default=False,
                  help="Remove emails")
        parser.add_option(
                  "-f",
                  "--force",
                  dest="address",
                  default=None,
                  help="Send an email to specified address")
        (options, args) = parser.parse_args()

        if  len(args) != 1:
            parser.error("Missing newsletter directory.")
            sys.exit(-1)

        if hasattr(options, 'address'):
            # simple check
            if '@' not in options.address:
                parser.error("Invalid email address.")
                sys.exit(-1)

        newsletter_path = args[0]
        mg = MailGenerator(newsletter_path, options.address)
        mg.massive_send()

        if options.purge:
            src = mg.csv_file_path
            if os.path.exists(src):
                i = 0
                dst = src+'.%i'%i
                while os.path.exists(dst):
                    i += 1
                    dst = src+'.%i'%i
                    if i > 100:
                        raise Exception('Reached max number of backup files')

                shutil.move(src, dst)
                empty_mails(src)
            print 'Removed emails'

        return 0

def main():
    """Entry point for setuptools.
    """
    sys.exit(CommandGenerator().run())

if __name__ == '__main__':
    main()

