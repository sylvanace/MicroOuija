##############################################################################
'''INFORMATIVE'''
#Name: MicrOuija
#Version 0.1.0
#Status: Excutable 
#What's new: 
#Problem Remained: 
#Auther: YJS
##############################################################################
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

from MO_AppMap import Appmap
from MO_Device import PI_Device
from MO_Func import OnTargetTimer as OTT

import sys

#The Main Programme
class MainThread(QMainWindow):
    devdict=[]
    threadlist=[]
    timerdict={}
    devstring={0:'X',1:'Y',2:'Z'}
    def __init__(self):
        super().__init__()
        
        self.LoadUI()
        self.WidgetWrap() 
        self.Restyle()
        self.SignalSlotBinding()
        self.show()
## Load UI file
    def LoadUI(self):
        self.ui=uic.loadUi('PI_GUI.ui',self)
## Wrap Widget for Indexing
    def WidgetWrap(self):
        self.labelaxiset=[self.label_xaxis,self.label_yaxis,self.label_zaxis]
        self.btnlset=[self.pushButton_xl,self.pushButton_yl,self.pushButton_zl]
        self.btnrset=[self.pushButton_xr,self.pushButton_yr,self.pushButton_zr]
        self.gtbtnset=[self.pushButton_xgo,self.pushButton_ygo,self.pushButton_zgo]
        self.btnhaltset=[self.pushButton_haltx,self.pushButton_halty,self.pushButton_haltz]
        self.lineEdit_axisset=[self.lineEdit_x,self.lineEdit_y,self.lineEdit_z]
        self.lineEdit_tpset=[self.lineEdit_xtp,self.lineEdit_ytp,self.lineEdit_ztp]
        self.lineEdit_ssset=[self.lineEdit_xss,self.lineEdit_yss,self.lineEdit_zss]
        self.lineEdit_velset=[self.lineEdit_xvel,self.lineEdit_yvel,self.lineEdit_zvel]
        self.servoset=[self.checkBox_x,self.checkBox_y,self.checkBox_z]
## Format Widgets
    def Restyle(self):
        #Widget Style Setting
        self.setWindowTitle('Microuija')
        self.setWindowIcon(QIcon('icon.png'))
        self.resize(1500,300)
        self.lineEdit_x.setText('0.0000')
        self.lineEdit_y.setText('0.0000')
        self.lineEdit_z.setText('0.0000')
        self.lineEdit_x.setFont(QFont('MS Shell Dlg 2',26))
        self.lineEdit_y.setFont(QFont('MS Shell Dlg 2',26))
        self.lineEdit_z.setFont(QFont('MS Shell Dlg 2',26))
        self.checkBox_x.setFont(QFont('Roboto',10))
        self.checkBox_y.setFont(QFont('Roboto',10))
        self.checkBox_z.setFont(QFont('Roboto',10))
        self.lineEdit_x.setAlignment(Qt.AlignCenter)
        self.lineEdit_y.setAlignment(Qt.AlignCenter)
        self.lineEdit_z.setAlignment(Qt.AlignCenter)
        self.log.setFont(QFont('Roboto',10))
        self.log.setText('Program Log：\n')
        self.pushButton_haltx.setStyleSheet("background-color: red")
        self.pushButton_halty.setStyleSheet("background-color: red")
        self.pushButton_haltz.setStyleSheet("background-color: red")
        self.pushButton_haltx.setFont(QFont('Roboto',10))
        self.pushButton_halty.setFont(QFont('Roboto',10))
        self.pushButton_haltz.setFont(QFont('Roboto',10))
        self.pushButton_appmap.setFont(QFont('Roboto',16))
        self.pushButton_cs.setFont(QFont('Roboto',16))
## General Signal-Slot Binding
    def SignalSlotBinding(self):
### Menu Bar and Shortkey
        self.actionconnect.triggered.connect(self.ConnectDev)
        self.actionconnect.setShortcut(QKeySequence("F2"))
        self.actionRefresh_Position_F5.triggered.connect(
            lambda: self.ShowPos([0,1,2]))
        self.actionRefresh_Position_F5.setShortcut(QKeySequence("F5"))
        self.actionUnlock_buttons.triggered.connect(self.UnlockButtons)
        self.actionUnlock_buttons.setShortcut(QKeySequence("F3"))
### Check Box to Turn On Servo        
        self.checkBox_x.clicked.connect(lambda: self.Servo(0))
        self.checkBox_y.clicked.connect(lambda: self.Servo(1))
        self.checkBox_z.clicked.connect(lambda: self.Servo(2))
### Buttons to Move Micropositioner
        self.pushButton_xl.clicked.connect(
            lambda: self.MoveTo(0,'-'+self.lineEdit_xss.text(),self.lineEdit_xvel.text()))
        self.pushButton_yl.clicked.connect(
            lambda: self.MoveTo(1,'-'+self.lineEdit_yss.text(),self.lineEdit_yvel.text()))
        self.pushButton_zl.clicked.connect(
            lambda: self.MoveTo(2,'-'+self.lineEdit_zss.text(),self.lineEdit_zvel.text()))
        self.pushButton_xr.clicked.connect(
            lambda: self.MoveTo(0,self.lineEdit_xss.text(),self.lineEdit_xvel.text()))
        self.pushButton_yr.clicked.connect(
            lambda: self.MoveTo(1,self.lineEdit_yss.text(),self.lineEdit_yvel.text()))
        self.pushButton_zr.clicked.connect(
            lambda: self.MoveTo(2,self.lineEdit_zss.text(),self.lineEdit_zvel.text()))
### Buttons to Set Micropositioner Position
        self.pushButton_xgo.clicked.connect(
            lambda: self.GoTo(0,self.lineEdit_xtp.text(),self.lineEdit_xvel.text())
        )
        self.pushButton_ygo.clicked.connect(
            lambda: self.GoTo(1,self.lineEdit_ytp.text(),self.lineEdit_yvel.text())
        )
        self.pushButton_zgo.clicked.connect(
            lambda: self.GoTo(2,self.lineEdit_ztp.text(),self.lineEdit_zvel.text())
        )
### Buttons to Halt Movement
        self.pushButton_haltx.clicked.connect(lambda: self.Halt(0))
        self.pushButton_halty.clicked.connect(lambda: self.Halt(1))
        self.pushButton_haltz.clicked.connect(lambda: self.Halt(2))
### Buttons to Open Programmed Method
        self.pushButton_appmap.clicked.connect(self.Run_Appmap)

## Micropositioner Connection Functions
### Make Connection in QThread
    def ConnectDev(self):
        self.LogWriter('Making connection')
        self.pidevice=PI_Device()
        self.pidevice.sig_log.connect(self.LogWriter)
        self.pidevice.sig_complete.connect(self.GetDevice)
        self.threadlist.append(self.pidevice)
        self.pidevice.start()
### Pass Device Variables to Main Thread
    def GetDevice(self):
        self.devdict={0:self.pidevice.devx, 1:self.pidevice.devy, 2:self.pidevice.devz}
        for widget in self.findChildren(QPushButton):
            widget.setEnabled(True)

    def ShowPos(self,axis):
        if type(axis)==list:
            for axes in axis:
                pos=str(format(self.devdict[axes].qPOS('1')['1'],'.4f'))
                self.lineEdit_axisset[axes].setText(pos)
        else:
            axes=axis
            pos=str(format(self.devdict[axes].qPOS('1')['1'],'.4f'))
            self.lineEdit_axisset[axes].setText(pos)

    def Servo(self,axis):
        if self.servoset[axis].isChecked()==True:
            try:
                servoOn=False
                self.devdict[axis].SVO(1,True)
                servoOn=self.devdict[axis].qSVO()['1']
                self.ShowPos(axis)
            except Exception as arg_err:
                self.LogWriter(arg_err)
            finally:
                if servoOn==True:
                    self.labelaxiset[axis].setStyleSheet('color: lime')
                    self.servoset[axis].setChecked(True)
                else: 
                    self.labelaxiset[axis].setStyleSheet('color: red')
                    self.servoset[axis].setChecked(False)
        else:
            try:
                servoOn=True
                self.devdict[axis].SVO(1,False)
                servoOn=self.devdict[axis].qSVO()['1']
            except Exception as arg_err:
                self.LogWriter(arg_err)
            finally:
                if servoOn==True:
                    self.labelaxiset[axis].setStyleSheet('color: lime')
                    self.servoset[axis].setChecked(True)
                else: 
                    self.labelaxiset[axis].setStyleSheet('color: red')
                    self.servoset[axis].setChecked(False)

    def MoveTo(self,index,step='0',vel='2'):
        arg_err=None
        try:
            self.btnlset[index].setEnabled(False)
            self.btnrset[index].setEnabled(False)
            self.gtbtnset[index].setEnabled(False)
            label=self.labelaxiset[index]
            device=self.devdict[index]
            lineedit=self.lineEdit_axisset[index]
            step=float(step)
            vel=float(vel)
            label.setStyleSheet('color:yellow')
            QApplication.processEvents()
            cpos=float(format(device.qPOS('1')['1'],'.4f'))
            tpos=float(format(cpos+step,'.4f'))
            self.LogWriter('axis '+self.devstring[index]+': '+str(cpos) +' to '+ str(tpos))
            device.VEL('1',vel)
            device.MVR('1',step)
            self.ot_count=0
            self.timerdict[index]=OTT()
            self.timerdict[index].sig_refresh.connect(lambda: self.OnTarget(device,lineedit,label,index))
            self.timerdict[index].start()
        except Exception as arg_err:
            self.LogWriter(arg_err)

    def GoTo(self,index,tpos,vel='2'):
        try:
            self.btnlset[index].setEnabled(False)
            self.btnrset[index].setEnabled(False)
            self.gtbtnset[index].setEnabled(False)
            label=self.labelaxiset[index]
            device=self.devdict[index]
            lineedit=self.lineEdit_axisset[index]
            tpos=float(tpos)
            vel=float(vel)
            label.setStyleSheet('color:yellow')
            QApplication.processEvents()
            cpos=float(format(device.qPOS('1')['1'],'.4f'))
            self.LogWriter('axis '+self.devstring[index]+': '+str(cpos) +' to '+ str(tpos))
            device.VEL('1',vel)
            device.MOV('1',tpos)
            self.ot_count=0
            self.timerdict[index]=OTT()
            self.threadlist.append(self.timerdict[index])
            self.timerdict[index].sig_refresh.connect(lambda: self.OnTarget(device,lineedit,label,index))
            self.timerdict[index].start()
        except Exception as arg_err:
            self.LogWriter(arg_err)
            
    def Halt(self,devnum):
        try:
            for thread in self.threadlist:
                thread.terminate()
            dev=self.devdict[devnum]
            dev.HLT('1',noraise=True)
            self.labelaxiset[devnum].setStyleSheet('color: red')
            for widget in self.findChildren(QCheckBox):
                widget.setEnabled(False)
            for widget in self.findChildren(QPushButton):
                widget.setEnabled(False)
            QApplication.processEvents()
            self.LogWriter(
                "<span style=\" font-size:10pt; font-weight:600; color:#ff0000;\" >"
                'HALT!'
                "</span>")
            self.OnTarget(self.devdict[devnum],self.lineEdit_axisset[devnum],self.labelaxiset[devnum],devnum)
            QApplication.processEvents()
            for widget in self.findChildren(QCheckBox):
                widget.setEnabled(True)
            for widget in self.findChildren(QPushButton):
                widget.setEnabled(True)
            self.labelaxiset[devnum].setStyleSheet('color: red')
            QApplication.processEvents()
            self.LogWriter('Halt finished')
        except Exception as arg_err:
            self.LogWriter('Halt Error:')
            self.LogWriter(arg_err)

    def OnTarget(self,device,lineedit,label,index):
        self.timerdict[index].flag=False
        pos1=device.qPOS('1')['1']
        pos2=device.qPOS('1')['1']
        err=abs(pos2-pos1)
        lineedit.setText(str(format(device.qPOS('1')['1'],'.4f')))
        QApplication.processEvents()
        if err<0.0001 and self.ot_count<5:
            self.ot_count+=1
            self.timerdict[index].flag=True
        elif self.ot_count>=5:
            self.timerdict[index].flag=False
            self.timerdict[index].terminate()
            lineedit.setText(str(format(device.qPOS('1')['1'],'.4f')))
            self.btnlset[index].setEnabled(True)
            self.btnrset[index].setEnabled(True)
            self.gtbtnset[index].setEnabled(True)
            label.setStyleSheet('color:lime')
            QApplication.processEvents()
        else: 
            self.timerdict[index].flag=True

    def ServoCheck(self):
        for dev in self.devdict.values():
            if dev.qSVO()['1']==False:
                raise ValueError('qSVO of a device returned False')

    def UnlockButtons(self):
        for widget in self.findChildren(QPushButton):
            widget.setEnabled(True)

    def LogWriter(self,content):
        #write input string to log widget or locate input exception in script and write to log widget.
        arg_err=None
        try:
            if type(content)==str: #if input is string
                self.log.append(content)
                self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())
            else: #if input is Exception
                xc_type, exc_obj, exc_tb = sys.exc_info()
                exc_dir=exc_tb.tb_frame.f_code.co_filename
                exc_line=exc_tb.tb_lineno
                exc_str=', '.join(list(map(str,(xc_type,exc_dir,exc_line,exc_obj))))
                self.log.append(exc_str)
                self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())
        except Exception as arg_err: #if above code goes wrong output LogWriter Error
            xc_type, exc_obj, exc_tb = sys.exc_info()
            exc_dir=exc_tb.tb_frame.f_code.co_filename
            exc_line=exc_tb.tb_lineno
            exc_str=', '.join(list(map(str,(xc_type,exc_dir,exc_line,exc_obj))))
            self.append('LogWriter Error, check input argument: '+exc_str)
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def Run_Appmap(self):
            self.appmap_win=Appmap(self)

    def closeEvent(self, event):
        super(MainThread, self).closeEvent(event)
        self.appmap_win.deleteLater()
        for thread in self.threadlist:
            thread.terminate()
        print('close')
    



if __name__== '__main__':
    try:
        app = QApplication(sys.argv)
        mainthread=MainThread()
        sys.exit(app.exec())
    except Exception as arg_err:
        xc_type, exc_obj, exc_tb = sys.exc_info()
        exc_dir=exc_tb.tb_frame.f_code.co_filename
        exc_line=exc_tb.tb_lineno
        exc_str=', '.join(list(map(str,(xc_type,exc_dir,exc_line,exc_obj))))
        print(exc_str)
        
