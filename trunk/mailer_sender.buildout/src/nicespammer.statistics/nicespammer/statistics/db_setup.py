import sys
from pysqlite2 import dbapi2 as sqlite3

def creation(path='./example.db'):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    # Table Emails
    c.execute('''
        create table emails
        (email_id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT)''')

    # Table Newsletters
    c.execute('''
        create table newsletters
        (newsletter_id INTEGER PRIMARY KEY AUTOINCREMENT, newsletter_name TEXT)''')

    # Table Bindings
    c.execute('''
        create table bindings
        (newsletter_id INTEGER, email_id INTEGER)''')

    # Table Clicks: newsletter-id mail-id date
    c.execute('''
        create table clicks
        (newsletter_id INTEGER, email_id INTEGER, date TEXT)''')

    conn.commit()
    c.close()


if __name__=='__main__':
    creation(sys.argv[1])
