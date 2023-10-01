# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com
# python for S60

import sys,os,marshal
import e32,socket

from AstroTypes import datPath
import dbS60, AppS60

if '--dat' in sys.argv:
    datPath = sys.argv[sys.argv.index('--dat')+1]
assert globals().has_key('datPath') ,"datPath should have been defined by HastroRun"

class btClient:
    """ Base class for 'S60' bluetooth communication
    """
    sock = socket.socket(family=socket.AF_BT, type=socket.SOCK_STREAM)
    def __init__(self):
        """
        Connect to server using bluetooth
        Lets user pick a particular service on a particular device
        """
        # For quicker startup, enter here the address and port to connect to.
        target='' #('00:20:e0:76:c3:52',1)
        if not target:
            address,services=socket.bt_discover()
            print "Discovered: %s, %s"%(address,services)
            if len(services)>1:
                import appuifw
                choices=services.keys()
                choices.sort()
                choice=appuifw.popup_menu(
                    [unicode(services[x])+": "+x for x in choices],u'Choose port:')
                target=(address,services[choices[choice]])
            else:
                target=(address,services.values()[0])        
        print "Connecting to "+str(target)
        self.sock.connect(target)
    def __del__(self):
        self.sock.close()
    def read(self,n=1):
        """ read a number (n) of characters from the bluetooth socket
        """
        return self.sock.recv(n)
    def write(self,str):
        return self.sock.send(str.replace('\n','\r\n'))
    def readline(self,n=None):
        buffer=[]
        while 1:
            ch=self.read(1)
            if ch == '\n' or ch == '\r':   # return
                buffer.append('\n')
                break
            if ch == '\177' or ch == '\010': # backspace
                del buffer[-1:] # and from the buffer
            else:
                buffer.append(ch)
            if n and len(buffer)>=n:
                break
        return ''.join(buffer)
    def raw_input(self,prompt=""):
        self.write(prompt)
        return self.readline()
    def flush(self):
        pass

ack = '\n'

class btServer(btClient):
    """ Base class for 'S60' bluetooth communication as a server
    """
    def __init__(self, service=u"S60db"):
        #self.sock=socket.socket(family=socket.AF_BT, type=socket.SOCK_STREAM)
        port = socket.bt_rfcomm_get_available_server_channel(self.sock)
        host = "" # local
        print "listening on port %d" % port
        self.sock.bind((host, port))
        socket.set_security(self.sock, socket.AUTHOR)
        self.sock.listen(1) # queue size
        socket.bt_advertise_service(service, self.sock, True, socket.RFCOMM)  # or socket.OBEX
        print "service %s advertised" % service
        self.client, addr = self.sock.accept()
        print "connected  to %s" % addr
         
    def read(self,n=1):
        return self.client.recv(n)
    def write(self,str):
        return self.client.send(str)
    def close(self):
        self.client.close()
        #self.sock.close()  # will be closed by del
        
class btDBserver(AppS60.AppS60):
    """ class for database server on S60 phone to
        cooperate with a btDBclient class on pyBlues device
        to act as a partial DB-API 2.0 (PEP 249) interface to a S60 database
        as seen from a device connected to a S60 phone over bluetooth
    """
    def __init__(self, dbms):
        AppS60.AppS60.__init__(self)
        self.btSock = btServer()
        self.dbms=dbms

    def close(self):
        self.con.close()
        self.btSock.close()
        AppS60.AppS60.exit(self)
        
    def MainView(self):
        """ overrides AppS60.MainView
        """
        ln=self.btSock.readline().lower()
        ln = ln.strip(' \r\n\t'+ack).split('=')
        opr= None
        if len(ln)>1:
            cmd,opr = ln
        elif len(ln)>0:
            cmd=ln[0]
        else:
            cmd = None
        print cmd,opr
        if cmd == 'connect':
            opr = os.path.join(datPath, opr)
            self.con = self.dbms.connect(opr)
            self.btSock.write(ack)
        elif cmd=='query':
            cur = self.con.cursor()
            cur.execute(opr)
            lst = cur.fetchall()
            dat = marshal.dumps(lst)
            self.btSock.write("%d%s" % (len(dat),ack))
            self.btSock.write(dat)
        elif cmd=='execute':
            self.cur = self.con.cursor()
            self.cur.execute(opr)
            self.btSock.write("%d%s" % (self.cur.rowcount,ack))
        elif cmd=='fetchone':
            #cur = self.con.cursor()
            lst = self.cur.fetchone()
            dat = marshal.dumps(lst)
            self.btSock.write("%d%s" % (len(dat),ack))
            self.btSock.write(dat)
        elif cmd=='close':
            self.btSock.write(ack)
            e32.ao_sleep(2)
            self.close()
        elif cmd=='exit':
            self.btSock.write(ack)
            e32.ao_sleep(1)
            self.exit()  # leave AppS60
        elif cmd=='echo':
            self.btSock.write(opr+ack)
        self.RedrawDue()
       

if __name__ == '__main__':
    try:
        #app = btClient()
        print "starting btDBserver"
        app = btDBserver(dbS60)
        print "running"
        app.run("btDBserver")
    finally:
        print "closing"
        app.close()
