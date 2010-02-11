import os
import unittest

from nicespammer.statistics import stats
from nicespammer.statistics import db_setup
from nicespammer.statistics import report

class Newsletters(object):

    def __init__(self, user):
        self.subscribed = user[1]
        self.read= user[2]

##

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.path = './test.db'
        if os.path.exists(self.path):
            os.remove(self.path)
        db_setup.creation(self.path)
        self.s = stats.Stats(self.path)

    def tearDown(self):
        self.s.conn.commit()
        self.s.cursor.close()


class AddingTestCase(BaseTestCase):

    def testUserAndNewsletter(self):
        email_id = self.s.addEmail('riccardo@reflab.it')
        self.assertEqual(email_id, self.s.getEmailId('riccardo@reflab.it'))
        self.assertEqual(email_id, self.s.addEmail('riccardo@reflab.it'))

        newsletter_id = self.s.addNewsletter('a newsletter')
        self.assertEqual(newsletter_id, self.s.getNewsletterId('a newsletter'))

        self.failUnlessRaises(Exception, self.s.addNewsletter, 'a newsletter')

        self.s.bindMail(email_id, newsletter_id)
        self.failUnless(newsletter_id in self.s.getNewsletterIds(email_id))

        # checks binding cases
        self.failUnlessRaises(Exception, self.s.bindMail, '2', newsletter_id)
        self.failUnlessRaises(Exception, self.s.bindMail, email_id, '2')
        self.failUnlessRaises(Exception, self.s.bindMail, email_id, newsletter_id)

        # another newsletter
        newsletter_id = self.s.addNewsletter('another newsletter')
        self.s.bindMail(email_id, newsletter_id)
        self.failUnless(newsletter_id in self.s.getNewsletterIds(email_id))

    def testNewslettersMethods(self):
        newsletter_name = 'a newsletter'
        newsletter_id = self.s.addNewsletter(newsletter_name)

        self.failUnless(self.s.getNewsletterId(newsletter_name) == newsletter_id)
        self.failUnless(self.s.getNewsletter(newsletter_id) == newsletter_name)

    def testEmailMethods(self):
        email = 'info@reflab.it'
        email_id = self.s.addEmail(email)

        self.failUnless(self.s.getEmailId(email) == email_id)
        self.failUnless(self.s.getEmail(email_id) == email)


class StatsTestCase(BaseTestCase):

    def setUp(self):
        super(StatsTestCase, self).setUp()
        self.s.addEmail('riccardo@reflab.it')
        self.s.addNewsletter('a newsletter')

    def testHtml(self):
        email_id = self.s.getEmailId('riccardo@reflab.it')
        newsletter_id = self.s.getNewsletterId('a newsletter')

        base = "<html><body> ...</body></html>"
        html = self.s.addImage(base, newsletter_id, email_id)
        self.failUnless(str(newsletter_id) in html)
        self.failUnless(str(email_id) in html)

    def testClickAndStats(self):
        email_id = self.s.getEmailId('riccardo@reflab.it')
        newsletter_id = self.s.getNewsletterId('a newsletter')

        self.assertEqual(self.s.clicksFor(newsletter_id, email_id), 0)

        # without bind
        self.failUnlessRaises(Exception, self.s.click, (newsletter_id, email_id))

        # with binding
        self.s.bindMail(email_id, newsletter_id)

        # first click
        self.s.click(newsletter_id, email_id)
        self.assertEqual(self.s.clicksFor(newsletter_id, email_id), 1)

        # another click
        self.s.click(newsletter_id, email_id)
        self.assertEqual(self.s.clicksFor(newsletter_id, email_id), 1)

        # checks for exceptions
        fake_newsletter_id = 2
        fake_email_id = 2

        self.failIf(self.s.existsNewsletterId(fake_newsletter_id))
        self.failIf(self.s.existsEmailId(fake_email_id))

        self.failUnlessRaises(Exception, self.s.click, (fake_newsletter_id, email_id))
        self.failUnlessRaises(Exception, self.s.click, (newsletter_id, fake_email_id))
        self.failUnlessRaises(Exception, self.s.click, (fake_newsletter_id, fake_email_id))


class ReportTestCase(BaseTestCase):

    def setUp(self):
        super(ReportTestCase, self).setUp()

        self.newsletter_id = self.s.addNewsletter('a newsletter')
        self.email_ids = []
        for i in range(1,10):
            email = 'user%s@reflab.it'%i
            self.s.addEmail(email)
            email_id = self.s.getEmailId(email)
            self.s.bindMail(email_id, self.newsletter_id)
            self.email_ids.append(email_id)

        self.r = report.Reports(self.path)

    def testNewsletters(self):

        newsletters = self.r.newsletters()

        # subscribers
        self.assertEqual(newsletters[0][0], 'a newsletter')
        self.assertEqual(newsletters[0][1], 9)

        # readers
        self.assertEqual(newsletters[0][2], 0)

        self.s.click(self.newsletter_id, self.email_ids[0])
        self.assertEqual(self.r.newsletters()[0][2], 1)

        self.s.click(self.newsletter_id, self.email_ids[1])
        self.assertEqual(self.r.newsletters()[0][2], 2)

        # duplicate click
        self.s.click(self.newsletter_id, self.email_ids[1])
        self.assertEqual(self.r.newsletters()[0][2], 2)

    def testEmails(self):

        for item in self.r.emails():
            newsletters = Newsletters(item)
            self.assertEqual(newsletters.subscribed, 1)
            self.assertEqual(newsletters.read, 0)

        # now user 0 click
        self.s.click(self.newsletter_id, self.email_ids[0])
        newsletters = Newsletters(self.r.emails()[0])
        self.assertEqual(newsletters.subscribed, 1)
        self.assertEqual(newsletters.read, 1)

        # add another newsletter
        another_newsletter_id = self.s.addNewsletter('another newsletter')

        # check user 0 before bind
        newsletters = Newsletters(self.r.emails()[0])
        self.assertEqual(newsletters.subscribed, 1)
        self.assertEqual(newsletters.read, 1)

        # check other users
        for item in self.r.emails()[1:]:
            newsletters = Newsletters(item)
            self.assertEqual(newsletters.subscribed, 1)
            self.assertEqual(newsletters.read, 0)

        # check user 0 after bind
        self.s.bindMail(self.email_ids[0], another_newsletter_id)
        newsletters = Newsletters(self.r.emails()[0])
        self.assertEqual(newsletters.subscribed, 2)
        self.assertEqual(newsletters.read, 1)

        # check user 0 after click another newsletter
        self.s.click(another_newsletter_id, self.email_ids[0])
        newsletters = Newsletters(self.r.emails()[0])
        self.assertEqual(newsletters.subscribed, 2)
        self.assertEqual(newsletters.read, 2)

    def testUserNewsletters(self):
        self.assertEqual(self.r.email_newsletters(), {})

        self.s.click(self.newsletter_id, self.email_ids[0])
        self.assertEqual(len(self.r.email_newsletters()['user1@reflab.it']), 1)

        self.s.click(self.newsletter_id, self.email_ids[1])
        self.assertEqual(len(self.r.email_newsletters()['user2@reflab.it']), 1)

        n = self.s.addNewsletter('another newsletter')
        self.s.bindMail(self.email_ids[0], n)
        self.s.click(n, self.email_ids[0])
        self.assertEqual(len(self.r.email_newsletters()['user1@reflab.it']), 2)
        self.assertEqual(len(self.r.email_newsletters()['user2@reflab.it']), 1)

    def testNewsletterEmails(self):
        self.assertEqual(self.r.newsletter_emails(), {})

        self.s.click(self.newsletter_id, self.email_ids[0])
        self.assertEqual(len(self.r.newsletter_emails()['a newsletter']), 1)

        self.s.click(self.newsletter_id, self.email_ids[1])
        self.assertEqual(len(self.r.newsletter_emails()['a newsletter']), 2)

        n = self.s.addNewsletter('another newsletter')
        self.s.bindMail(self.email_ids[0], n)
        self.s.click(n, self.email_ids[0])
        self.assertEqual(len(self.r.newsletter_emails()['a newsletter']), 2)
        self.assertEqual(len(self.r.newsletter_emails()['another newsletter']), 1)

if __name__ == '__main__':
    suite= unittest.makeSuite(AddingTestCase)
    suite.addTest(unittest.makeSuite(StatsTestCase))
    suite.addTest(unittest.makeSuite(ReportTestCase))
    runner = unittest.TextTestRunner()
    runner.run(suite)



