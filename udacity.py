# appcfg.py --oauth2 -A winter-charmer-551 update udacity

import webapp2
import datetime

form = """
<form method="post" action="/">
  What is your birthday?
  <br>
  <label> Month
  <input type="text" name="month">
  </label>
  <label> Day
  <input type="text" name="day">
  </label>
  <label> Year
  <input type="text" name="year">
  </label>
  <br>
  <br>
  <input type="submit">
</form>
"""

def f(month, day, year):
  try:
    month = int(month)
    day = int(day)
    year = int(year)
    return datetime.datetime(month=month, day=day, year=year)
  except ValueError:
     return "whooopss!!"

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(form)

    def post(self):
      month  = self.request.get("month");
      day = self.request.get("day");
      year  = self.request.get("year");
      self.response.write(str(f(month,day,year)));

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
