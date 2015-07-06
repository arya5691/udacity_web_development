# appcfg.py --oauth2 -A winter-charmer-551 update udacity

import cgi
import datetime
import os
import re
import webapp2
import jinja2
from google.appengine.ext import db
import logging
import string
import random
import hmac

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
        loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class User(db.Model):
  name = db.StringProperty(required = True)
  password_hash = db.StringProperty(required = True)
  email = db.StringProperty(required = False)
  created = db.DateTimeProperty(auto_now_add = True)

USERNAME_REGEX = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_REGEX = re.compile("^.{3,20}$")
EMAIL_REGEX = re.compile("^[\S]+@[\S]+\.[\S]+$")
COOKIE_SECRET = "COOKIE!!!"

class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

  def getSalt(self):
    return ''.join(random.choice(string.letters) for _ in range(10))

  def getSaltedPassword(self, password, salt=""):
    if not salt:
      salt = self.getSalt()
    return "%s|%s" % (hmac.new(str(salt), str(password)).hexdigest(),salt)

  def getCodedCookie(self, cookie):
    return "%s|%s" % (cookie, hmac.new(COOKIE_SECRET, str(cookie)).hexdigest())

  def verifyPassword(self, password, hashValue):
    salt = hashValue.split("|")[1]
    expectedHash = self.getSaltedPassword(password = password, salt = salt)
    return expectedHash == hashValue

  def verifyCookie(self, hashValue):
    value = hashValue.split("|")[0]
    expectedCookie = self.getCodedCookie(value)
    if expectedCookie == hashValue:
      return value

class SignupPage(Handler):

    def get(self):
        self.render("form.html", title = "Registration", heading = "Signup");

    def checkMatchingRegex(self, value, regex):
      return regex.match(value)

    def post(self):
      username  = self.request.get("username");
      password  = self.request.get("password");
      verify  = self.request.get("verify");
      email  = self.request.get("email");

      username_error=""
      password_error=""
      verify_error=""
      email_error=""

      if (not self.checkMatchingRegex(username, USERNAME_REGEX)):
        username_error="Invalid username. Please reenter."
      
      # Check if user already exists.
      if not username_error:
        query = "select * from User where name ='%s'" % username
        user = db.GqlQuery(query)
        if (user.count() > 0):
          username_error="User already exists!"

      if (not self.checkMatchingRegex(password, PASSWORD_REGEX)):
        password_error="Invalid password. Please reenter."
      if (email and not self.checkMatchingRegex(email, EMAIL_REGEX)):
        email_error="Invalid email. Please reenter."
      if (password != verify):
        verify_error="Passwords do not match. Please reenter."

      if (username_error or password_error or verify_error or email_error):
        self.render("form.html", username = username,
                    username_error = username_error,
                    password_error = password_error,
                    verify_error = verify_error,
                    email = email,
                    email_error = email_error,
                    title = "Registration",
                    heading = "Signup")
      else:
        new_user = User(name = username, email = email, password_hash=self.getSaltedPassword(password = password))
        new_user.put()
        user_id_cookie = self.getCodedCookie(new_user.key().id())
        self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % str(user_id_cookie))
        self.redirect("/welcome")

class LoginPage(Handler):

    def get(self):
        self.render("login.html", title = "Login", heading = "Enter your credentials");

    def post(self):
      username  = self.request.get("username");
      password  = self.request.get("password");
      login_error=False
      
      query = "select * from User where name ='%s'" % username
      user = db.GqlQuery(query)
      if (user.count() < 1):
         login_error=True
      else:
        login_error = not self.verifyPassword(password = password, hashValue = user.get().password_hash)

      if (login_error):
        self.render("login.html", login_error = "Invalid login!",
                    username = username,
                    title = "Login",
                    heading = "Enter your credentials")
      else:
        user_id_cookie = self.getCodedCookie(user.get().key().id())
        self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % str(user_id_cookie))
        self.redirect("/welcome")

class LogoutPage(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % "")
        self.redirect("/signup")

class WelcomePage(Handler):
    def get(self):
      user_id  = self.verifyCookie(self.request.cookies.get("user_id"))
      if not user_id:
          self.redirect("/signup")
          return
      user = User.get_by_id(int(user_id))
      if not user:
          self.redirect("/signup")
          return
      self.render("welcome.html", username = user.name, title = "Welcome!!", heading = "Login successful")

app = webapp2.WSGIApplication([
    ('/signup', SignupPage), ('/welcome', WelcomePage),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
], debug=True)
