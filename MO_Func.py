from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, pyqtSignal 
import os,time

#####Monkey Patch


class ExpMonitor(QThread):
    sig_ascent=pyqtSignal(list)
    sig_goto=pyqtSignal(list)
    sig_complete=pyqtSignal()
    sig_progressbar=pyqtSignal(int)
    sig_error=pyqtSignal()

    def __init__(self,mainthread,xlist,ylist,zlist,maxval,monitee):
        super().__init__()
        self.mainthread=mainthread
        self.xlist=xlist
        self.ylist=ylist
        self.zlist=zlist
        self.maxval=maxval-1
        self.ddif=[]
        self.monitee=monitee
        for i in range(1,len(self.zlist)):
            self.ddif.append(self.zlist[i]-self.zlist[i-1])
        
    def run(self):
        arg_err=None
        try:
            ready=self.CheckReady()
            if ready==True:
                self.RunExp()
                self.sig_complete.emit()
        except Exception as arg_err:
            self.mainthread.LogWriter(arg_err)

    def CheckReady(self):
        ready=False
        try:
            self.file = open(self.monitee, "w")
            self.file.write('0')
            self.file.close()
            ready=True
        except Exception as arg_err:
            self.mainthread.LogWriter('ExpMonitor class error: ')
            self.mainthread.LogWriter(arg_err)
        finally:
            self.file.close()
            return ready

    def RunExp(self):
        n=0
        for i in range(len(self.xlist)):
            if i==0:
                xdif=self.xlist[i]-0
            else:
                xdif=self.xlist[i]-self.xlist[i-1]
                self.sig_ascent.emit([1,(0-self.ylist[-1])/1000])
                self.sig_ascent.emit([2,(0-self.zlist[-1])/1000])
            self.sig_ascent.emit([0,xdif/1000])
            for j in range(len(self.ylist)):
                if j==0:
                    ydif=self.ylist[j]-0
                else:
                    ydif=self.ylist[j]-self.ylist[j-1]
                    self.sig_ascent.emit([2,(0-self.zlist[-1])/1000])
                self.sig_ascent.emit([1,ydif/1000])
                for k in range(len(self.zlist)):
                    if k==0:
                        zdif=self.zlist[k]-0
                    else:
                        zdif=self.zlist[k]-self.zlist[k-1]
                    self.sig_ascent.emit([2,zdif/1000])

    
                    # start to monitor:
                    self.file = open(self.monitee, "r")
                    self.before=self.file.read()
                    self.file.close()
                    arg_err=None
                    while True:
                        try:
                            self.file = open(self.monitee, "r")
                            time.sleep(0.2)
                            self.after = self.file.read()
                            self.file.close()
                            # loop-terminate trigger
                            if self.before!=self.after:
                                n+=1
                                self.sig_progressbar.emit(int(n/self.maxval*100))
                                self.mainthread.LogWriter('one loop done.')
                                break         
                        except Exception as arg_err:
                            if arg_err==PermissionError:
                                pass
                            else:
                                self.mainthread.LogWriter('count.txt file Error:')
                                self.mainthread.LogWriter(arg_err)


class RenameMonitor(QThread):

    def __init__(self,mainthread,path,format_list,value_list):
        super().__init__()
        self.mainthread=mainthread
        self.path=path
        self.format_list=format_list
        self.value_list=value_list
    def run(self):
        for value in self.value_list:
            for symbol in self.format_list:
                # self.animation.emit(str(value))
                flag=True
                while flag==True:
                    time.sleep(1)
                    flag=self.Rename(symbol,value)
    def Rename(self,symbol,value):
        flag=True
        filelist=os.listdir(self.path)
        for file in filelist:
            if symbol in file:
                try:
                    flag=False
                    newname=file.replace(symbol, str(value))
                    os.rename(self.path+os.sep+file,self.path+os.sep+newname)
                except Exception as arg_err:
                    if arg_err==FileExistsError:
                        newname=file.replace('.txt', ' new.txt')
                        os.rename(self.path+os.sep+file,self.path+os.sep+newname)
                    elif arg_err==PermissionError or FileNotFoundError:
                        flag=True
                        print('PE,FNF error')
                    else:
                        print(arg_err)
                        self.mainthread.LogWriter('Unexpected rename thread Error: ')
                        self.mainthread.LogWriter(arg_err)
        return flag 

class OnTargetTimer(QThread):
    sig_refresh=pyqtSignal()
    flag=True
    def __init__(self):
        super().__init__()
        
    def run(self):
        while True:
            if self.flag==True:
                self.sig_refresh.emit()
                time.sleep(0.5)
            else:
                continue
