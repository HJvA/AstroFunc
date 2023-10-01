# -*- coding: utf-8 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# henk.jan.van.aalderen@gmail.com
import sys,os


if sys.platform=="win32":
    raise OSError("only for symbian_S60")
else:
    import e32,appuifw
    #ChkSrcPath('subs')
    #appuifw.note(unicode(sys.argv[0]))

    import AppS60, dbS60
    #ConStr = "c:\\HastroDat\\GeoLocs.db"
    #dbms = dbS60.connect(ConStr)


class RecordForm:
    def __init__(self, Record, app, EditFlds):
        """ setup list & menu combination acting as a form
        """
        self.app = app  # expected to have dbms member
        self.content = []
        flds = EditFlds.split(',')
        for elm in Record:
            fld = unicode(flds[len(self.content)])
            if type(elm) in (type(""),type(u"")):
                self.content.append(((fld,elm), 'text'))
            elif type(elm) in (int,long):
                self.content.append(((fld,elm), 'number'))
            elif type(elm) in (float,):
                self.content.append(((fld,elm), 'float'))
            elif isinstance(elm, tuple) and len(elm)==9:
                (yr, mo, da, h, m, s, wd, jd, ds) = elm  # time.localtime()
                self.dt = (yr, mo, da)
                self.tm = (h, m, s)
                self.content.append(((fld+'_date',self.dt), 'date'))
                self.content.append(((fld+'_time',self.tm), 'time'))
            else:
                raise TypeError("Unknown dbField type")
        self.app.ShowList(self.content, self.handle_list)

        self.app.SetMenu([(u"Pick",self.handle_pick),
                          (u"Save",self.handle_save),
                          (u"Delete",self.handle_del)])
        self.app.SetRightKeyHandler(self.handle_next)
        self.app.SetLeftKeyHandler(self.handle_back)
        
    def close(self):
        self.app.SetMenu([])
    #def accept(self):
    #    self.app.rec = self.GetRecord()
    def GetRecord(self):
        """ Retrieve values from list (form) being edited
        """
        types = [item[1] for item in self.content]
        rec =[]
        for i in range(len(types)):
            val = self.app.GetListVal(i)
            if types[i]=='text':
               rec.append(val)
            elif types[i]=='number':
               rec.append(int(val))
            elif types[i]=='float':
               rec.append(float(val))
            elif types[i]=='date':
               if  types[i+1]=='time':
                   pass
               rec.append(float(val))
        return tuple(rec)
    def GetName(self):
        """ Retrieve the value of the actual NameFld
        """
        return self.app.GetListVal(self.app.dbms.GetNameIdx())

    def handle_list(self):
        """ edit a field
        """
        Idx = self.app.CurrentListIdx()
        val = self.app.EditListItem()
        if not val is None:
            self.app.SetListVal(val)
            #self.accept()
    def handle_pick(self):
        """ show a list of name flds of records from the database
            Let user pick an item 
        """
        nms = self.app.dbms.GetNames()
        idx = self.app.PopUpMenu(nms,u"pick name")
        if not idx is None:
            self.app.dbms.GotoRecord(idx,'absolute')
            self.app.tab=1
            self.app.RedrawDue()
        
    def handle_next(self):
        self.app.tab +=1
        self.app.RedrawDue()
    def handle_back(self):
        self.app.tab -=1
        self.app.RedrawDue()
    def handle_save(self):
        self.app.dbms.CheckRecord(self.GetRecord())
        self.app.dbms.ReloadRecord()  # may be duplicated if name had changed
        self.app.RedrawDue()
    def handle_del(self): 
        self.app.dbms.DeleteRecord(Name=self.GetName())
        self.app.dbms.ReloadRecord()
        self.app.RedrawDue()


class dbBrowser(AppS60.AppS60):
    def __init__(self, AnyDBms):
        self.view = None
        AppS60.AppS60.__init__(self)  # install callbacks
        self.dbms = AnyDBms
        self.tab=1
        self.RedrawDue()

    def MainView(self):
        if self.view is None or self.tab!=0: # or self._RedrawFlag:
            try:
                self.dbms.GotoRecord(self.tab-1)
                Record = self.dbms.NextRecord()
                self.view = RecordForm(Record, self, self.dbms.EditFlds)
            except (IndexError):
                appuifw.note(u'beyond available records')
            self.tab=0
        else:
            pass

if __name__ == '__main__':
    pass  # see dbGeoLocs.py for example of usage