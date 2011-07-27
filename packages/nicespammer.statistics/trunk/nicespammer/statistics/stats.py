import time
import uuid
from pysqlite2 import dbapi2 as sqlite3

class Stats(object):

    def __init__(self, path='./example.db', catcher_url='http://localhost:8080'):
          self.conn = sqlite3.connect(path)
          self.cursor = self.conn.cursor()
          self.catcher_url = catcher_url

    def getEmailId(self, email):
        self.cursor.execute('''
            select email_id from emails where email==?''', (email,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

    def getEmail(self, email_id):
        self.cursor.execute('''
            select email from emails where email_id==?''', (email_id,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

    def getEmailUiid(self, email):
        self.cursor.execute('''
            select email_uuid from emails where email==?''', (email,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

    def addEmail(self, email, email_uuid=None):
        email_id = self.getEmailId(email)
        if not email_id:
            if email_uuid is None:
                email_uuid = uuid.uuid4().hex
            self.cursor.execute('''
                insert into emails (email, email_uuid) values (?,?)''',
                (email, email_uuid))
            self.cursor.execute('''select last_insert_rowid();''')
            email_id = self.cursor.fetchone()[0]
            self.conn.commit()
        else:
            # do check if email and email_uuid are binded or update the uuid?
            email_uuid = self.getEmailUiid(email)
        return email_id, email_uuid

    def existsEmailId(self, email_id):
        self.cursor.execute('''
            select * from emails where email_id=?''',
            (email_id,))
        if self.cursor.fetchone() is None:
            return False
        else:
            return True

    def getNewsletterId(self, newsletter_name):
        self.cursor.execute('''
            select newsletter_id from newsletters where newsletter_name==?''',
            (newsletter_name,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

    def getNewsletter(self, newsletter_id):
        self.cursor.execute('''
            select newsletter_name from newsletters where newsletter_id==?''',
            (newsletter_id,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

    def getNewsletterUuid(self, newsletter_name):
        self.cursor.execute('''
            select newsletter_uuid from newsletters where newsletter_name==?''',
            (newsletter_name,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

    def addNewsletter(self, newsletter_name):
        newsletter_id = self.getNewsletterId(newsletter_name)
        if newsletter_id is not None:
            raise Exception('Exists')
        else:
            newsletter_uuid = uuid.uuid4().hex
            self.cursor.execute('''
                insert into newsletters (newsletter_name, newsletter_uuid) values (?,?)''',
                (newsletter_name, newsletter_uuid))
            self.cursor.execute('''select last_insert_rowid();''')
            last = self.cursor.fetchone()[0]
            self.conn.commit()
            return last, newsletter_uuid

    def getNewsletterIds(self, email_id):
        self.cursor.execute('''
            select newsletter_id from bindings where email_id==?''',
            (email_id,))
        results = self.cursor.fetchall()
        if results is not None:
            return [r[0] for r in results]
        else:
            return []

    def existsNewsletterId(self, newsletter_id):
        self.cursor.execute('''
            select * from newsletters where newsletter_id=?''',
            (newsletter_id,))

        if self.cursor.fetchone() is None:
            return False
        else:
            return True

    def existsBinding(self, newsletter_id, email_id):
        self.cursor.execute('''
            select *
            from bindings
            where newsletter_id=? and email_id=?''',
            (newsletter_id,email_id))

        if self.cursor.fetchone() is None:
            return False
        else:
            return True

    def bindMail(self, email_id, newsletter_id):
        if not self.existsNewsletterId(newsletter_id):
            raise Exception('invalid newsletter')

        if not self.existsEmailId(email_id):
            raise Exception('invalid email')

        if self.existsBinding(newsletter_id, email_id):
            raise Exception('just bound')

        self.cursor.execute('''
            insert into bindings values (?,?)''',
            (newsletter_id, email_id))
        self.conn.commit()

    def image_tag(self, newsletter_uuid, email_uuid):
        return """<img alt="" src="%s/%s/%s/1.png" width=1 height=1>"""% \
            (self.catcher_url, newsletter_uuid, email_uuid)

    def addImage(self, html, newsletter_uuid, email_uuid):
        end_tag_pos = html.index('</body>')
        tmp = html[:end_tag_pos]
        tmp += self.image_tag(newsletter_uuid, email_uuid)
        tmp += html[end_tag_pos:]
        return tmp

    def getNewsletterIdFromUiid(self, uuid):
        self.cursor.execute('''
            select newsletter_id from newsletters where newsletter_uuid=?''',
            (uuid,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            raise Exception('invalid newsletter uuid')

    def getEmailIdFromUiid(self, uuid):
        self.cursor.execute('''
            select email_id from emails where email_uuid=?''', (uuid,))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            raise Exception('invalid email uuid')

    def clicksFor(self, newsletter_id, email_id):
        self.cursor.execute('''
            select * from clicks where newsletter_id=? and email_id=?''',
            (newsletter_id, email_id))
        return len(self.cursor.fetchall())

    def click(self, newsletter_id, email_id):

        if not self.existsNewsletterId(newsletter_id):
            raise Exception('invalid newsletter id')

        if not self.existsEmailId(email_id):
            raise Exception('invalid email id')

        if not newsletter_id in self.getNewsletterIds(email_id):
            raise Exception('email not bound to newsletter')

        if self.clicksFor(newsletter_id, email_id) == 0:
            self.cursor.execute('''
                insert into clicks values (?,?,?)''',
                (newsletter_id, email_id, time.strftime('%Y-%m-%d %H:%M')))
            self.conn.commit()
