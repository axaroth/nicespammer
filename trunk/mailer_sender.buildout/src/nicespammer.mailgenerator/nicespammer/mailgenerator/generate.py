#! /usr/bin/env python

import sys
import os
import shutil
from optparse import  OptionParser

from nicespammer.mailgenerator import MailGenerator

def empty_mails(src):
    f = open(src, 'w')
    f.write('mail\n')
    f.close()

def listdirs(src_folder):
    paths = []
    for (dirpath, dirnames, filenames) in os.walk(src_folder):
        for name in dirnames:
            path = os.path.join(src_folder, name)
            conf = os.path.join(path, 'newsletter.cfg')
            if os.path.exists(conf):
                paths.append(path)
    return paths


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
                  "-a",
                  "--address",
                  dest="address",
                  default=None,
                  help="Generate an email for specified address (imply -f)")
        parser.add_option(
                  "-f",
                  "--force",
                  action="store_true",
                  dest="force",
                  default=False,
                  help="Generate emails now")
        parser.add_option(
                  "-c",
                  "--container",
                  action="store_true",
                  dest="isContainer",
                  default=False,
                  help="The path is to a container of newsletter configurations")
        (options, args) = parser.parse_args()

        if  len(args) != 1:
            parser.error("Missing newsletter directory.")
            return -1

        if options.address is not None:
            # simple check
            if '@' not in options.address:
                parser.error("Invalid email address.")
                return -1

        path = args[0]
        if options.isContainer == True:
            newsletter_paths = listdirs(path)
        else:
            newsletter_paths = [path, ]

        for newsletter_path in newsletter_paths:

            print "Go for: ", newsletter_path

            mg = MailGenerator(newsletter_path)

            if options.address is not None:
                mg.generate_single_mail(options.address)
            elif options.force:
                mg.generate()
            else:
                mg.check_and_generate()

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

