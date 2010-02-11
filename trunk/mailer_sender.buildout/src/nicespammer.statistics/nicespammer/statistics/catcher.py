# wsgi catcher
import sys
import os
import ConfigParser

from paste import httpserver
from paste.request import parse_formvars
from paste.response import HeaderDict
from paste.httpexceptions import HTTPNotFound

from nicespammer.statistics import stats
import nicespammer.statistics as PACKAGE_PATH

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
        newsletter_id = int(uri[1])
        email_id = int(uri[2])
        s = stats.Stats(self.filename)
        s.click(newsletter_id, email_id)

    def image(self):
        f = open(os.path.join(PACKAGE_PATH.__path__[0], '1.png'))
        img = f.read()
        f.close()
        return img


def app_factory(global_config=None, **local_conf):
    app = Catcher(local_conf['filename'])
    return app

def main():
    """ """
    config_file = open(os.path.join(sys.argv[1]))
    config = ConfigParser.ConfigParser()
    config.readfp(config_file)
    config_file.close()

    httpserver.serve(
        app_factory(
            None,
            filename=config.get('default', 'filename')
            ),
        host=config.get('catcher', 'host'),
        port=config.get('catcher', 'port')
        )
    sys.exit(0)

if __name__ == '__main__':
    main()
