# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

import sys,os,math
import string
#assert sys.platform=="win32",  "only to be run on windows PC"
from CelestData import dbStarCat
from ELPmpp02 import dbElpMain,dbElpPertub
from Constel import dbConstels,ConstelList
from AnyDB import dbConnect

toPhone = False
fromTxt = True
nodb = False
dropTbl=False
DestDbms = dbConnect('dbCATdat',toPhone)

if not DestDbms:
	if sys.platform=="win32":
	    if nodb:
	        DestDbms = None
	    else:
	        if toPhone:
	            import btDBclient,adodbapi
	            DestDbms=None
	            #ConStr = os.path.join(datPath, "ELP.db")
	            #ConStr = "ELP.db"
	            #DestDbms = btDBclient.connect(ConStr)
	            #dns='dsELPdat'
	            #SrcDbms = adodbapi.connect('Data Source=%s;' % (dns))
	        elif fromTxt:
	            import adodbapi
	            dbname='dsCATdat'
	            #dbname='dsELPdat'
	            DestDbms = adodbapi.connect('Data Source=%s;' % (dbname))
	            DestDbms.commit()
	        else:
	            DestDbms = None


class adoCelestData(dbStarCat):
    Fields=r'name,Ra,decl,distance,Vapparent,constellation' 
    def __init__(self, con):
        dbStarCat.__init__(self, con)
        #self.cur = DestDbms.cursor()

def btStarsCopy(Src='dsCATdat'):
    import btDBclient,adodbapi
    dbSrc = adoCelestData(adodbapi.connect('Data Source=%s;' % Src))
    #dbSrc.cond = "WHERE Vapparent<3 OR distance<5" 
    #dbSrc.Fields += ',id'
    dbDest = dbStarCat(btDBclient.connect('stars.db'))
    dbDest.db.cursor().execute("DELETE FROM stars WHERE id>0")
    dbDest.commit()
    #dbDest.Fields += ',id'
    #_CopyAnyDb(dbSrc,dbDest,"WHERE Vapparent<1")
    _CopyAnyDb(dbSrc,dbDest,"WHERE Vapparent<6.5 OR distance<4")
    dbDest.close()
    dbSrc.close()
    
def btConstelCopy(Src='dsCATdat'):
    import btDBclient,adodbapi
    dbSrc = dbConstels(adodbapi.connect('Data Source=%s;' % Src))
    #dbSrc.cond = "WHERE Vapparent<3 OR distance<5" 
    #dbSrc.Fields += ',id'
    if dropTbl:
        dbDest = dbConstels(btDBclient.connect('stars.db'))
        dbDest.DropTable()
        #dbDest.close()
    dbDest = dbConstels(btDBclient.connect('stars.db'))
    #dbDest.Fields += ',id'
    _CopyAnyDb(dbSrc,dbDest)
    dbDest.close()
    dbSrc.close()


catFile   = 'H:\\projects\\AstroFunc\\doc\\catalogs\\crossref\\catalog.dat'
tbl3File  = 'H:\\projects\\AstroFunc\\doc\\catalogs\\crossref\\table3.dat'
tycho1Cat = 'H:\\projects\\AstroFunc\\\doc\catalogs\\I-259 tycho2\\suppl_1.dat'
tycho2Cat = 'H:\\projects\\AstroFunc\\\doc\catalogs\\I-259 tycho2\\catalog.dat'
SAOcat    = 'H:\\projects\\AstroFunc\\doc\\catalogs\\I-131A SAO\\sao'
HIPcat    = 'H:\\projects\\AstroFunc\\doc\\catalogs\\hipparcos\\I-311\\hip2.dat'
fELPmain  = 'H:\\projects\\AstroFunc\\doc\\moon\\elp\\mpp02\\ELP_MAIN.S%d'
fELPpertub= 'H:\\projects\\AstroFunc\\doc\\moon\\elp\\mpp02\\ELP_PERT.S%d'
fConstelBnds = 'C:\\projects\\AstroFunc\\doc\\catalogs\\VI-49 constel_bound\\asu.tsv'

greekl = ('alf','bet','gam','del','eps','zet','eta','the','iot','kap','lam','mu.',
          'nu.','ksi','omi','pi.','rho','sig','tau','ups','phi','chi','psi','ome')
MagLim = 9

def toInt(s):
    s = s.strip(' |')
    if len(s)>0:
        return int(s)
    else:
        return None

def toFloat(s):
    s = s.strip(' |')
    if len(s)>0:
        return float(s)
    else:
        return None

def _CopyAnyDb(dbSrc,dbDest,cond=""):
    rec = dbSrc.FirstRecord(cond)
    cnt=0
    while not rec is None:
        if not None in rec:
            dbDest.InsertRecord(rec)
            cnt+=1
        rec = dbSrc.NextRecord()
    dbDest.commit()
    return cnt

class txtReader:
    """ read numbers from text file
    """
    def __init__(self, fname):
        self.f=open(fname,'r')
        self.nextln()
    def nextln(self):
        self.ln=self.f.readline()
        self.lnpos = 0
        return self.ln
    def EOF(self):
        return len(self.ln)==0
    def ReadItem(self, lnpos=-1, length=-1, allowed='+-.eED', wspace=' |\t', fortranE=''):
        if lnpos>=0:
            self.lnpos=lnpos
        pos = self.lnpos
        if pos>=len(self.ln):
            return None
        while self.ln[pos] in wspace:
            pos+=1
            if length>0:
                if pos-self.lnpos>=length:
                    break
        i=pos
        while self.ln[i].isdigit() or allowed is None or self.ln[i] in allowed:
            i+=1
            if length>0:
                if i-self.lnpos>=length:
                    break
            if self.ln[i]==fortranE: # 'D': # fortran uses D for exponent
                self.ln = self.ln[:i]+'E'+self.ln[i+1:]
                i+=2  # skip D plus sign of exponent
                allowed = ''
        if length>0:
            self.lnpos += length
        else:
            self.lnpos = i
        if i>pos:
            return self.ln[pos:i]
        else:
            return None
    def rdInt(self, lnpos=-1, len=-1):
        item = self.ReadItem(lnpos,len,allowed='+-')
        if item is None:
            return None
        else:
            return int(item)

    def rdFloat(self, lnpos=-1, len=-1):
        item = self.ReadItem(lnpos,len, fortranE='D')
        if item is None:
            return None
        else:
            return float(item)


def btELPcopy(Src='dsELPdat'):
    """ copy ELP moon data to bluetooth db
    """
    import btDBclient,adodbapi
    SrcCon = adodbapi.connect('Data Source=%s;' % Src)
    DstCon = btDBclient.connect('elp.db')
    dbSrc = dbElpPertub(SrcCon)
    dbSrc.cond = "WHERE S>0.1 OR S<-0.1 OR C>0.1 OR C<-0.1" 
    dbDest = dbElpPertub(DstCon)
    _CopyAnyDb(dbSrc,dbDest)

    dbSrc = dbElpMain(SrcCon)
    dbSrc.cond = "WHERE A>0.1 OR A<-0.1" 
    dbDest = dbElpMain(DstCon)
    _CopyAnyDb(dbSrc,dbDest)
    dbSrc.close()
    dbDest.close()

class ELPcopy:
    def __init__(self, dbms, idx):
        if idx in [1,2,3]:
            if nodb:
                db=None
            else:
                db = dbElpMain(dbms)
            self.ParseMain(db, fELPmain, idx)
        elif idx in [11,12,13]:
            if nodb:
                db=None
            else:
                db = dbElpPertub(dbms)
            self.ParsePertub(db, fELPpertub, idx)
    def ParseMain(self,db,fname,idx):
        f=txtReader(fname % idx)
        f.nextln()   # skip first line
        while not f.EOF():  #  s-1:e   (VUr,A,D,F,l,l_)
            D=f.rdInt()
            F=f.rdInt()
            l=f.rdInt()
            l_=f.rdInt()
            A=f.rdFloat()
            rec = (A,D,F,l,l_,idx)
            if nodb:
                print (rec)
            else:
                db.InsertRecord(rec)
                db.commit()
            f.nextln()
    def ParsePertub(self,db,fname,idx):
        idx = idx % 10
        f=txtReader(fname % idx)
        while not f.EOF():  #(VUr,S,C,D,F,l,l_,Me,Ve,T,Ma,Ju,Sa,Ur,Ne,zet)
            S=f.rdFloat(5,len=20)
            if S is None:
                tpow = f.rdInt(lnpos=40)
                f.nextln()
                continue
            C=f.rdFloat(len=20)
            D=f.rdInt(len=3)
            F=f.rdInt(len=3)
            l=f.rdInt(len=3)
            l_=f.rdInt(len=3)
            rec = [idx,tpow, S,C,D,F,l,l_]
            for i in range(9):
                rec.append(f.rdInt(len=3))
            if nodb:
                print (rec)
            else:
                db.InsertRecord(tuple(rec), Fields=db.KeyFld+','+db.Fields)
                db.commit()
            f.nextln()

    
class SAOCopy:
   def __init__(self,dbms):
      cur = dbms.cursor()
      cur.execute('SELECT MAX(Id) FROM starcat')
      t = cur.fetchone()
      self.maxId = t[0]
      self.ParseCat(cur)
      cur.close()
      dbms.commit()   
   def ParseCat(self,cur):
      f=open(SAOcat,'r')
      for ln in f:   #  s-1:e
          self.SAO = toInt(ln[:6])
          self.DM = toInt(ln[109:114])
          self.HD = toInt(ln[117:123])
          self.Ra = toFloat(ln[183:193])*180/math.pi
          self.Dec= toFloat(ln[193:204])*180/math.pi
          #t = (self.SAO,self.DM,self.HD,self.Ra*0.99,self.Ra*1.01,self.Dec*0.99,self.Dec*1.01)
          t = (self.SAO,self.HD)
          if not (None in t):
              cur.execute('UPDATE crossref AS c SET c.SAO=%d ' \
                          'WHERE (c.HD=%d) ' \
                          'AND c.SAO IS NULL' % t)
                          #'AND (s.Ra BETWEEN %.8f AND %.8f) AND (s.decl BETWEEN %.8f AND %.8f) ' \
              if cur.rowcount==0:
                  print ('unknown',t)
          else:
              print ('bad',t)
          
          
class HIPcopy:
   def __init__(self, dbms):
      cur = dbms.cursor()
      cur.execute('SELECT MAX(Id) FROM starcat')
      t = cur.fetchone()
      self.maxId = t[0]
      cur.close()
      self.ParseCat(dbms)
      dbms.commit()   
    
   def ParseCat(self, dbms):
      f=open(HIPcat,'r')
      cur = dbms.cursor()
      for ln in f:   #  s-1:e
          self.HIP = toInt(ln[:7])
          self.Ra  = toFloat(ln[15:29])*180/math.pi
          self.Decl= toFloat(ln[29:43])*180/math.pi
          self.Parallax = toFloat(ln[43:51])
          t = (self.Ra,self.Decl,self.Parallax,self.HIP)
          if not None in t:
              cur.execute('UPDATE starcat AS s,crossref AS c SET ' \
                          'Ra=%.10f,decl=%.10f,Parallax=%.2f ' \
                          'WHERE c.HIP=%d AND s.id=c.starId' % t)
              if cur.rowcount<=0:
                  print ('unk',t)
              dbms.commit()
      cur.close()
        


class ConstelBndsCopy:
    def __init__(self, dbms):
        cur = dbms.cursor()
        cur.execute('SELECT MAX(Id) FROM ConstelBounds')
        t = cur.fetchone()
        self.maxId = t[0]
        cur.close()
        self.Constels = ConstelList("ORDER BY Id")
        self.ParseCat(dbms,fConstelBnds)
        dbms.commit()   

    def ParseCat(self,db,fname):
        f=txtReader(fname)
        cur = db.cursor()
        while not f.EOF() and \
              (f.ln.startswith(('#','---','"','RA')) or len(f.ln.strip())==0) :
            f.nextln()
        idx=0
        pabrev=''
        while not f.EOF():
            RaDeg = f.rdInt()
            RaMin = f.rdInt()
            RaSec = f.rdFloat()
            DEdeg = f.rdFloat()
            abrev = f.ReadItem(length=4,allowed=None)
            if abrev==pabrev:
                idx+=1
            else:
                idx=0
            pabrev=abrev
            #id = self.Constels.index(abrev)
            if nodb:
                print (rec)
            elif RaDeg and DEdeg:
                RaDeg = 15*(RaDeg + RaMin/60.0 + RaSec/3600.0)
                rec = (idx,RaDeg,DEdeg)
                cur.execute("INSERT INTO ConstelBounds " +
                    " (idx,Ra,Decl,id) " +
                    " SELECT %d,%.8f,%.8f,id " % rec +
                    " FROM Constellations WHERE abrev LIKE '%s' " % abrev )
                db.commit()
            f.nextln()



class Tycho1Copy:
    def __init__(self, dbms):
        cur = dbms.cursor()
        cur.execute('SELECT MAX(Id) FROM starcat')
        t = cur.fetchone()
        self.maxId = t[0]
        cur.close()
        #cur.close()
        self.ParseCat(dbms,tycho1Cat)
        dbms.commit()   

    def ParseCat(self,db,fname):
        f=txtReader(fname)
        #f.nextln()   # skip first line
        dEpoch = 2000.0-1991.5
        deg2mas = 3600000.0
        deg2rad = math.pi/180.0
        cur = db.cursor()
        while not f.EOF():  # 
            TYC1  =f.rdInt()
            TYC2  =f.rdInt()
            TYC3  =f.rdInt()
            fl    = f.ReadItem(allowed='HT')
            RAdeg = f.rdFloat()
            DEdeg = f.rdFloat()
            pmRA  =f.rdFloat(len=8)
            pmDE  =f.rdFloat(len=8)
            if pmRA and pmDE:
                RAdeg = RAdeg + pmRA/deg2mas * dEpoch/math.cos(DEdeg*deg2rad)
                DEdeg = DEdeg + pmDE/deg2mas * dEpoch
            e_RA  =f.rdFloat(len=6)
            e_DE  =f.rdFloat(len=6)
            e_pmRA=f.rdFloat(len=6)
            e_pmDE=f.rdFloat(len=6)
            mflag =f.ReadItem(length=2,allowed=' BVH')
            BT    =f.rdFloat(len=7)
            e_BT  =f.rdFloat(len=6)  # e_BT
            VT    =f.rdFloat(len=7)
            e_VT  =f.rdFloat(len=6)  # e_VT
            prox  =f.rdInt(len=4)
            TYC   =f.ReadItem(length=2,allowed=' T')
            HIP   =f.rdInt()
            CCDM  =f.ReadItem(length=1,allowed='ABCDEFGHIJ')
            insert = False
            if nodb:
                print (rec)
            elif pmRA and pmDE and RAdeg and DEdeg and VT:
                if BT:
                    BT= "%.3f" % BT
                else:
                    BT='NULL'
                if HIP:
                    #if CCDM and CCDM<>'A':
                    #    pass
                    if VT<MagLim:
                        t = (BT,VT,pmRA,pmDE,RAdeg,DEdeg,TYC1,TYC2,TYC3,HIP)
                        if not CCDM or CCDM=='A':
                            cur.execute('UPDATE starcat AS s,crossref AS c SET BT=%s,VT=%.3f,pmRa=%.1f,pmdecl=%.1f' \
                                      ',mRa=%.8f,mdecl=%.8f,c.TYC1=%d,c.TYC2=%d,c.TYC3=%d,orgCatalog=13 ' \
                                      'WHERE c.HIP=%d AND s.id=c.starId AND orgCatalog<>11' % t)
                        else:
                            cur.execute('UPDATE starcat AS s,crossref AS c SET BT=%s,VT=%.3f,pmRa=%.1f,pmdecl=%.1f' \
                                ',mRa=%.8f,mdecl=%.8f,orgCatalog=13 ' \
                                'WHERE c.HIP=%d AND c.TYC1=%d AND c.TYC2=%d AND c.TYC3=%d AND s.id=c.starId' % t)
                        if cur.rowcount<=0:
                            cur.execute('UPDATE starcat AS s,crossref AS c SET BT=%s,VT=%.3f,pmRa=%.1f,pmdecl=%.1f' \
                                ',mRa=%.8f,mdecl=%.8f,orgCatalog=13,c.HIP=%d ' \
                                'WHERE c.TYC1=%d AND c.TYC2=%d AND c.TYC3=%d AND s.id=c.starId' % t)
                        if cur.rowcount<=0:
                            insert = True
                        else:
                            db.commit()
                elif VT<MagLim:
                    t = (BT,VT,pmRA,pmDE,RAdeg,DEdeg,TYC1,TYC2,TYC3)
                    cur.execute('UPDATE starcat AS s,crossref AS c SET BT=%.3f,VT=%.3f,pmRa=%.1f,pmdecl=%.1f' \
                              ',mRa=%.8f,mdecl=%.8f,orgCatalog=13 ' \
                              'WHERE s.id=c.starId AND c.TYC1=%d AND c.TYC2=%d AND c.TYC3=%d' % t)
                    if cur.rowcount<=0:
                        insert = True
                    else:
                        db.commit()
                    
                if insert:
                    self.maxId+=1
                    t = (BT,VT,pmRA,pmDE,RAdeg,DEdeg,self.maxId)
                    cur.execute('INSERT INTO starcat (BT,VT,pmRa,pmdecl,mRa,mdecl,Id,orgCatalog) ' +
                       'VALUES (%s,%.3f,%.1f,%.1f,%.8f,%.8f,%d,13)' % t)
                    t = (self.maxId,TYC1,TYC2,TYC3)
                    cur.execute('INSERT INTO crossref (starId,TYC1,TYC2,TYC3) ' \
                              'VALUES (%d,%d,%d,%d)' % t)
                    if HIP:
                       cur.execute('UPDATE crossref SET HIP=%d WHERE starId=%d' %
                                  (HIP,self.maxId))
                    db.commit()
            f.nextln()


class Tycho2Copy:
   def __init__(self, dbms):
      cur = dbms.cursor()
      cur.execute('SELECT MAX(Id) FROM starcat')
      t = cur.fetchone()
      self.maxId = t[0]
      #cur.close()
      self.ParseCat(cur,dbms)
      cur.close()
      dbms.commit()   

   def ParseCat(self,cur,dbms=None):
      f=open(tycho2Cat,'r')
      for ln in f:   #  s-1:e
          self.HIP = toInt(ln[142:148])
          self.BT  = toFloat(ln[110:117]) # blue magn
          self.VT  = toFloat(ln[123:130])
          self.pmRa = toFloat(ln[41:49])
          self.pmDe = toFloat(ln[49:57])
          self.mRa  = toFloat(ln[15:28])
          self.mDe  = toFloat(ln[28:41])
          self.TYC1 = toInt(ln[:4])
          self.TYC2 = toInt(ln[5:10])
          self.TYC3 = toInt(ln[11:13])
          insert = self.HIP is None
          if (not insert) and self.VT<MagLim:
              t = (self.BT,self.VT,self.pmRa,self.pmDe,self.mRa,self.mDe,
                           self.TYC1,self.TYC2,self.TYC3,self.HIP)
              if not None in t:
                  cur.execute('UPDATE starcat AS s,crossref AS c SET BT=%.3f,VT=%.3f,pmRa=%.1f,pmdecl=%.1f' \
                              ',mRa=%.8f,mdecl=%.8f,c.TYC1=%d,c.TYC2=%d,c.TYC3=%d ' \
                              'WHERE c.HIP=%d AND s.id=c.starId' % t)
                  if cur.rowcount<=0:
                      insert = True
              else:
                  print ('unk',t)
          if  self.VT<MagLim and (insert):
              self.maxId+=1
              t = (self.BT,self.VT,self.pmRa,self.pmDe,self.mRa,self.mDe,self.maxId)
              if not None in t:
                  cur.execute('INSERT INTO starcat (BT,VT,pmRa,pmdecl,mRa,mdecl,Id) ' +
                      'VALUES (%.3f,%.3f,%.1f,%.1f,%.8f,%.8f,%d)' % t)
              else:
                  t = (self.BT,self.VT,self.mRa,self.mDe,self.maxId)
                  if not None in t:
                     cur.execute('INSERT INTO starcat (BT,VT,mRa,mdecl,Id) ' +
                         'VALUES (%.3f,%.3f,%.8f,%.8f,%d)' % t)
              if None in t:
                  print ('bad',t,cur.rowcount)
              else:
                  t = (self.maxId,self.TYC1,self.TYC2,self.TYC3)
                  cur.execute('INSERT INTO crossref (starId,TYC1,TYC2,TYC3) ' \
                              'VALUES (%d,%d,%d,%d)' % t)
                  if (self.HIP is not None):
                     cur.execute('UPDATE crossref SET HIP=%d WHERE starId=%d' %
                                  (self.HIP,self.maxId))
          if not dbms is None:
              dbms.commit()
       

class CrossCatCopy:
   def __init__(self, dbms):
      cur = dbms.cursor()

      #cur.close()
      self.ParseTbl3(cur)
      self.ParseCat(cur)

      cur.close()
      dbms.commit()   

   def ParseCat(self, cur):
      self.id=1000
      f=open(catFile,'r')
      for ln in f:
         self.id=self.id+1
         self.HD = int(ln[:6])
         self.DM = ln[7:19]
         self.GC = ln[20:25]
         self.HR = ln[26:30]
         self.HIP= ln[31:37]
         self.Ra = float(ln[38:40])*15.0
         self.Ra += float(ln[40:42])/60*15
         self.Ra += float(ln[42:47])/3600*15
         self.DE = float(ln[49:51])
         self.DE += float(ln[51:53])/60
         self.DE += float(ln[53:57])/3600
         if ln[48]=='-':
             self.DE = -self.DE
         self.Vmag = ln[58:63]
         self.Flamsteed = ln[64:67].strip()
         self.Bayer = ln[68:71].strip()
         self.BayerSup = ln[71:73]
         self.Constel  = ln[74:77]
         self.CatToDb(cur, False)
      f.close()

   def ParseTbl3(self, cur):
      f=open(tbl3File,'r')
      for ln in f:
         self.HD = int(ln[:6])
         self.name = ln[21:76].strip()
         refs = ln[77:100].strip().split(',')
         if '19' in refs:
            cur.execute("UPDATE starcat AS s,CrossRef AS cr SET s.name='%s' WHERE s.id=cr.starid " \
                        "AND cr.HD=%d " % (self.name, self.HD))
      f.close()
         
        

   def CatToDb(self, cur, new=True):
      if new:
          cur.execute("INSERT INTO stars (id, Ra, decl) VALUES (%d, %.9f, %.9f)" \
                       % (self.id, self.Ra, self.DE ))
          cur.execute("INSERT INTO CrossRef (starid) VALUES (%d)" % (i))

      if len(self.Vmag.strip())>0:
          cur.execute("UPDATE Stars SET magnitude=%.3f WHERE id=%d"
                      % (float(self.Vmag), self.id))

      cur.execute("UPDATE stars SET Ra=%.9f, decl=%.9f WHERE id=%d" %
                  (self.Ra, self.DE, self.id))
      cur.execute(
         "UPDATE stars AS s,constellations AS c SET constellation=c.id" \
         " WHERE s.id=%d AND abrev='%s'" % (self.id, self.Constel))

      cur.execute("UPDATE CrossRef SET HD=%d WHERE starid=%d" % (self.HD, self.id))
      if len(self.HR.strip())>0:
          cur.execute("UPDATE CrossRef SET HR=%d WHERE starid=%d" % (int(self.HR), self.id))
      if len(self.HIP.strip())>0:
          cur.execute("UPDATE CrossRef SET HIP=%d WHERE starid=%d" % (int(self.HIP), self.id))

      if len(self.Bayer)>0:
         i=-1
         if self.Bayer in greekl:
             i=list(greekl).index(self.Bayer)+1
         elif self.Bayer[0] in string.ascii_lowercase:
             i=string.ascii_lowercase.index(self.Bayer[0]) + 25
         elif self.Bayer[0] in string.ascii_uppercase:
             i=string.ascii_uppercase.index(self.Bayer[0]) + 51
         if i>0:
             cur.execute("UPDATE CrossRef SET Bayer=%d WHERE starid=%d"
                         % (i, self.id))

      if len(self.Flamsteed)>0:
         cur.execute("UPDATE CrossRef SET Flamsteed=%d WHERE starid=%d"
                         % (int(self.Flamsteed), self.id))

if __name__ == '__main__':
    import beaupy
    prgs = \
        (
          ('CrossCatCopy', (CrossCatCopy, [DestDbms])),
          ('Tycho1Copy', (Tycho1Copy, [DestDbms])),
          ('Tycho2Copy', (Tycho2Copy, [DestDbms])),
          ('SAOCopy', (SAOCopy, [DestDbms])),
          ('HIPcopy', (HIPcopy, [DestDbms])),
          ('ELPcopy Vmain', (ELPcopy, [DestDbms,1])),
          ('ELPcopy Umain', (ELPcopy, [DestDbms,2])),
          ('ELPcopy rmain', (ELPcopy, [DestDbms,3])),
          ('ELPcopy Vpertub', (ELPcopy, [DestDbms,11])),
          ('ELPcopy Upertub', (ELPcopy, [DestDbms,12])),
          ('ELPcopy rpertub', (ELPcopy, [DestDbms,13])),
          ('btELPcopy', (btELPcopy, [])),
          ('btStarsCopy', (btStarsCopy,[])),
          ('ConstelBndsCopy', (ConstelBndsCopy,[DestDbms])),
          ('btConstelCopy', (btConstelCopy,[]))
        )
    prg = beaupy.select([r[0] for r in prgs], return_index=True)
    #for i in range(len(prgs)):
    #    print ("%d.%s" % (i,prgs[i][0]))
    #prg = int(raw_input("%d..%d? " % (0,len(prgs)-1)))
    prgs[prg][1][0](*prgs[prg][1][1])  # calling the choice
 