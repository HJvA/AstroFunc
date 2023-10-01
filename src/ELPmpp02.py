# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

# from 'elpmpp02.pdf'
# LUNAR SOLUTION ELP
# version ELP/MPP02
# Jean CHAPRONT and G´erard FRANCOU
# Observatoire de Paris -SYRTE department - UMR 8630/CNRS
# October 2002


import sys,math,os
from Rotation import DegAngle,ArcsAngle,Angle,Coordinate,PolarCoord,RotMatrix,RotAx,SQR
from AstroTypes import CelestialObj,datPath
from Matrix import Matrix
from AstroTime import AstroTime,JulianDay
from AnyDB import AnyDB

# W1, the mean mean longitude of the Moon,
# W2, the mean longitude of the lunar perigee,
# W3, the mean longitude of the lunar ascending node,
# T, the heliocentric mean longitude of the Earth-Moon barycenter,  (eart,Te)
# peri, the mean longitude of the perihelion of the Earth-Moon barycenter, (peri,Pip)

# W1,W2 and W3 are angles of the inertial mean ecliptic of date referred to the departure point ƒÁŒ 2000 (see sub-
# section 5.1). T and peri are angles of the inertial mean ecliptic of J2000 referred to the inertial mean equinox
# 2000 of J2000.
crNone = 0
crD405 = 1
crLLR  = 2
crCorr = crNone


MeMargs = {
    'W1':(DegAngle(218,18,59.95571), #t^0
          ArcsAngle(1732559343.73604),    #t^1
          ArcsAngle(-6.8084),             #t^2
          ArcsAngle(0.006604),            #t^3
          ArcsAngle(-0.00003169)),        #t^4
    'W2':(DegAngle(83,21,11.67475),
          ArcsAngle(14643420.3171),
          ArcsAngle(-38.2631),
          ArcsAngle(-0.045047),
          ArcsAngle(0.00021301)),
    'W3':(DegAngle(125,02,40.39816),
          ArcsAngle(-6967919.5383),
          ArcsAngle(6.359),
          ArcsAngle(0.007625),
          ArcsAngle(-0.00003586)),
    'T' :(DegAngle(100,27,59.13885), #eart
          ArcsAngle(129597742.293),
          ArcsAngle(-0.0202),
          ArcsAngle(0.000009),
          ArcsAngle(0.00000015)),
    'peri':(DegAngle(102,56,14.45766), #peri
          ArcsAngle(1161.24342),
          ArcsAngle(0.529265),
          ArcsAngle(-0.00011814),
          ArcsAngle(0.000011379))
          }

def Correction(crCorr):
    if crCorr==crD405:
        Dw1_1   = -0.35106
        Deart_1 =  0.00732
        Dep     =  0.00224
        Dgam    =  0.00085
        De      = -0.00006
        MeMargs['W1'][0].arcs+=-0.07008
        MeMargs['W1'][1].arcs+=-0.35106
        MeMargs['W1'][2].arcs+=-0.03743
        MeMargs['W1'][3].arcs+=-0.00018865
        MeMargs['W1'][4].arcs+=-0.00001024
        MeMargs['W2'][0].arcs+=0.20794
        MeMargs['W2'][1].arcs+=0.08017
        MeMargs['W2'][2].arcs+=+0.00470602
        MeMargs['W2'][3].arcs+=-0.00025213
        MeMargs['W3'][0].arcs+=-0.07215
        MeMargs['W3'][1].arcs+=-0.04317
        MeMargs['W3'][2].arcs+=-0.00261070
        MeMargs['W3'][3].arcs+=-0.00010712
        MeMargs['T'][0].arcs+=-0.00033
        MeMargs['T'][1].arcs+=0.00732
        MeMargs['peri'][0].arcs+=-0.00749
    elif crCorr==crLLR:
        Dw1_1   = -0.32311
        Dgam    =  0.00069
        De      = +0.00005
        Deart_1 =  0.01442
        Dep     =  0.00226
        MeMargs['W1'][0].arcs+=-0.10525
        MeMargs['W1'][1].arcs+=-0.32311
        MeMargs['W1'][2].arcs+=-0.03794
        MeMargs['W2'][0].arcs+=0.16826
        MeMargs['W2'][1].arcs+=0.08017
        MeMargs['W3'][0].arcs+=-0.10760
        MeMargs['W3'][1].arcs+=-0.04317
        MeMargs['T'][0].arcs+=-0.04012
        MeMargs['T'][1].arcs+=0.01442
        MeMargs['peri'][0].arcs+=-0.04854

    am     =  0.074801329
    alpha  =  0.002571881
    xa     =  (2.0*alpha)/3

    x2     =   MeMargs['W2'][1].arcs/MeMargs['W1'][1].arcs
    x3     =   MeMargs['W3'][1].arcs/MeMargs['W1'][1].arcs
    y2     =   am*0.311079095 + xa*+0.50928e-4
    y3     =   am*-0.103837907 + xa*-0.37342e-4

    d21    =   x2-y2
    d22    =   MeMargs['W1'][1].arcs*-0.4482398e-2
    d23    =   MeMargs['W1'][1].arcs*-0.110248500e-2
    d24    =   MeMargs['W1'][1].arcs*0.1056062e-2
    d25    =   y2/am

    d31    =   x3-y3
    d32    =   MeMargs['W1'][1].arcs*0.6682870e-3
    d33    =   MeMargs['W1'][1].arcs*-0.129807200e-2
    d34    =   MeMargs['W1'][1].arcs*-0.1780280e-3
    d35    =   y3/am

    Cw2_1  =  d21*Dw1_1+d25*Deart_1+d22*Dgam+d23*De+d24*Dep
    Cw3_1  =  d31*Dw1_1+d35*Deart_1+d32*Dgam+d33*De+d34*Dep

    MeMargs['W2'][1].arcs +=  Cw2_1
    MeMargs['W3'][1].arcs +=  Cw3_1
        
#Correction(crLLR)

PlanArgs = {  # mean longitudes and mean motions  (VSOP2000)
    'Me':(DegAngle(252,15,03.216919),ArcsAngle(538101628.68888)),
    'Ve':(DegAngle(181,58,44.758419),ArcsAngle(210664136.45777)),
    'Ma':(DegAngle(355,26,03.642778),ArcsAngle( 68905077.65936)),
    'Ju':(DegAngle( 34,21,05.379392),ArcsAngle( 10925660.57335)),
    'Sa':(DegAngle( 50,04,38.902495),ArcsAngle(  4399609.33632)),
    'Ur':(DegAngle(314,03,04.354234),ArcsAngle(  1542482.57845)),
    'Ne':(DegAngle(304,20,56.808371),ArcsAngle(   786547.897))
           }



nodb = False
def elpConnect():
    """ connect to elp mpp02 database
    """
    if sys.platform=="win32":
        if nodb:
            return None # let catalog define dbms
        else:
            import adodbapi
            return adodbapi.connect('Data Source=%s;User ID=%s;Password=%s;'%
                            ('dsELPdat','Admin',''))
    elif sys.platform=="symbian_s60":
        import dbS60
        if '--dat' in sys.argv:
            global datPath
            datPath = sys.argv[sys.argv.index('--dat')+1]
        #assert globals().has_key('datPath') ,"datPath should have been defined by HastroRun"

        ConStr = os.path.join(datPath, "ELP.db")
        return dbS60.connect(ConStr)


class dbElpMain(AnyDB):
    """ define database structure by overriding virtual members from AnyDB
    """
    dbTbl         ="main"   # name of a table defined in ConStr
    KeyFld        ="VUr"
    Fields        ="A,D,F,l,l_"    # must map to EditFlds, Note: KeyFld not included
    EditFlds      = Fields  # long verbose names, must map to database Fields
    sqlCreateTable="CREATE TABLE main (VUr INTEGER,A FLOAT, " \
                    "D INTEGER,F INTEGER,l INTEGER,l_ INTEGER)"
    sqlInsert     ="INSERT INTO main (%s) VALUES (%#.5f,%d,%d,%d,%d)"
    sqlUpdate     =""
    def __init__(self, con):
        AnyDB.__init__(self, con)

class dbElpPertub(AnyDB):
    """ define database structure by overriding virtual members from AnyDB
    """
    dbTbl         ="pertub"   # name of a table defined in ConStr
    Fields        ="tpow,S,C,D,F,l,l_,Me,Ve,T,Ma,Ju,Sa,Ur,Ne,zet"    # must map to EditFlds, Note: KeyFld not included
    KeyFld        ="VUr"
    EditFlds      =Fields  # long verbose names, must map to database Fields
    sqlCreateTable="CREATE TABLE pertub (VUr INTEGER,tpow INTEGER, S FLOAT, C FLOAT, " \
                    "D INTEGER,F INTEGER,l INTEGER,l_ INTEGER," \
                    "Me INTEGER,Ve INTEGER,T INTEGER,Ma INTEGER,Ju INTEGER,Sa INTEGER,Ur INTEGER,Ne INTEGER,zet INTEGER)" 
    #sqlInsert     ="INSERT INTO pertub (%s) VALUES (%d,%d,%.18g,%.18g,%d,%d,%d,%d" \
    sqlInsert     ="INSERT INTO pertub (%s) VALUES (%d,%.12g,%.12g,%d,%d,%d,%d" \
                    ",%d,%d,%d,%d,%d,%d,%d,%d,%d)"
    sqlUpdate     =""
    def __init__(self, con):
        AnyDB.__init__(self, con)

  
class Moon(CelestialObj):
    ObliquityJ2000 = 84381.406  # eps0 USNO 179 table 5.1
    Dprec = -0.29965  #IAU2000 corr to const of precession

    def __init__(self, AstrTime, Precision=1):
        self.SetTime(AstrTime,Precision)
        self.name='Moon (elp)'

    def SetTime(self, AstrTime,  Precision=1):
        """ modify time & compute delaunay arguments
        """
        if isinstance(AstrTime, AstroTime):
            cy = AstrTime.cyTJ2000()
        #else:
        #    cy = AstroTime(AstrTime,UTCofs).cyTJ2000()
        self.t = [1,cy]
        for i in range(3):
            self.t.append(cy * self.t[-1])
        
        self.W1 = self.EvalPolyn(MeMargs['W1'])
        W2 = self.EvalPolyn(MeMargs['W2'])
        W3 = self.EvalPolyn(MeMargs['W3'])
        self.T  = self.EvalPolyn(MeMargs['T'])
        peri = self.EvalPolyn(MeMargs['peri'])
        #Delaunay arguments
        self.D = self.W1 - self.T +180.0*3600.0
        self.F = self.W1-W3
        self.l = self.W1-W2
        self.l_= self.T-peri
        if Precision>3:
            self.zeta = self.W1 +(5029.0966 +self.Dprec)*cy  # Mean longitude W1 + Rate of the precession 
            self.Me = self.EvalPolyn(PlanArgs['Me'])
            self.Ve = self.EvalPolyn(PlanArgs['Ve'])
            self.Ma = self.EvalPolyn(PlanArgs['Ma'])
            self.Ju = self.EvalPolyn(PlanArgs['Ju'])
            self.Sa = self.EvalPolyn(PlanArgs['Sa'])
            self.Ne = self.EvalPolyn(PlanArgs['Ne'])
            self.Ur = self.EvalPolyn(PlanArgs['Ur'])
        Coordinate.__init__(self, self.elpJ2000(Precision))
        
    def EvalPolyn(self,coeffs):
        """ evaluate polynome using coeffs c0,c1,c2...
            into co*t[0]+c1*t[1]+c2*t[2]+....
        """
        val=0.0
        i=0
        for coeff in coeffs:
            val += coeff.arcs * self.t[i]
            i+=1
        return val

    def elpEcliptic(self,Precision):
        """ moon coordinates refered to inertial mean ecliptic of date
        """
        V=0.0
        U=0.0
        r=0.0
        db =dbElpMain(elpConnect())
        if Precision<=4:            
            rec = db.FirstRecord("WHERE A>1 OR A<-1")
        else:
            rec = db.FirstRecord("")
        assert len(rec)>0, "no ELP fourier records found"
        while not rec is None:   
            (A,D,F,l,l_,VUr) = rec
            ang = ArcsAngle(D*self.D + F*self.F + l*self.l + l_*self.l_ )
            if VUr==1:
                V += A * math.sin(ang.rad)
            elif VUr==2:
                U += A * math.sin(ang.rad)
            elif VUr==3:
                r += A * math.cos(ang.rad)
            rec = db.NextRecord()
        #db.close()
        if Precision>3:
            db = dbElpPertub(elpConnect())
            if Precision>4:            
                rec = db.FirstRecord("")
            else:
                rec = db.FirstRecord("WHERE S>1 OR S<-1 OR C>1 OR C<-1")
            assert len(rec)>0, "no ELP Poisson records found"
            while not rec is None:  
                (tpow,S,C,D,F,l,l_,Me,Ve,T,Ma,Ju,Sa,Ur,Ne,zet,VUr) = rec
                ang = self.D*D + self.l_*l_ + self.l*l + self.F*F + self.T*T
                ang += self.zeta*zet+self.Me*Me+self.Ve*Ve+self.Ma*Ma+self.Ju*Ju+self.Sa*Sa+self.Ne*Ne+self.Ur*Ur
                ang = ArcsAngle(ang)
                term = self.t[tpow] * (S * math.sin(ang.rad) + C * math.cos(ang.rad))
                if VUr==1:
                    V += term
                elif VUr==2:
                    U += term
                elif VUr==3:
                    r += term
                rec = db.NextRecord()
            db.close()
        if Precision>4:
            r *= (384747.9613701725/384747.980674318)
        return PolarCoord(ArcsAngle(V+self.W1), ArcsAngle(U), r)

    def EclipticOfDate(self,Precision):
        """ moon ecliptic coordinates with actual equinox origin
        """
        Pa = 5029.0966*self.t[1] + 1.112*self.t[2] + 0.000077*self.t[3] -0.00002353*self.t[4]
        crd = self.elpEcliptic(Precision)
        Vd = crd.Longitude().arcs +Pa +self.Dprec*self.t[1]
        Ud = crd.Latitude().arcs
        r  = crd.Distance()
        return PolarCoord(ArcsAngle(Vd), ArcsAngle(Ud), r)
        

    def EclipticJ2000(self,Precision):
        """ apply precession according to Lascar 1986
        """
        cy = self.t[1]
        P = (0.10180391e-4 +(0.47020439e-6 +(-0.5417367e-9 +(-0.2507948e-11 +(0.463486e-14)*
                                                              cy)*cy)*cy)*cy)*cy
        Q = (-0.113469002e-3 +(0.12372674e-6 +(0.1265417e-8 +(-0.1371808e-11 +(-0.320334e-14)*
                                                              cy)*cy)*cy)*cy)*cy
        sPQ = 2*math.sqrt(1-SQR(P)-SQR(Q))
        RotM = Matrix( [
            [1-2*SQR(P), 2*P*Q, P*sPQ],
            [2*P*Q, 1-2*SQR(Q), -Q*sPQ],
            [-P*sPQ, Q*sPQ, 1-2*SQR(P)-2*SQR(Q)] ])
        return Coordinate(RotM * self.elpEcliptic(Precision))

    def elpJ2000(self,Precision):
        """ moon epoch J2000 coordinates
        """
        crd = self.EclipticJ2000(Precision)
        return crd.Rotated(RotMatrix(ArcsAngle(-self.ObliquityJ2000), RotAx.R1))

if __name__ == '__main__':
    def ElpBrowser(db):
        import dbBrowser
        app = dbBrowser.dbBrowser(db)
        app.run("ElpBrowser")
        app.close()
    def MoonPos(astm, precision=3):
        #astm = AstroTime(tm,UTCofs=0)
        print "LocTm=%s JD=%f, UTCofs=%d" % (astm.LocalTime().AsHHMMSS(),JulianDay(tm),astm.UTCOffset)
        body = Moon(astm,precision)
        print 'Ecliptic elp=%s' % body.elpEcliptic(precision)
        print 'Ecliptic Of Date=%s' % body.EclipticOfDate(precision)
        print 'Ecliptic J2000=%s' % body.EclipticJ2000(precision)
        print 'GeoCentric J2000 X,Y,Z=',body
        #s = body.Polar().__repr__()
        print 'GeoCentric J2000 Ra,decl,dist=%s, %s, %s' % body.Polar()

    import time
    tm = time.localtime()
    tm = (1980, 1, 1, 0, 0, 0)
    #tm = (1985, 6, 23, 0, 0, 0)
    #tm = (1990,12, 14, 0, 0, 0)
    tm = (1996, 6, 5, 0, 0, 0)
    #tm = (2001, 11, 26, 0, 00, 0)
    ast = AstroTime(tm,UTCofs=1)
    conn = elpConnect()
    prgs = \
        (
          ('ElpMainBrowser',   (ElpBrowser, [dbElpMain(conn)])),
          ('ElpPertubBrowser', (ElpBrowser, [dbElpPertub(conn)])),
          ('MoonPos precis1',  (MoonPos,    [ast,1])),
          ('MoonPos precis3',  (MoonPos,    [ast,3])),
          ('MoonPos precis4',  (MoonPos,    [ast,4])),
          ('MoonPos precis5',  (MoonPos,    [ast,5]))
        )
    for i in range(len(prgs)):
        print "%d.%s" % (i,prgs[i][0])
    prg = int(raw_input("%d..%d? " % (0,len(prgs)-1)))
    prgs[prg][1][0](*prgs[prg][1][1])
    
