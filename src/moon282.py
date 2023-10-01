# -*- coding: iso-8859-1 -*-
# from document Astron.Astrophys 282
# Numerical expressions for precession formulae and mean elements for the moon and the planets
# M.Chapront-Touzé, J.Chapront, J.L.Simon, P.Bretagnon, G.Francou, J.Laskar

# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import math
from AstroTypes import CelestialObj,pn
from Rotation import Angle,DegAngle,ArcsAngle 
from AstroTime import AstroTime

if pn.dbElm:
    from dbOscElm import dbOscElmObj
    #dbOscElmObj = dbOscElm()
else:
    from plan282data import MoonElm


#(a,e,I,L,w,W) = range(6)
(D,F,l,l_) = range(4)
arcs=3600.0


_Delaunay = ((297.8502042*arcs,1602961601.4603,-5.8679,0.006609,-0.00003169), #Delaunay D
             (93.27209932*arcs,1739527263.0983,-12.2505,-0.001021,0.00000417),#Delaunay F
             (134.96341138*arcs,1717915923.4728,32.3893,0.051651,-0.0002447), #Delaunay l
             (357.52910918*arcs,129596581.0481,-0.5532,0.000136,-0.00001149)) #Delaunay l_


_Pterms = {
         #Sin,  Cos,      D, F, l, l_
 pn.a : ((0,    3400.4,   2, 0, 0, 0),
         (0,   -635.6,    2, 0,-1, 0),
         (0,   -235.6,    0, 0, 1, 0),
         (0,    218.1,    2, 0, 0,-1),
         (0,    181.0,    2, 0, 1, 0)),
 pn.e : ((0,    0.014216, 2, 0,-1, 0),
         (0,    0.008551, 2, 0,-2, 0),
         (0,   -0.001383, 0, 0, 1, 0),
         (0,    0.001356, 2, 0, 1, 0),
         (0,   -0.001147, 4, 0,-3, 0),
         (0,   -0.000914, 4, 0,-2, 0),
         (0,    0.000869, 2, 0,-1,-1),
         (0,   -0.000627, 2, 0, 0, 0),
         (0,   -0.000394, 4, 0,-4, 0),
         (0,    0.000282, 2, 0,-2,-1),
         (0,   -0.000279, 1, 0,-1, 0),
         (0,   -0.000236, 0, 0, 2, 0),
         (0,    0.000231, 4, 0, 0, 0),
         (0,    0.000229, 6, 0,-4, 0),
         (0,    0.000201, 0,-2, 2, 0)),
 pn.I : ((0,  486.26,     2,-2, 0, 0),
         (0,  -40.13,     2, 0, 0, 0),
         (0,   37.51,     0, 2, 0, 0),
         (0,   25.73,     0,-2, 2, 0),
         (0,   19.97,     2,-2, 0,-1)),
 pn.L : ((-3332.9, 0,     2, 0, 0, 0),
         ( 1197.4, 0,     2, 0,-1, 0),
         ( -662.5, 0,     0, 0, 0, 1),
         (  396.3, 0,     0, 0, 1, 0),
         ( -218.0, 0,     2, 0, 0,-1)),
 pn.w : (( -55609, 0,     2, 0,-1, 0),
         ( -34711, 0,     2, 0,-2, 0),
         (  -9792, 0,     0, 0, 1, 0),
         (   9385, 0,     4, 0,-3, 0),
         (   7505, 0,     4, 0,-2, 0),
         (   5318, 0,     2, 0, 1, 0),
         (   3484, 0,     4, 0,-4, 0),
         (  -3417, 0,     2, 0,-1,-1),
         (  -2530, 0,     6, 0,-4, 0),
         (  -2376, 0,     2, 0, 0, 0),
         (  -2075, 0,     2, 0,-3, 0),
         (  -1883, 0,     0, 0, 2, 0),
         (  -1736, 0,     6, 0,-5, 0),
         (   1626, 0,     0, 0, 0, 1),
         (  -1370, 0,     6, 0,-3, 0)),
 pn.W : ((  -5392, 0,     2,-2, 0, 0),
         (   -540, 0,     0, 0, 0, 1),
         (   -441, 0,     2, 0, 0, 0),
         (    423, 0,     0, 2, 0, 0),
         (   -288, 0,     0,-2, 2, 0))
    }

class MoonBase(CelestialObj):
    def __init__(self, AstrTime, Precision=1):
        self.SetTime(AstrTime,Precision)
        self.name='Moon282'
        if pn.dbElm:
            self._MoonElm = dbOscElmObj.read_oscelm(pn.Moon,pnOrg=pn.aa282_moonmean)
        else:
            self._MoonElm = MoonElm


    def SetTime(self, AstrTime,  Precision=1):
        """ modify time & compute delaunay arguments
        """
        if isinstance(AstrTime, AstroTime):
            cy = AstrTime.cyTJ2000()
        self.t = [1,cy]
        for i in range(3):
            self.t.append(cy * self.t[-1])

    def EvalPolyn(self,coeffs):
        """ evaluate polynome using coeffs c0,c1,c2...
            into co*t[0]+c1*t[1]+c2*t[2]+....
        """
        val=0.0
        ln = len(coeffs)
        for i in range(ln):
            val += coeffs[i] * self.t[i]
        return val


    def SemiMajorAxis(self):
        return self.EvalPolyn(self._MoonElm[pn.a])
    def Eccentricity(self):
        return self.EvalPolyn(self._MoonElm[pn.e])
    def Inclination(self):
        return ArcsAngle(self.EvalPolyn(self._MoonElm[pn.I]))
    def MeanLongitude(self):
        return ArcsAngle(self.EvalPolyn(self._MoonElm[pn.L]))
    def LongitudePerihelion(self):
        return ArcsAngle(self.EvalPolyn(self._MoonElm[pn.w]))
    def LongitudeAscendingNode(self):
        return ArcsAngle(self.EvalPolyn(self._MoonElm[pn.W]))
 
class MoonMean(MoonBase):
    def __init__(self, AstrTime, Precision=1):
        MoonBase.__init__(self, AstrTime, Precision)
        self.D = ArcsAngle(self.EvalPolyn(_Delaunay[D])).rad
        self.F = ArcsAngle(self.EvalPolyn(_Delaunay[F])).rad
        self.l = ArcsAngle(self.EvalPolyn(_Delaunay[l])).rad
        self.l_= ArcsAngle(self.EvalPolyn(_Delaunay[l_])).rad
    def EvalPterms(self,Pterms):
        val=0.0
        ln = len(Pterms)
        for i in range(ln):
            (S,C,D,F,l,l_) = Pterms[i]
            ang = D*self.D + F*self.F + l*self.l + l_*self.l_
            if S:
                val += S*math.sin(ang) 
            if C:
                val += C*math.cos(ang) 
        return val
        
        
    def SemiMajorAxis(self):
        mn = self.EvalPolyn(self._MoonElm[pn.a]) + self.EvalPterms(_Pterms[pn.a])
        return mn
    def Eccentricity(self):
        return self.EvalPolyn(self._MoonElm[pn.e])+ self.EvalPterms(_Pterms[pn.e])
    def Inclination(self):
        return ArcsAngle(self.EvalPolyn(self._MoonElm[pn.I])+ self.EvalPterms(_Pterms[pn.I]))
    def MeanLongitude(self):
        mn = self.EvalPolyn(self._MoonElm[pn.L])+ self.EvalPterms(_Pterms[pn.L])
        return ArcsAngle(mn)
    def LongitudePerihelion(self):
        return ArcsAngle(self.EvalPolyn(self._MoonElm[pn.w])+ self.EvalPterms(_Pterms[pn.w]))
    def LongitudeAscendingNode(self):
        return ArcsAngle(self.EvalPolyn(self._MoonElm[pn.W])+ self.EvalPterms(_Pterms[pn.W]))
    
_psi = (310.17137918*arcs,-6967051.436,6.2068,0.007618,-0.00003219)

class MoonJ2000(MoonMean):
    def __init__(self, AstrTime, Precision=1):
        MoonMean.__init__(self, AstrTime, Precision)
        self.psi = ArcsAngle(self.EvalPolyn(_psi)).rad
        self.D2F2 = 2*self.D-2*self.F
    def Inclination(self):
        return ArcsAngle(MoonMean.Inclination(self).arcs + self.EvalPolyn(
            ((46.997*math.cos(self.psi))  -0.614*math.cos(self.D2F2+self.psi)+0.614*math.cos(self.D2F2-self.psi),
             (-0.0297*math.cos(2*self.psi)-0.0335*math.cos(self.psi)         +0.0012*math.cos(self.D2F2+2*self.psi)),
             (-0.00016*math.cos(self.psi) +0.00004*math.cos(3*self.psi)      +0.00004*math.cos(2*self.psi)))))
    def _dLambda(self):
        return ArcsAngle(self.EvalPolyn(
            ((2.116*math.sin(self.psi)-0.111*math.sin(self.D2F2-self.psi)),
             (-0.0015*math.sin(self.psi)))))
    def MeanLongitude(self):
        return MoonMean.MeanLongitude(self) + self._dLambda()
    def LongitudePerihelion(self):
        return MoonMean.LongitudePerihelion(self) + self._dLambda()
    def LongitudeAscendingNode(self):
        return MoonMean.LongitudeAscendingNode(self) + ArcsAngle(self.EvalPolyn(
          ((-520.77*math.sin(self.psi)+13.66*math.sin(self.D2F2+self.psi)+1.12*math.sin(2*self.D-self.psi)    -1.06*math.sin(2*self.F-self.psi)),
           (0.66*math.sin(2*self.psi) +0.371*math.sin(self.psi)          -0.035*math.sin(self.D2F2+2*self.psi)-0.015*math.sin(self.D2F2+self.psi)),
           (0.0014*math.sin(self.psi) -0.0011*math.sin(3*self.psi)       -0.0009*math.sin(2*self.psi)))))

if __name__ == '__main__':
    import time

    t = (2007, 4, 5, 14, 0, 0)
    t = time.localtime()
    body = MoonBase(AstroTime(t))
    bodyCorr = MoonJ2000(AstroTime(t))
    print '%s\t' % body.name
    print 'a=%.10f\t(%.10f)' % (body.SemiMajorAxis(),bodyCorr.SemiMajorAxis())
    print 'I=%s\t(%s)' % (body.Inclination(),bodyCorr.Inclination())
    print 'e=%.10f\t(%.10f)' % (body.Eccentricity(),bodyCorr.Eccentricity())
    print 'L=%s\t(%s)' % (body.MeanLongitude(),bodyCorr.MeanLongitude())
    print 'wp=%s\t(%s)' % (body.LongitudePerihelion(),bodyCorr.LongitudePerihelion())
    print 'Wa=%s\t(%s)' % (body.LongitudeAscendingNode(),bodyCorr.LongitudeAscendingNode())

