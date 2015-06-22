# appcfg.py --oauth2 -A winter-charmer-551 update udacity

import jinja2
import os
import cgi
import datetime
import re
import webapp2
from google.appengine.ext import db
import logging
  
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Post(db.Model):
  title = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

class RootPage(Handler):
  def get(self):
    self.redirect("/blog")

class MainPage(Handler):

  def render_blog(self, posts, is_main_page=True):
    self.render("blog.html", posts = posts, is_main_page=is_main_page)

  def get(self):
    query = "select * from Post order by created desc limit 10"
    posts = db.GqlQuery(query)
    self.render_blog(posts=posts)

class NewPost(Handler):
  
  def render_form(self, title="", content="", error="", blog_id=""):
    self.render("new_post.html", title=title, content=content, error=error, blog_id=blog_id)

  def get(self):
    self.render_form()

  def post(self):
    title = self.request.get("subject")
    content = self.request.get("content")

    if title and content:
      new_post  = Post(title=title, content=content)
      new_post.put()
      blog_id = new_post.key().id()
      self.redirect("/blog/"+ str(blog_id))

    else:
      error = "We need both a title and content, buddy!!"
      self.render_form(error=error, title=title, content=content)

class PostByIdHandler(MainPage):
  def get(self, blog_id):
    blog = Post.get_by_id(int(blog_id))
    content = []
    content.append(blog)
    self.render_blog(posts=content,is_main_page=False)

class EditByIdHandler(NewPost):
  def get(self, blog_id):
    blog = Post.get_by_id(int(blog_id))
    self.render_form(title=blog.title, content=blog.content, blog_id=blog_id)

  def post(self, blog_id):
    title = self.request.get("subject")
    content = self.request.get("content")
    blog_id = self.request.get("id")
    
    orig_post = Post.get_by_id(int(blog_id))
    logging.info(orig_post.title)
    
    if title==orig_post.title and content==orig_post.content:
      error = "You did not change anything!!"
      self.render_form(error=error, title=title, content=content, blog_id=blog_id)

    elif title and content:
      orig_post.title = title
      orig_post.content = content
      orig_post.put()
      self.redirect("/blog/"+ str(blog_id))

    else:
      error = "We need both a title and content, buddy!!"
      self.render_form(error=error, title=title, content=content)

class DeleteByIdHandler(Handler):
  def get(self, blog_id):
    blog = Post.get_by_id(int(blog_id))
    blog.delete()
    self.render("success.html")

app = webapp2.WSGIApplication([
    ('/', RootPage),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    (r'/blog/(\d+)', PostByIdHandler),
    (r'/blog/(\d+)/edit', EditByIdHandler),
    (r'/blog/(\d+)/delete', DeleteByIdHandler),
], debug=True)
