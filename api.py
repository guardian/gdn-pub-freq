import webapp2
import jinja2
import os
import json
import logging
import urllib
import re

from collections import Counter

from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache

import headers
import content_api

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

def page_url(date, page, production_office=None):
	params = {
		'api-key': content_api.capi_key(),
		'from-date': date,
		'to-date': date,
		'page-size': 50,
		'page': page,
	}

	if production_office:
		params['production-office'] = production_office

	#logging.info(params)

	url = "http://{host}/search?{params}".format(host=content_api.capi_host(),
		params=urllib.urlencode(params))

	#logging.info(url)
	return url

def extract_results(rpc):
	r = rpc.get_result()
	if not r.status_code == 200:
		logging.warning("Async call to CAPI failed, results will be inaccurate")
		return []
	response = json.loads(r.content)
	data = response.get('response', {})
	return data.get('results', [])

def extract_hour_of_publication(content):
	pattern = re.compile(r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})Z$')


	#logging.info(content['webPublicationDate'])
	dt_elements = pattern.search(content['webPublicationDate']).groups()
	#logging.info(dt_elements)

	return dt_elements[3]

def read_all_content_for_day(date, production_office=None, section=None):

	params = {
		'api-key': content_api.capi_key(),
		'from-date': date,
		'to-date': date,
		'page-size': 50,
	}

	if production_office:
		params['production-office'] = production_office

	if section:
		params['section'] = section


	url = "http://{host}/search?{params}".format(host=content_api.capi_host(),
		params=urllib.urlencode(params))

	logging.info(url)

	r = fetch(url)

	if not r.status_code == 200:
		logging.error("CAPI read failed: diediedie: status code {0}".format(r.status_code))
		return None

	response = json.loads(r.content)
	data = response.get('response', {})
	results = data.get('results', [])

	page_count = int(data['pages'])
	#logging.info(page_count)

	if not page_count > 1:
		return results

	other_pages = [(urlfetch.create_rpc(), page+1) for page in range(1, page_count)]
	async_calls =[urlfetch.make_fetch_call(rpc, page_url(date, page, production_office)) for rpc, page in other_pages]
	page_responses = map(extract_results, async_calls)
	all_content = reduce(lambda r, rs: r + rs, page_responses, results)

	return all_content

class DayData(webapp2.RequestHandler):
	def get(self, date, production_office=None, section=None):
		headers.json(self.response)

		cache_key = date

		if production_office:
			cache_key = "{0}-{1}".format(date, production_office)

		if section and not production_office:
			cache_key = '{0}-s{1}'.format(date, section)

		if section and production_office:
			cache_key = "{0}-{1}-{2}".format(date, production_office, section)

		days_content = memcache.get(cache_key)

		if not days_content:
			days_content = read_all_content_for_day(date, production_office=production_office, section=section)
			memcache.set(cache_key, days_content, 30 * 60)

		counts = Counter(map(extract_hour_of_publication, days_content))

		hour_counts = {str(i).zfill(2):0 for i in range(24)}

		hour_counts.update(counts)
		
		data = {
			'date': date,
			'hour_counts': hour_counts,
			'total_content': len(days_content),
			'count_series': [hour_counts[k] for k in sorted(hour_counts.keys())],
			'hour_series': [k for k in sorted(hour_counts.keys())]
		}

		self.response.out.write(json.dumps(data))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/api/data/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>/section/<section>', handler=DayData),
	webapp2.Route(r'/api/data/<date:\d{4}-\d{2}-\d{2}>/section/<section>', handler=DayData),
	webapp2.Route(r'/api/data/<date:\d{4}-\d{2}-\d{2}>/production-office/<production_office>', handler=DayData),
	webapp2.Route(r'/api/data/<date:\d{4}-\d{2}-\d{2}>', handler=DayData),
	], debug=True)