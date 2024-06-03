# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 

#from AstroTypes import CelestialObj,datPath
import sys,os

def dbConnect(dbFname, atPhone = False, datPath=r"HastroDat"):
    wildcard='*'
    if sys.platform=="win32":
        if atPhone:
            import btDBclient
            #ConStr = os.path.join(datPath, "Stars.db")
            ConStr = dbFname # "stars.db"
            dbms = btDBclient.connect(ConStr)
        else:
            import adodbapi
            dsn=dbFname #'dsCATdat'
            provider='MSDASQL'  # ODBC for OLEDB
            dbms = adodbapi.connect('Data Source=%s;Provider=%s;'% (dsn,provider))
            wildcard='%%'
    elif sys.platform=="symbian_s60":
        import dbS60
        if '--dat' in sys.argv:
            datPath = sys.argv[sys.argv.index('--dat')+1]
        ConStr = os.path.join(datPath, dbFname) #r'stars.db')
        dbms = dbS60.connect(ConStr)
    elif sys.platform=="linux":
        from sqlite3 import connect,OperationalError
        store = os.path.join(datPath, dbFname) # r'stars.db')
        store = os.path.expanduser(store) 
        if not os.path.isabs(store):
            store = os.path.abspath(store)
        if not os.path.exists(store):  # => create database
            breakpoint()
            dbms=connect(store, check_same_thread=False)
            if dbms:
                dbms=dbCreate(dbms)
            else:
                print("Unable to create {}".format(store))
        else:
            dbms=connect(store, check_same_thread=False)
    return dbms

def dbCreate(con):
		#logger.info("creating sqlStore in %s" % fname)
		#con=connect(store, check_same_thread=False)
		#con=dbConnect(fname)	# will create file
		with con:
			cur = con.cursor()
			"""
			cur.execute('CREATE TABLE logdat( '
				'ddJulian REAL	NOT NULL,'
				'quantity INT  NOT NULL,'
				'numval	REAL,'
				'strval  TEXT);' )
			cur.execute('CREATE INDEX ld1 ON logdat(ddJulian,quantity);')
			cur.execute('CREATE TABLE quantities( '
				'ID	 INT PRIMARY KEY NOT NULL,'
				"name  TEXT NOT NULL,"
				"source TEXT,"
				"type  INT,"
				"active INT DEFAULT 1,"
				"firstseen REAL);")
			cur.execute("CREATE TABLE quantitytypes(ID INT PRIMARY KEY NOT NULL, name TEXT NOT NULL, unit TEXT);")
			"""
			cur.close()
		return con


class AnyDB:
    """ interface to an arbitrary database table.
        abstract class i.e. not to be instantiated directly
    """
    # virtual members, to be overriden (here just dummy examples)
    dbTbl         ="dbTbl"
    Fields        ="name,fld1,fld2"  # first fld must be name to pick from
    KeyFld        ="id"
    NameFld       ="name"
    sqlCreateTable="CREATE TABLE dbTbl (id INTEGER, fld1 VARCHAR, fld2 FLOAT)"
    sqlInsert     ="INSERT INTO dbTbl (%s) VALUES ('%s',%f,%d)"
    sqlUpdate     ="UPDATE dbTbl SET fld1='%s',fld2=%f WHERE id=%d"
    # real members, %% to be filled by virtual members
    sqlDelete     ="DELETE FROM %s WHERE %s LIKE '%s'"
    sqlSelect     ="SELECT %s FROM %s %s"
    sqlMaxId      ="SELECT %s FROM %s ORDER BY %s DESC"
    sqlSelNames   ="SELECT %s FROM %s %s"
    sqlGetId      ="SELECT %s FROM %s WHERE %s LIKE '%s'"

    def __init__(self, dbms):
        """ create database and or table if not existant
        """
        # self.db = dbms.connect(ConStr)
        self.db = dbms
        self.AtCurs = None
        self.cond = ""
        self.MaxId=5 # existing tbl, no records
        with dbms:
            cur = dbms.cursor()
            try:  # test presence of table
                cur.execute(self.sqlMaxId % (self.KeyFld,self.dbTbl,self.KeyFld))
                if cur.rowcount==-2:
                    raise RuntimeError( "remote tbl not found")
            except:
                cur.execute(self.sqlCreateTable)
            self.MaxId=10 # table created
            if self.MaxId<10:
                rec = cur.fetchone()
                if not rec is None:
                    if len(rec)>0:
                        self.MaxId=rec[0]  # existing records
            dbms.commit()
    def DropTable(self):
        cur = self.db.cursor()
        cur.execute("DROP TABLE %s" % self.dbTbl)
        cur.close()
    def GetNames(self, cond=""):
        """ Get list of NameFld of all records
        """
        if cond is None:
            cond=self.cond
        cur = self.db.cursor()
        cur.execute(f"select * from {self.dbTbl}")
        fields = [column[0] for column in cur.description]
        return fields
        cur.execute(self.sqlSelNames % (self.NameFld, self.dbTbl, cond))
        lst = cur.fetchall()
        cur.close()
        #return lst
        return [unicode(elm[0]) for elm in lst]
    def GetNameIdx(self):
        """ Get index of NameFld in Fields list
        """
        return self.Fields.split(',').index(self.NameFld)
    '''
    def ReloadRecord(self):
        """ cause recordset to be reloaded
        """
        self.AtCurs = None
    def GotoRecord(self, jump, mode='relative'):
        """ create cursor (if it did not exist) and
            scroll cursor to a particular record
        """
        if self.AtCurs is None:
            #self.db.commit()
            self.AtCurs = self.db.cursor()
            self.AtCurs.execute(self.sqlSelect % \
                                (self.Fields+','+self.KeyFld,self.dbTbl,self.cond))
            rownr=0
            if not vars(self.AtCurs).has_key('rownumber'):
                self.AtCurs.rownumber=None # will be overruled by driver (not adodbapi)
        else:
            rownr = self.AtCurs.rownumber
        if mode=='absolute':
            if self.AtCurs.rownumber is None:  # i.e. adodbapi
                if jump==0:
                    if rownr!=0:
                        self.AtCurs.execute(self.sqlSelect % \
                                        (self.Fields+','+self.KeyFld,self.dbTbl,self.cond))
                else:
                    raise NotSupportedErrors("not supported")
            else:
                if jump!=rownr:
                    self.AtCurs.scroll(jump,mode)  # first record not supported by all
        elif mode=='relative':
            if jump!=0:
                self.AtCurs.scroll(jump,mode)  # not supported by all
    def FirstRecord(self, cond=None):
        if not cond is None:
            self.cond=cond
            self.AtCurs = None
        self.GotoRecord(0,'absolute')
        return self.AtCurs.fetchone()
    def NextRecord(self):
        if self.AtCurs is None:
            return self.FirstRecord()
        else:
            try:
                return self.AtCurs.fetchone()
            except IndexError:
                return None
    def PrevRecord(self):
        self.GotoRecord(-2)
        return self.AtCurs.fetchone()
    '''
    def FirstRecord(self, cond=None):
        self.AtCurs =None
        self.cond = cond
        return self.NextRecord()
    def NextRecord(self):
        if self.AtCurs is None:
            #self.db.commit()
            self.AtCurs = self.db.cursor()
            self.AtCurs.execute(self.sqlSelect % (self.Fields+','+self.KeyFld, self.dbTbl, self.cond))
        try:
            return self.AtCurs.fetchone()
        except IndexError:
            return None
    def GetRecords(self, numb=1, cond="", sql=None):
        if not cond is None:
            self.cond=cond
        cur = self.db.cursor()
        if sql is None:
            sql=self.sqlSelect % (self.Fields+','+self.KeyFld,self.dbTbl,self.cond)
        cur.execute(sql)
        if numb:
            recs = cur.fetchmany(numb)
        else:
            recs = cur.fetchall()
        cur.close()  # hjva 081227
        return recs
    def SqlExecute(self, sql):
        cur = self.db.cursor()
        cur.execute(sql)
        return cur.rowcount
    def InsertRecord(self, Values, Fields=None):
        lst = list(Values)
        if Fields is None:
            lst[:0] = [self.Fields+','+self.KeyFld]
        else:
            lst[:0] = Fields
        return self.SqlExecute(self.sqlInsert % tuple(lst))
        cur = self.db.cursor()
        cur.execute(self.sqlInsert % tuple(lst))
        return cur.rowcount
    def CheckRecord(self, Record):
        """ check presence of nameFld in all nameflds of database table
            if not : insert new record with name
            if so : update record having name
        """
        cur = self.db.cursor()
        Nidx = self.GetNameIdx()
        cur.execute(self.sqlGetId % \
                    (self.KeyFld,self.dbTbl,self.NameFld,Record[Nidx]))  # check presence of NameFld
        rwcnt = cur.rowcount
        values = list(Record)
        lst = None
        if cur.rowcount<0: # rowcount not supported for some dbms
            lst = cur.fetchone()
            if lst is None:
                rwcnt=0
            elif len(lst)==0:
                rwcnt=0
            else:
                rwcnt=1
        if rwcnt==0:   # INSERT
            self.MaxId+=1
            values.append(self.MaxId)   # key at end
            values[:0] = [self.Fields+','+self.KeyFld]  # insert at start
            cur.execute(self.sqlInsert % tuple(values))
        elif rwcnt==1:  # UPDATE
            if lst is None:
                lst = cur.fetchone()
            values.append(lst[0])
            cur.execute(self.sqlUpdate % tuple(values))
        else:
            assert (0,"names must be unique")
    def DeleteRecord(self, Name):
        """ delete record having name from table
        """
        cur = self.db.cursor()
        cur.execute(self.sqlDelete % (self.dbTbl,self.NameFld,Name))
    def RecordCount(self):
        #self.GotoRecord(0,'absolute')
        return self.AtCurs.rowcount
    def close(self):
        self.db.commit()
        self.db.close()  # will also close connection
    def commit(self):
        self.db.commit()

if __name__ == '__main__':
	sys.path.append('.')
	import submod.pyCommon.tls as tls
	logger = tls.get_logger(__file__)

	dbms = dbConnect('stars.db')
	db = AnyDB(dbms)
	logger.info("mxId:{} nms:{}".format(db.MaxId,db.GetNames()))
	db.close()
else:
	import logging
	logger = logging.getLogger(__name__)
        
