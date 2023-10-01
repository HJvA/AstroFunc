# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import sys,os

from AnyDB import AnyDB

class dbGeoLocs(AnyDB):
    """
    define database structure by overriding virtual members from AnyDB
    """
    dbTbl         ="GeoLocs"   # name of a table defined in ConStr
    Fields        ="name,lon,lat,height,tzone"    # must map to EditFlds, Note: KeyFld not included
    EditFlds      ='name,longitude,latitude,height,time zone'  # long verbose names, must map to database Fields
    sqlCreateTable="CREATE TABLE GeoLocs (id INTEGER, name VARCHAR, lon FLOAT, lat FLOAT, height FLOAT, tzone INTEGER)" 
    sqlInsert     ="INSERT INTO GeoLocs (%s) VALUES ('%s',%f,%f,%f,%d,%d)"
    sqlUpdate     ="UPDATE GeoLocs SET name='%s',lon=%f,lat=%f,height=%f,tzone=%d WHERE id=%d"
    def __init__(self, dbms):
        AnyDB.__init__(self, dbms)
        if self.GetRecords()==None:
            self.CheckRecord(('Veldhoven',5.4, 51.4, 20, 2))
            self.CheckRecord(('Nizas',    3.4, 43.5, 80, 2))
            self.db.commit()

          
if __name__ == '__main__':
    if sys.platform=="win32":
        raise OSError("only for symbian_S60")
    else:
        import dbBrowser, dbS60
        ConStr = os.path.join(datPath, "GeoLocs.db")
        dbms = dbS60.connect(ConStr)

        app = dbBrowser.dbBrowser(dbGeoLocs(dbms))
        app.run("S60dbBrowser")
        app.close()

    

