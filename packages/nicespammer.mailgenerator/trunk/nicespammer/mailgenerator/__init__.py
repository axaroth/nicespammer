import os
import csv
import time
import tempfile
import ConfigParser
from random import randint
import stoneagehtml
import logging
from string import Template

from iw.email import MultipartMail
from nicespammer.statistics import stats

def makeTempPath(spool):
    """ Helper to create a temp file name safely """
    """ based on MaildropHost code """
    temp_path = os.path.join(spool, str(randint(100000, 9999999)))

    while os.path.exists(temp_path):
        temp_path = os.path.join(spool, str(randint(100000, 9999999)))

    return temp_path


class MailGenerator(object):

    def __init__(self, newsletter_path, options_file='nicespammer.cfg'):
        self.newsletter_path = newsletter_path
        self.generated_path = os.path.join(self.newsletter_path, 'generated.info')
        self.options_file = options_file

        self.setup_logs()
        self.parse_newsletter_conf()
        self.parse_mailgenerator_conf()

    def setup_logs(self):
        self.log_path = os.path.join(self.newsletter_path, 'newsletter.log')
        logging.basicConfig(filename=self.log_path,
                            level=logging.DEBUG,
                            format="%(asctime)s - %(levelname)s - %(message)s")

    def parse_newsletter_conf(self):
        """ Parse configuration file named newsletter.cfg in newsletter folder """
        config_file = open(os.path.join(self.newsletter_path, 'newsletter.cfg'))
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(config_file)
        config_file.close()

        # must be present a column named 'mail'
        self.csv_file_path = os.path.join(self.newsletter_path,
                                          self.config.get('default', 'mails'))

    def parse_mailgenerator_conf(self):
        """ read the path to DB """
        config_file = open(self.options_file, 'r')
        self.mailgenerator_config = ConfigParser.ConfigParser()
        self.mailgenerator_config.readfp(config_file)
        config_file.close()

        self.db_path = self.mailgenerator_config.get('default', 'filename')
        self.catcher_url = self.mailgenerator_config.get('default', 'catcher_url')

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

    def generate_mail_with_stats(self, newsletter, email):
        """ """
        s =  stats.Stats(self.db_path, self.catcher_url)
        email_id = s.addEmail(email)
        newsletter_id = s.getNewsletterId(newsletter)
        if newsletter_id is None:
            newsletter_id = s.addNewsletter(newsletter)
        s.bindMail(email_id, newsletter_id)

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
            html_mail = s.addImage(html_mail, newsletter_id, email_id)
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

        if self.config.has_option('default', 'stats'):
            add_stats = self.config.getboolean('default', 'stats')
        else:
            add_stats = False

        if not add_stats:
            mail_template = unicode(self.generate_mail())
        else:
            newsletter = self.config.get('default', 'newsletter-name')

        mfrom = '##From:%s\n'%self.config.get('default', 'mfrom')

        for user in users:
            email = user['mail']
            if add_stats:
                mail_template = unicode(self.generate_mail_with_stats(newsletter, email))

            mail  = '##To:%s\n'%email
            mail += mfrom

            mail += Template(mail_template).safe_substitute(
                      newsletter_to_addr=email,
                      **user)

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
            now = time.strftime('%Y/%m/%d %H:%M')
            if not self.config.has_option('default', 'date'):
                date = now
            else:
                date = self.config.get('default', 'date')

            if date <= now:
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
