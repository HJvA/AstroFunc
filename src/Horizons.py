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
J2000 = 2451545.0  # jd @ 20000101:12h
"""
https://ssd-api.jpl.nasa.gov/doc/horizons.html
https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='499'&OBJ_DATA='YES'&MAKE_EPHEM='YES'&EPHEM_TYPE='OBSERVER'&CENTER='500@399'&START_TIME='2006-01-01'&STOP_TIME='2006-01-20'&STEP_SIZE='1%20d'&QUANTITIES='1,9,20,23,24,29'
"""

async def restGet(url, params={}, timeout=2):
	""" queries json device with restfull api over ethernet 
		 """
	headers = {'content-type': 'application/json'}
	stuff={}
	try:
		async with aiohttp.ClientSession() as session:
			async with session.get( url=url, timeout=timeout, params=params) as response:
				logger.info('{%d}http.get=%s' % (response.status,response.url))
				if response.status==200:
					try:
						stuff = await response.json()
						logger.debug('json(%s)=%s' % (params,stuff))
					except aiohttp.client_exceptions.ContentTypeError as ex:
						stuff = await response.text()
						logger.warning('bad json:%s' % (stuff,))
						stuff=None
				else:
					logger.warning('bad response :%s on %s' % (response.status,url))
					await session.close()
					await asyncio.sleep(0.2)
	except asyncio.TimeoutError as te:
		logger.warning("horizons timeouterror %s :on:%s" % (te,url))
		await asyncio.sleep(10)
	except Exception as e:
		logger.exception("horizons unknown exception!!! %s :on:%s" % (e,url))
	#logger.debug('hueGET resource:%s with %s ret:%d' % (resource,r.url,r.status_code))
	return stuff
	
async def restPost(url, fparm):
	""" https://ssd-api.jpl.nasa.gov/doc/horizons_file.html """ 
	f = open(fparm)
	headers = {'content-type': 'application/json'}
	stuff={}
	try:
		response = await session.post(url=url, data={"format": "json"}, files={'input': f}, headers={"Content-Type": "application/json"})
		stuff =await response.json()
	except asyncio.TimeoutError as te:
		logger.warning("openweather timeouterror %s :on:%s" % (te,url))
		await asyncio.sleep(10)
	return stuff 

async def get_timezone(area='Europe', location='Paris'):
	TZF ="%Y-%m-%dT%H:%M:%S.%f%z"
	url = url_timezone.format(area=area, location=location)
	tz = await restGet(url, timeout=20)
	if not tz:
		logger.warning('failed to get tz from:{}'.format(url))
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
	'MB':'major bodies', # Major Body Refers to planet, natural satellite, spacecraft, Sun, barycenter, or other objects having pre-computed trajectories. Only major bodies can be coordinate centers (observing sites) in Horizons. Their state vectors are obtained by interpolating previously defined ephemerides, such as DE441. Interpolation generally recovers the state to the millimeter level. In some special cases, an asteroid or comet can be defined as a major body. An example might be a particular asteroid solution used for a spacecraft mission flyby or other historically “fixed” purpose, such as the Eros solution for the NEAR mission. In such cases, the particular trajectory is precomputed and stored as a “major body”, while the objects’ ground-based solution otherwise continues to be updated in the JPL small-body database as new observations are reported. Therefore, it may be possible to use either the fixed (historical) major-body trajectory solution or the “latest” small-body solution. Details for the specific cases are given in the object’s data-sheet summaries.
	'SB':'small bodies', # Small Body Refers to a comet or asteroid for which the trajectory is numerically integrated on demand from an initial set of previously statistically estimated orbital elements in the JPL database. Typically, no cartographic coordinate system is available for these objects, but there are a growing number of exceptions.
	'NEWS':'Display program news (new capabilities, updates, etc)',
	'301': 'center of the Moon', 
	'Apollo-11 @ 301':'Apollo-11', 
	'*@301':'sites on moon',
	'*@399':'sites on earth'
} 

async def get_place(place='MB'):
	""" """
	params = {
		'format':'json',
		'COMMAND':place,
		}
	logger.debug('getting place({}):{}'.format(place,places[place]))
	resp = await restGet(URL,params)
	return resp

async def get_body(bodyId='499', JD=J2000):
	""" """
	STARTOFEPH='$$SOE'  # Start of ephemeris
	ENDOFEPH  ='$$EOE'
	CAP = 'CAP' #flag (closest-apparition)
	
	params = {
		'format':'json',
		'COMMAND':bodyId,  # Planetary systems may have two associated integer ID numbers assigned. Those greater than 100 and ending in 99 (199, 299, 399, 499, 599, 699, 799, 899, 999) refer to the planet CENTER only. To instead select planetary (system) BARYCENTERS, use the numeric ID codes less than 10 and greater than or equal to 0: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10. This selects the center-of-mass the objects in the planetary system move with respect to, including the planet itself and its natural satellites. For example, 399 is the Earth’s center, 3 is the Earth-Moon Barycenter point about which the Earth and Moon both move, and 301 is the center of the Moon.
		#'REF_PLANE':'ECLIPTIC',  # ECLIPTIC, FRAME, BODY EQUATOR
		# """ Ecliptic: In this reference frame, the x-y plane is based on the orbit of the Earth around the Sun. Since the Earth’s orbit plane fluctuates slightly due to gravitational perturbations, the ecliptic chosen can be at a fixed standard time (such as the J2000.0 epoch 2000-Jan-1.5) providing an inertial frame, or instead the time of interest (“of-date”), providing a dynamic frame, depending on the purpose. Both amount to adopting a standard due to definitional ambiguities caused by the Earth and Moon’s mutual motion affecting the Earth’s orbit plane. When transforming between the underlying ICRF reference frame, Horizons uses the IAU76/80 fixed obliquity of 84381.448 arcsec at the J2000.0 standard epoch, and an associated time-varying model for “of-date” ecliptic. When transforming between FK4/B1950, a fixed obliquity of 84404.8362512 arcseconds is used at the standard epoch, with an associated time-varying model for other instants. """
		'OBJ_DATA':'NO',
		'MAKE_EPHEM':'YES',
		'EPHEM_TYPE':'ELEMENTS',  #'ELEMENTS', #  'OBS', 
			#OBSERVER	Observables (RA/DEC, Az/El, physical aspect, angles, uncertainties)	telescope observations; 
			#ELEMENTS	Osculating orbital elements	instantaneous geometry over time, celestial mechanics; 
			#VECTORS	Cartesian state vectors and uncertainties	dynamical studies, propagation, programming; 
			#APPROACH	Close approaches to planets (and 16 largest asteroids)	encounter planning & hazards; 
			#SPK	SPK binary trajectory files (asteroids and comets only)	time-continuous states, navigation, mission-planning, plug-in for visualization tools
		'QUANTITIES':"A",
		'TLIST':"'{}' '{}'".format(J2000, julianday()),
		'TLIST_TYPE':'JD',
		#'START_TIME':'{}'.format(JD),
		#'STOP_TIME':'{}'.format(JD),
		#'STEP_SIZE':'0',  # the interval between specified START_TIME and STOP_TIME
		'CENTER':'500@10', #'coord',   # Center (or coordinate origin, or observering location) This is the point to which output quantities for the target (such as coordinates) are referred: (0,0,0). It is typically where the observer is located. An observation point is “topocentric” if on the surface of a body with a known rotational state. If at the center of a physical body, the observing point is “bodycentric” (with “geocentric” referring to the particular case of origin at the Earth’s center). If at the center-of-mass of some dynamical system, the center or observer is “barycentric”. 
		'COORD_TYPE':'GEODETIC',  # CYLINDRICAL:E-long - Angle eastward from XZ plane      (DEGREES), DXY    - Distance from, Z axis              (KM), DZ     - Height above XY equator plane     (KM) ; GEODETIC: (generally this means map coordinates), E-long - Geodetic east longitude (DEGREES), lat    - Geodetic latitude  (DEGREES), h      - Altitude above reference ellipsoid (km)
		#'SITE_COORD':  "'5.5', '51.5', '0.022'",  # '5.5,51.5,0.022',  # {E. long., lat, height} (KM and DEG). 
		'CAL_FORMAT' : 'JD',
		'ANG_FORMAT':'DEG',  #  DEG  HMS
		#'RTS_ONLY' : 'YES' # rise transit set 
		}
	logger.debug('getting body:{}'.format(bodyId))
	body = await restGet(URL,params)
	if 'result' in body:
		lns	=body['result'].split('\n')
		eph=[]
		ineph=False
		for ln in lns:
			if ENDOFEPH in ln:
				ineph=False
			if ineph:
				eph.append(ln)
			if STARTOFEPH in ln:
				ineph=True
			logger.debug(ln)
		#logger.info("eph:{}".format(eph))
		return eph
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
	
	list = _loop.run_until_complete(get_place())
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
	if hasattr(body, '__iter__'):
		eph=[]
		ineph=False
		logger.info("eph:{}".format(body))
	else:
		logger.info("body:{}".format(body))

