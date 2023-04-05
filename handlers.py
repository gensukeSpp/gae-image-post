# -*- coding: utf-8 -*-

import os
import cgi
import sys
import urllib
from PIL import Image
from itertools import chain

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.api import app_identity
from google.appengine.ext.webapp import blobstore_handlers
from models import PostUser, ImageBlob, ExplainArticle

import webapp2
from auth import BaseHandler

from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

import webapp2_extras.appengine.auth.models as auth_models

from webapp2_extras import jinja2

from wtforms import Form, StringField, PasswordField, validators

import cloudstorage as gcs

# GCSタイムアウト設定                                                                          
retry_params = gcs.RetryParams(                                                                
    initial_delay=0.2,
    max_delay=5.0,
    backoff_factor=2,
    max_retry_period=15)                                                                       
gcs.set_default_retry_params(retry_params)

def jinja2_factory(app):
    "True ninja method for attaching additional globals/filters to jinja"

    config = {'template_path': app.config.get('templates_path', 'template'),}
    j = jinja2.Jinja2(app, config=config)
    j.environment.globals.update({
        # 'config': app.config, 
        'uri_for': webapp2.uri_for,
    })
    return j

def get_bucket_name():
    return os.environ.get(
        'BUCKET_NAME',
        app_identity.get_default_gcs_bucket_name())

def get_BlobInfo(blobkey):
    """
        This image_key and bskey works with blobstore APIs
        that do not expect a corresponding BlobInfo in datastore.
    """
    key = str(urllib.unquote(blobkey))
    blob_instance = blobstore.BlobInfo.get(key)
    return blob_instance

def user_required(handler):
    """
         Decorator for checking if there's a user associated with the current session.
         Will also fail if there's no session present.
     """
    # def check_login(self, *args, **kwargs):
    def check_login(self, *args):
        auth = self.auth
        if not auth.get_user_by_session():
            # If handler has no login_url specified invoke a 403 error
            try:
                self.redirect(self.auth_config['login_url'], abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)
        else:
            user_session = self.auth.get_user_by_session()
            user_instance = PostUser.get_by_id(user_session['user_id'])
            # return handler(self, *args, **kwargs)
            return handler(self, user_instance)
    return check_login

class SecureRequestHandler(BaseHandler):

    """
         Only accessible to users that are logged in
     """
    @user_required
    def get(self, principal_info):

        bucket_name = get_bucket_name()
        # self.response.out.write(principal_info)

        # create_upload_url にてGCSのバケット名を「gs_bucket_name」に指定する
        upload_url = blobstore.create_upload_url('/uploaded', gs_bucket_name = bucket_name + '/' + principal_info.nickname + '/')

        context = {
            'you': principal_info.nickname,
            'up_url': upload_url,
        }

        self.render_response('secure.html', **context)

class ImageUploadHandler(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    
    @user_required
    def post(self, parent_info):

        # inputのname="file"と対応している
        file_blob = self.get_uploads('file')[0]
        serve_url = images.get_serving_url(file_blob.key())

        image_obj = ImageBlob(parent=parent_info.key)
        image_obj.populate(
            file_name=file_blob.filename,
            content_type=file_blob.content_type,
            file_size=file_blob.size,
            image_url=serve_url,
            proprietor=parent_info.nickname
        )
        image_obj.put()

        return self.redirect('/view_image/%s' % file_blob.key())

class InputArticlesHandler(BaseHandler):

    def get(self, image_key):

        bi_obj = get_BlobInfo(image_key)
        image_url = images.get_serving_url(bi_obj.key())

        # route /view-image*
        context = {
            'image_url': image_url,
            'item_name': bi_obj.filename # To name="item"
        }
        self.render_response('view-image.html', **context)

    @user_required
    def post(self, parent_info):

        """
            # incomplete key!
                assignment_item = self.request.get('item')
                ib_name_key = ndb.Key('PostUser', parent_info.email, 'ImageBlob', assignment_item)
                parent('PostUser')'s key which is express id()
         """

        assignment_item = self.request.get('item')
        ib_query_keys = ImageBlob.query(ImageBlob.file_name == assignment_item).fetch(keys_only=True)

        # ib_name_key = ib_name_kei.urlsafe()
        # img_query_keys = ndb.Key(urlsafe=ib_name_key)
        # target_article = ExplainArticle.query(ExplainArticle.blob_key == self.key, ancestor=self.key).fetch()

        form_articles = []
        zodiac_signs = ["rat", "ox", "tiger", "hare", "dragon", "serpent", "horse", "sheep", "monky", "rooster", "dog", "boar"]
        for twelve in zodiac_signs:
            form_articles.append(self.request.get(twelve))

        self.session['articles'] = form_articles
        self.session['img_key'] = ib_query_keys[0]

        return self.redirect('/confirm')

class PersistArticlesHandler(BaseHandler):

    def get(self):

        confirm_articles = ",".join(self.session.get('articles'))

        self.render_response('confirm.html', confirm=confirm_articles)

    def post(self):

        confirm_articles = self.session.get('articles')
        img_key = self.session.get('img_key')

        article_obj = ExplainArticle(parent=img_key)
        article_obj.populate(
            articles=confirm_articles,
            blob_key=img_key
        )
        # return self.response.out.write("Object:%s" % article_obj)
        article_obj.put()

        return self.redirect('/secure')

def require_child_keys(parent_key):

    child_keylist = ImageBlob.query_content(parent_key).fetch(keys_only=True)
    return child_keylist

def multi_image(img_query_keys, direction, resize="150"):

    list_context = []
    # for img_query_key in img_query_keys:
    image_objs = ndb.get_multi(img_query_keys)
    for image_obj in image_objs:
        to_edit_url = "http://" + os.environ['HTTP_HOST'] + "/" + direction + "?ib_name=" + image_obj.file_name
            
        image_url = image_obj.image_url #+ '=s' + resize
        context = {
            'indicate_url': to_edit_url, # link url(a href)
            'image_url': image_url
        }
        list_context.append(context)
        # self.render_response('inner.html', **context)
    return list_context

class RetrieveImageListHandler(BaseHandler):

    @user_required
    def get(self, parent_info):

        string = "edit"
        image_keylist = require_child_keys(parent_info.key)
        list_image_urls = multi_image(image_keylist, string)
        # for list_photo_url in list_photo_urls:

        self.render_response('inner.html', list_img_urls=list_image_urls)

def require_selected_key(method):
    def _require_selected_key(handler):
        def wrapper(self, parent_info):
            if os.environ['REQUEST_METHOD'] != method:
                return self.response.out.write('不正なアクセスです。')
                sys.exit()

            form = cgi.FieldStorage()

            if not form.has_key('ib_name'):
                return self.response.out.write('ありません。')
                sys.exit()
            else:
                search_name = form['ib_name'].value

                img_query_keys = ImageBlob.query(ImageBlob.file_name == search_name, ancestor=parent_info.key).fetch(keys_only=True)

                return handler(self, img_query_keys[0])
        return wrapper
    return _require_selected_key

class EditPageHandler(BaseHandler):

    @user_required
    @require_selected_key('GET')
    def get(self, ib_get_key):

        target_blobimage = ib_get_key.get()
        insert_image = target_blobimage.image_url

        target_article = target_blobimage.getting()

        list_article = target_article.articles
        article_str = ",".join(list_article)
        unitary_article = {
            'image_src': insert_image,
            'article': article_str
        }

        # article_str = article_str.encode('utf_8')
        # return self.response.out.write(target_article)
        self.render_response('edit.html', **unitary_article)

    @user_required
    @require_selected_key('POST')
    def post(self, ib_get_key):

        # target_article = ExplainArticle.query(ExplainArticle.blob_key == ib_get_key, ancestor=ib_get_key).fetch()
        target_blobimage = ib_get_key.get()
        target_article = target_blobimage.getting()

        form_articles = []
        zodiac_signs = ["rat", "ox", "tiger", "hare", "dragon", "serpent", "horse", "sheep", "monky", "rooster", "dog", "boar"]
        for twelve in zodiac_signs:
            form_articles.append(self.request.get(twelve))

        target_article.articles = form_articles
        target_article.put()

        return self.redirect('/secure')

class DeleteItemHandler(BaseHandler):

    @user_required
    @require_selected_key('POST')
    def post(self, ib_get_key):

        # target_article_keys = ExplainArticle.query(ExplainArticle.blob_key == ib_get_key, ancestor=ib_get_key).fetch(keys_only=True)
        target_article_keys = require_child_keys(ib_get_key)

        ib_get_key.delete()
        target_article_keys[0].delete()

        return self.redirect('/secure')

class MatesContentsHandler(BaseHandler):

    @user_required
    def get(self, principal_info):

        mate_imageblob_keylist = []
        string = "focus"

        for mate in principal_info.mates:
            mate_imageblob_keylist.append(require_child_keys(mate))

        # self.response.out.write(mate_imageblob_keylist)

        """
        多重リストを平坦化
         """
        mate_keylist_flat = list(chain.from_iterable(mate_imageblob_keylist))

        mate_multi_image = multi_image(mate_keylist_flat, string, "200")
        
        self.render_response('mate.html', multi_image=mate_multi_image)

class MateArticleHandler(BaseHandler):

    def get(self, ib_name):

        form = cgi.FieldStorage()

        if not form.has_key('ib_name'):
            return self.response.out.write('ありません。')
            sys.exit()
        else:
            search_name = form['ib_name'].value
            mate_imageblob = ImageBlob.query(ImageBlob.file_name == search_name).fetch()

        mate_target_article = mate_imageblob[0].getting()
        article_str = ",".join(mate_target_article.articles)

        # return self.response.out.write(article_str)
        mate_uni_content = {
            'mate_image': mate_imageblob[0].image_url,
            'image_proprietor': mate_imageblob[0].proprietor,
            'article': article_str
        }

        self.render_response('focus.html', **mate_uni_content)
