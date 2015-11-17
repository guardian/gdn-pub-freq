import re
import datetime
import logging

import pytz
import isodate

timezones = {
	'us': pytz.timezone('America/New_York'),
	'uk': pytz.timezone('Europe/London'),
	'aus': pytz.timezone('Australia/Sydney'),
}

def date_start_and_end(production_office, iso_date_string):

	pattern = re.compile('(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})')

	match = re.match(pattern, iso_date_string)

	assert match, "{0} didn't match the expected iso date format".format(iso_date_string)

	year = int(match.groupdict()['year'])
	month = int(match.groupdict()['month'])
	day = int(match.groupdict()['day'])

	tz = timezones.get(production_office, timezones['uk'])

	start = datetime.datetime(year=year, month=month, day=day, hour=0, minute=0, tzinfo=tz)
	end = datetime.datetime(year=year, month=month, day=day, hour=23, minute=59, tzinfo=tz)
	return (start.astimezone(tz=pytz.utc).isoformat(),
		end.astimezone(tz=pytz.utc).isoformat())

def rewrite_publication_date(production_office, content_item):
	if not production_office:
		return content_item

	utc_dt = isodate.parse_datetime(content_item['webPublicationDate'])

	tz = timezones.get(production_office, timezones['uk'])

	rewritten_date = utc_dt.astimezone(tz=tz).isoformat()

	content_item['webPublicationDate'] = rewritten_date
	return content_item
