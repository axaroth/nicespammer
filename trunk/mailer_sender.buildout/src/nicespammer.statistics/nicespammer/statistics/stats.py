import time
from pysqlite2 import dbapi2 as sqlite3 

class Stats(object):

    def __init__(self, path='./example.db'):
          self.conn = sqlite3.connect(path)
          self.cursor = self.conn.cursor()

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

    def addEmail(self, email):
        email_id = self.getEmailId(email)
        if not email_id:
            self.cursor.execute('''
                insert into emails (email) values (?)''', (email,))
            self.cursor.execute('''select last_insert_rowid();''')
            email_id = self.cursor.fetchone()[0]
            self.conn.commit()
        return email_id

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

    def addNewsletter(self, newsletter_name):
        newsletter_id = self.getNewsletterId(newsletter_name)
        if newsletter_id is not None:
            raise Exception('Exists')
        else:
            self.cursor.execute('''
                insert into newsletters (newsletter_name) values (?)''',
                (newsletter_name,))
            self.cursor.execute('''select last_insert_rowid();''')
            last = self.cursor.fetchone()[0]
            self.conn.commit()
            return last

    def getNewsletterIds(self, email_id):
        self.cursor.execute('''
            select newsletter_id from bindings
            where email_id==?''',
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

    def bindMail(self, email_id, newsletter_id):
        self.cursor.execute('''
            insert into bindings values (?,?)''',
            (newsletter_id, email_id))
        self.conn.commit()

    def image_tag(self, host, newsletter_id, email_id):
        return """<img alt="" src="%s/stats/%s/%s/1.png" width=1 height=1>"""% \
            (host, newsletter_id, email_id)

    def addImage(self, html, newsletter_id, email_id):
        end_tag_pos = html.index('</html>')
        tmp = html[:end_tag_pos]
        tmp += self.image_tag('host', newsletter_id, email_id)
        tmp += html[end_tag_pos:]
        return tmp


    def clicksFor(self, newsletter_id, email_id):
        self.cursor.execute('''
            select * from clicks where newsletter_id=? and email_id=?''',
            (newsletter_id, email_id))
        return len(self.cursor.fetchall())

    def click(self, newsletter_id, email_id):

        if not self.existsNewsletterId(newsletter_id):
            raise Exception('invalid newsletter')

        if not self.existsEmailId(email_id):
            raise Exception('invalid email')

        if not newsletter_id in self.getNewsletterIds(email_id):
            raise Exception('email not binded to newsletter')

        if self.clicksFor(newsletter_id, email_id) == 0:
            self.cursor.execute('''
                insert into clicks values (?,?,?)''',
                (newsletter_id, email_id, time.strftime('%Y-%m-%d %H:%M')))
            self.conn.commit()
