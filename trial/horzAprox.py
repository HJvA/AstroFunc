# https://ssd.jpl.nasa.gov/planets/approx_pos.html
import math,sys,os
sys.path.append('.')
import lib
from lib.Matrix import Matrix,Vector
from lib.Rotation import Angle,RotMatrix,RotAx,DegAngle,Coordinate
from submod.pyCommon.brentRoot import BrentRootFinder


G = 6.7430e-11  # gravitational constant [N⋅m2⋅kg−2],  F = G⋅(m1⋅m2)/rˆ2
AU = 1.495978707e11 # astronomical unit [m] 


TERMS = {
	'eccentricity':"e= distance between the foci divided by the length of the major axis: how much it is elongated compared to a circle, e = sqrt(1-(b/a)ˆ2)",
	'semi_major_axis':"a= half the distance between perihelion and aphelion [a]",
	'semi_minor_axis':"b= half the distance between  [b]",
	
	'inclination':"I= tilt of the ellipse with respect to the reference plane",
	'LongitudeAscendingNode':"Ω= angle in ref plane of the ascending node of the ellipse",
	'arg-periapsis':"w=; angle measured from the ascending node to the periapsis: orientation of the ellipse in the orbital plane",
	'true_anomaly':"f=; angle from the periapsis at epoch from focus of ellipse",
	'mean_anomaly':"M=E-e*sin(E); fraction of an elliptical orbit's period that has elapsed since the orbiting body passed periapsis, expressed as an angle",
	
	'mean':"fictitious 'value': varies linearly with time",
	'eccentric_anomaly':"E = ",
	'ascending node':" where the orbit passes from south to north through the reference plane",
	'apoapsis':"farthest point in an orbit,  largest distance between the orbiter and its host body",
	'periapsis':"point in an orbit closest to the primary",
	
	'vernal equinox':"solar equinox is a moment in time when the Sun crosses the Earth's equator (daytime and nighttime are of approximately equal duration all over the planet) equinoxes are currently defined to be when the apparent geocentric longitude of the Sun is 0° and 180° , Intersection of J2000 equatorial and ecliptic planes",
	'Topocentric':"Associated with an object on or near the surface of a natural body. X:North, Y:West, Z:Up",
	'Planetocentric':"Z:North, ",
	'Longitude':"Spherical Coordinates angle from +X axis to projection of position vector on X-Y plane increases in counter-clockwise direction",
	'Azimuth':"Angle from +X axis to projection of position vector on x-y plane",
	'Elevation':"Angle between position vector and x-y plane",
}

class KeplerOrbit():
	def __init__(self, semi_major_axis, eccentricity, Inclination, LongitudeAscendingNode, argument_periapsis, mean_anomaly):
		""" ref = Earth orbital plane J2000 """
		self.a = semi_major_axis
		self.e = eccentricity
		self.I = DegAngle(Inclination)
		self.MA = DegAngle(mean_anomaly)
		self.OM = DegAngle(LongitudeAscendingNode)
		self.w = DegAngle(argument_periapsis)

	def velocity(self, m1,m2, r):
		mu = G*(m1+m2)
		return math.sqrt(mu*(2/r-1/self.a)) 
	
	def eccentricAnomaly(self):
		""" M = E−e*sinE  (Kepler equation) """
		def func(E):
			es = 180/math.pi * self.e
			return E- es * math.sin(E) - self.MA.rad  
		brt = BrentRootFinder(func, 0, 2*math.pi)
		E,fE = brt.Solve()
		return E
	
	def heliocentric(self):  # ecliptic
		""" x′ =a(cosE−e) ; y′ =a√1−e2 sinE ; z′ =0. """
		E = self.eccentricAnomaly()
		x = self.a*(math.cos(E)-self.e)
		y = self.a*math.sqrt(1-self.e*self.e)*math.sin(E)
		z =0
		return x,y,z
	
	def ecliptic(self):  # equatorial
		""" recl so that xecl = yecl = zecl == Mr′ ≡ Rz(−Ω)Rx(−I)Rz(−ω)r′ """
		x,y,z = self.heliocentric()
		vec = Coordinate([x,y,z])
		ro = RotMatrix(-self.OM, RotAx.R3)
		ri = RotMatrix(-self.I, RotAx.R1)
		rw = RotMatrix(-self.w, RotAx.R3)
		vec.Rotate(ro)
		vec.Rotate(ri)
		vec.Rotate(rw)
		return vec
	
	def meanAnomaly(self, Teph):
		T=(Teph-2451545.0)/36525
		#M =self.OM − math.pi  + bT2 + ccos(fT) + ssin(fT)

""" Osculating orbital elements table
	Output quantities (fixed):
           JDTDB    Epoch Julian Date, Barycentric Dynamical Time
            EC      Eccentricity
            QR      Periapsis distance
            IN      Inclination w.r.t. xy-plane (degrees)
            OM      Longitude of Ascending Node (degrees)
            W       Argument of Perifocus (degrees)
            Tp      Periapsis time (user specifies absolute or relative date)
             N      Mean motion (degrees/DU)
            MA      Mean anomaly (degrees)
            TA      True anomaly (degrees)
             A      Semi-major axis
            AD      Apoapsis distance
            PER     Orbital Period  """

""" Planet	Equatorial
Radius	Mean
Radius	 
Mass	Bulk
Density	Sidereal
Rotation Period	Sidereal
Orbital Period	 
V(1,0)	Geometric
Albedo	Equatorial
Gravity	Escape
Velocity


 	(km)	(km)	(×1024 kg)	(g cm-3)	(d)	(y)	(mag)	 	(m s-2)	(km s-1)

Mercury	2440.53 [D]
±0.04    	2439.4 [D]
±0.1    	0.330103 [F]
±0.000021    	5.4289 [*]
±0.0007    	58.6462 [C]
 	0.2408467 [B]
 	-0.60 [E]
±0.10    	0.106 [B]
 	3.70 [*]
 	4.25 [*]
 
Venus	6051.8 [D]
±1.0    	6051.8 [D]
±1.0    	4.86731 [G]
±0.00023    	5.243 [*]
±0.003    	-243.018 [C]
 	0.61519726 [B]
 	-4.47 [E]
±0.07    	0.65 [B]
 	8.87 [*]
 	10.36 [*]
 
Earth	6378.1366 [D]
±0.0001    	6371.0084 [D]
±0.0001    	5.97217 [H]
±0.00028    	5.5134 [*]
±0.0003    	0.99726968 [B]
 	1.0000174 [B]
 	-3.86 [B]
 	0.367 [B]
 	9.80 [*]
 	11.19 [*]
 
Mars	3396.19 [D]
±0.1    	3389.50 [D]
±0.2    	0.641691 [I]
±0.000030    	3.9340 [*]
±0.0007    	1.02595676 [C]
 	1.8808476 [B]
 	-1.52 [B]
 	0.150 [B]
 	3.71 [*]
 	5.03 [*]
 
Jupiter	71492 [D]
±4    	69911 [D]
±6    	1898.125 [J]
±0.088    	1.3262 [*]
±0.0003    	0.41354 [C]
 	11.862615 [B]
 	-9.40 [B]
 	0.52 [B]
 	24.79 [*]
 	60.20 [*]
 
Saturn	60268 [D]
±4    	58232 [D]
±6    	568.317 [K]
±0.026    	0.6871 [*]
±0.0002    	0.44401 [C]
 	29.447498 [B]
 	-8.88 [B]
 	0.47 [B]
 	10.44 [*]
 	36.09 [*]
 
Uranus	25559 [D]
±4    	25362 [D]
±7    	86.8099 [L]
±0.0040    	1.270 [*]
±0.001    	-0.71833 [C]
 	84.016846 [B]
 	-7.19 [B]
 	0.51 [B]
 	8.87 [*]
 	21.38 [*]
 
Neptune	24764 [D]
±15    	24622 [D]
±19    	102.4092 [M]
±0.0048    	1.638 [*]
±0.004    	0.67125 [C]
 	164.79132 [B]
 	-6.87 [B]
 	0.41 [B]
 	11.15 [*]
 	23.56 [*]
 
   """

if __name__ == '__main__':
	import submod.pyCommon.tls as tls
	logger = tls.get_logger(__file__)
	# mars 1-1-2000
	A = 2.279391329739729E+08 #km
	EC= 9.331510145826100E-02
	IN= 1.849876477108884E+00
	OM= 4.956200565861963E+01
	W = 2.865373830861993E+02
	MA= 1.935648274725794E+01
	mars = KeplerOrbit(A, EC, IN, OM, W, MA)
	logger.info("mars:{}".format(mars.ecliptic()))