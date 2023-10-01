# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

# dd     by   update
# 090211 hjva OutProduct

import math
import sys
from Matrix import Matrix,Vector,Rational

#axis = dict(R1=0, R2=1, R3=2)
class RotAx:
    R1=0
    R2=1
    R3=2

def SQR(x):
    return x*x

def AngDiff (ang1,ang2):
    """ shortest difference between 2 angles
    """
    return (ang1-ang2).Modulo(0)

class RotMatrix(Matrix):
    def __init__(self, RotAngle, RotAxis=None):
        if isinstance(RotAngle, Matrix):
            Matrix.__init__(self, RotAngle)  # just copy the matrix
        else:
            Matrix.__init__(self,Matrix.id(3))
            if isinstance(RotAngle, Angle):
                pass                         # use this
            else:
                RotAngle = Angle(RotAngle)   # may be numeric or string
            CosPhi = math.cos(RotAngle.rad)
            SinPhi = math.sin(RotAngle.rad)
            if isinstance(RotAxis, Vector):  # rotation axis is a vector
                self *= CosPhi
                TmpM = Matrix([
                    [SQR(RotAxis[0]),       RotAxis[0]*RotAxis[1], RotAxis[0]*RotAxis[2]],
                    [RotAxis[1]*RotAxis[0], SQR(RotAxis[1]),       RotAxis[1]*RotAxis[2]],
                    [RotAxis[2]*RotAxis[0], RotAxis[2]*RotAxis[1], SQR(RotAxis[2])]])
                TmpM *= (1-CosPhi)
                self += TmpM

                TmpM = Matrix(
                    [[0, -RotAxis[2], RotAxis[1]],
                     [RotAxis[2], 0, -RotAxis[0]],
                     [-RotAxis[1], RotAxis[0], 0]])
                TmpM *= SinPhi
                self += TmpM
                
            elif type(RotAxis) in (int,long):
                if RotAxis==RotAx.R1:
                    Matrix.__init__(self,
                        [[1,   0,     0],
                         [0,   CosPhi,SinPhi],
                         [0,  -SinPhi,CosPhi]])
                elif RotAxis==RotAx.R2:
                    Matrix.__init__(self,
                        [[CosPhi,0.0, -SinPhi],
                         [0.0,   1.0,  0.0],
                         [SinPhi,0.0,  CosPhi]])
                elif RotAxis==RotAx.R3:
                    Matrix.__init__(self, 
                        [[ CosPhi, SinPhi, 0.0],
                         [-SinPhi, CosPhi, 0.0],
                         [ 0.0,      0.0,  1.0]])
                else:
                    assert 0, "RotAxis must be one of R1,R2,R3"
    def Rotate(self, RotAngle, RotAxis):
        """ modify self to have extra rotation 
        """
        Matrix.__init__(self, RotMatrix(RotAngle, RotAxis) * self)
        return None
    

class Angle:
    """ all kind of angle representations united
    """
    #   AngleCodes = u"*'\""
    AngleCodes = u"°'\""  # ALT 0176
    #    AngleCodes = u"º'\""  # ALT 0186
    TimeCodes = "hms:"
    Deg2Rad = math.pi/180.0
    arcSec2Rad = Deg2Rad/3600.0
    Hour2Rad = Deg2Rad*15.0
    rev2rad = 2*math.pi

    def getrad(self):          return self._rad
    def setrad(self, radian):  self._rad = radian
    rad = property (getrad, setrad)

    def getdeg(self):          return self.rad / self.Deg2Rad
    def setdeg(self, degr):    self.rad = degr * self.Deg2Rad
    deg = property (getdeg, setdeg)

    def getarcs(self):         return self.rad / self.arcSec2Rad
    def setarcs(self, arcs):   self.rad = arcs * self.arcSec2Rad
    arcs= property (getarcs, setarcs)

    def getrev(self):         return self.rad / self.rev2rad
    def setrev(self, rev):    self.rad = rev * self.rev2rad
    rev= property (getrev, setrev)

    def __float__(self):
        return self.rad

#    def get__float__(self): return self.rad 
#    def set__float__(self, rad): self.rad = rad
#    __float__ = property (get__float__, set__float__)

    def __init__(self, ang):
        """  accept radian float or deg°min'sec" string or hh:mm:ss string
        """
        if type(ang)==float:   # assume radian
            self.rad = ang 
        elif type(ang)==str or isinstance(ang, unicode):   # parse string trying different formats
            ang.lstrip()
            neg = ang[0]=='-'
            if neg:
                ang=ang[1:]
            l = ang.split(self.AngleCodes[0])
            degree=0.0
            if len(l)>1:
               degree=float(l[0])           # degrees
               ang = l[1]
            l = ang.split(self.AngleCodes[1])
            if len(l)>1:
               degree += float(l[0])/60     # minutes
               ang = l[1]
            l = ang.split(self.AngleCodes[2])
            if len(l)>1:
               degree += float(l[0])/3600   # seconds
               ang=""
            elif len(ang)>0 and degree==0.0:# no angle codes found
                l = ang.split(self.TimeCodes[0])
                degree=0.0
                if len(l)>1:
                    degree=float(l[0])*15           # hours
                    ang = l[1]
                l = ang.split(self.TimeCodes[1])
                if len(l)>1:
                    degree += float(l[0])/60*15     # minutes
                    ang = l[1]
                l = ang.split(self.TimeCodes[2])
                if len(l)>1:
                    degree += float(l[0])/3600*15   # seconds
                    ang=""
                elif len(ang)>0 and degree==0.0:# no time codes found
                    degree=float(ang)            # assume degrees
            if neg:
                degree = -degree
            self.rad = degree * self.Deg2Rad
        elif isinstance(ang, Angle):  # allready in radian
            self.rad = ang.rad  
        elif isinstance(ang, Rational):
            self.rad = ang.toFloat()
        else:   # assume numeric
            self.rad = float(ang)

    def __neg__(self):
        return Angle(-self.rad)
    def __add__(x, y):
        return Angle(x.rad + y.rad)
    def __mul__(x, y):
        return Angle(x.rad * y.rad)
    def __sub__(x, y):
        """ operators - and -= (elementwise subtraction)
        """
        return Angle(x.rad - y.rad)

    def Modulo(self, MidFrac=0.5, Range=1.0):    # 0-2pi*MidFrac .. 2pi - 2pi*MidFrac
        """ Reduce angle to fraction of Range rotation
            MidFrac specifies middle of range to be returned, in units of rotation
            default : 0..360°
        """
        #full = self.rev2rad
        radRng = self.rev2rad*Range
        radOfs = radRng*(0.5-MidFrac)  #radRng*MidFrac
        #f = math.fmod(self.rad + radOfs, radRng)
        f = (self.rad + radOfs) % radRng
        return Angle(f- radOfs)
    def Hour(self):
        return self.rad / self.Hour2Rad
    def __repr__(self):
        """ Object representation as string
        """
        ang = self.deg
        neg = ang<0
        if neg:
            s = u"-"
            ang = -ang
        else:
            s=u""
        if ang<0.00001:
            s += u"0" + self.AngleCodes[0]
        else:    
            ang += 0.5 / 3600  # rounding last 
            if int(ang)>0:
                s += "%d" % int(ang) + self.AngleCodes[0]
                ang -= int(ang)
            ang *= 60
            if int(ang)>0:
                s += "%d" % int(ang) + self.AngleCodes[1]
                ang -= int(ang)
            ang *= 60
            if int(ang)>0:
                s += "%d" % int(ang) + self.AngleCodes[2]
                ang -= int(ang)
            if len(s)==0:
                s = u"0"+self.AngleCodes[2]
        return  s  #.encode('iso-8859-1')
    def AsHHMMSS(self):
        """ Object representation as string.
        """
        ang = self.Modulo().Hour()
        if ang<0:
            ang+=24
        s=""
        if ang<0.00001:
            s += "0" +self.TimeCodes[0]
        else:
            if int(ang)>0:
                s += "%d" % int(ang) + self.TimeCodes[0]
            ang -= int(ang)
            ang *= 60
            if int(ang)>0:
                s += "%d" % int(ang) + self.TimeCodes[1]
                ang -= int(ang)
            ang *= 60
            if int(ang)>0:
                s += "%d" % int(ang) + self.TimeCodes[2]
            ang -= int(ang)
            if ang>0.001:
                pass
        return  s  #.encode('latin1')

    def AsNESW(self, NorthAngle=None, rng = 22.5,  # 360/16
               segm = ('n','nne','ne','ene','e','ese','se','sse','s','ssw','sw','wsw','w','wnw','nw','nnw')):
        """ Object representation as string compass.
        """
        if NorthAngle is None:
            NorthAngle=Angle(0)
        elm = math.fmod(((self-NorthAngle).deg+rng) / rng, len(segm))
        return segm[int(elm+0.5)-1]

    def AsMoonPhase(self, NewAngle=None, rng=45.0,
               segm = ('new','wxc','fq','wxg','f','wng','lq','wnc')):
        """ Object representation as moon phase abrev.
            ('f','wng','lq','wnc','new','wxc','fq','wxg')
        """
        return self.AsNESW(NewAngle, rng, segm)

class DegAngle(Angle):
    """ as Angle but accept degrees,minutes,seconds as constructor args
    """
    def __init__(self, deg=0,min=0,sec=0):
        if type(deg) in (float,int,long):   # now assume degrees
            Angle.__init__(self, (deg +(min+sec/60.0)/60.0) * self.Deg2Rad)
        elif isinstance(deg, Rational):
            Angle.__init__(self, (deg.toFloat()+(min+sec/60.0)/60.0) * self.Deg2Rad)
        else:
            Angle.__init__(self, deg) # probably string
    def __float__(self):
        return self.deg
class ArcsAngle(Angle):
    def __init__(self, ang):
        if type(ang) in (float,int,long):   # now assume arcs
            Angle.__init__(self, ang * self.arcSec2Rad)
        elif isinstance(ang, Rational):
            Angle.__init__(self, ang.toFloat() * self.arcSec2Rad)
        else:
            Angle.__init__(self, ang) # assume AngleCodes in string 
    def __float__(self):
        return self.arcs

class VectorAngle(Angle):
    """ angle defined as angle between two vectors
    """
    def __init__(self,vector1,vector2):
        Angle.__init__(self,math.acos((vector1 * vector2)/(vector1.norm()*vector2.norm())))
    
class Coordinate(Vector):
    """ 3d cartesian coordinate
    """
    def __init__(self, vec=[0.0, 0.0, 0.0]):
        assert len(vec)==3, "Coordinates must have 3 elements presently"
        self.PolCrd = None
        Vector.__init__(self, vec)
        
    def Distance(self):
        if self.PolCrd==None:
           return math.sqrt(SQR(self[0]) + SQR(self[1]) + SQR(self[2]))
        else:
           return self.PolCrd[2]

    def Longitude(self):
        if self.PolCrd==None:
            self.PolCrd = self.Polar()
        return self.PolCrd[0]

    def Latitude(self):  # origin at equator
        """ angle measured in degrees north and south of the celestial equator
        """
        if self.PolCrd==None:
            self.PolCrd = self.Polar()
        return Angle(math.pi/2) - self.PolCrd[1]

    def Polar(self):
        """ either (azimuth, elevation, distance) or
           (longitude, latitude, height ) or
           (right ascention, declination, distance)
        """
        go = 4.0 * (abs(self[0]) + abs(self[1])+ abs(self[2]) )
        EpsDbl = 2.220446E-16
        dist = self.Distance()
        lon=0.0
        if abs(self[0])<=EpsDbl * go:
            if abs(self[1])<=EpsDbl * go:
                lon=0.0
            else:
                lon=math.pi /2.0
            if self[1]<-EpsDbl * go:
                lon=-lon
        else:
            lon=math.atan2(self[1], self[0])
        if go<= EpsDbl:
            lat = math.pi/2.0
        else:
            lat = math.acos(self[2]/dist)  # north=0
        return (Angle(lon), Angle(lat), dist)
    def Rotate(self, RotMtrx):
        """ Rotate self by rotation matrix
        """
        self.__init__(RotMtrx * self)
#       self =  Coordinate(RotMtrx * self)
        return None
    def Rotated(self, RotMtrx):
        return Coordinate(RotMtrx * self)

    def OutProduct(self, vec):  
        """ cross (outer) vector product
        """
        return Coordinate(
            [self[1]*vec[2]-self[2]*vec[1],
            self[2]*vec[0]-self[0]*vec[2],
            self[0]*vec[1]-self[1]*vec[0]])


class PolarCoord(Coordinate):
    """ allows to define cartesian Coordinate as Polar
    """
    def __init__(self, lon,lat,dist):
        Cs=dist*math.cos(lat.rad)
        Coordinate.__init__(self,[
                Cs*math.cos(lon.rad),
                Cs*math.sin(lon.rad),
                dist*math.sin(lat.rad)
                ])

def _test():
    print 'Rotation test '
    lat = Angle(u'5h59m30s')
    lat = Angle(u'6h01m30s')
    lon = Angle(u"-51°59'59.49\"")
    #lon = Angle(u"51*30'30\"")
    print 'lon=%s' % lon  #.__repr__().encode('iso-8859-1')
    s ='lat=%s =|%s| = %s' % (lat, lat.Modulo(), lat.AsHHMMSS())
    print s

    ang = DegAngle(180,12,10)
    for i in range(16):
        print 'ang=%.6f (%s) |ang|=%.6f lon=%s phase=%s' %\
           (ang.deg, ang.AsNESW(DegAngle(0)),ang.Modulo(0.5).deg, ang.AsHHMMSS(), ang.AsMoonPhase())
        ang += DegAngle(22,12,9.9)

    vec =PolarCoord(DegAngle(45.0),DegAngle(0.0), math.sqrt(2.0))
    print vec

    vec = Coordinate([1.0, 0.0, 1.0])
    pol = vec.Polar()
    try:
        print u"\n%s \n polar=%s" % (vec, pol)
    except:
        pass
    print

    ang = DegAngle(175)
    RotM = RotMatrix(ang, RotAx.R2)
    rot = vec.Rotated(RotM)
    print "dot (inner) product %s norm(vec)=%s norm(rot)=%s" % (vec*rot, vec.norm(), rot.norm())
    print "VectorAngle %s" % VectorAngle(vec,rot)
    print "cross(outer) product %s" % (vec.OutProduct(rot))
    print RotM._pp('RotM =')
    print
    try:
        print u"\n%s \n polar=%s" % (rot, rot.Polar())
    except:
        pass
    print
    RotM.Rotate(Angle('-60'), RotAx.R3)
   # ang = Angle('-30Â°')
   # RotM = RotMatrix(ang, 1)
    print RotM._pp('RotM -30=')
    rot.Rotate(RotM)
    print
    print 'rotated back=',rot
    try:
        print u"%s \n polar=%s" % (vec, rot.Polar())
    except:
        pass
    
if __name__ == '__main__':
    _test()
