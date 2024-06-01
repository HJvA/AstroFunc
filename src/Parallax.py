# copyright (c) 2007-2009 H.J.v.Aalderen
# 


import Rotation
from Rotation import Angle
import math

LightyearToParsec = 3.2616

class Parallax:
    def __init__(self):
        pass

    Vabs = None     # mag
    Vappar = None   # mag
    distance = None # parsec
    parallax = Angle(0) # arcs

    def GetAbsMag(self):
        if self.distance is None:
            return self.Vappar +5+ 5*(math.log10(self.parallax.arcs))
        else:            
            return self.Vappar +5- 5*(math.log10(self.distance))
    def GetDistance(self):
        if self.Vabs is None:
            return 1/self.parallax.arcs           # d in parsec
        else:
            return math.pow(10.0,(self.Vappar+5-self.Vabs)/5)
        return 1/math.sin(self.parallax.rad)  # d in AU
    def GetVappar(self):
        return self.Vabs - 5 - 5*math.log10(self.parallax.arcs)
        return self.Vabs - 5 + 5*math.log10(self.distance)

def _test():
    print (r'-5/4=%f' % (-5 % 4))

    par = Parallax()
    par.Vappar = 0.18
    par.distance = 773.0/LightyearToParsec
    par.Vabs = par.GetAbsMag()
    print (par.GetAbsMag())
    print ("%f %f" % (par.distance,par.GetDistance()))
    

    
if __name__ == '__main__':
    _test()
