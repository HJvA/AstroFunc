# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 
"""

"""
# run this module either on S60 phone or on PC 
# both to create local LocationsDB database
# on PC first create ODBC link 'dsLOCSdb' to an existing database

import sys,os
from AstroTypes import datPath

if '--dat' in sys.argv:
    datPath = sys.argv[sys.argv.index('--dat')+1]
#assert globals().has_key('datPath') , "datPath should have been defined by HastroRun"

if sys.platform=="win32":
    import adodbapi   # http://adodbapi.sourceforge.net/
    #ChkSrcPath('subs')
    ConStr = 'Provider=%s;Data Source=%s;User ID=%s;Password=%s;' % \
             ('MSDASQL',  'dsLOCSdb',    'Admin',   '')
    dbms = adodbapi.connect(ConStr)
else:   # symbian_S60 
    import appuifw  #e32db,e32
    #ChkSrcPath('subs')
    import dbS60
    ConStr = os.path.join(datPath, "GeoLocs.db")
    dbms = dbS60.connect(ConStr)

from dbGeoLocs import dbGeoLocs # get db scheme definition

if __name__ == '__main__':  # just testing db functions
    class GeoSite:
        def __init__(self,Record):
            self.rec = Record 
        def GetRecord(self):
            return self.rec
else:
    from AstroTypes import GeoLocation

    class GeoSite(GeoLocation):
        """ enhance GeoLocation accepting tuple
        """
        def __init__(self,Record):
            assert isinstance(Record, tuple)
            iName=0
            iLongitude=1
            iLatitude=2
            iHeight=3
            iTzone=4
            GeoLocation.__init__(self,
                    Record[iLongitude],Record[iLatitude],
                    Record[iHeight])
            self.name=Record[iName]
            self.tzone=int(Record[iTzone])
        def SetName(self, name):
            self.name=name
        def GetRecord(self):
            return (self.name,self.Longitude.deg,self.Latitude.deg,
                    self.Height,self.tzone)


class LocationsDB(dbGeoLocs):
    def __init__(self):
        dbGeoLocs.__init__(self, dbms)
    def GetGeoSite(self, name):
        lst = self.GetRecords(cond="WHERE name LIKE '%s'" % name)
        if len(lst)>0:
            return GeoSite(lst[0])
    def SaveGeoSite(self, GeoSite):
        self.CheckRecord(GeoSite.GetRecord())
    def DelGeoSite(self, name):
        self.DeleteRecord(name)
        
if __name__ == '__main__':
    from Rotation import DegAngle
    print ConStr
    app = LocationsDB()
    sites =\
      [GeoSite(('Veldhoven',5.4, 51.4, 20, 1)),
       GeoSite(('Nizas',   3.4, 43.5, 80,  1)),
       GeoSite(('Paris',   DegAngle(2,17,40).deg, DegAngle(48,51,30).deg, 40,  1)),
       GeoSite(('Berlin',  DegAngle(13,22,40).deg, DegAngle(52,31,0).deg, 35,  1)),
       GeoSite(('Warszawa',  DegAngle(21,2,29).deg, DegAngle(52,14,12).deg, 80,  1)),
       GeoSite(('Kaapstad',  DegAngle(18,24,59).deg, DegAngle(-33,-54,-52).deg, 190,  1)),
       GeoSite(('New Delhi',  DegAngle(77,13,0).deg, DegAngle(28,38,).deg, 220,  5.5)),
       GeoSite(('Beijing',  DegAngle(116,23,15).deg, DegAngle(39,54,45).deg, 50,  8)),
       GeoSite(('Buenos Aires',  DegAngle(-58,-23,-29).deg, DegAngle(-34,-35,-24).deg, 32,  -3)),
       GeoSite(('New York',  DegAngle(-74,-1,0).deg, DegAngle(40,42,13).deg, 3,  -5))]
    print app.MaxId
    app.DeleteRecord('Nizas')
    for site in sites:
        app.CheckRecord(site.GetRecord())
    print app.GetNames()
    app.close()
    
