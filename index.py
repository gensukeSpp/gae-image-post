# -*- coding: utf-8 -*-

# [START all]

import os
import cgi

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

from models import PostUser

class MainHandler(webapp2.RequestHandler):

    def get(self):

        # user = users.get_current_user()
        admin = users.is_current_user_admin()
        # if user:
        #     return self.redirect('/login')
        if admin:
            return self.redirect('/admin')
        else:
            # return self.redirect('/login')
            login_url = users.create_login_url('/')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)

            self.response.write('''
                <html><body>
                If you hope to perform in admin page, You have to Login in Google Account from here.<br>''' + 
                '''{}</body></html>
                '''.format(greeting))

class AdminHandler(webapp2.RequestHandler):

    def get(self):

        admin = users.is_current_user_admin()
        if admin:
            self.response.write('''
                <html>
                <title>トップ - 管理者用ページ</title>
                <body>
                You are an administrator.
                <a href="./login">**Login**</a>
                <a href="./register">**MemberRegister**</a>
                <a href="./member_list">**MemberList**</a>
                </body></html>
                ''')
        else:
            self.response.write('You are not an administrator.')

# I Would like to be Decorator
def pass_admin(func):
    def inner(self, *args, **kwargs):
        if users.get_current_user():
            if not users.is_current_user_admin():
                webapp2.abort(401)
            return func(self, *args, **kwargs)
        return self.redirect(users.create_login_url(request.url))
    return inner

class UserListHandler(webapp2.RequestHandler):

    @pass_admin
    def get(self):

        # I Would like to be Decorator
        # admin = users.is_current_user_admin()
        # if not admin:
        #     self.response.write('You are not an administrator.')
        # else:
        member_keys = PostUser.query().fetch(keys_only=True)
        member_objs = ndb.get_multi(member_keys)
        self.response.out.write('''<html><body>
            <head>
            <meta charset="UTF-8">
            <title>メンバー一覧 - 管理者用ページ</title>
            <link rel="stylesheet" href="../static/css/style.css">
            </head>''')

        for member_obj in member_objs:
            self.response.out.write('''<div class="mate-outside">''')
            self.response.out.write('''
                <div class="keyid-area">Member Name: {0}
                <form class="form" action="/connect" method="GET">
                    <input type="text" value={1} name="specify_user_id" />
                    <button type="submit" class="">Select</button>
                </form></div>
                '''.format(member_obj.nickname, member_obj.key.id()))

            mate_objs = ndb.get_multi(member_obj.mates)
            self.response.out.write('''<div class="mate-listarea">''')            
            self.response.out.write('''Mates:　''')            
            for mate_obj in mate_objs:
                self.response.out.write('''
                    <div class="mate-oneline">{}　</div>'''.format(mate_obj.nickname))

            self.response.out.write('''</div><!-- .mate-listarea -->
                </div><!-- .mate-outside -->''')
        self.response.out.write('''</body></html>''')

class MakeMateHandler(webapp2.RequestHandler):

    @pass_admin
    def get(self):

        if os.environ['REQUEST_METHOD'] != 'GET':
            return self.response.out.write('不正なアクセスです。')
            sys.exit()

        form = cgi.FieldStorage()

        if not form.has_key('specify_user_id'):
            return self.response.out.write('ありません。')
            sys.exit()
        else:
            search_id = form['specify_user_id'].value
            specify_user_obj = PostUser.get_by_id(int(search_id))

        self.response.out.write('''<html>
            <title>メンバーコネクト - 管理者用ページ</title>
            <body>
            {}さんが、誰と　？
            <form class="form" method="POST">
                <input type="text" name="mate_key" />
                <button type="submit" class="">つながる</button>
            </form>'''.format(specify_user_obj.nickname))
        self.response.out.write('<a href="./member_list">戻る</a><br><br>')
        self.response.out.write('''</body></html>''')

        member_keys = PostUser.query().fetch(keys_only=True)
        member_objs = ndb.get_multi(member_keys)
        for member_obj in member_objs:
            self.response.out.write('''
                <p>Member:{0}, 
                {1}</p>'''.format(member_obj.nickname, member_obj.key.id()))

    def post(self):

        form = cgi.FieldStorage()
        search_id = form['specify_user_id'].value

        specify_user_key = ndb.Key('PostUser', int(search_id))
        specify_user_obj = specify_user_key.get()

        mate_id = self.request.get('mate_key')
        mate_side_key = ndb.Key('PostUser', int(mate_id))

        specify_user_obj.mates.append(mate_side_key)
        specify_user_obj.put()

        other_side_obj = mate_side_key.get()
        other_side_obj.mates.append(specify_user_key)
        other_side_obj.put()

        self.redirect('/member_list')

# [END all]
