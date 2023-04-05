# -*- coding: utf-8 -*-

import os

import webapp2

from webapp2_extras.routes import HandlerPrefixRoute, RedirectRoute

from models import PostUser
from handlers import InputArticlesHandler, EditPageHandler, DeleteItemHandler, MateArticleHandler

def _generate_secret_key():
    return os.urandom(256).encode("hex")

webapp2_config = {}
webapp2_config['webapp2_extras.sessions'] = {
    # 'secret_key': "".format(_generate_secret_key())
    'secret_key': '_PUT_KEY_HERE_YOUR_SECRET_KEY_'
}
webapp2_config['webapp2_extras.auth'] = {
    'user_model': PostUser
}

application = webapp2.WSGIApplication([
    HandlerPrefixRoute(r'index.', [
        webapp2.Route('/', handler='MainHandler', name='index'),
        webapp2.Route('/admin', handler='AdminHandler', name='admin'),
        webapp2.Route('/member_list', handler='UserListHandler', name='members'),
        webapp2.Route('/connect', handler='MakeMateHandler', name='connect')
    ]),
    HandlerPrefixRoute(r'auth.', [
        webapp2.Route('/login', handler='LoginHandler', name='login'),
        webapp2.Route('/logout', handler='LogoutHandler', name='logout'),
        webapp2.Route('/register', handler='SignupHandler', name='register')
    ]),
    HandlerPrefixRoute(r'handlers.', [
        webapp2.Route('/secure', handler='SecureRequestHandler', name='secure'),
        webapp2.Route('/uploaded', handler='ImageUploadHandler', name='upload'),
        webapp2.Route('/confirm', handler='PersistArticlesHandler', name='confirm'),
        webapp2.Route('/inner', handler='RetrieveImageListHandler', name='list'),
        # webapp2.Route('/update', handler='EditPageHandler', name='edit')
        # webapp2.Route('/remove', handler='DeleteItemHandler', name='delete'),
        # webapp2.Route('/delete_judge', handler='DeleteExcuteHandler', name='delete'),
        webapp2.Route('/mate', handler='MatesContentsHandler', name='mates')
    ]),
    # After redirect, get method has two params
    (r'/view_image/([^/]+)?', InputArticlesHandler),
    (r'/edit([^/]+)?', EditPageHandler),
    (r'/delete([^/]+)?', DeleteItemHandler),
    (r'/focus([^/]+)?', MateArticleHandler),
    # (r'/connect([^/]+)?', MakeMateHandler)
], debug=True, config=webapp2_config)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
