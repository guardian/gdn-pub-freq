import webapp2
import jinja2
import os
import json
import logging
import datetime

import content_api

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')

		today = datetime.date.today()
		yesterday = today + datetime.timedelta(days=-1)
		
		template_values = {
			'yesterday': yesterday.isoformat()
		}

		self.response.out.write(template.render(template_values))

class DayPage(webapp2.RequestHandler):
	def get(self, date, production_office=None):
		template = jinja_environment.get_template('page.html')

		api_url = "/api/data/{0}".format(date)

		if production_office:
			api_url = api_url + "/production-office/{0}".format(production_office)
		
		template_values = {
			'date_string': date,
			'date': datetime.datetime.strptime(date, '%Y-%m-%d'),
			'production_office': production_office,
			'api_url' : api_url,
		}

		self.response.out.write(template.render(template_values))

def new_date_string(date, days=1):
	current_date = datetime.datetime.strptime(date, '%Y-%m-%d')
	new_date = current_date + datetime.timedelta(days=days)
	return new_date.strftime('%Y-%m-%d')

class PreviousDay(webapp2.RequestHandler):
	def get(self, date):
		return webapp2.redirect('/day/{0}'.format(new_date_string(date, days=-1)))

class NextDay(webapp2.RequestHandler):
	def get(self, date):
		return webapp2.redirect('/day/{0}'.format(new_date_string(date)))

def new_week_string(date, days=7):
	current_date = datetime.datetime.strptime(date, '%Y-%m-%d')
	new_date = current_date + datetime.timedelta(days=days)
	return new_date.strftime('%Y-%m-%d')

class PreviousWeek(webapp2.RequestHandler):
	def get(self, date):
		return webapp2.redirect('/day/{0}'.format(new_week_string(date, days=-7)))

class NextWeek(webapp2.RequestHandler):
	def get(self, date):
		return webapp2.redirect('/day/{0}'.format(new_week_string(date)))

class TitlePage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('title.html')
		
		template_values = {
			'app_title': 'gdn-pub-freq.appspot.com',
		}

		self.response.out.write(template.render(template_values))		

class HourPage(webapp2.RequestHandler):
	def get(self, date, hour):
		template = jinja_environment.get_template('hour.html')

		logging.info(hour)

		hour_string = '{0}T{1}'.format(date, hour)
		start_hour = datetime.datetime.strptime(hour_string, '%Y-%m-%dT%H')
		end_hour = start_hour + datetime.timedelta(hours=1)

		params = {
			'api-key': content_api.capi_key(),
			'from-date': start_hour.isoformat(),
			'to-date': end_hour.isoformat(),
			'page-size': 50,
		}

		r = content_api.search(params)

		content = []

		if r:
			data = json.loads(r)
			content = data.get("response", {}).get("results", [])
		
		template_values = {
			'date_string': date,
			'date': datetime.datetime.strptime(date, '%Y-%m-%d'),
			'hour': hour,
			'content': content,
		}

		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/', handler=MainPage),
	webapp2.Route(r'/title', handler=TitlePage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/hour/<hour:\d{2}>', handler=HourPage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>', handler=DayPage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>', handler=DayPage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/previous', handler=PreviousDay),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/next', handler=NextDay),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/previous/week', handler=PreviousWeek),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/next/week', handler=NextWeek),
	],
                              debug=True)