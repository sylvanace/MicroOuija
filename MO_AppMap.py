
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QProgressBar
from  PyQt5.QtWidgets import QFileDialog
from  PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

import sys
import re
import numpy as np
import MO_Func as mof

class Appmap(QWidget):
    sig_log=pyqtSignal(list)
    xlist=[]
    ylist=[]
    zlist=[]
    replaced_list=[]
    def __init__(self,mainthread):
        super().__init__()
        self.mainthread=mainthread
        self.UILoader()
        self.Restyle()
        self.SignalSlotBinding()
        self.show()
#——————————————————————————————————#
    def UILoader(self):
        self.ui=uic.loadUi('PI_GUI_App_Map.ui',self)
    def Restyle(self):
        self.setWindowTitle('Approach Curve-Map')
        with open(r'appmap_his.txt','r') as file:
            history=file.readlines()
        self.lineEdit_xp.setText(history[0])
        self.lineEdit_yp.setText(history[1])
        self.lineEdit_monitee.setText(history[2])
        self.lineEdit_stbr.setText(history[3])
        # self.lineEdit_xp.setText('0')
        # self.lineEdit_yp.setText('0')
        self.combo_zp.addItem('450,350,300,250,200,150,125,100,90,80,70,60,50,45,40,35,30,25,20,15,10,8,6,4,2,0')
        self.combo_zp.addItem('0,2,4,6,8,10,15,20,25,30,35,40,45,50,60,70,80,90,100,125,150,200,250,300,350,450')
        self.combo_zp.setCurrentText(self.combo_zp.itemText(0))
        # self.lineEdit_monitee.setText(r'C:\Users\jy1u18\OneDrive - University of Southampton\PhD\Second Project\Electrochemistry')
        # self.lineEdit.setText('dis,dis')
    def SignalSlotBinding(self):
        self.checkBox.clicked.connect(self.RenameSwitch)
        self.proceed.clicked.connect(self.StartExp)
        self.toolButton.clicked.connect(self.FileBrowser)

##### GUI Slots
    def RenameSwitch(self):
        if self.checkBox.isChecked():
            self.label_3.setEnabled(True)
            self.lineEdit_stbr.setEnabled(True)
        else:
            self.label_3.setEnabled(False)
            self.lineEdit_stbr.setEnabled(False)

    def StartExp(self):
        permission=False
        self.SaveRecord()
        permission=self.StatusCheck()
        if permission==True:
            self.ExpMonitor()
            if self.checkBox.isChecked():
                self.RenameMonitor()

    def SaveRecord(self):
        file=open(r'appmap_his.txt','w')
        file.close()
        with open(r'appmap_his.txt','a') as file:
            for widget in [self.lineEdit_xp, self.lineEdit_yp,self.lineEdit_monitee,self.lineEdit_stbr]:
                text=widget.text()
                file.write(text)

    def StatusCheck(self):
        try: 
            self.mainthread.ServoCheck()
            self.list_read(widget=self.lineEdit_xp,tlist=self.xlist,ty=int)
            self.list_read(widget=self.lineEdit_yp,tlist=self.ylist,ty=int)
            self.list_read(widget=self.combo_zp,tlist=self.zlist,ty=int)
            self.num3d=len(self.xlist)*len(self.ylist)*len(self.zlist)
            self.num2d=len(self.xlist)*len(self.ylist)
            self.filename=self.lineEdit_monitee.text().rstrip()
            print(self.filename)
            self.list_read(widget=self.lineEdit_stbr,tlist=self.replaced_list,ty=str)
            self.count_file=self.filename+r'\count.txt'
            return True
        except Exception as arg_err:
            if arg_err==FileNotFoundError:
                self.mainthread.LogWriter('Create a count.txt file in the target directory first.')
                self.mainthread.LogWriter(arg_err)
            elif arg_err==ValueError('qSVO of a device returned False'):
                self.mainthread.LogWriter('Turn on servo of each axis first.')
                self.mainthread.LogWriter(arg_err)
            else:
                self.mainthread.LogWriter('Unknown Error.')
                self.mainthread.LogWriter(arg_err)

    def ExpMonitor(self):
        self.ProgressBar()
        self.mon_thrd=mof.ExpMonitor(self.mainthread,self.xlist,self.ylist,self.zlist,self.num3d,self.count_file)
        self.mainthread.threadlist.append(self.mon_thrd)
        self.mon_thrd.sig_ascent.connect(self.Signal_Ascent)
        self.mon_thrd.sig_complete.connect(self.ExpComplete)
        self.mon_thrd.sig_progressbar.connect(self.progressbar.setValue)
        # self.mon_thrd.sig_error.connect(lambda: self.msgrunning.cancel())
        self.mon_thrd.start()
        self.proceed.setEnabled(False)     

    def RenameMonitor(self):
        self.rename_thrd=mof.RenameMonitor(self.mainthread,self.filename,self.replaced_list,self.zlist)
        self.mainthread.threadlist.append(self.rename_thrd)
        self.rename_thrd.start()

    def FileBrowser(self):
        path=self.lineEdit_monitee.text()
        self.filename=QFileDialog.getExistingDirectory(None,'Monitor Folder',path)
        if self.filename=='':
            pass
        else:
            self.lineEdit_monitee.setText(self.filename)

##### Monitor Thread Slots
    def ThreadError(self,string):
        self.thread_error=QMessageBox()
        self.thread_error.setIcon(QMessageBox.Warning)
        self.thread_error.setText(string)
        self.thread_error.setStandardButtons(QMessageBox.Ok)
        self.thread_error.setWindowTitle('Error')
        self.thread_error.show()

    def Signal_Ascent(self,paraset):
        index=paraset[0]
        step=paraset[1]
        if paraset[1]==0:
            vel=0.001
        elif paraset[1]>0.1:
            vel=float(format(np.abs(paraset[1]/2),'.4f'))
        else: 
            vel=float(format(np.abs(paraset[1]),'.4f'))
        self.mainthread.MoveTo(index,step,vel)

    def ExpComplete(self):
        self.mainthread.LogWriter('Experiments done!')
        try:
            self.mon_thrd.terminate()
            self.rename_thrd.terminate()
        except Exception as arg_err:
            self.mainthread.LogWriter('Thread Terminating Error: ')
            self.mainthread.LogWriter(arg_err)
        self.proceed.setEnabled(True)
        self.progressbar.deleteLater()
        self.progresslabel.deleteLater()
        QApplication.processEvents()

    def ProgressBar(self):
        self.progressbar=QProgressBar()
        self.progressbar.setValue(0)
        self.progressbar.setAlignment(Qt.AlignCenter)
        self.progresslabel=QLabel()
        self.progresslabel.setText(
            'Approach Curve experiments running. Do not close this window while running! '
            )
        self.progresslabel.setAlignment(Qt.AlignCenter)
        sizePolicy=QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.progresslabel.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.progressbar)
        self.verticalLayout.addWidget(self.progresslabel)

        
##### Auxilary  Function
    def list_read(self,widget,tlist,ty=int):
        try:
            try:
                string=widget.text()
            except Exception:
                string=widget.currentText()
            res=[]
            element=string.split(",")
            sets=[]
            num=[]
            for ele in element:
                if '(' in ele:
                    sets.append(ele)           
                else:
                    num.append(ty(ele))
            res+=list(map(ty, num))
            for i in sets:
                numset=re.findall(r'[(](.*?)[)]', i)
                rangepara=numset[0].split(' ')
                rangepara=list(map(ty, rangepara))
                res+=np.arange(rangepara[0],rangepara[1]+1,rangepara[2]).tolist()
            tlist[:]=res
        except Exception as arg_err:
            self.mainthread.LogWriter('Input parameter error:')
            self.mainthread.LogWriter(arg_err)
            self.reading_error=QMessageBox()
            self.reading_error.setIcon(QMessageBox.Critical)
            self.reading_error.setText('Potentially input error, please check your inputs\n See log widget for more infomation.')
            self.reading_error.setStandardButtons(QMessageBox.Ok)
            self.reading_error.setWindowTitle('Error')
            self.reading_error.show()
        return res
        
    def closeEvent(self,event):
        try:
            self.mon_thrd.terminate()
            self.rename_thrd.terminate()
            self.mainthread.LogWriter('Thread terminated.')
        except Exception as arg_err:
            if type(arg_err)!=AttributeError:
                self.mainthread.LogWriter(arg_err)

    
        
if __name__=='__main__':
    app = QApplication(sys.argv)
    win=QWidget()
    ui=Appmap(win)
    sys.exit(app.exec_())