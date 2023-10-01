# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# info @ henk.jan.van.aalderen@gmail.com

import sys,os
from AstroTypes import pn
from AnyDB import AnyDB
from Rotation import DegAngle
from Constel import ClosestConstels

def SideOfLine(lpnt0,lpnt1, pnt):
    dx = lpnt1[0] - lpnt0[0]
    dy = lpnt1[1] - lpnt0[1]
    cc=-(-lpnt0[0]*dy + lpnt0[1]*dx)
    dd=-dy*pnt[0] + dx*pnt[1] + cc
    return dd>0


#int pnpoly(int nvert, float *vertx, float *verty, float testx, float testy)
#{
#  int i, j, c = 0;
#  for (i = 0, j = nvert-1; i < nvert; j = i++) {
#    if ( ((verty[i]>testy) != (verty[j]>testy)) &&
#	 (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]) )
#       c = !c;
#  }
#  return c;
#}


def IsInPolygon(pnt, polygon):
    """ Jordan curve theorem
    """
    # http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
    c = False
    vj = polygon[-1]  # last point
    for i in range(0,len(polygon)):
        vi = polygon[i]
        if ((vi[1]>pnt[1]) != (vj[1]>pnt[1])):
            if ( (pnt[0] < (vj[0]-vi[0]) * (pnt[1]-vi[1]) /
                  (vj[1]-vi[1]) + vi[0])):
                c = not c
        vj = vi
    return c

class dbConstelBnds(AnyDB):
    dbTbl         ="ConstelBounds"   # name of a table defined in ConStr
    Fields        ="Ra,Decl,idx"    # must map to EditFlds, Note: KeyFld not included
    KeyFld        ="Id"
    EditFlds      = 'Ra,Decl,idx'  # long verbose names, must map to database Fields
    sqlCreateTable="CREATE TABLE ConstelBounds " \
                    "(Id INTEGER,idx INTEGER, Ra FLOAT, decl FLOAT )" 
    sqlInsert     ="INSERT INTO ConstelBounds (%s) VALUES (%.8f,%.8f,%d,%d)"
    sqlUpdate     ="UPDATE ConstelBounds SET Ra=%.8f,Decl=%.8f WHERE idx=%d AND Id=%d"
    def __init__(self):
        if sys.platform=="win32":
            import adodbapi   # http://adodbapi.sourceforge.net/
            ConStr = 'Data Source=%s;' %   ('dsCATdat',)
            dbms = adodbapi.connect(ConStr)
        else:   # symbian_S60 
            import dbS60
            ConStr = os.path.join(datPath, "stars.db")
            dbms = dbS60.connect(ConStr)
        AnyDB.__init__(self, dbms)
    
    def IsInConstel(self,ConstelId, Ra, Decl, RaZeroPass=0):
        recs = self.GetRecords(numb=None,
                 sql = "SELECT Ra,Decl FROM ConstelBnds WHERE Id=%d ORDER BY idx" % ConstelId)
        if RaZeroPass:
            return IsInPolygon((Ra.Modulo(0.0).deg,Decl.Modulo(0.0).deg),recs)
        else:
            return IsInPolygon((Ra.Modulo(0.5).deg,Decl.Modulo(0.0).deg),recs)

    def FindConstel(self, Ra, Decl):
        recs = ClosestConstels(Ra, Decl,n=80)
        for rec in recs:
            if self.IsInConstel(rec[1], Ra,Decl, rec[2]):
                return rec[1]

    def Median(self, ConstelId):
        recs = self.GetRecords(numb=None,
                 sql = "SELECT Ra,Decl FROM ConstelBnds WHERE Id=%d ORDER BY idx" % ConstelId)
        Ra0 = DegAngle(recs[0][0])
        Ras = [DegAngle(rec[0]).Modulo(Ra0.rev).deg for rec in recs]
        return Ras.median()
        
        

if __name__ == '__main__':
    print "in polygon: %s , out polygon: %s " % (IsInPolygon((0.18,0.33), \
            ((0.22,0.22),(0.26,0.23),(0.27,0.33),(0.34,0.4),(0.34,0.42),(0.14,0.42))), \
              IsInPolygon((0.17,0.33), \
            ((0.22,0.22),(0.26,0.23),(0.27,0.33),(0.34,0.4),(0.34,0.42),(0.14,0.42))))
    dbConstBnds = dbConstelBnds()
    print "auriga id=8 %s" % dbConstBnds.IsInConstel(8, DegAngle(90.4), DegAngle(40.4))
    print dbConstBnds.FindConstel(DegAngle(90.5), DegAngle(40.5))
    from CelestData import StarsListIds,StarObj,WriteConstellation
    lst = StarsListIds("WHERE (Vapparent>4 AND Vapparent<6 OR distance<4) ORDER BY Vapparent")
    for id in lst:
        obj = StarObj(id)
        ConstelId = dbConstBnds.FindConstel(obj.Longitude(), obj.Latitude())
        if ConstelId == None:
            print "no constel for %s (%d) expected=%s" % (obj.name,obj.id,obj.ConstelId)
        elif (obj.ConstelId != ConstelId):
            if obj.ConstelId == None:
                print "set constel to %d for %s (id=%d)" % (ConstelId,obj.name,obj.id)
                n=WriteConstellation(obj.id, ConstelId)
            else:
                print "%s wrong constel %d != %d" % (obj.name,obj.ConstelId,ConstelId)


