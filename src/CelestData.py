# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import sys
import math
from Rotation import Angle,DegAngle,Coordinate
from AstroTypes import CelestialObj,datPath

dbStars = True
atPhone = False


if not dbStars:
    # The Cambridge star atlas
    _Stars =  {
        u'sirius'    : ((Angle('6h45.2m'),Angle("-16*43'")),'CMa'),    
        u'arcturus'  : ((Angle('14h15.7m'),Angle("19*11'")),'Boo'),
        u'vega'      : ((Angle('18h36.9m'),Angle("38*47'")),'Lyr'),
        u'capella'   : ((Angle('5h16.7m'), Angle("46*0'")), 'Aur'),
        u'procyon'   : ((Angle('7h39.3m'),Angle("5*14'")),  'CMi'),
        u'betelgeuse': ((Angle('5h55.2m'),Angle("7*24'")),  'Ori'),
        u'altair'    : ((Angle('19h50.8m'),Angle("8*52'")),'Aql'), #268Â°37'52", 12Â°28'22"
        u'pollux'    : ((Angle('7h45.3m'),Angle("28*2'")), 'Gem'),
        u'deneb'     : ((Angle('20h41.4m'),Angle("45*17'")),'Cyg'),
        u'castor'    : ((Angle('7h34.6m'),Angle("31*53'")),'Gem'),
        u'polaris'   : ((Angle('2h31.8m'),Angle("89*16'")),'UMi')     }

    def StarObj(name):
        tup = _Stars[name.lower()][0]
        obj = CelestialObj(tup[0], tup[1])
        obj.name=name
        return obj
    def StarsList(cond=None):
        return _Stars.keys()
    class dbStarCat:
        pass

else:
    from AnyDB import AnyDB
    wildcard='*'
    if sys.platform=="win32":
        if atPhone:
            import btDBclient
            #ConStr = os.path.join(datPath, "Stars.db")
            ConStr = "stars.db"
            dbms = btDBclient.connect(ConStr)
        else:
            import adodbapi
            dsn='dsCATdat'
            provider='MSDASQL'  # ODBC for OLEDB
            dbms = adodbapi.connect('Data Source=%s;Provider=%s;'% (dsn,provider))
            wildcard='%%'

    elif sys.platform=="symbian_s60":
        import os,dbS60
        if '--dat' in sys.argv:
            datPath = sys.argv[sys.argv.index('--dat')+1]

        ConStr = os.path.join(datPath, r'stars.db')
        dbms = dbS60.connect(ConStr)

    class dbStarCat(AnyDB):
        """ define database structure by overriding virtual members from AnyDB
        """
        dbTbl         ="stars"   # name of a table defined in ConStr
        Fields        ="name,Ra,decl,distance,Vapparent,constellation"    # must map to EditFlds, Note: KeyFld not included
        EditFlds      = 'name,Ra,decl,distance,magnitude,constellation'  # long verbose names, must map to database Fields
        sqlCreateTable="CREATE TABLE stars (id BIGINT, name VARCHAR, Ra FLOAT, decl FLOAT, " \
                        "Vapparent FLOAT, distance FLOAT, constellation INTEGER)" 
        sqlInsert     ="INSERT INTO stars (%s) VALUES ('%s',%.8f,%.8f,%.4f,%.4f,%d,%d)"
        sqlUpdate     ="UPDATE stars SET name='%s',Ra=%.8f,decl=%.8f,distance=%.4f,Vapparent=%.4f,constellation=%d WHERE id=%d"
        def __init__(self, con=dbms):
            AnyDB.__init__(self, con)
    StarCat = None
    def StarObj (name):
        """ retrieve star properties from database of a single star
        """
        global StarCat
        if StarCat is None:
            StarCat = dbStarCat()
        if type(name) == str:
            recs = StarCat.GetRecords(cond="WHERE name LIKE '%s%s'" % (name,wildcard))
        elif type(name) in (int,float):
            recs = StarCat.GetRecords(cond="WHERE id=%d" % (name))
        if recs:
            (name,Ra,decl,distance,Vappar,constel,id) = recs[0]
            obj = CelestialObj(DegAngle(Ra), DegAngle(decl), distance)
            obj.Vapparent = Vappar
            obj.name=name
            obj.ConstelId = constel
            obj.id = id
            return obj 
        else:
            return None
    def StarsList(cond=""):
        """ retrieve a filtered list of stars from the database
        """
        global StarCat
        if StarCat is None:
            StarCat = dbStarCat()
        #if not cond is None:
            #StarCat.cond = cond
        return StarCat.GetNames(cond)
    def StarsListIds(cond=""):
        """ retrieve a filtered list of star Ids from the database
        """
        global StarCat
        if StarCat is None:
            StarCat = dbStarCat()
        lst = StarCat.GetRecords(numb=None,cond="", \
                                 sql=StarCat.sqlSelNames % (StarCat.KeyFld, StarCat.dbTbl, cond))
        #return lst
        return [int(elm[0]) for elm in lst]
        
    def WriteConstellation(StarId, ConstelId):
        global StarCat
        if StarCat is None:
            StarCat = dbStarCat()
        return StarCat.SqlExecute("UPDATE %s SET constellation=%d WHERE id=%d" % \
                           (StarCat.dbTbl,ConstelId,StarId))

def _test():
    #lst = StarsList("WHERE Vapparent<2 AND NOT name IS NULL")
    #lst = StarsList("WHERE distance<9.0")
    lst = StarsList("WHERE (Vapparent<6.5 OR distance<4) ORDER BY Vapparent")
    print lst," len=%d" % len(lst)
    idx=15
    obj = StarObj(lst[idx])
    print "%s geocentric J2000 coord: " % lst[idx],obj
    obj = StarObj('arcturus')
    if not obj is None:
        print 'Arcturus','Ra=%s,Decl=%s,Vappar=%f' % \
              (obj.Longitude().AsHHMMSS(), obj.Latitude(), obj.Vapparent)

if __name__ == '__main__':
    _test()
    #_CopyCat()