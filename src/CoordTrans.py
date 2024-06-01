# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

import math
import PrecNut
from Rotation import Angle,DegAngle,Coordinate,RotMatrix,RotAx,SQR
import AstroTypes
from AstroTime import AstroTime

Solar2Sidereal = 1.00273781191135448   # USNO formula 2.10
RefractionAtHorizon = DegAngle(-0.5667)  # Meeus page 101

class GeoObserver(PrecNut.CardinalPoints):
    """ models earth surface positions
    """

    def __init__(self, localtime, UTCofs=None):
        PrecNut.CardinalPoints.__init__(self, localtime, UTCofs)
        self.G2Topo = None
        #defaults
        self.GeoLoc = AstroTypes.GeoLocation(5.4, 51.4, 20) 
        self.Precision = 1

        
    def ITRS(self):  
        """ International Terrestrial Reference System
        """
        if self.Precision>3:  # formala 6.10 USNO circular 179
            a = 6378137;  # appproximation of WGS84 (GPS) ellipsoid 
            f = 1 / 298.257223563
            Cs = math.cos(self.GeoLoc.Latitude.rad)
            Sn = math.sin(self.GeoLoc.Latitude.rad)
            C = 1 / math.sqrt(SQR(Cs) + SQR((1 - f) * Sn))
            return Coordinate([
                (a*C+self.GeoLoc.Height)*Cs*math.cos(self.GeoLoc.Longitude.rad),
                (a*C+self.GeoLoc.Height)*Cs*math.sin(self.GeoLoc.Longitude.rad),
                (a*C* SQR(1-f) + self.GeoLoc.Height)*Sn])
        else:  # formala 5.10 USNO circular 179
            Cs=math.cos(self.GeoLoc.Latitude.rad)
            return Coordinate([
                Cs*math.cos(self.GeoLoc.Longitude.rad),
                Cs*math.sin(self.GeoLoc.Longitude.rad),
                math.sin(self.GeoLoc.Latitude.rad) ])
            

    def GCRStoITRS(self):   #  Nomenclature for Fundamental Astronomy
        """ GeoCentric to ITRS  (verified with http://www.iau-sofa.rl.ac.uk/ sofa_pn.pdf)
        """
        RotM = RotMatrix(self.C2t)  # nutation precession framebias  (COPY!!)
        RotM.Rotate(self.ERA(), RotAx.R3)  # CIRS to TIRS  ( to terrestrial system )
        if self.Precision>4:
            RotM = RotMatrix(RotM * self.T2T())   # TIRS to ITRS  ( polar motion )
        return RotM

    def ITRStoTopo(self):
        """ ITRS to TopoCentric rotation
        """
        vITRS = self.ITRS()
        RotM = RotMatrix(vITRS.Longitude(), RotAx.R3)  # ITRS ( to local meridean )
#        RotM.Rotate(vITRS.Latitude() - Angle(math.pi/2), 1)     # ( to horizon )
        RotM.Rotate(Angle(math.pi/2) -vITRS.Latitude(), RotAx.R2)     # ( to horizon )
#       RotM.Rotate(vITRS.Longitude(), 2)  # ITRS ( to local meridean )
        return RotM

    def Viewing(self, CelestialObj):  # Z = zenit,   Y = north,  X = east  ???
        """+Z is normal to ICRF Mean Earth Equator of Epoch J2000.0
           +X is parallel to ICRF Mean Earth Dynamical Equinox of Epoch J2000.0
           +Y completes the right-handed system
        """
        assert  isinstance(CelestialObj, Coordinate)
        if self.Precision<2:  # no frameBias precession nutation wobble
            obj = CelestialObj.Rotated(RotMatrix(self.ERA(), RotAx.R3))
            obj.Rotate(RotMatrix(self.GeoLoc.Longitude, RotAx.R3))
            obj.Rotate(RotMatrix(Angle(math.pi/2) - self.GeoLoc.Latitude, RotAx.R2))
            return obj
        else:
            if self.G2Topo is not object:
                self.G2Topo = self.ITRStoTopo()
                self.G2Topo *= self.GCRStoITRS()
            return CelestialObj.Rotated(self.G2Topo)
#            obj = CelestialObj.Rotated(self.GCRStoITRS())
#            obj = CelestialObj.Rotated(RotMatrix(self.ERA(), 2))
#            obj.Rotate(self.ITRStoTopo())
#            return obj  
#            return Coordinate(self.G2T * CelestialObj)

    def Azimuth(self, CelestialObj, north=0.0):
        """ iapg_fesg_rpt_13.pdf dieter egger  north=zero
            formula 5.2 USNO circular 179
        """
        north += math.pi
        return Angle(
            north - self.Viewing(CelestialObj).Longitude().rad).Modulo()

    def Elevation(self, CelestialObj): #Altitude
        """ Angle above horizon
        """
        return Angle(
             self.Viewing(CelestialObj).Latitude().rad).Modulo(0.0)
    def HorizonDip(height):
        """Pythagorean theorem              R^2+x^2=(R+h)^2  
           algebraic expansion of (R+h)^2   R*2+x^2=R^2+2Rh+h^2  
           subtract R2 from both sides      x^2=h^2+2Rh 
           R = earth radius, h=height, x=dist to pnt on horizon
        """
        pass
              
    def LMST(self):
        """ angle between local meridean and vernal equinox
        """
        LMST = self.GMST() + self.GeoLoc.Longitude  # formula 2.15 USNO circular 179
        if self.Precision>4:
            pass    # formula 2.16 USNO circular 179
        return LMST
        
    def Transit(self, CelestialObj):   # LST=Ra  i.e. LHA=0
        """ localtime when body at true south
            assumes sidereal movement!
        """
        Ra = CelestialObj.Longitude()  # changes with time for moon,sun
        LHA = self.LMST()
        LHA -= Ra
        #LHA = Angle(2*math.pi - LHA.rad)
        LHA = LHA.Modulo(0.0)
        #if LHA.rad>math.pi:
        #    LHA = Angle(-2*math.pi*Solar2Sidereal+LHA.rad)
        #elif LHA.rad<-math.pi:
        #    LHA = Angle(2*math.pi + LHA.rad)
        loctm = Angle(self.LocalTime().rad - LHA.rad*Solar2Sidereal)
        return AstroTime (loctm, self.UTCOffset)

    def _RiseSet(self, CelestialObj, HorzAng, RiseSet=-1, Refine=False):
        """ local time when body rises or sets
        """
        Lat = self.GeoLoc.Latitude.rad
        Ra = CelestialObj.Longitude()  # changes with time for moon,sun 
        Decl = CelestialObj.Latitude().rad
        cosha = (math.sin(HorzAng.rad) - math.sin(Decl)*math.sin(Lat)) / \
             (math.cos(Decl)*math.cos(Lat))
        if cosha<1 and cosha>-1:
           GAST = Angle(RiseSet*math.acos(cosha) + Ra.rad) #greenwich aparent sidereal time
           LHA = self.LMST() - GAST   # GMST ?
           tm = Angle(self.LocalTime().rad - LHA.Modulo(0.0).rad*Solar2Sidereal) #ok with sun
           tm = AstroTime(tm, self.UTCOffset)
        else:
           return None
        if Refine:
            elev = [0, 0]
            tim  = [0, tm.rad]

            tim[0] = self.Transit(CelestialObj)
            elev[0] = Elevation(tim[0], self.GeoLoc, CelestialObj).rad
            tim[0] = tim[0].rad
            #print "tm0=%s elev0=%#g  LocLat=%s" % (Angle(tim[0]).AsHHMMSS(),elev[0],self.GeoLoc.Latitude)
            i=1
            cnt=0
            import copy
            body = copy.copy(CelestialObj)
            
            while True:
                #if hasattr(body, 'SetTime'):
                body.SetTime(tm, Precision=self.Precision)
                elev[i] = Elevation(tm, self.GeoLoc, body).rad+ HorzAng.rad
                #print "tm=%s elev=%#g " % (tm.AsHHMMSS(),elev[i])
                if abs(elev[i])<0.04/self.Precision or cnt>10:
                    break
                i = RootFind(tim,elev,cnt==0)
                tm.rad =tim[i]
                cnt+=1
        return tm


    def Rise_Time(self, CelestialObj, HorzAng=RefractionAtHorizon):   # www.stjarnhimlen.se/comp/riset.html
        return self._RiseSet(CelestialObj,HorzAng, Refine=self.Precision>1)
        
    def Set_Time(self, CelestialObj, HorzAng=RefractionAtHorizon):
        return self._RiseSet(CelestialObj,HorzAng, RiseSet=1, Refine=self.Precision>1)

def Elevation(AstrTime, GeoLocation, CelestialObj):
    """ Angle of elevation above horizon
    """
    assert isinstance(AstrTime, AstroTime)
    frm =GeoObserver(AstrTime.LocalTime(),AstrTime.UTCOffset)
    frm.GeoLoc = GeoLocation
    return frm.Elevation(CelestialObj)
    
def RootFind(x,f, start=False):
    """ find x where f approaches 0 using (iterative) secant method
    """
    global r,s,cnt
    if start:
        cnt=0
    if cnt==0:
        if abs(f[0])<abs(f[1]):
            r=0
            s=1
        else:
            s=0
            r=1
        if f[0]*f[1]>0:  # try bracketing
            cnt=0
            #dx = (x[s] - x[r]) *f[r]/(f[r]-f[s])
            dx = (x[s]-x[r])/50.0
            x[s] = x[r]
            f[s] = f[r]
            x[r] -= dx   
            return r
    dx = (x[s] - x[r]) *f[r]/(f[r]-f[s])
    x[s] = x[r]
    f[s] = f[r]
    x[r] +=dx
    cnt+=1
    return r
    
# todo: brent method
    if len(x)==2:
        hlfx = (x[0]+x[1])/2
        if f[0]*f[1]<0:
            x.append(hlfx)
        else:  # no zero in interval
            if abs(f[0])<abs(f[1]):
                x.append(hlfx - (x[1]-x[0]))
            else:
                x.append(hlfx - (x[0]-x[1]))
        f.append(0)
    pim=2
    return pim

    if len(x)==2:  # secant method
        xn = x[1] - (x[1] - x[0]) /(1-f[0]/f[1])
        x.append(xn)
        f.append(0)
        pim=2
        return pim
    elif len(x)==3:  # http://mathworld.wolfram.com/BrentsMethod.html
        R=f[1]/f[2]
        S=f[1]/f[0]
        T=f[0]/f[2]
        P=S*(T*(R-T)*(x[2]-x[1])-(1-R)*(x[1]-x[0]))
        Q=(T-1)*(R-1)*(S-1)
        xn = x[1]+P/Q
        im=0
        if abs(f[im])<abs(f[1]):
            im=1
        if abs(f[im])<abs(f[2]):
            im=2
        if im==pim:
            im +=1
            im = im % 3
        pim = im
        x[im]=xn
        return pim


if __name__ == '__main__':

    def _test():
        import CelestData
        import OscElm282,Kepler
        from AstroTime import AstroTime 
        import ELPmpp02
        import time
        t = time.localtime()
        #t = (2007, 4, 5, 14, 0, 0)          # sofa example
        #t = (2003, 8,26,  0,37,38.973810)   # wallace iau2000 ExpW04.pdf
        #t = (2008, 11, 2, 7, 34, 0)         # sun rise
        #t = (1961, 3, 11, 15,15,0)
        #t = (1957, 8, 13, 0,0,0)
        #t =  (2006, 1, 1, 0, 0, 0) 
            
        frame = GeoObserver(t,UTCofs=1)

        #frame.UTCOffset =1
        frame.Precision = 4
        print()
        print ('GeoLoc lon=%s lat=%s tm=%s UT1=%s' % \
           (frame.GeoLoc.Longitude,frame.GeoLoc.Latitude, \
            frame.LocalTime().AsHHMMSS(),frame.UT1().AsHHMMSS()))
        #    frame.GeodeticLatitude= Angle('52.385639')  # wallace example
        #    frame.GeodeticLongitude= Angle('9.712156')
        
        print ("Celestial to terrestrial")
        G2I = frame.GCRStoITRS()
        print (G2I._pp(u'GCRStoITRS='))

        print (RotMatrix(frame.ERA(), 2)._pp(u'Low Precision='))

        print ("GeoCentric to TopoCentric")
        I2T = frame.ITRStoTopo()
        print (I2T._pp(u'ITRStoTopo='))
    
        frame.Precision = 3
        for i in range(2):
            obj = ELPmpp02.Moon(frame, frame.Precision)
            print()
            print ('Moon@precision %d' % frame.Precision)
            print ("Ra=%s, decl=%s, dist=%s" % frame.Viewing(obj).Polar())
            print (obj.__class__.__name__,'Ra,Decl=%s, %s' % (obj.Longitude().AsHHMMSS(), obj.Latitude()))
            print (' azim=%s' % frame.Azimuth(obj),' (',frame.Azimuth(obj).AsNESW(),') elev=%s' % frame.Elevation(obj))
            print ('LHA=%s' % (frame.ERA() + obj.Longitude() - frame.GeoLoc.Longitude).Modulo())
            print ('RiseTime=%s Transit=%s SetTime=%s' % \
               (frame.Rise_Time(obj).AsFormat('%H:%M:%S %d'),
                frame.Transit(obj).AsFormat('%H:%M:%S %d'),
                frame.Set_Time(obj).AsFormat('%H:%M:%S %d')))
            frame.Precision -=1

        print()
        frame.Precision = 4
        for i in range(6):
            obj = Kepler.Sun(frame)
            #obj= KeplerPlan.Planet(KeplerData.pn.Saturn, frame)
            print ('%s   loctime=%s GMST=%s JD=%s' %\
              (obj.name, frame.LocalTime().AsHHMMSS(),frame.GMST(), frame.JulianDay()))
            #print "Ra=%s, decl=%s, dist=%s" % frame.Viewing(obj).Polar()
            print (obj.__class__.__name__,'Ra,Decl=%s, %s' % (obj.Longitude().AsHHMMSS(), obj.Latitude()))
            print (' azim=%s' % frame.Azimuth(obj),' (',frame.Azimuth(obj).AsNESW(),') elev=%s' % frame.Elevation(obj))
            print ('LHA=%s' % (frame.ERA() + obj.Longitude() - frame.GeoLoc.Longitude).Modulo())
            print ('RiseTime=%s Transit=%s SetTime=%s' % \
               (frame.Rise_Time(obj).AsFormat('%H:%M:%S %d'),
                frame.Transit(obj).AsFormat('%H:%M:%S %d'),
                frame.Set_Time(obj).AsFormat('%H:%M:%S %d')))
            frame.IncTime(3600)

    _test()
