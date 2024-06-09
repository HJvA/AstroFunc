import aiohttp,asyncio
import datetime,time
import logging
import json
import sys,os,re
sys.path.append('.')
import submod.pyCommon.tls as tls # get_logger
from submod.pyCommon.timtls import julianday

URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
url_timezone = 'http://worldtimeapi.org/api/timezone/{area}/{location}'   #[/:region]'
J2000 = 2451545.0  # 20000101:12h
"""
https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='499'&OBJ_DATA='YES'&MAKE_EPHEM='YES'&EPHEM_TYPE='OBSERVER'&CENTER='500@399'&START_TIME='2006-01-01'&STOP_TIME='2006-01-20'&STEP_SIZE='1%20d'&QUANTITIES='1,9,20,23,24,29'
"""

async def restGet(url, params={}, timeout=2):
	""" queries json device with restfull api over ethernet """
	headers = {'content-type': 'application/json'}
	stuff={}
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get( url=url, timeout=timeout, params=params) as response:
				logger.info('{%d}getting=%s' % (response.status,response.url))
				if response.status==200:
					try:
						stuff = await response.json()
						#logger.debug('got:%s:%s' % (cityId,stuff))
					except aiohttp.client_exceptions.ContentTypeError as ex:
						stuff = await response.text()
						logger.warning('bad json:%s' % (stuff,))
						stuff=None
				else:
					logger.warning('bad response :%s on %s' % (response.status,url))
					await session.close()
					await asyncio.sleep(0.2)
	except asyncio.TimeoutError as te:
		logger.warning("openweather timeouterror %s :on:%s" % (te,url))
		await asyncio.sleep(10)
	except Exception as e:
		logger.exception("openweather unknown exception!!! %s :on:%s" % (e,url))
	#logger.debug('hueGET resource:%s with %s ret:%d' % (resource,r.url,r.status_code))
	return stuff

async def get_timezone(area='Europe', location='Paris'):
	TZF ="%Y-%m-%dT%H:%M:%S.%f%z"
	url = url_timezone.format(area=area, location=location)
	tz = await restGet(url, timeout=20)
	if not tz:
		url = 'http://worldtimeapi.org/api/ip'   #timezone/{area}/{location}'   #[/:region]'
		tz = await restGet(url, timeout=10)
	if tz:
		dt = tz['datetime']
	else:
		dt = datetime.datetime.now().isoformat()+"+02:00"
	dto = datetime.datetime.strptime(dt, TZF)  # '2021-06-19T18:09:14.896810+00:00'
	tzo = dto.tzinfo  #datetime.datetime.strptime(dt['utc_offset'],"%z")   # 
	logger.info('dto:{} tz:{}'.format(dto,tzo))
	#tz = await restGet(url)
	#logger.info('tz:{}'.format(tz))
	return tz

places = {
	'MB':'major bodies',
	'SB':'small bodies',
	'*@301':'sites on moon',
	'*@399':'sites on earth'
} 

async def get_list(place='MB'):
	""" """
	params = {
		'format':'json',
		'COMMAND':place,
		}
	return await restGet(URL,params)

async def get_body(bodyId='499', JD=J2000):
	""" """
	params = {
		'format':'json',
		'COMMAND':bodyId,
		'REF_PLANE':'ECLIPTIC',  # ECLIPTIC, FRAME, BODY EQUATOR
		'OBJ_DATA':'NO',
		'MAKE_EPHEM':'YES',
		'EPHEM_TYPE':'OBS',  #'ELEMENTS', #  'OBS', 
			#OBSERVER	Observables (RA/DEC, Az/El, physical aspect, angles, uncertainties)	telescope observations; 
			#ELEMENTS	Osculating orbital elements	instantaneous geometry over time, celestial mechanics; 
			#VECTORS	Cartesian state vectors and uncertainties	dynamical studies, propagation, programming; 
			#APPROACH	Close approaches to planets (and 16 largest asteroids)	encounter planning & hazards; 
			#SPK	SPK binary trajectory files (asteroids and comets only)	time-continuous states, navigation, mission-planning, plug-in for visualization tools
		'QUANTITIES':"A",
		'TLIST':"'2451545.0' '{}'".format(julianday()),
		'TLIST_TYPE':'JD',
		#'START_TIME':'{}'.format(JD),
		#'STOP_TIME':'{}'.format(JD),
		#'STEP_SIZE':'0',
		'CENTER':'coord',  # 'geo',   #  geo  coord
		'COORD_TYPE':'GEODETIC',  #  GEODETIC or CYLINDRICAL
		#'SITE_COORD':  "'5.5', '51.5', '0.022'",  # '5.5,51.5,0.022',  # {E. long., lat, height} (KM and DEG). 
		'CAL_FORMAT' : 'JD',
		'ANG_FORMAT':'DEG',  #  DEG  HMS
		#'RTS_ONLY' : 'YES' # rise transit set 
		}
	body = await restGet(URL,params)
	return body


class Horizons(object):
	def __init__(self, cityId=None,lat=None,lon=None):
		""" query horizons data for a specific location """

if __name__ == '__main__':
	_loop = asyncio.get_event_loop()
	logger = tls.get_logger(__file__,logging.INFO,logging.DEBUG)
	JD = julianday()
	#January 1st 2000 at noon was 2451545.0
	logger.info('jdnow={} J2000(now):{}'.format(JD, JD-2451545.0))
	
	tz = _loop.run_until_complete(get_timezone() )
	logger.info('tz={}'.format(tz))
	
	list = _loop.run_until_complete(get_list())
	#logger.debug("list:{}".format(list))
	bodies={}
	if list:
		lines = list['result'].split('\n')
		#logger.info("lines:{}".format(lines))
		for ln in lines:
			mtch = re.search('^\s*(\-?[0-9]+)(?:\s+)(.{30}\S*)(?:\s+)(\w*\s\w*)(?:\s+)(\w*)', ln)
			if mtch:
				hid = int(mtch.group(1))
				nm = mtch.group(2).strip()
				desg =mtch.group(3).strip()
				alias =mtch.group(4).strip()
				if desg or alias:
					logger.info("{},{},{},{}".format(hid,nm,desg,alias))
					bodies[hid]=(nm,desg,alias)
					#breakpoint()
			else:
				logger.debug("no match:{}:".format(ln))
	logger.info("bodies:{}".format(bodies))
	breakpoint()
	body = _loop.run_until_complete(get_body('499'))
	logger.info("body:{}".format(body))

