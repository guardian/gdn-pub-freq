import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode
from google.appengine.api import urlfetch

import headers

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class DayData(webapp2.RequestHandler):
	def get(self, date):
		headers.json(self.response)
		
		data = {
			'19' : 20,
			'20': 32,
			'date': date,
		}

		self.response.out.write(json.dumps(data))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/api/data/<date:\d{4}-\d{2}-\d{2}>', handler=DayData)],
                              debug=True)