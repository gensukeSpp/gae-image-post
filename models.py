# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

import webapp2_extras.appengine.auth.models as auth_models

class PostUser(auth_models.User):
    nickname = ndb.StringProperty()
    mates = ndb.KeyProperty(repeated=True)

class ImageBlob(ndb.Model):
    file_name = ndb.StringProperty()
    content_type = ndb.StringProperty()
    file_size = ndb.IntegerProperty()
    upload_date = ndb.DateTimeProperty(auto_now_add=True)
    image_url = ndb.StringProperty()
    proprietor = ndb.StringProperty()

    # @property
    def getting(self):
        article_objs = ExplainArticle.query(ExplainArticle.blob_key == self.key, ancestor=self.key).fetch()
        return article_objs[0]

    @classmethod
    def query_content(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)

class ExplainArticle(ndb.Model):
    articles = ndb.StringProperty(repeated=True)
    update_date = ndb.DateTimeProperty(auto_now_add=True)
    blob_key = ndb.KeyProperty(kind=ImageBlob)
