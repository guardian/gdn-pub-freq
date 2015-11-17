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

def hour(production_office, iso_date, hour):

	logging.info(production_office)
	tz = timezones.get(production_office, timezones['uk'])
	iso_d = isodate.parse_date(iso_date)

	logging.info(tz)

	local_start_dt = datetime.datetime(year=iso_d.year,
		month=iso_d.month,
		day=iso_d.day,
		hour=int(hour),
		minute=0, tzinfo=tz)

	local_end_dt = datetime.datetime(year=iso_d.year,
		month=iso_d.month,
		day=iso_d.day,
		hour=int(hour),
		minute=59, tzinfo=tz)

	logging.info(local_start_dt)
	logging.info(local_end_dt)

	utc_start_dt = local_start_dt.astimezone(tz=pytz.utc)
	utc_end_dt = local_end_dt.astimezone(tz=pytz.utc)

	logging.info(utc_start_dt)
	logging.info(utc_end_dt)

	start = datetime.datetime(year=iso_d.year,
		month=iso_d.month,
		day=iso_d.day,
		hour=utc_start_dt.hour,
		minute=utc_start_dt.minute, tzinfo=pytz.utc)

	end = datetime.datetime(year=iso_d.year,
		month=iso_d.month,
		day=iso_d.day,
		hour=utc_end_dt.hour,
		minute=utc_end_dt.minute, tzinfo=pytz.utc)

	return (start.isoformat(), end.isoformat())
