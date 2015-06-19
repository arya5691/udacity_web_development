# appcfg.py --oauth2 -A winter-charmer-551 update udacity

import cgi
import datetime
import webapp2

form = """
<form method="post" action="/">
  Enter your text:
  <br>
    <textarea rows="10" cols="50" name="text">%(text)s</textarea>
  <br>
  <input type="submit">
</form>
"""
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.writeForm();

    def writeForm(self, text=""):
      self.response.out.write(form % {"text": text})

    def rot13(self, text=""):
      rotated_result=""
      for c in text:
        if (c.isalpha()):
          if (c.isupper()):
            base = ord('A')
          else:
            base = ord('a')
          # Rotate by 13 postions
          rot = chr(base + (ord(c) - base + 13)%26)
          rotated_result+=rot
        else:
          rotated_result+=c
      return cgi.escape(rotated_result, quote=True)

    def post(self):
      text  = self.request.get("text")
      output = self.rot13(text)
      self.response.out.write(form % {"text": output})


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
