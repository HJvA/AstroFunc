# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import sys
import math
from AstroTypes import pn
from Rotation import Angle,DegAngle,ArcsAngle 
import AstroTime

if pn.dbElm:
    from dbOscElm import dbOscElmObj
    #dbOscElmObj = dbOscElm()
else:
    from plan282data import PlanetElm,trigonometric_terms,trigonometric_terms_extra


class BaseOscElements:
    def __init__(self, pnPlanet, AstTime, Precision=1):
        if pn.dbElm:
            self.KepDef = dbOscElmObj.read_oscelm(pnPlanet,pnOrg=pn.aa282_planmean)
        else:
            self.KepDef = PlanetElm[pnPlanet]
        #self.pln = pnPlanet
        cm = AstTime.cyTJ2000()
        if pnPlanet!=pn.Moon:
            cm/=10.0
        self.t = [1,cm]
        for i in range(1):
            self.t.append(cm * self.t[-1])
        self.name =pn.nmPlanet(pnPlanet)
    def EvalPolyn(self,coeffs):
        """ evaluate polynome using coeffs c0,c1,c2...
            into co*t[0]+c1*t[1]+c2*t[2]+....
        """
        val=0.0
        ln = len(coeffs)
        if ln>2: ln=2
        for i in range(ln):
            val += coeffs[i] * self.t[i]
        return val

    def SemiMajorAxis(self):
        return self.EvalPolyn(self.KepDef[pn.a])
    def Eccentricity(self):
        return self.EvalPolyn(self.KepDef[pn.e])
    def Inclination(self):
        return ArcsAngle(self.EvalPolyn(self.KepDef[pn.I]))
    def MeanLongitude(self):
        return ArcsAngle(self.EvalPolyn(self.KepDef[pn.L]))
    def LongitudePerihelion(self):
        return ArcsAngle(self.EvalPolyn(self.KepDef[pn.w]))
    def LongitudeAscendingNode(self):
        return ArcsAngle(self.EvalPolyn(self.KepDef[pn.W]))
    def MeanMotion(self):
        """ dLambda per cy
        """
        return ArcsAngle(self.KepDef[pn.L][1])

class OscElements(BaseOscElements):
    (kp,ca,sa,kq,cl,sl) = range(6)
    def __init__(self, pnPlanet, AstTime, Precision=1):
        BaseOscElements.__init__(self,pnPlanet,AstTime,Precision)
        if pn.dbElm:
            self.TrigTerms = dbOscElmObj.read_oscelm(pnPlanet,pnOrg=pn.aa282_trigterms)
            self.TrigExtra = dbOscElmObj.read_oscelm(pnPlanet,pnOrg=pn.aa282_etrigterms)
        else:
            self.TrigTerms = trigonometric_terms[pnPlanet]
            self.TrigExtra = trigonometric_terms_extra[pnPlanet]
    def _EvalCorr(self,elm,tpl):
        if not tpl:
            return 0.0
        if elm == pn.a:
            i=self.kp
        elif elm == pn.L:
            i=self.kq
        else:
            return 0.0
        if i>=len(tpl):  # mars has no kq
            return 0.0
        v = 0.0
        mu = 0.3595362*self.t[1]
        for k in range(len(tpl[i])):
            pmu = ArcsAngle(tpl[i][k]*mu).rad
            v += (tpl[i+1][k] * math.cos(pmu) + \
                  tpl[i+2][k] * math.sin(pmu))*1e-7
        return v
    def _EvalTerms(self,elm):
        return self._EvalCorr(elm,self.TrigTerms)
    def _EvalTermsExtra(self,elm):
        """ formula 19
        """
        if len(self.KepDef[elm])>2:
            v = self.KepDef[elm][2]*self.t[2]
        else:
            v=0.0
        v += self.t[1]*self._EvalCorr(elm,self.TrigExtra)
        return v + self._EvalCorr(elm,self.TrigTerms)

    def SemiMajorAxis(self):
        mn = self.EvalPolyn(self.KepDef[pn.a])
        return mn + self._EvalTermsExtra(pn.a)
    def Eccentricity(self):
        return self.EvalPolyn(self.KepDef[pn.e]) + self._EvalTerms(pn.e)
    def Inclination(self):
        return ArcsAngle(self.EvalPolyn(self.KepDef[pn.I]) + self._EvalTerms(pn.I))
    def MeanLongitude(self):
        mn = self.EvalPolyn(self.KepDef[pn.L])
        mn += self._EvalTermsExtra(pn.L)
        return ArcsAngle(mn)
    def LongitudePerihelion(self):
        return ArcsAngle(self.EvalPolyn(self.KepDef[pn.w]) + self._EvalTerms(pn.w))
    def LongitudeAscendingNode(self):
        return ArcsAngle(self.EvalPolyn(self.KepDef[pn.W]) + self._EvalTerms(pn.W))
            
if __name__ == '__main__':
    import time

    t = (2007, 4, 5, 14, 0, 0)
    t = time.localtime()
    pnBodies = (pn.Earth,pn.Moon,pn.Saturn,pn.Mars)
    for pnBody in pnBodies:
        body = BaseOscElements(pnBody, AstroTime.AstroTime(t))
        bodyCorr = OscElements(pnBody, AstroTime.AstroTime(t))
        print '%s\t' % (pn.nmPlanet(pnBody))
        print 'a=%.10f\t(%.10f)' % (body.SemiMajorAxis(),bodyCorr.SemiMajorAxis())
        print 'I=%s\t(%s)' % (body.Inclination(),bodyCorr.Inclination())
        print 'e=%.10f\t(%.10f)' % (body.Eccentricity(),bodyCorr.Eccentricity())
        print 'L=%s\t(%s)' % (body.MeanLongitude(),bodyCorr.MeanLongitude())
        print 'wp=%s\t(%s)' % (body.LongitudePerihelion(),bodyCorr.LongitudePerihelion())
        print 'Wa=%s\t(%s)' % (body.LongitudeAscendingNode(),bodyCorr.LongitudeAscendingNode())
