# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com

import sys,os
from AstroTypes import pn,datPath
from AnyDB import AnyDB

class dbOscElm(AnyDB):
    """ define database structure by overriding virtual members from AnyDB
    """
    dbTbl         ="OscElm"   # name of a table defined in ConStr
    NameFld       =None
    Fields        ="coeff,idx,elm"    # must map to EditFlds, Note: KeyFld not included
    EditFlds      = 'coefficient,order'  # long verbose names, must map to database Fields
    sqlCreateTable="CREATE TABLE OscElm (id INTEGER, elm INTEGER,idx INTEGER, coeff FLOAT)" 
    sqlInsert     ="INSERT INTO OscElm (%s) VALUES (%#.20e,%d,%d,%d)"
    sqlUpdate     ="UPDATE OscElm SET coeff=%#.20e WHERE idx=%d, elm=%d AND id=%d"
    def __init__(self):
        if sys.platform=="win32":
            import adodbapi   # http://adodbapi.sourceforge.net/
            ConStr = 'Data Source=%s;' %   ('dsOscElm',)
            dbms = adodbapi.connect(ConStr)
        else:   # symbian_S60 
            import dbS60
            ConStr = os.path.join(datPath, "SolSyst.db")
            dbms = dbS60.connect(ConStr)
        AnyDB.__init__(self, dbms)

    def write_oscelm(self, pnPlanet, KepDef, pnOrg=0):
        for i in range(len(KepDef)): # all oscelms
            for c in range(len(KepDef[i])):  # all coeff
                self.InsertRecord((KepDef[i][c],c,i,pnPlanet+100*pnOrg))
            self.commit()
    def read_oscelm(self, pnPlanet, pnOrg=0):
        KepDef=[]
        rec=self.FirstRecord("WHERE id=%d ORDER BY elm,idx" % (pnPlanet+100*pnOrg))
        while rec:
            polyn=[]
            elm=rec[2]
            while rec and elm==rec[2]:
                polyn.append(rec[0])
                rec=self.NextRecord()
            KepDef.append(tuple(polyn))
        return tuple(KepDef)
        cm = AstTime.cyTJ2000()/10 
        self.t = [1,cm]
        for i in range(1):
            self.t.append(cm * self.t[-1])

if globals().has_key('dbOscElmObj'):
    dbOscElmObj.close()
    del (dbOscElmObj)
dbOscElmObj = dbOscElm()


if __name__ == '__main__':
    bodies = (pn.Earth, pn.Jupiter)
    for body in bodies:
        print pn.nmPlanet(body)
        elms =dbOscElmObj.read_oscelm(body)
        for elm in elms:
            print "%s" % elm.__repr__()
