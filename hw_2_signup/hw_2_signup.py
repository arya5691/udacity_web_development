# appcfg.py --oauth2 -A winter-charmer-551 update udacity

import cgi
import datetime
import re
import webapp2

form = """
<form method="post" action="/">
  <br>
  <label> Username
    <input type="text" name="username" value=%(username)s>
    <div style="color: red">%(username_error)s</div>
  </label> <br>
  <label> Password
    <input type="password" name="password">
    <div style="color: red">%(password_error)s</div>
  </label> <br>
  <label> Verify Password
    <input type="password" name="verify">
    <div style="color: red">%(verify_error)s</div>
  </label> <br>
  <label> Email
    <input type="text" name="email" value=%(email)s>
    <div style="color: red">%(email_error)s</div>
  </label>
  <br>
  <br>
  <input type="submit">
</form>
"""

USERNAME_REGEX = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_REGEX = re.compile("^.{3,20}$")
EMAIL_REGEX = re.compile("^[\S]+@[\S]+\.[\S]+$")

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.writeForm();

    def checkMatchingRegex(self, value, regex):
      return regex.match(value)

    def writeForm(self, username="", username_error="", password_error="",
                  verify_error="", email="", email_error=""):
      self.response.out.write(form % {"username": username,
                                      "username_error": username_error,
                                      "password_error":password_error,
                                      "verify_error":verify_error,
                                      "email":email,
                                      "email_error":email_error})

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
      if (not self.checkMatchingRegex(password, PASSWORD_REGEX)):
        password_error="Invalid password. Please reenter."
      if (not self.checkMatchingRegex(email, EMAIL_REGEX)):
        email_error="Invalid email. Please reenter."
      if (password != verify):
        verify_error="Passwords do not match. Please reenter."

      if (username_error or password_error or verify_error or email_error):

        self.response.out.write(form % {"username": cgi.escape(username, quote=True),
                                      "username_error": username_error,
                                      "password_error":password_error,
                                      "verify_error":verify_error,
                                      "email": cgi.escape(email, quote=True),
                                      "email_error":email_error})
      else:
        self.redirect("/thanks?username="+username)

class ThanksPage(webapp2.RequestHandler):
    def get(self):
      username  = self.request.get("username")  
      self.response.write("Thanks, " + username + " for entering correct data !! Welcome !!")


app = webapp2.WSGIApplication([
    ('/', MainPage), ('/thanks', ThanksPage),
], debug=True)
