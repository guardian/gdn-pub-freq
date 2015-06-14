from collections import namedtuple

Link = namedtuple('Link', ['name', 'url'])

def hour_path(date, production_office, section=None):

	if not production_office:
		return '/day/{0}/hour/'.format(date)

	return '/day/{0}/production-office/{1}/hour/'.format(date, production_office)

def navigation_links(date, production_office):


	navigation = [
		("previous day", "previous"),
		("next day", "next"),
		("previous week", "previous/week"),
		("next week", "next/week"),
	]

	def mk_path(path, date, production_office):
		if not production_office:
			return "/day/{0}/{1}".format(date, path)

		return "/day/{0}/production-office/{1}/{2}".format(date, production_office, path)

	return [Link(name, mk_path(path, date, production_office)) for name, path in navigation]

def navigation(date, production_office):
	return {name.replace(' ', '_'):url for name, url in navigation_links(date, production_office)}