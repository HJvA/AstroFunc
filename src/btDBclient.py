# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com
"""
Communicate with btDBserver to do manipulations on a symbian database
Client for btDBserver which is to be run on a S60 phone
"""

import sys,os,marshal
assert sys.platform!="symbian_S60", "only to be run on win32 PC, not %s" % sys.platform
import bluetooth  #pyBlues
# http://pybluez.googlecode.com/svn/www/docs-0.7/index.html

ack = '\n'

class btClient:
    """
    Base class for 'pyBlues' bluetooth communication to a server (on a S60 phone)
    """
    def __init__(self, service='S60db', device='hjvaTel'):
        """
        Connect to server using bluetooth
        @param service: the name of the advertised service
        @type  service: string
        """
        # For quicker startup, enter here the address and port to connect to.
        host='' #('00:1C:9A:6D:FD:B5',1)
        name=None
        if not host:
            devices = bluetooth.discover_devices(lookup_names = True)
            for address,devname in devices:
                print "  %s - %s" % (address, devname)
                if devname==device:
                    break

            #services = bluetooth.find_service(name=service, address = address )
            services = bluetooth.find_service(address = address )
            for srv in services:
                print "host='%s', name='%s', port=%d, provider='%s', protocol='%s',descr='%s'" % \
                      (srv["host"],srv["name"],srv["port"],srv["provider"],srv["protocol"],srv["description"])
                if srv["name"]==service:
                    match = srv
                    name = match["name"]
                    host = (match["host"],match["port"])
                    break
            #assert name==service, "unable to find %s on %s" % (service, devname)
            if not name==service:
                name=service
                host = (services[0]["host"],5)
                    
        self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.sock.connect(host)
        self.ExitFlag = False

    def readline(self,n=None):
        """
        Read a line of text from bluetooth socket
        @param n: max number of characters in the line
        @return: line of text including terminators
        """
        buffer=[]
        while 1:
            ch=self.sock.recv(1)
            if ch == '\n' or ch == '\r':   # return
                buffer.append('\n')
                break
            buffer.append(ch)
            if n and len(buffer)>=n:
                break
        return ''.join(buffer)


    def _test(self, title):
        while not self.ExitFlag:
            data = raw_input()
            if len(data) == 0: break
            self.sock.send(data+'\n')
            data = self.readline(100)
            print data
            
    def close(self):
        """ close bluetooth socket
            (so connection can not be reused)
        """
        if not self.sock is None:
            self.sock.close()
            self.sock = None

def connect(ConStr):
    """
    Open database connection from PC over bluetooth connection to a running btDBserver program on a symbian_S60 phone
    Path and database will be created if not existant
    @param ConStr : complete path on S60 phone of a database file (.db extension)
    """
    dbms = btDBclient()
    dbms._connect(ConStr)
    return dbms

class btDBclient(btClient):
    """ Looks from PC to S60 database following DB-API 2.0 (paratially implemented)
    """
    def __init__(self):
        self.curs = None
        btClient.__init__(self)
    def _connect(self, dbPath):
        """
        Open database connection
        """
        self.sock.send("connect=%s\n" % dbPath)
        ch=self.sock.recv(1)
    def cursor(self):
        """
        Create cursor class for access to recordset
        @return: cursor class
        @rtype: CursorBT
        """
        if self.curs is None:
            self.curs= _CursorBT(self)
        return self.curs
    def begin(self):
        pass
    def commit(self):
        pass
    def rollback(self):
        pass
    def close(self):
        self.sock.send("close\n")
        ch=self.sock.recv(1)  # receive ack
        btClient.close(self)


class _CursorBT:
    """
    cursor class for access to recordsets on S60 phone through bluetooh connection
    to be instantiated by cursor() member of btDBclient class
    """
    def __init__(self, con):
        self.con=con
        self.arraysize=1
    def execute(self, sql):
        """
        Send sql command to S60 phone
        Read back rowcount as number of affected rows
        @param sql: sql command
        @type  sql: string
        """
        self.con.sock.send("execute=%s\n" % sql)
        self.rowcount = int(self.con.readline(100).strip('\r\n '))
        self.rownumber=0
    def fetchone(self):
        """
        Read one row (at cursor position) from S60 database that has been requested by a previous execute call
        Move cursor to next row
        @return: the record received
        @rtype: tuple of field values
        """
        self.rownumber +=1
        self.con.sock.send("fetchone\n")
        length = int(self.con.readline().strip('\r\n '))
        data = self.con.sock.recv(length)
        return marshal.loads(data)
    def fetchmany(self, size=-1):
        """
        Get a number of records from the S60 database calling fetchone()
        @rtype: list of tuples of fields values
        """
        if size<0:
            cnt=self.arraysize
        else:
            cnt=size
        if cnt>self.rowcount-self.rownumber and self.rowcount>=0:
            cnt=self.rowcount-self.rownumber
        rows=[]
        for i in range(cnt):
            row = self.fetchone()
            if row is None:
                break
            rows.append(row)
        return rows
    def fetchall(self):
        """
        Get all remaining records from the S60 database calling fetchmany()
        """
        if self.rowcount>=0:
            cnt=self.rowcount-self.rownumber
        else:
            cnt=100000 # unknown number of records
        return self.fetchmany(cnt)
    def close(self):
        pass  
    

if __name__ == '__main__':
   # try:
        app = btClient()
        app._test("btDBclient")
   # finally:
        app.close()
