# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

import math
from Rotation import Angle,DegAngle,Coordinate,SQR,RotMatrix,RotAx,VectorAngle
from AstroTypes import CelestialObj,pn,AU
import AstroTime

#import OscElmJPL
import OscElm282
import moon282

MoonEarthMassRatio =734.9e20 / (5.9736e24 + 734.9e20)

class OscElms:
    def __init__(self, pnBody, AstTime, Precision=2):
        if pnBody==pn.Moon and Precision>1:
            self.OscElms = moon282.MoonJ2000(AstTime, Precision)
        else:
            self.OscElms = OscElm282.OscElements(pnBody, AstTime, Precision)
    def SemiMajorAxis(self):
        return self.OscElms.SemiMajorAxis()
    def Eccentricity(self):
        return self.OscElms.Eccentricity()
    def Inclination(self):
        return self.OscElms.Inclination()
    def MeanLongitude(self):
        return self.OscElms.MeanLongitude()
    def LongitudePerihelion(self):
        return self.OscElms.LongitudePerihelion()
    def LongitudeAscendingNode(self):
        return self.OscElms.LongitudeAscendingNode()
    

class KeplerMotion(OscElms):
    EccentAnomaly = None
    ObliquityJ2000 = 84381.406/3600  # eps0 USNO 179 table 5.1

    def SolveKepler(self, MeanAnomaly, Eccentricity):
        EccentricAnomaly = \
            Angle(MeanAnomaly.rad + Eccentricity * math.sin(MeanAnomaly.rad))       # 8.36
        while True:
                # 8.37
            dM = Angle(MeanAnomaly.rad -
                    (EccentricAnomaly.rad -
                        Eccentricity * math.sin(EccentricAnomaly.rad)))
            dE = dM.rad / (1.0 - Eccentricity * math.cos(EccentricAnomaly.rad))
            if (abs(dE) < 1e-6):
                break
            else:
                EccentricAnomaly.rad += dE
        return EccentricAnomaly

    def EccentricAnomaly(self):
        if self.EccentAnomaly == None:
            MeanAnomaly = (self.MeanLongitude() - self.LongitudePerihelion()).Modulo()
            if MeanAnomaly.rad > math.pi:
                MeanAnomaly.rad = MeanAnomaly.rad - 2 * math.pi
            self.EccentAnomaly = self.SolveKepler(MeanAnomaly, self.Eccentricity())
        return self.EccentAnomaly

    def OrbitalPosition(self):
        return Coordinate([   # 8.32 
             (self.SemiMajorAxis() * 
                        (math.cos(self.EccentricAnomaly().rad)-self.Eccentricity())),
             (self.SemiMajorAxis() *
                        math.sqrt(1-SQR(self.Eccentricity()))*
                        math.sin(self.EccentricAnomaly().rad)),
             0.0 ] )
    def OrbitalVelocity(self):  # Kaula 1966
        v = n*self.SemiMajorAxis()/ (1 - self.Eccentricity()*math.cos(self.EccentricAnomaly().rad))
        return Coordinate([
            -v*math.sin(self.EccentricAnomaly().rad),
            v*math.sqrt(1-SQR(self.Eccentricity()))*
                        math.cos(self.EccentricAnomaly().rad),
            0.0 ])

class KeplerPlanet(KeplerMotion):
    def __init__(self, pnBody, AstTime, Precision=2):
        KeplerMotion.__init__(self, pnBody, AstTime, Precision)
        if pnBody in [pn.Earth,pn.Sun]:
            if Precision>33:  #tbd correction for BaryCenter -> EarthCenter 
                self._crdEarth = Coordinate(KeplerPlanet(pn.Moon, AstTime).CoordEclipticEquinox() * (MoonEarthMassRatio *1000/AU))
            else:
                self._crdEarth = Coordinate([0,0,0])
        else:
            self._crdEarth = KeplerPlanet(pn.Earth, AstTime, Precision).CoordEclipticEquinox()
            if pnBody==pn.Moon:
                self._crdEarth *= (AU/1000.0)  # AU -> km

    def CoordEclipticEquinox(self):
        """ heliocentric for planets, geocentric for moon
        """
        crd = self.OrbitalPosition()
        if crd == None: 
            return None
        ArgOfPerihelion = self.LongitudePerihelion() - self.LongitudeAscendingNode()
        # 8.33
        crd.Rotate(RotMatrix(-ArgOfPerihelion, RotAx.R3))   
        crd.Rotate(RotMatrix(-self.Inclination(), RotAx.R1))
        crd.Rotate(RotMatrix(-self.LongitudeAscendingNode(), RotAx.R3))
        return crd

    def PhaseAngle(self):
        """ angle @ body between earth and sun
        """
        crd1 = self.CoordEclipticEquinox()
        crd2 = crd1 - self._crdEarth
        ang = VectorAngle(crd1, crd2)
        out = crd1.OutProduct(crd2)
        if out[2]>0:
            ang = -ang
        return ang.Modulo()

    def CoordGeoBaryCentric(self):  # geoCentric geoMetric J2000 Equatorial frame
        crd = Coordinate(self.CoordEclipticEquinox() - self._crdEarth) 
        return crd.Rotated(RotMatrix(DegAngle(-self.ObliquityJ2000), RotAx.R1))


class Sun(CelestialObj):
    """ compute location of sun in earthmoon-centric coordinates
    """
    def __init__(self, AstTime, Precision=1):
        self.SetTime(AstTime, Precision)
        self.name = u'Sun'

    def SetTime(self, AstTime, Precision=1):
        self.Kepler = KeplerPlanet(pn.Earth, AstTime, Precision)
        crd = Coordinate(-self.Kepler.CoordEclipticEquinox())
        Coordinate.__init__(self, crd.Rotated(RotMatrix(DegAngle(-self.Kepler.ObliquityJ2000), RotAx.R1)))
    def PhaseAngle(self):
        return None
  
class Planet(CelestialObj):
    def __init__(self, pnPlanet, AstTime, Precision=1):
        self.pPlanet = pnPlanet
        self.name = pn.nmPlanet(pnPlanet)
        self.SetTime(AstTime, Precision)
    def SetTime(self, AstTime, Precision=1):
        CelestialObj.SetTime(self, AstTime, Precision)
        self.Kepler = KeplerPlanet(self.pPlanet, AstTime, Precision)
        Coordinate.__init__(self, self.Kepler.CoordGeoBaryCentric())

    def CoordICRS(self):  
        # Heliocentric equatorial
        crd = self.Kepler.CoordEclipticEquinox();
        return crd.Rotated(RotMatrix(DegAngle(-self.Kepler.ObliquityJ2000), RotAx.R1))

    def PhaseAngle(self):
        return self.Kepler.PhaseAngle()


class Moon(CelestialObj):
    """ compute moon position using Kepler's laws
    """
    def __init__(self, AstTime, Precision=1):
        self.SetTime(AstTime, Precision)
        #self.name = pn.nmPlanet(pn.Moon) 
    def SetTime(self, AstTime, Precision=1):
        self.Kepler = KeplerPlanet(pn.Moon, AstTime, Precision)
        self.name = self.Kepler.OscElms.name
        crd = Coordinate(self.Kepler.CoordEclipticEquinox())
        Coordinate.__init__(self, crd.Rotated(RotMatrix(DegAngle(-self.Kepler.ObliquityJ2000), RotAx.R1)))
    def PhaseAngle(self):
        return self.Kepler.PhaseAngle()
    

if __name__ == '__main__':
    import time
    prec=5
    print (pn.PlanetsList())
    t = time.localtime()
    t = (2009, 2, 10, 17, 0, 0)
    astm = AstroTime.AstroTime(t,UTCofs=1)
    bodies = (Sun(astm,Precision=prec), Moon(astm,Precision=prec),
              Planet(pn.Saturn, astm, Precision=prec))
    for body in bodies:
        print (body.name)
        if isinstance(body, Planet):
            print ('HelioCentric ICRS=%s' % body.CoordICRS())
        #print 'GeoCentric= %s, %s, %s' % body.Polar()
        print ('GeoCentric Ra=%s, Declination=%s, distance=%s' % \
              (body.RightAscension().deg,body.Declination().deg,body.Distance()))
        if not (body.PhaseAngle() is None):
            print ('PhaseAngle %s (%s)' % (body.PhaseAngle(),body.PhaseAngle().AsMoonPhase()))
