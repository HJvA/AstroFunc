# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 
# first attempt to implement 'www.python.org/dev/peps/pep-0249/' for S60

import os
import e32db,e32,appuifw


def connect(ConStr):
    dbms = _dbS60()
    dbms._connect(ConStr)
    return dbms

class _dbS60:
    """ implements partially DB-API 2.0 (PEP 249)
        for a symbian_s60 phone running python
    """
    def __init__(self):
        self.curs = None
        self.transaction=0
        self.dbms = None
        self.description= [None for i in range(7)] #(name,type_code,display_size,internal_size,precision,scale,null_ok
    def __del__(self):
        if not self.dbms is None:
            self.dbms.close()
    def _connect(self, dbPath):
        """ create directory, database if any do not exist
        """
        self.commit()
        self.dbms = e32db.Dbms()
        dir = os.path.dirname(dbPath)
        if not os.path.exists(dir):
            os.mkdir(dir)
            print "dir created:"+dir
        try:
            self.dbms.open(unicode(dbPath))
        except:
            self.dbms.create(unicode(dbPath))
            self.dbms.open(unicode(dbPath))

    def cursor(self):
        #if self.curs is None:
        self.curs= _CursorS60(self.dbms)
        return self.curs
    def begin(self):
        self.transaction +=1
        self.dbms.begin()
    def commit(self):
        if self.transaction>0:
            self.dbms.commit()
            self.transaction = 0
    def rollback(self):
        if self.transaction>0:
            self.dbms.rollback()
            self.transaction = 0
    def close(self):
        """ close connection
            with implicit rollback
        """
        if not self.curs is None:
            self.curs.close()
            self.curs = None
        if not self.dbms is None:
            self.dbms.close()

class _CursorS60:
    def __init__(self, dbms):
        #assert isinstance(dbms, e32db.Dbms), "illegal class for db"
        self.dbms = dbms
        self.dbv=None
        self.rowcount=-1
        self.arraysize=1
        self.rownumber=None
    def execute(self, sql):
        self.rownumber=0  # next record to be fetched
        try:
            if sql.strip().lower().startswith('select'):
                if self.dbv is None:
                    self.dbv = e32db.Db_view()
                self.dbv.prepare(self.dbms, unicode(sql))
                self.rowcount=self.dbv.count_line()
                if self.rowcount is None or self.rowcount<0:
                    self.rowcount=0
                if self.rowcount>0:
                    self.dbv.first_line()
            else:
                self.rowcount = self.dbms.execute(unicode(sql))
                self.dbv = None
        except:
            self.rowcount=-2  # used to detect tbl not found in btClient
            self.dbv = None
            self.rownumber=None

    def fetchone(self):
        row = []
        if (self.rownumber is None) or (self.dbv is None):
            raise ReferenceError("first execute select, rowcount=%d" % self.rowcount)
        if self.rowcount==0:
            return () # no records found
        if self.rownumber>=self.rowcount:
            raise IndexError
        self.dbv.get_line()
        self.rownumber +=1
        for i in range(self.dbv.col_count()):
            row.append(self.dbv.col(i+1))
        if self.rownumber<self.rowcount:
            self.dbv.next_line()
        return tuple(row)
    def fetchmany(self, size=-1):
        if size<0:
            cnt=self.arraysize
        else:
            cnt=size
        if cnt>self.rowcount-self.rownumber:
            cnt=self.rowcount-self.rownumber
        rows=[]
        for i in range(cnt):
            rows.append(self.fetchone())
        return rows
    def fetchall(self):
        return self.fetchmany(self.rowcount-self.rownumber)
    
    def scroll (self, value, mode='relative'):
        if mode=='relative':
            n = value
        elif mode=='absolute':
            n = value-self.rownumber
        else:
            raise ValueError
        if n+self.rownumber>self.rowcount or n+self.rownumber<0:
            raise IndexError
        if n<0:
            self.dbv.first_line()
            n = self.rownumber+n
            self.rownumber=0
        if n>0:
            for i in range(n):
                self.dbv.next_line()
                self.rownumber+=1
                
    def close(self):
        """ Close the cursor now (rather than whenever __del__ is
            called).  The cursor will be unusable from this point
            forward
        """
        pass  # self.dbv.close()


def Date(year,month,day):
    "This function constructs an object holding a date value. "
    return None

def Time(hour,minute,second):
    "This function constructs an object holding a time value. "
    return None

def Timestamp(year,month,day,hour,minute,second):
    "This function constructs an object holding a time stamp value. "
    return None

def DateFromTicks(ticks):
    """This function constructs an object holding a date value from the given ticks value
    (number of seconds since the epoch; see the documentation of the standard Python time module for details). """
    return None #time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    """This function constructs an object holding a time value from the given ticks value
    (number of seconds since the epoch; see the documentation of the standard Python time module for details). """
    return None # time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    """This function constructs an object holding a time stamp value from the given
    ticks value (number of seconds since the epoch;
    see the documentation of the standard Python time module for details). """
    return None #time.localtime(ticks)[:6])

def Binary(aString):
    """This function constructs an object capable of holding a binary (long) string value. """
    return buffer(aString)

STRING = 'VARCHAR'
NUMBER = 'FLOAT'
DATETIME = ''
BINARY = None



if __name__ == '__main__':
    pass
