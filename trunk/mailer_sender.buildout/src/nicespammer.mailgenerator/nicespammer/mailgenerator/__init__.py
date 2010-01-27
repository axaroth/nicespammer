import os
import csv
import time
import tempfile
import ConfigParser
from random import randint
import stoneagehtml
import logging

from iw.email import MultipartMail

def makeTempPath(spool):
    """ Helper to create a temp file name safely """
    """ based on MaildropHost code """
    temp_path = os.path.join(spool, str(randint(100000, 9999999)))

    while os.path.exists(temp_path):
        temp_path = os.path.join(spool, str(randint(100000, 9999999)))

    return temp_path


class MailGenerator(object):

    def __init__(self, newsletter_path):
        self.newsletter_path = newsletter_path
        self.generated_path = os.path.join(self.newsletter_path, 'generated.info')

        self.log_path = os.path.join(self.newsletter_path, 'newsletter.log')
        logging.basicConfig(filename=self.log_path,
                            level=logging.DEBUG,
                            format="%(asctime)s - %(levelname)s - %(message)s")

        self.parse_config()

    def parse_config(self):
        """ Parse configuration file named newsletter.cfg in newsletter folder """
        config_file = open(os.path.join(self.newsletter_path, 'newsletter.cfg'))
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(config_file)
        config_file.close()

        # must be present a column named 'mail'
        self.csv_file_path = os.path.join(self.newsletter_path, self.config.get('default', 'mails'))

    def generate_mail(self):
        """ Generate a template email """

        mfrom = self.config.get('default', 'mfrom')
        mto = '$newsletter_to_addr'
        subject = unicode(self.config.get('default', 'subject'), 'utf-8')

        if self.config.has_option('default', 'txt'):
            txt_path = self.config.get('default', 'txt')
            txt = open(os.path.join(self.newsletter_path, txt_path), 'r').read()
            txt_mail = unicode(txt, 'utf-8')
        else:
            txt_mail = None

        if self.config.has_option('default', 'html'):
            html_path = self.config.get('default', 'html', None)
            html = open(os.path.join(self.newsletter_path, html_path), 'r').read()
            html_mail = stoneagehtml.compactify(html).decode('utf-8')
        else:
            html_mail = None

        if txt_mail is None and html_mail is None:
            txt_mail = 'No body'

        mail = MultipartMail(
                  text=txt_mail,
                  html=html_mail,
                  mfrom=mfrom,
                  mto=mto,
                  subject=subject)

        return mail

    def send_to_spool(self, mail):
        """ Create a file containing the mail.
            A temp lock file is created, the mailer should check the presence
            (as MaildropHost do)
        """
        temp_path = makeTempPath(self.config.get('default', 'spool'))
        lock_path = '%s.lck' % temp_path

        lock = open(lock_path, 'w')
        lock.write('locked')
        lock.close()

        temp = open(temp_path, 'w')
        temp.write(mail)
        temp.close()

        os.unlink(lock_path)

    def _generate(self, address=None):
        """ Read the csv file containing the email addresses, render template,
            send the mails to spool
        """
        if address is None:
            csv_file = open(self.csv_file_path, 'rt')
            users = csv.DictReader(csv_file)
        else:
            users = [dict(mail=address),]

        mail_template = unicode(self.generate_mail())
        mfrom = '##From:%s\n'%self.config.get('default', 'mfrom')
        for user in users:
            mail  = '##To:%s\n'%user['mail']
            mail += mfrom
            mail += mail_template.replace('$newsletter_to_addr', user['mail'])
            self.send_to_spool(mail)

    def generate_single_mail(self, address):
        """  """
        self._generate(address)
        logging.info('Single generation: %s'%address)

    def generate(self):
        """ """
        self._generate()
        logging.info('Forced generation.')

    def generated(self):
        """ """
        f = open(self.generated_path, 'w')
        f.write(time.strftime('%Y/%m/%d %H:%M'))
        f.close()

    def just_generated(self):
        return os.path.exists(self.generated_path)

    def check_and_generate(self):
        """ """
        if self.just_generated():
            logging.info('Just generated.')
        else:
            if not self.config.has_option('default', 'date'):
                date = time.strftime('%Y/%m/%d %H:%M') #?
            else:
                date = self.config.get('default', 'date')

            if date <= time.strftime('%Y/%m/%d %H:%M'):
                self._generate()
                self.generated() # before generate?
                logging.info('Default generation.')
            else:
                logging.info('Waiting for date.')


def testing():
    # .../mypython __init__.py
    mg = MailGenerator('./newsletter_example')
    #print mg.generate_mail()
    mg.massive_send()

if __name__=="__main__":
    testing()