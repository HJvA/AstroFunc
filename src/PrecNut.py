# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

import math
import time
#import sys

from Matrix import Matrix,Vector,Rational
from Rotation import Angle,DegAngle,Coordinate,RotMatrix,RotAx,SQR
from AstroTime import AstroTime
#import CelestData
        
class PrecessionNutation(AstroTime):
    def GCRStoCIRS_org(self):  # C2t
        """compute precession and nutation matrix according to
           http://syrte.obspm.fr/iauJD16/wallace.pdf
           low accuracy i.e. 0.9 arcs in years 2000..2100
           Tau is julian days since JulianDayJ2000
        """
        ang = 2.182 - 9.242e-4 * self.Tau
        X = 2.6603e-7 - 32.2e-6*math.sin(ang)
        Y = -8.14e-14 * self.Tau*self.Tau + 44.6e-6*math.cos(ang)
        return RotMatrix(Matrix(
                 [[1, 0, -X],
                  [0, 1, -Y],
                  [X, Y, 1 ]]))

    def GCRStoCIRS(self):  # C2t
        """compute precession and nutation matrix according to
           http://syrte.obspm.fr/journees2007/pdf/Wallace.pdf
           low accuracy i.e. 0.38 arcs in years 1995..2050
           T is julian centuries since JulianDayJ2000
        """
        T = self.cyTJ2000()
        ang1 = 2.182 - 33.757*T
        ang2 =-2.776 + 1256.664*T 
        X = 0.0097166*T - 0.00003318*math.sin(ang1) - 0.00000254*math.sin(ang2)
        Y = -0.00010863*T*T + 0.00004463*math.cos(ang1) + 0.00000278*math.cos(ang2)
        return RotMatrix(Matrix(
                 [[1, 0, -X],
                  [0, 1, -Y],
                  [X, Y, 1 ]]))


class CardinalPoints(PrecessionNutation):
    def __init__(self, localtime, UTCofs=None):
        AstroTime.__init__(self, localtime, UTCofs)
        #self.SetTime(self)
        self.C2t = self.GCRStoCIRS()

    def SetTime(self, AstTime,  Precision=None):
        AstroTime.SetTime(self, AstTime, Precision)
        self.C2t = self.GCRStoCIRS()

    def CIP(self):
        """ GCRS Celestial Intermediate pole
            formula 6.1 USNO circular 179
        """
        return Vector(self.C2t[2])
        #   return ~C2I * ~matrix.Vector([0, 0, 1])

    def Equinox(self):
        """ GCRS true Equinox of date
        """
        return Vector(self.C2t[0])
        #   return ~C2I * ~matrix.Vector([1, 0, 0])
        
    def T2T(self):   # polar motion (Wobble)
        """
           TIRS to ITRS
        """
        sa = Angle(-47.0 /1e6/3600 * self.TT() );
        xp = Angle(self.CIP()[0]/3600)  # ITRS coordinates of the CIP
        yp = Angle(self.CIP()[1]/3600)
        RotM = RotMatrix(-sa, 2);
        RotM.Rotate(xp, 1);
        RotM.Rotate(yp, 0);
        return RotM;

    def CIRS(self, CelestialObj):  # Celestial Intermediate Ref System
        assert isinstance(CelestialObj, Coordinate)
        return CelestialObj.Rotated(self.C2t)   # formala 6.22 USNO circular 179



def _test():
    #t = time.localtime()
    t = (2007, 4, 5, 14, 0, 0)   # sofa example
#    t = (2003, 8,26,  0,37,38.973810)   # wallace iau2000 ExpW04.pdf
        
    frame = CardinalPoints(t, UTCofs=2)

    R = frame.GCRStoCIRS()
    print (R._pp('NPB matrix'))

    print (u'\n')
    cip = frame.CIP()
    print ('cip=',cip)
    print ('equinox=',frame.Equinox())
    print (u'\n')

    print ("Polar Motion")
    t2t = frame.T2T()
    print (t2t._pp(u'T2T='))

if __name__ == '__main__':
    _test()
