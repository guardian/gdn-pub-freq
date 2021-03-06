import webapp2
import jinja2
import os
import json
import logging
import datetime

from collections import namedtuple
from functools import partial

import content_api
import config
import urls
import local
import api

CountryLink = namedtuple('CountryLink', ['name', 'link'])

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

		section = self.request.get("section", default_value=None)

		api_url = "/api/data/{0}".format(date)

		if production_office:
			api_url = api_url + "/production-office/{0}".format(production_office)
		
		if section:
			api_url = api_url + "/section/{0}".format(section)

		def mk_path(production_office_code):
			if production_office_code:
				return "/production-office/{0}".format(production_office_code)

			return ''

		country_links = [CountryLink(name, "/day/{0}{1}".format(date, mk_path(code))) for name, code in config.production_offices]

		template_values = {
			'date_string': date,
			'date': datetime.datetime.strptime(date, '%Y-%m-%d'),
			'production_office': production_office,
			'section': section,
			'api_url' : api_url,
			'country_links': country_links,
			'hour_base_path': urls.hour_path(date, production_office),
			'navigation_links': urls.navigation_links(date, production_office),
			'navigation_urls': urls.navigation(date, production_office)
		}

		self.response.out.write(template.render(template_values))

def new_date_string(date, days=1):
	current_date = datetime.datetime.strptime(date, '%Y-%m-%d')
	new_date = current_date + datetime.timedelta(days=days)
	return new_date.strftime('%Y-%m-%d')

class PreviousDay(webapp2.RequestHandler):
	def get(self, date, production_office=None):
		url = '/day/{0}'.format(new_date_string(date, days=-1))
		
		if production_office:
			url = '/day/{0}/production-office/{1}'.format(new_date_string(date, days=-1), production_office)
		
		return webapp2.redirect(url)

class NextDay(webapp2.RequestHandler):
	def get(self, date, production_office=None):
		url = '/day/{0}'.format(new_date_string(date))
		
		if production_office:
			url = '/day/{0}/production-office/{1}'.format(new_date_string(date), production_office)
		
		return webapp2.redirect(url)

def new_week_string(date, days=7):
	current_date = datetime.datetime.strptime(date, '%Y-%m-%d')
	new_date = current_date + datetime.timedelta(days=days)
	return new_date.strftime('%Y-%m-%d')

class PreviousWeek(webapp2.RequestHandler):
	def get(self, date, production_office=None):
		url = '/day/{0}'.format(new_week_string(date, days=-7))
		
		if production_office:
			url = '/day/{0}/production-office/{1}'.format(new_week_string(date, days=-7), production_office)
		
		return webapp2.redirect(url)

class NextWeek(webapp2.RequestHandler):
	def get(self, date, production_office=None):
		url = '/day/{0}'.format(new_week_string(date))
		
		if production_office:
			url = '/day/{0}/production-office/{1}'.format(new_week_string(date), production_office)
		
		return webapp2.redirect(url)

class TitlePage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('title.html')
		
		template_values = {
			'app_title': 'gdn-pub-freq.appspot.com',
		}

		self.response.out.write(template.render(template_values))		

class HourPage(webapp2.RequestHandler):
	def get(self, date, hour, production_office=None):
		template = jinja_environment.get_template('hour.html')

		parameters_description = ''

		if production_office:
			parameters_description += 'Production Office: {0}'.format(production_office.upper())

		logging.info(hour)

		days_content = api.read_all_content_for_day(date, production_office=production_office)

		content = [i for i in days_content if partial(api.extract_hour_of_publication, production_office)(i) == hour]
		template_values = {
			'date_string': date,
			'date': datetime.datetime.strptime(date, '%Y-%m-%d'),
			'hour': hour,
			'content': content,
			'production_office': production_office,
			'parameters_summary': parameters_description
		}

		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/', handler=MainPage),
	webapp2.Route(r'/title', handler=TitlePage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>/hour/<hour:\d{2}>', handler=HourPage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/hour/<hour:\d{2}>', handler=HourPage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>', handler=DayPage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>', handler=DayPage),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>/previous', handler=PreviousDay),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>/next', handler=NextDay),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>/previous/week', handler=PreviousWeek),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>/next/week', handler=NextWeek),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/previous', handler=PreviousDay),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/next', handler=NextDay),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/previous/week', handler=PreviousWeek),
	webapp2.Route(r'/day/<date:\d{4}-\d{2}-\d{2}>/next/week', handler=NextWeek),
	],
                              debug=True)