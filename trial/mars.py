from skyfield.api import load
from skyfield.api import N,E,S,W, wgs84

import sys
sys.path.append('.')
import submod.pyCommon.tls as tls


if __name__ == '__main__':
	logger = tls.get_logger(__file__)

	planets = load('de421.bsp')   
	earth, planet = planets['earth'], planets['mars']   
	ts = load.timescale()                                                              
	t = ts.now()                           
	position = earth.at(t).observe(planet)           
	ra, dec, distance = position.radec()  
	logger.info("#  planet:{}".format(planet))
	logger.info("## ra:{} dec:{} dist:{}".format(ra,dec,distance))
	
	nizas     = earth + wgs84.latlon(43.514 * N, 3.409 * E, 73)
	bouboules = earth + wgs84.latlon(43.531 * N, 3.258 * E, 190)
	veldhoven = earth + wgs84.latlon(51.418 * N, 5.406 * E, 24)
	logger.info("# veldhoven:{} @tm:{}".format(veldhoven,t))
	astrometric = veldhoven.at(t).observe(planet)
	alt, az, d = astrometric.apparent().altaz()

	logger.info("## apparent: alt:{}  az:{}".format(alt,az))
	