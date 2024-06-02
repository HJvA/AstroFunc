# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

import os,sys,math
from Rotation import Coordinate,Angle,DegAngle
from AstroTime import AstroTime

AU = 1.495978e11  # m   (astronomical unit)
ly = 9.46053e15   # m   (light year)
pc = 3.085678e16  # m   (parsec) 

#modPath = os.path.split(sys.argv[0])[0]  #get prg name
modPath = os.path.dirname(__file__)
#if not modPath in sys.path:
#    sys.path.append(modPath)
global datPath
#datPath = os.path.join(os.path.splitdrive(modPath)[0], r'..','HastroDat')
datPath = os.path.abspath(os.path.join(modPath, '..','HastroDat'))
#if not os.path.isdir(datPath):
#    datPath = os.path.join(modPath, r'..','HastroDat')
    
print ("module:{} dat:{}".format(modPath,datPath))
del modPath

class bo:
    """ CelestialObj type enum
    """
    Planet = 1
    Star   = 2
    Constellation =3
    Sun    = 4
    Moon   = 5
    Day    = 6
    Hour   = 7
    StarInConstel =8
    DistUnits=('','au','ly','','au','km')
    #BodyTypes = set ([i for i in range(boPlanet,boMoon)])

class pn:
    """ planet identification (enums and names)
    """
    (Mercury,Venus,Mars,Jupiter,Saturn,Uranus,Neptune,Pluto,\
     Moon,Earth,Sun) = range(11)
    (a,e,I,L,w,W) = range(6) # Osculating Elements
    (aa282_planmean,
     aa282_trigterms,
     aa282_etrigterms,
     aa282_moonmean,
     JPL) = range(5)
    dbElm = True #True  # get elements from database
    def nmPlanet(idPlanet):
        """ planet name
        """
        return _nmPlanets[idPlanet]
    nmPlanet = staticmethod(nmPlanet)
    def PlanetsList():
        return [_nmPlanets[i] for i in range(len(_nmPlanets)-3)]
    PlanetsList = staticmethod(PlanetsList)
    def idPlanet(name):
        return pn.PlanetsList().index(name)
    idPlanet = staticmethod(idPlanet)

_nmPlanets = {
    pn.Mercury :u'mercury',
    pn.Venus   :u'venus',
    pn.Mars    :u'mars',
    pn.Jupiter :u'jupiter',
    pn.Saturn  :u'saturn',
    pn.Uranus  :u'uranus',
    pn.Neptune :u'neptune',
    pn.Pluto   :u'pluto',
    pn.Moon    :u'maan',
    pn.Earth   :u'earthmoon',
    pn.Sun     :u'sun'  }

class GeoLocation(object):
    """ base class for location on earth surface
    """
    def __init__(self, Longitude, Latitude, Height=1.0):
        """
        """
        self.Longitude = DegAngle(Longitude)
        self.Latitude = DegAngle(Latitude)
        self.Height = float(Height)
        self.tzone=0 # filled later by derived GeoSite

class CelestialObj(Coordinate):
    """ base class for star,planet,moon,sun
    """
    name=""    # name of body
    ConstelId=0  # id of constellation
    Vapparent=None  # apparent magnitude
    def __init__(self, RightAscension, Declination, Distance=1):
        """  to cartesian coordinates (formula 5.1 USNO circular 179)
        """
        assert isinstance(RightAscension, Angle)
        assert isinstance(Declination, Angle)
        Coordinate.__init__(self,[ 
            Distance * math.cos(Declination.rad) * math.cos(RightAscension.rad),
            Distance * math.cos(Declination.rad) * math.sin(RightAscension.rad),
            Distance * math.sin(Declination.rad)])
    def RightAscension(self):
        return self.Longitude()
    def Declination(self):
        """ angle measured in degrees north and south of the celestial equator
        """
        return self.Latitude()
    def SetTime(self, AstrTime,  Precision=1):
        """ virtual : defines time at which to compute position
        """
        assert isinstance(AstrTime, AstroTime), "time as AstroTime"
        