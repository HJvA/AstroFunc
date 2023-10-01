# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import math
import sys,os,time,string
#import win32traceutil

modPath = os.path.split(sys.argv[0])[0]
if not modPath in sys.path:
    sys.path.append(modPath)
    print modPath
del modPath

from AstroTypes import datPath,pn
import AstroTime
import CoordTrans
import Kepler
import CelestData
import dbLocations
import ELPmpp02
import moon282

def filtertxt(txt):
    tbl = string.join([chr(i) for i in range(256)],'')
    return string.translate(txt.encode('ascii'),tbl,'e')

def _test():
    prec=4
    global datPath
    if '--dat' in sys.argv:
        datPath = sys.argv[sys.argv.index('--dat')+1]
    #assert globals().has_key('datPath') ,"datPath should have been defined by HastroRun"
    print "data path=%s" % datPath
    
    t = time.localtime()
    #t = (2007, 4, 5, 14, 0, 0)
    #t = (2008, 9, 24, 13, 28, 0)
    frame = CoordTrans.GeoObserver(t,UTCofs=1)
    print frame.AsFormat('--- %Y %m %d ------ %H:%M:%S ---')
    #frame.UTCOffset =2
    frame.Precision =prec

    location = 'Veldhoven'
    LocDB = dbLocations.LocationsDB()
    frame.GeoLoc = LocDB.GetGeoSite(location)
    print 'location %s, UTCoffset %.1f, precision %d' % \
          (frame.GeoLoc.name, frame.UTCOffset, frame.Precision)
    print 'localtime=', frame.LocalTime().AsHHMMSS()

    bodies = (Kepler.Sun(frame,Precision=prec),
              Kepler.Planet(pn.Saturn, frame, Precision=prec),
              CelestData.StarObj('arcturus'),
              Kepler.Moon(frame, Precision=1),
              Kepler.Moon(frame, Precision=prec),
              ELPmpp02.Moon(frame, Precision=prec))
    for body in bodies:
        print
        print '%s @ %s ' % (body.name,frame.GeoLoc.name)
        print 'TopoCentric azimuth =%s (%s)  altitude=%s' % \
          (frame.Azimuth(body).AsHHMMSS(),frame.Azimuth(body).AsNESW(),frame.Elevation(body))
        print 'Rise=%s Transit=%s Set=%s' % \
              (frame.Rise_Time(body).AsHHMMSS(), frame.Transit(body).AsHHMMSS(), frame.Set_Time(body).AsHHMMSS())
        print 'GeoCentric=%s' % (body)
        print 'GeoCentric polar=%s %s %s' % body.Polar()
        #print "Ra=%s, decl=%s, dist=%s" % frame.Viewing(body).Polar()
        print 'Ra=%s decl=%s dist=%.4f' % \
              (body.Longitude().AsHHMMSS(),body.Latitude(),body.Distance())
        if hasattr(body, 'CoordICRS'):
            print 'HelioCentric=',body.CoordICRS()

   
    
if __name__ == '__main__':
    _test()
