# wsgi catcher

from paste.request import parse_formvars
from paste.response import HeaderDict
from paste.httpexceptions import HTTPNotFound

from nicespammer.statistics import stats

class Catcher(object):

    def __init__(self, filename):
        """ """
        self.filename = filename

    def __call__(self, environ, start_response):
        uri = environ.get('PATH_INFO').split('/')

        try:
            self.click(uri)
        except:
            start_response(
                '404 Not Found', [('Content-type', 'text/html')])
            return ['Not a valid entry']

        start_response('200 OK', [('Content-type', 'image/png')])
        return self.image()

    def click(self, uri):
        newsletter_id = uri[1]
        email_id = uri[2]
        s = stats.Stats(self.filename)
        s.click(newsletter_id, email_id)

    def image(self):
          f = open('1.png')
          img = f.read()
          f.close()
          return img


def app_factory(global_config=None, **local_conf):
    app = Catcher(local_conf['filename'])
    return app

if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app_factory(None,
                                 filename='example.db'),
                                 host='127.0.0.1',
                                 port='8080')