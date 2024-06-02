# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

import sys,os,math
from AstroTypes import pn
from Rotation import Angle,DegAngle,Coordinate,PolarCoord,SQR

class projection(Coordinate):
    R=1.0   # radius of sphere
    lon0=0.0  # central meridian
    lat0=0.0  # central latitude
    def toMap(self):
        return (0.0,0.0)
    def fromMap(self,x,y):
        return projection(0.0,0.0,0.0)

class mercator(projection):
    def toMap(self):
        x = self.R * (self.Longitude().rad - self.lon0)
        y = self.R * math.log(math.tan(math.pi/4+ self.Latitude().rad/2))
        return (x,y)
    def fromMap(self,x,y):
        lat = math.pi/2 - 2*math.atan(math.exp(-y/self.R))
        lon = x/self.R +self.lon0
        return PolarCoord(Angle(lon),Angle(lat),self.R)


class stereographic(projection):
    def toMap(self):
        R = 2 * self.R * math.tan(math.pi-self.Latitude().rad/2)
        x = R * math.sin(self.Longitude().rad-self.lon0)
        y = -R * math.cos(self.Longitude().rad-self.lon0)
        return (x,y)
    def fromMap(self,x,y):
        lat = (2 * math.atan2(math.sqrt(SQR(x)+SQR(y)),2*self.R) - math.pi/2)
        lon = self.lon0 + math.atan2(x,y)
        return PolarCoord(Angle(lon),Angle(lat),self.R)

class Stereographic(projection):
    """ http://mathworld.wolfram.com/StereographicProjection.html
    """
    def toMap(self):
        lon = self.Longitude().rad-self.lon0
        k = 2*self.R/(1+math.sin(self.lat0)*math.sin(self.Latitude().rad)+
                      math.cos(self.lat0)*math.cos(self.Latitude().rad)*
                      math.cos(lon))
        x = k*math.cos(self.Latitude().rad)*math.sin(lon)
        y = k*(math.cos(self.lat0)*math.sin(self.Latitude().rad)-
                      math.sin(self.lat0)*math.cos(self.Latitude().rad)*
                      math.cos(lon))
        return (x,y)
        
    def fromMap(self,x,y):
        rho = math.sqrt(SQR(x)+SQR(y))
        c = 2*math.atan2(rho,2*self.R)
        lat = math.asin(math.cos(c)*math.sin(self.lat0)+
                        y*math.sin(c)*math.cos(self.lat0)/rho)
        lon = self.lon0 + math.atan2(x*math.sin(c),
                                rho*math.cos(self.lat0)*math.cos(c)-
                                y*math.sin(self.lat0)*math.sin(c))
        return PolarCoord(Angle(lon),Angle(lat),self.R)


class StereographicEquatorial(projection):
    """ x' = cos(Lat)* sin(Lon)
        y' = sin(Lat)
        z' = cos(Lat) *cos(Lon)
    """
    def toMap(self):
        x = self[0] / (1 + self[2])
        y = self[1] / (1 + self[2])
        return (x,y)
        
if __name__ == '__main__':
    print("projection mercator")
    vec = Stereographic([1.0, 0.0, 1.0])
    onMap = vec.toMap()
    print ("vec %s onMap:%s" % (vec.fromMap(onMap[0],onMap[1]), onMap))
    
