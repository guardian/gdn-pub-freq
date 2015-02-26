import webapp2
import jinja2
import os
import json
import logging
import urllib

from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache

import headers
import content_api

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

def page_url(date, page):
	params = {
		'api-key': content_api.capi_key(),
		'from-date': date,
		'to-date': date,
		'page-size': 50,
		'page': page,
	}


	return "http://{host}/search?{params}".format(host=content_api.capi_host(),
		params=urllib.urlencode(params))

def extract_results(rpc):
	r = rpc.get_result()
	if not r.status_code == 200:
		logging.warning("Async call to CAPI failed, results will be inaccurate")
		return []
	response = json.loads(r.content)
	data = response.get('response', {})
	return data.get('results', [])

def read_all_content_for_day(date):

	params = {
		'api-key': content_api.capi_key(),
		'from-date': date,
		'to-date': date,
		'page-size': 50,
	}


	url = "http://{host}/search?{params}".format(host=content_api.capi_host(),
		params=urllib.urlencode(params))

	r = fetch(url)

	if not r.status_code == 200:
		logging.error("CAPI read failed: diediedie: status code {0}".format(r.status_code))
		return None

	response = json.loads(r.content)
	data = response.get('response', {})
	results = data.get('results', [])

	page_count = int(data['pages'])
	logging.info(page_count)

	if not page_count > 1:
		return results

	other_pages = [(urlfetch.create_rpc(), page+1) for page in range(1, page_count)]
	async_calls =[urlfetch.make_fetch_call(rpc, page_url(date, page)) for rpc, page in other_pages]
	page_responses = map(extract_results, async_calls)
	logging.info(page_responses)

	return reduce(lambda r, rs: r + rs, page_responses, results)


class DayData(webapp2.RequestHandler):
	def get(self, date):
		headers.json(self.response)

		days_content = read_all_content_for_day(date)
		
		data = {
			'date': date,
			'content': days_content,
			'total_content': len(days_content),
		}

		self.response.out.write(json.dumps(data))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/api/data/<date:\d{4}-\d{2}-\d{2}>', handler=DayData)],
                              debug=True)