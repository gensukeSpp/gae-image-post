# -*- coding: utf-8 -*-

import os

from google.appengine.ext import ndb
from google.appengine.api import users
# from index import pass_admin

import webapp2

from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

import webapp2_extras.appengine.auth.models as auth_models

from webapp2_extras import jinja2

from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import DataRequired

def jinja2_factory(app):
    "True ninja method for attaching additional globals/filters to jinja"

    config = {'template_path': app.config.get('templates_path', 'template'),}
    j = jinja2.Jinja2(app, config=config)
    j.environment.globals.update({
    	# 'config': app.config, 
        'uri_for': webapp2.uri_for,
    })
    return j

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(backend="datastore")

    def dispatch(self):
        # self.session_store = sessions.get_store(request=self.request)
        # if self.session_store.get_session().new:
        #     #modified session will be re-sent
        #     self.session_store.get_session().update({})
        try:
            super(BaseHandler, self).dispatch()
        finally:
            # Save the session after each request        
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth(request=self.request)
    
    @webapp2.cached_property
    def user(self):
        user = self.auth.get_user_by_session()
        return user
    
    @webapp2.cached_property
    def user_model(self):
        # self.auth.store.user_model is used to refer to our user model
        user_model, timestamp = self.auth.store.user_model.get_by_auth_token(
                self.user['user_id'], 
                self.user['token']) if self.user else (None, None)
        return user_model

    # app = webapp2.WSGIApplication([
    #     # ... all of our applications URL routes
    #     ], config=config)
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(factory=jinja2_factory, app=self.app)

    def render_response(self, _template, **context):
        static_dir = ['static', 'css']
        current_dir = os.getcwd()
        add_path = os.path.join(current_dir, *static_dir)
        ctx = {
            'user': self.user_model,
            'static_path': add_path
        }
        # 2つの辞書オブジェクトを連結（合体）させる
        # 辞書オブジェクト.update(新しく連結させたい辞書オブジェクト)
        ctx.update(context)
        rv = self.jinja2.render_template(_template, **ctx)
        self.response.write(rv)

class SignupForm(Form):
    nickname = StringField('NickName', 
                    [validators.DataRequired()])
    password = PasswordField('Password', 
                    [validators.DataRequired(), 
                     validators.EqualTo('password_confirm', 
                                    message="Passwords must match.")])
    password_confirm = PasswordField('Confirm Password', 
                        [validators.DataRequired()])

class SignupHandler(BaseHandler):
    "Serves up a signup form, creates new users"
    # @pass_admin
    def get(self):

        # I Would like to be Decorator
        admin = users.is_current_user_admin()
        if not admin:
            self.response.write('You are not an administrator.')
        else:
            self.render_response("register.html", form=SignupForm())

    def post(self):

        form = SignupForm(self.request.POST)
        error = None
        if form.validate():
            # ensure that each user’s nickname address is unique
            """
                 When creating a user,
                 it first tries to create new unique objects for each unique property.
                 It uses transactions to see if the unique properties already exist and only creates them if they do not
                 すでにthe unique propertiesが存在するかどうか見るために、トランザクションを用いて、それらが存在しないならば、作成するだけである。
            """

            success, info = self.auth.store.user_model.create_user(
                "auth:" + form.nickname.data,
                unique_properties=['nickname'],
                nickname= form.nickname.data,
                password_raw= form.password.data)

            if success:
                self.auth.set_session(self.auth.store.user_to_dict(info), remember=True)
                return self.redirect_to("login")
            else:
                error = "That nickname is already in use. if 'nickname' in user else Something has gone horrible wrong."
                                         
        self.render_response("register.html", form=form, error=error)

class LoginForm(Form):
    nickname = StringField('NickName', 
                    [validators.DataRequired()])
    password = PasswordField('Password', 
                [validators.DataRequired()])

class LoginHandler(BaseHandler):

    def get(self):

        # user = users.get_current_user()
        # if user:
        logout_url = users.create_logout_url('/login')
        self.render_response("login.html", form=LoginForm(), out=logout_url)
        # else:
        #     return self.redirect('/')
        
    def post(self):
        
        form = LoginForm(self.request.POST)
        error = None
        if form.validate():
            try:
                self.auth.get_user_by_password(
                        "auth:"+form.nickname.data, 
                        form.password.data)
                return self.redirect_to('secure')
            except (auth.InvalidAuthIdError, auth.InvalidPasswordError):                    
                error = "Invalid NickName / Password"
                
        self.render_response("login.html", form=form, error=error)

class LogoutHandler(BaseHandler):
    """Destroy the user session and return them to the login screen."""

    def login_required(handler):
        "Requires that a user be logged in to access the resource"
        def check_login(self, *args, **kwargs):     
            if not self.user:
                return self.redirect_to('login')
            else:
                return handler(self, *args, **kwargs)
        return check_login

    @login_required
    def get(self):
        self.auth.unset_session()
        self.redirect_to('login')
