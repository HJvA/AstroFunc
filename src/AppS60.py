# -*- coding: iso-8859-1 -*-
# copyright (c) 2007-2009 H.J.v.Aalderen
# 
#
# 090218 FldTyp=='angle'

import e32,appuifw
from key_codes import *
import os,time
import graphics
import topwindow

bgBlue = 0x101080


class AppS60:
    """ interface to python S60 platform
    """
    def __init__(self):
        """ construct application
        """
        self.lock = e32.Ao_lock()
        self.exit_flag = False
        appuifw.app.exit_key_handler = self.exit
        self._RedrawFlag = False # allows to signal next time
        appuifw.app.body = None

    def run(self, title=""):
        """ main body of application
        """
        old_title = appuifw.app.title
        appuifw.app.title = unicode(title)
        while not self.exit_flag:
            self.MainView()  
            self._RedrawFlag = False
            self.lock.wait()
        appuifw.app.title = old_title

    def exit(self):
        """ default exit key handler
        """
        self.exit_flag=True
        self.RedrawDue()
    def close(self):
        """ terminate application
        """
        appuifw.app.menu = []
        appuifw.app.set_tabs([], None)
        appuifw.app.body = None
        appuifw.app.exit_key_handler = None
        

    def RedrawDue(self, val=True):
        """ True  : signal the os to redraw the screen
            False : acknoledge that the screen has been redrawn
        """
        if val and not self._RedrawFlag:  # ! crash when 2 subsequent signals ?
            self.lock.signal()
        self._RedrawFlag=val
    ReDraw = property (fget=lambda : self._RedrawFlag, fset=RedrawDue, fdel=None)
        
    def MainView(self):
        """ virtual: to be implemented by decendants
        """
        pass
        #content = [(u"(Empty)", u"")]
        #self.main_view.set_list(content)
        #self.menu = (u"Option", self.handle_menu)
        #appuifw.app.menu = [self.menu]

    def SetMenu(self, menu):
        """ setup menu for 'Options' function key
        """
        self.menu = menu
        appuifw.app.menu = self.menu

    def handle_menu(self):
        """ to be implemented by decendants
        """
        self.RedrawDue()

    def SetTabs(self, tabs, hook):
        appuifw.app.set_tabs(tabs, hook)

    def PopUpMenu(self, menu, title=None):
        if title is None:
            return appuifw.popup_menu(menu)
        else:
            return appuifw.popup_menu(menu, title)
        
    def ShowForm(self, data, menu=[]):
        """ show PyS60 form
        """
        flags = appuifw.FFormEditModeOnly
        self.frm = appuifw.Form(data, flags)
        self.frm.menu = menu
        self.frm.execute()
        return self.frm
        
    def ShowList(self, data, handle, key=None):
        """
            supports 2 formats : 
        """
        assert isinstance (data, list), "only list accepted"
        lb=None
        if len(data)>0:
            if isinstance(data[0][0], tuple): # [((v1,v2),type),((,)),)...]
                self.LstDat = [x[0] for x in data] #map(lambda x:x[0] ,data)  # take first element
                ListDat = map(lambda x:tuple([unicode(y) for y in x]), self.LstDat) # ensure unicode
                self.LstTypes = [x[1] for x in data] #map(lambda x:x[1] ,data)  # get data types for query
            else:
                self.LstDat = data
                ListDat = [unicode(x) for x in self.LstDat] #map(lambda x:unicode(x), self.LstDat)
                self.LstTypes = None
            if len(self.LstDat)>0:
                lb = appuifw.Listbox(ListDat, handle)
                if not key is None:
                    lb.set_list(ListDat, key)
            appuifw.app.body = None
        appuifw.app.body = lb
        return lb
        
    def CurrentListIdx(self):
        return appuifw.app.body.current()

    def SetListVal(self, val, Idx=-1, col=1):
        if Idx<0:
            i=self.CurrentListIdx()
        else:
            i=Idx
        item = self.LstDat[i]
        if isinstance(item, tuple):
            item = [x for x in item]
            item[col] = val
            self.LstDat[i] = tuple(item)
            appuifw.app.body.set_list(map(lambda x:tuple([unicode(y) for y in x]), self.LstDat))
        else:
            self.LstDat[i] = val
            appuifw.app.body.set_list([unicode(x) for x in self.LstDat])
        
    def GetListItem(self, Idx=-1, col=0):
        if Idx<0:
            i=self.CurrentListIdx()
        else:
            i=Idx
        return self.LstDat[i][col]

    def GetListVal(self, Idx=-1):
        return self.GetListItem(Idx, col=1)
        
    def EditListItem(self):
        FldTyp = self.LstTypes[self.CurrentListIdx()]
        FldVal = self.GetListVal()
        if FldTyp=='date':
            FldVal = time.mktime(FldVal+(0,0,0,0,0,-1))
            FldVal =appuifw.query(self.GetListItem(),FldTyp, FldVal)
            if FldVal is None:
                return None
            return time.localtime(FldVal)[:3]
        elif FldTyp=='time':
            val = (2000,1,1) + FldVal + (0,0,0)  # query converts to UTC
            UTCofs = time.localtime().tm_hour - time.gmtime().tm_hour
            s =appuifw.query(self.GetListItem(),FldTyp, time.mktime(val)+UTCofs*3600)  # -time.altzone
            if s is None:
                return None
            FldVal=time.gmtime(s)[3:6]
            #FldVal = tuple(time.localtime(s))
            return FldVal
        elif FldTyp=='number':  # does not allow negative numbers
            return appuifw.query(self.GetListItem(), 
               'number', FldVal)  
        elif FldTyp=='float':
            return appuifw.query(self.GetListItem(), 
               FldTyp, FldVal)  
        elif FldTyp=='angle':
            return appuifw.query(self.GetListItem(), 
               'text', unicode(FldVal))
        elif FldTyp=='int':
            return appuifw.query(self.GetListItem(), 
               'text', unicode(FldVal))
        else:
            return appuifw.query(self.GetListItem(), 
               FldTyp, unicode(FldVal))
        
    def SetRightKeyHandler(self, handle):
        """ hook handle to scroll right key
        """
        appuifw.app.body.bind(EKeyRightArrow, handle)
    def SetLeftKeyHandler(self, handle):
        appuifw.app.body.bind(EKeyLeftArrow, handle)
    def SetUpKeyHandler(self, handle):
        appuifw.app.body.bind(EKeyUpArrow, handle)
    def SetDownKeyHandler(self, handle):
        appuifw.app.body.bind(EKeyDownArrow, handle)
    
    def _NextTab(self, idx=None):
        if not idx is None:
            nIdx=idx
        elif vars(self).has_key('tab'):
            nIdx=self.tab+1
        else:
            nIdx=0
        if self.tab==nIdx:
            return
        appuifw.note(u'NextTab %d' % nIdx)
        appuifw.app.activate_tab(nIdx)
        self.tab=nIdx
        self.lock.signal()

    def JumpTab(self,tab):
        appuifw.app.activate_tab(tab)
        

class txtView:
    """ draw text window on screen using styles
        based on canvas
    """
    def __init__(self, bgColor=bgBlue, screen='normal'):
        self.ln=0
        appuifw.app.screen=screen
        self.canvas = appuifw.Canvas()
        #appuifw.app.screen = 'full'
        appuifw.app.body = self.canvas
        self.canvas.clear(bgColor)
        self.fgColor = 0xa0a080
        self.font = ('legend',12)
        #return self.canvas.size
    def _centre(self,txt,fnt):
        margin= (self.canvas.size[1] - self.canvas.measure_text(txt,font=fnt)[1])/2
        return margin-8
    def _txt(self,txt,margin=8):
        self.canvas.text((margin,self.ln),unicode(txt), fill=self.fgColor, font=self.font)
        
    def Head(self,txt):
        """ big centered colored
        """
        self.ln+=24
        self.font=('title',20)
        txt = txt.split('\t')
        m = self._centre(txt[0],self.font)
        self._txt(txt[0],m)
        if len(txt)>1:
            self._txt(txt[1],160)
        if len(txt)>2:
            self._txt(txt[2],200)
        self.ln-=4
        #self.canvas.text((m,self.ln),unicode(txt),fill=0xa08080, font=fnt)
    def Separ(self,txt):
        """ long small font centered line with horizontal line below
        """
        self.ln+=12
        self.font=('legend',10)
        m=self._centre(txt,self.font)
        self.fgColor=0xa0a080
        self.canvas.line(((0,self.ln+1),(self.canvas.size[1],self.ln+1)),
                         width=1 ,outline=0x1010d0)
        self._txt(txt,m)
        #self.canvas.text((m,self.ln),unicode(txt), fill=0xa0a080, font=fnt)
        
    def Chap(self,txt):
        """ medium size italic
        """
        self.ln+=24
        self.fgColor=0xa0a080
        self.font=('normal',16,graphics.FONT_ITALIC)
        self._txt(txt,8)
        #self.canvas.text((8,self.ln),unicode(txt), fill=0xa0a080, font=('normal',16,graphics.FONT_ITALIC))
    def Body(self,txt):
        """ small, multi column
        """
        self.ln+=16
        m=12
        self.font=('legend',12)
        self.fgColor=0xa0a080
        txt = txt.split('\t')
        for t in txt:
            self._txt(t,m)
            #self.canvas.text((m,self.ln),unicode(t), fill=0xa0a080, font=('legend',12))
            m+=80

class ImageView(txtView):
    def __init__(self, fname):
        size,pos = appuifw.app.layout(appuifw.EMainPane)
        txtView.__init__(self,bgBlue,'full')
        
        pos=(0,-40) #centre picture !?
        appuifw.app.body.blit(graphics.Image.open(fname).resize(size),pos)
        # take basename,remove ext, split @ -
        txt = os.path.splitext(os.path.basename(fname))[0].split('-')
        self.Chap(txt[0])
        if len(txt)>1:
            self.Separ(txt[1])
    

class txtEdit(txtView):
    def __init__(self, bgColor=0x101080):
        self.tv = appuifw.Text()
        self.tv.set_pos(0)
        self.tv.clear()
        self.tv.style=0
        self.ln=0
        self.fgColor = 0xa0a080
        self.font = ('legend',12)
    def _centre(self,txt,fnt):
        if txt is None:
            return 0
        margin= (40-len(txt))/2
        return margin-8
    def _txt(self,txt,margin=8):
        self.tv.font = self.font
        self.tv.color = self.fgColor
        if txt is None:
            return
        #self.tv.set_pos(margin,self.ln/8)
        #appuifw.note(unicode(txt))
        self.tv.add(unicode(txt))
    def Separ(self,txt):
        self.ln+=12
        self.font=('legend',10)
        self.fgColor=0xa0a080
        m=self._centre(txt,self.font)
        self.tv.style=appuifw.STYLE_UNDERLINE
        self._txt(txt,m)
        self.tv.style=0
        

def FileView(fname, anchor=None):
    #appuifw.Content_handler().open(r'file:///%s#%s' % (fname,anchor))
    if anchor:
        urlView('file:///%s#%s' % (fname,anchor))
    else:
        c=appuifw.Content_handler()
        c.open(fname)

def urlView(url):
    #print url
    #if os.path.exists('BrowserNG.exe'):
    e32.start_exe('BrowserNG.exe', ' "4 %s"' % url,1)
  
def message(txt):  # does not seem to work on phone with pyc 145
    appuifw.app.screen = 'normal'
    print txt
    global pu
    pu = appuifw.InfoPopup()
    pu.show(unicode(txt), (1,1), 6000, 0, appuifw.EHLeftVTop) #EHRightVCenter)
    #pu.hide()
    #del (pu)
    #e32.ao_sleep(5000)
    #e32.Ao_lock().wait()
    return
    
    #appuifw.app.focus = None
    appuifw.app.body = appuifw.Text()
    appuifw.app.body.clear()
    appuifw.app.body.set(unicode(txt))
    #appuifw.note(unicode(txt)) #,'info',1)

def dbgmsg(txt, path=r'\errlog.txt'):
    #print txt
    f = open(path,'a')
    f.write(txt)
    f.write('\n')
    f.close()

def topmsg(txt):
    window = topwindow.TopWindow()
    window.size = (210, 160)
    window.position = (10, 40)
    img = graphics.Image.new((195, 110))
    img.clear(0xFF0000)
    img.text((25, 25), unicode(txt), font = 'title')
    window.add_image(img, (10, 10))
    window.background_color = 0x00FF00
    window.shadow = 4
    window.corner_type = 'corner5'
    window.show()


class _test(AppS60):
    cnt=0
    def MainView(self):
        print "hello world %d" % self.cnt
        self.cnt +=1
        if self.PopUpMenu([u"stop",u"continue"],u"what?")==1:
            self.RedrawDue()
        else:
            self.exit()
    
if __name__ == '__main__':
    app = _test()
    app.run("testing")
    print "closing"
    app.close()
