
def hour_path(date, production_office):
	if not production_office:
		return '/day/{0}/hour/'.format(date)

	return '/day/{0}/production-office/{1}/hour/'.format(date, production_office)

