# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import math
import time
import sys,operator
from Rotation import Angle,DegAngle,ArcsAngle,SQR


JulianDayJ2000 = 2451545.0  # 1 jan 2000 12h TT at geocenter (epoch J2000)
JulianDaysPerCentury = 36525.0
SecondsPerDay = 86400.0  #3600*24

def _JulianDay (Year,Month,Day, Hour=0,Minute=0,Second=0):
    """calculate number of days since beg of year -4712  (=JDN)
       Astron.Algorith chap.7
    """
    if Month==1 or Month==2:
        Month += 12
        Year -= 1
    JD = (Hour + (Minute + Second/60.0) /60) /24
    JD += math.floor(365.25 * (Year + 4716)) + \
          math.floor(30.6001 * (Month+1)) + \
          Day - 1524.5
    if Year>1582 or \
       (Year==1582 and
        (Month>10 or (Month==10 and Day>4))):
       A = math.floor(Year/100.0)
       JD += 2.0 - A + math.floor(A/4)
    return JD

def JulianDay (gmtime):
    return _JulianDay(gmtime[0],gmtime[1],gmtime[2],\
                      gmtime[3],gmtime[4],gmtime[5])

def TimeTup(JulianDay):
    """ return python time struct
        Meeus Astron.Algorith chap.7
        note : not effective with mktime below year 1970
    """
    F,Z = math.modf(JulianDay+0.5)
    wd = int(Z % 7)
    if Z<2299161:
        A=Z
    else:
        alp = math.floor((Z-1867216.25)/36524.25)
        A = Z+1+alp-math.floor(alp/4)
    B=A+1524
    yy=int((B-122.1)/365.25)
    D = math.floor(365.25*yy)
    mo = int((B-D)/30.6001)
    dd = B-D-math.floor(30.6001*mo)+F
    if mo<14:
        mo -=1
    else:
        mo -=13
    if mo>2:
        yy-=4716
    else:
        yy-=4715
    F=round(F*86400) # whole seconds
    F,ss = divmod(F,60)
    hh,mm = divmod(F,60)
    tup = (yy,mo,int(dd),int(hh),int(mm),int(ss),wd,0,0)
    return tup
        

def systemUTCoffset():
    """ system UTC offset in hour
    """
    hdif = time.localtime().tm_hour - time.gmtime().tm_hour
    if hdif<-12:
        hdif+=24
    return hdif


class AstroTime(Angle):
    """ Time in different representations
        self.rev is Nr of days (earth rotations) since J2000.0 
    """
    def getUTCofs(self):     return self._UTCofs
    def setUTCofs(self, Hr):
        self.rev += (self._UTCofs - Hr)/24.0
        self._UTCofs = Hr
    UTCOffset = property(fget=getUTCofs, fset=setUTCofs,
                         doc="DST + Timezone")
    
    def __init__(self, localtime, UTCofs=None):
        """ construct AstroTime class setting localtime i.e. including UTCOffset
        """
        if UTCofs is None:
            self._UTCofs = systemUTCoffset()
        else:
            self._UTCofs = UTCofs
        if isinstance(localtime, Angle):
            # localtime starts at midnight, UT1 starts at 12h
            Angle.__init__(self,localtime.rad + (0.5 - self.UTCOffset/24.0)*self.rev2rad)
            #self.rev = localtime.rev + 0.5 - self.UTCOffset/24.0
        else:  # assert isinstance(localtime,tuple)  time_struct
            assert not isinstance (localtime, AstroTime), "use SetTime for this"
            self.setpytime(localtime)
            Angle.__init__(self,self.rad)

    def SetTime(self, AstTime, Precision=None):
        """ modify actual time
        """
        self.rad = AstTime.rad
        self._UTCofs = AstTime.UTCOffset
        if not Precision is None:
            self.Precision = Precision
    def IncTime(self, Seconds):
        """ increment AstroTime by Seconds (may be negative)
        """
        self.rad += Seconds/SecondsPerDay*self.rev2rad

    def JulianDay(self):
        """ number of days (earth rotations) since beg of year -4712
        """
        return self.rev + JulianDayJ2000  #+ self.UTCOffset/24.0

    def pytime(self):
        return TimeTup(self.JulianDay()+ self.UTCOffset/24.0)

    def setpytime(self,localtime):
        self.rad = \
           (JulianDay(localtime) - JulianDayJ2000 - self.UTCOffset/24.0)*self.rev2rad

    def ERA(self): # formula 2.11 USNO circular 179
        """ EarthRotationAngle (has not a constant rate)
            geocentric angle between
            CIO (Celestial Intermediate Origin) and
            TIO (Terrestrial Intermediate Origin)
        """
        #Duf,Dui = math.modf(self.rev)   
        Du = self.rev  #Du is the number of UT1 days from 2000 January 1, 12h UT1
        ang = Angle(
            ( 0.7790572732640 + 
              0.00273781191135448*Du + Du
            ) *  self.rev2rad)
        return ang
        #f = a + (1+b)(i+f) = a + i+f + b(i+f)  ~ a + f + b*Du  (Du=i+f let it be continuous)
        
    def DeltaT(self):     
        """ = 32.184 + TAI -UT1
        """
        return 32.184 + self.deltaAT()
        #JulianDayJ1820 = 2385801.0
        #-20 + 32*SQR((self.dUT1 + JulianDayJ2000 - JulianDayJ1820)/JulianDaysPerCentury)
        # http://asa.usno.navy.mil/SecK/DeltaT.html
        # http://eclipse.gsfc.nasa.gov/SEhelp/deltatpoly2004.html
        # http://www.solarark.fi/deltat.htm

    def deltaAT(self):
        """ integral nr of leap seconds since 1 jan 1977
            http://maia.usno.navy.mil/ser7/tai-utc.dat
            http://maia.usno.navy.mil/ser7/historic_deltat.data
        """
        return 33  # to be implemented!

    def UTC(self):
        """ universal coordinated time
            [days angle] since 1 jan 2000 0h (J1999.5)
            UTC = TAI - dAT
            dAT = accumulated nr of leap seconds  
            |UTC-UT1| < 0.9s
        """
        return Angle(self.rad + math.pi)
        

    def UT1(self):
        """ universal time [earth rotations angle] since 1 jan 2000 12h (J2000.0)
        """
        return Angle(self.rad)  

    def LocalTime(self):
        """ Local Time as Angle since J2000 0h
        """
        return DegAngle(self.deg - 180+ self.UTCOffset*15)  

    def AsFormat(self, format='%y%m%d'):
        """ LocalTime string representation as specified by format argument
        """
        return time.strftime(format,TimeTup(self.JulianDay()+ self.UTCOffset/24.0))

    def __repr__(self):
        """ LocalTime string representation as 'yyyy MMM dd HH:MM:SS'
        """
        return self.AsFormat('%Y %b %d %H:%M:%S')

    def TT(self):  # ~Teph ~TDB (Barycentric Dynamical Time)
        """ Terrestrial time (=TAI + 32.184) [SI days since J2000.0]
            'is what TDB is meant to be'
        """
        return self.rev + self.DeltaT()/SecondsPerDay  #  TAI + 32.184
        
    def cyTJ2000(self):
        """ Julian SI centuries since J2000.0
        """
        return self.TT() / JulianDaysPerCentury
        
    def TAI(self):
        """ International Atomic Time [s] based on SI time at sea level
        """
        return self.TT()*SecondsPerDay - 32.184 
        
    def GMST(self):    # formula 2.12 USNO circular 179
        """ greenwich mean sidereal time (mean: affected by precession not nutation)
            hour angle of inertial dynamical mean equinox of J2000.0 at prime meridean
        """
        T = self.cyTJ2000()
        arcs =  (0.014506 +      # accumulated precession of equinox in Ra
                (4612.156534+
                (1.3915817+
                (-0.00000044+
                (-0.000029956+
                (-0.0000000368 )*T)*T)*T)*T)*T); 
        return self.ERA() + ArcsAngle(arcs)


def _test():
    print
    #t =  [2008, 11, 19, 9, 0, 0] 
    t = [2000, 1, 1, 10, 0, 0]   # J2000.0
    t = [2007, 4, 5, 12, 0, 0]   #http://www.iau-sofa.rl.ac.uk/2008_0301/sofa/sofa_pn.pdf

    for i in range(5):  # n hours around J2000.0
       astT = AstroTime(tuple(t),0)
       print "J%.4f JD=%.4f GMST=%s ERA=%s TT=%.4f hms=%s" % \
          (2000+(astT.rev)/365.25, astT.JulianDay(), \
           astT.GMST().Modulo().deg,astT.ERA().deg, astT.TT(), \
           astT.AsFormat("%a %H:%M:%S"))
          #(2000.0+(i-1.0)/24.0, astT.ERA(), astT.JulianDay(), astT.GMST(),astT.TT(), astT.AsFormat("%a %H:%M:%S"))
       t[3]+=1  

    t = time.localtime()
    t = (1970, 1, 1, 15, 15, 0)   # deltaT formula
    t = (1961, 3, 12, 15, 15, 0)   
    JD = JulianDay(t)
    print 'JulianDay=%#4f localtime()=%s tzone=%#f' % (JD,t,time.altzone/3600.0)
    if t[0]>=1970:
        print 'TimeTup=%s' % time.ctime(time.mktime(TimeTup(JD)))
    print 'MJD=',JD - 2400000.5
    astT = AstroTime(t)
    print 'LocalTime sys=%s UTCOffset=%.1f JD=%.12g yymmdd=%s' % \
      (astT.LocalTime().AsHHMMSS(),astT.UTCOffset,astT.JulianDay(),astT.AsFormat('%y%m%d %a'))
    astT = AstroTime(astT.LocalTime(),UTCofs=1)
    print 'LocalTime CET=%s UTCOffset=%.1f JD=%.12g repr=%s' % \
          (astT.LocalTime().AsHHMMSS(),astT.UTCOffset,astT.JulianDay(),astT)
    astT._UTCofs = 2  # MEZT
    print 'LocalTime CEST=%s UTCOffset=%.1f JD=%.12g repr=%s' % \
          (astT.LocalTime().AsHHMMSS(),astT.UTCOffset,astT.JulianDay(),astT)
    print 'UTC=%s daysUT1=%f' % (astT.UTC().AsHHMMSS(),astT.rev)
    print 'LocalTime=',astT.LocalTime().AsHHMMSS()
    print 'EarthRotationAngle=',astT.ERA().Modulo().deg
    astT.UTCOffset = 1  # CET  !!! overwrites property
    print '!!! UTCOffset=',astT._UTCofs
    print 'UTC=%s daysUT1=%f' % (astT.UTC().AsHHMMSS(),astT.rev)
    print 'LocalTime=',astT.LocalTime().AsHHMMSS()
    print 'EarthRotationAngle=',astT.ERA().Modulo().deg
    print 'GMST=',astT.GMST().Modulo().deg
    print 'DeltaT=',astT.DeltaT()
    print u'\n'

if __name__ == '__main__':
    _test()
