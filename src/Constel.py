# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

import sys,math
from AstroTypes import CelestialObj,datPath
from Rotation import DegAngle,SQR,AngDiff

dbConstel = True
toPhone   = False
ConstelCat= None

if dbConstel:
    from AnyDB import AnyDB
    wildcard='*'
    if sys.platform=="win32":
        if toPhone:
            import btDBclient
            #ConStr = os.path.join(datPath, "Stars.db")
            ConStr = "stars.db"
            dbms = btDBclient.connect(ConStr)
        else:
            import adodbapi
            dsn='dsCATdat'
            provider='MSDASQL'  # ODBC for OLEDB
            dbms = adodbapi.connect('Data Source=%s;'% (dsn))
            wildcard='%%'

    elif sys.platform=="symbian_s60":
        import os,dbS60
        if '--dat' in sys.argv:
            datPath = sys.argv[sys.argv.index('--dat')+1]
        ConStr = os.path.join(datPath, r'stars.db')
        dbms = dbS60.connect(ConStr)

    class dbConstels(AnyDB):
        """ define database structure by overriding virtual members from AnyDB
        """
        KeyFld        ="id"
        dbTbl         ="constel"   # name of a table defined in ConStr
        Fields        ="name,abrev,medRa,medDecl,RaZeroPass"    # must map to EditFlds, Note: KeyFld not included
        EditFlds      ="name,abreviation,median Ra,median decl,RaZeroPass"  # long verbose names, must map to database Fields
        sqlCreateTable="CREATE TABLE constel (id INTEGER,name VARCHAR, abrev CHAR(3), medRa FLOAT, medDecl FLOAT, RaZeroPass INTEGER)" 
        sqlInsert     ="INSERT INTO constel (%s) VALUES ('%s','%s',%.4f,%.4f,%d,%d)"
        sqlUpdate     ="UPDATE constel SET name='%s',abrev='%s',medRa=%.8f,medDecl=%.8f,RaZeroPass=%d WHERE id=%d"
        def __init__(self, con=dbms):
            AnyDB.__init__(self, con)
    ConstelCat = None

    def _bldObj(rec):
        (name,abrev,avgRa,avgDecl,id) = rec
        obj = CelestialObj(DegAngle(avgRa), DegAngle(avgDecl), 1)
        obj.Vapparent = 0
        obj.name=name
        obj.abrev=abrev
        obj.ConstelId=id
        return obj
        
    def ConstelObj (name="",id=None):
        """ retrieve constellation properties from database 
        """
        global ConstelCat
        if ConstelCat is None:
            ConstelCat = dbConstels()
        if id:
            recs = ConstelCat.GetRecords(cond="WHERE id=%d" % (id))
        else:
            recs = ConstelCat.GetRecords(cond="WHERE name LIKE '%s%s'" % (name,wildcard))
        if recs:
            return _bldObj(recs[0]) 
        else:
            return None
    def ClosestConstels(Ra,Decl,n=5):
        """ get sorted list of constellations closest to obj
        """
        global ConstelCat
        if ConstelCat is None:
            ConstelCat = dbConstels()
        lst = [(1e99,0) for i in range(n+1)]
        rec = ConstelCat.FirstRecord(cond="")
        while not rec is None:
            (name,abrev,medRa,medDecl,RaZeroPass,id) = rec
            dist = SQR(AngDiff(Ra,DegAngle(medRa)).deg) + \
                   SQR(AngDiff(Decl,DegAngle(medDecl)).deg)
            lst[n]=(dist,id,RaZeroPass)
            lst.sort()   #(cmp=lambda x,y: cmp(x[0], y[0]) )
            rec = ConstelCat.NextRecord()
        del(lst[n])
        return lst  # [id[1] for id in lst]
        
    def ConstelObjOfBody(body):
        """ find constellation where body belongs to or is closest to
        """
        #global ConstelCat
        if body.ConstelId>0:
            return ConstelObj(id=body.ConstelId)
        else:
            id = ClosestConstels(body.RightAscension(),body.Declination(),n=1)[0]
            return ConstelObj(id=id)

            if ConstelCat is None:
                ConstelCat = dbConstels()
            Ra = body.RightAscension()
            Decl = body.Declination()
            minDist = 1e9
            rec = ConstelCat.FirstRecord(cond="")
            minRec = rec
            while not rec is None:
                (name,abrev,avgRa,avgDecl,RaZeroPass,id) = rec
                dist = SQR((Ra-DegAngle(avgRa)).Modulo(0.0).deg) + \
                       SQR((Decl-DegAngle(avgDecl)).Modulo(0.0).deg)
                if dist<minDist:
                    minDist=dist
                    minRec=rec
                rec = ConstelCat.NextRecord()
            return _bldObj(minRec)
            
    def ConstelList(cond=""):
        """ retrieve a filtered list of constellations from the database
        """
        global ConstelCat
        if ConstelCat is None:
            ConstelCat = dbConstels()
        #if not cond is None:
            #StarCat.cond = cond
        return ConstelCat.GetNames(cond)

if __name__ == '__main__':
    def ConstelBrowser(db):
        import dbBrowser
        app = dbBrowser.dbBrowser(db)
        app.run("ConstelBrowser")
        app.close()
    lst = ConstelList()
    print lst," len=%d" % len(lst)
    idx=13
    obj = ConstelObj(lst[idx])
    print "%s geocentric J2000 coord: " % lst[idx],obj
    body = CelestialObj(obj.Longitude(), obj.Latitude(), 1)
    print "Body  lon=%s, lat=%s " % \
          (body.Longitude().AsHHMMSS(), body.Latitude())
    ids = ClosestConstels(body.RightAscension(),body.Declination())
    print "ClosestConstels: %s" % ids
    obj = ConstelObjOfBody(body)
    print "Constel=%s lon=%s, lat=%s id=%d" % \
          (obj.name, obj.Longitude().AsHHMMSS(), obj.Latitude(), obj.ConstelId)
