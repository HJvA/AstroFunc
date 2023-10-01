# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import sys
import math
from AstroTypes import pn
from Rotation import Angle,DegAngle,ArcsAngle 
import AstroTime


# Keplerian elements and their rates, with respect to the mean ecliptic
# and equinox of J2000, valid for the time-interval 1800 AD - 2050 AD.
# http://ssd.jpl.nasa.gov/?planet_pos

_Planets =  {
    pn.Mercury :
            ((0.38709927,0.00000037),        #SemiMajorAxis  [au,au/cy]
             (0.20563593,0.00001906),        #Eccentricity   [1,1/cy]
             (7.00497902,-0.00594749),       #Inclination    [deg,deg/cy]
             (252.25032350,149472.67411175), #MeanLongitude  [deg,deg/cy]
             (77.45779628,0.16047689),       #LongitudePerihelion  (periapsis) [deg,deg/cy]
             (48.33076593,-0.12534081),      #LongitudeAscendingNode  [deg,deg/cy]
             (0,0),                          #MeanMotion
             (0,0)),                         #Mass
    pn.Venus : 
            ((0.72333566,0.00000390),(0.00677672,-0.00004107),(3.39467605,-0.00078890),
             (181.97909950,58517.81538729),(131.60246718,0.00268329),(76.67984255,-0.27769418),(0,0)),
    pn.Earth: 
            ((1.00000261,0.00000562),
             (0.01671123,  -0.00004392),
             (-0.00001531,   -0.01294668),
             (100.46457166, 35999.37244981), # T elp = 100*27'59.13885" + 129597742.2930" t
             (102.93768193, 102.93768193),   # w_elp = 102*56'14.45766" + 1161.24342" t
             (0.0, 0.0),
             (0,0),
             (0,0)), 
    pn.Mars:  
            (( 1.52371034,0.00001847),       #SemiMajorAxis
             (0.09339410,0.00007882),        #Eccentricity
             (1.84969142,-0.00813131),       #Inclination
             (-4.55343205,19140.30268499),   #MeanLongitude
             (-23.94362959,0.44441088),      #LongitudePerihelion
             (49.55953891,-0.29257343),      #LongitudeAscendingNode
             (0,0),                          #MeanMotion
             (0,0)),                         #Mass
    pn.Jupiter:
            ((5.20288700,-0.00011607),       #SemiMajorAxis
             (0.04838624,-0.00013253),       #Eccentricity
             (1.30439695,-0.00183714),       #Inclination
             (34.39644051,3034.74612775),    #MeanLongitude
             (14.72847983,0.21252668),       #LongitudePerihelion
             (100.47390909,0.20469106),      #LongitudeAscendingNode
             (0,0),                          #MeanMotion
             (0,0)),                         #Mass
    pn.Saturn: 
            ((9.53667594, -0.00125060),
             (0.05386179, -0.00050991),
             (2.48599187,  0.00193609),
             (49.95424423, 1222.49362201),
             (92.59887831,-0.41897216),
             (113.66242448,-0.28867794),
             (0,0),
             (5.68462313752e26, 0)),
    pn.Uranus: 
            ((19.18916464,-0.00196176),        #SemiMajorAxis
             (0.04725744,-0.00004397),        #Eccentricity
             (0.77263783,-0.00242939),       #Inclination
             (313.23810451,428.48202785), #MeanLongitude
             (170.95427630,0.40805281),       #LongitudePerihelion
             (74.01692503,0.04240589),      #LongitudeAscendingNode
             (0,0),                          #MeanMotion
             (0,0)),                         #Mass
    pn.Neptune:
            ((30.06992276,0.00026291),        #SemiMajorAxis
             (0.00859048,0.00005105),        #Eccentricity
             (1.77004347,0.00035372),       #Inclination
             (-55.12002969,218.45945325), #MeanLongitude
             (44.96476227,-0.32241464),       #LongitudePerihelion
             (131.78422574,-0.00508664),      #LongitudeAscendingNode
             (0,0),                          #MeanMotion
             (0,0)),                         #Mass
    pn.Pluto: 
            ((39.48211675,-0.00031596),        #SemiMajorAxis
             (0.24882730,0.00005170),        #Eccentricity
             (17.14001206,0.00004818),       #Inclination
             (238.92903833,145.20780515), #MeanLongitude
             (224.06891629,-0.04062942),       #LongitudePerihelion
             (110.30393684,-0.01183482),      #LongitudeAscendingNode
             (0,0),                          #MeanMotion
             (0,0)),                         #Mass
    pn.Moon:       # preliminary
            ((60.2666  ,0),        #SemiMajorAxis [earth radii]
             (0.054900,0),        #Eccentricity
             (5.1454,0),       #Inclination
             (DegAngle(218,18,59.95571).deg, ArcsAngle(1732559343.73604).deg), #MeanLongitude  elp
             (DegAngle(83,21,11.67475).deg, ArcsAngle(14643420.3171).deg),  #LongitudePerigee  elp
             (125.1228, -0.0529538083*365.25 ),   #LongitudeAscendingNode  125*02'40.39816" + 6967919.5383" * t
             (0,0),                          #MeanMotion
             (0,0))           #Mass
                }                        



class OscElm:
    (a,e,I,L,w,W) = range(6)
    def __init__(self, KepDef):
        self.KepDef = KepDef

    def SemiMajorAxis(self, Coeff=0):  # a [au]
        return self.KepDef[0][Coeff]
    def Eccentricity(self, Coeff=0):   # e []
        return self.KepDef[1][Coeff]
    def Inclination(self, Coeff=0):    # I [deg]
        return self.KepDef[2][Coeff]
    def MeanLongitude(self, Coeff=0):  # L [deg]
        return self.KepDef[3][Coeff]
    def LongitudePerihelion(self, Coeff=0): # w [deg}
        return self.KepDef[4][Coeff]
    def LongitudeAscendingNode(self, Coeff=0):  # W Ohm [deg]
        return self.KepDef[5][Coeff]


class OscElements(OscElm):
    def __init__(self, pnPlanet, AstTime):
        OscElm.__init__(self, _Planets[pnPlanet])
        #self.TJ2000 = AstTime.cyTJ2000()
        cy = AstTime.cyTJ2000() 
        self.t = [1,cy]
        for i in range(1):
            self.t.append(cy * self.t[-1])
    def EvalPolyn(self,coeffs):
        """ evaluate polynome using coeffs c0,c1,c2...
            into co*t[0]+c1*t[1]+c2*t[2]+....
        """
        val=0.0
        i=0
        for coeff in coeffs:
            val += coeff * self.t[i]
            i+=1
        return val

    def SemiMajorAxis(self):
        return self.EvalPolyn(self.KepDef[self.a])
        #return OscElm.SemiMajorAxis(self,0) + \
        #   OscElm.SemiMajorAxis(self,1) * self.TJ2000
    def Eccentricity(self):
        return self.EvalPolyn(self.KepDef[self.e])
        #return OscElm.Eccentricity(self,0) + \
        #   OscElm.Eccentricity(self,1) * self.TJ2000
    def Inclination(self):
        return DegAngle(self.EvalPolyn(self.KepDef[self.I]))
        #return DegAngle(OscElm.Inclination(self,0) + \
        #   OscElm.Inclination(self,1) * self.TJ2000)
    def MeanLongitude(self):
        return DegAngle(self.EvalPolyn(self.KepDef[self.L]))
        #return DegAngle(OscElm.MeanLongitude(self,0) + \
        #   OscElm.MeanLongitude(self,1) * self.TJ2000)
    def LongitudePerihelion(self):
        return DegAngle(self.EvalPolyn(self.KepDef[self.w]))
        #return DegAngle(OscElm.LongitudePerihelion(self,0) + \
        #   OscElm.LongitudePerihelion(self,1) * self.TJ2000)
    def LongitudeAscendingNode(self):
        return DegAngle(self.EvalPolyn(self.KepDef[self.W]))
        #return DegAngle(OscElm.LongitudeAscendingNode(self,0) + \
        #   OscElm.LongitudeAscendingNode(self,1) * self.TJ2000)

def _test():
    pnBody = pn.Saturn
    print _Planets[pnBody][0]
    t = (2007, 4, 5, 14, 0, 0)
    pnBody = pn.idPlanet('saturn')
    body = OscElements(pnBody, AstroTime.AstroTime(t))
    print pn.nmPlanet(pnBody)
    print 'a=',body.SemiMajorAxis()
    print 'I=%s' % body.Inclination()
    print 'e=%s' % body.Eccentricity()
    print 'L=%s' % body.MeanLongitude()
    print 'wp=%s' % body.LongitudePerihelion()
    print 'Wa=%s' % body.LongitudeAscendingNode()


if __name__ == '__main__':
    _test()
