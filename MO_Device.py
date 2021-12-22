##############################################################################
'''INFORMATIVE'''
#Name: MicrOuija
#Version 0.1.0
#Status: Excutable 
#What's new: 
#Problem Remained: 
#Auther: YJS
#Desciption: Make connection to C-863 micropositioner controller. Pass control to main thread.
##############################################################################
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal 

from pipython import GCSDevice

class PI_Device(QThread): 
    sig_log=pyqtSignal(object) 
    sig_complete=pyqtSignal()
    def __init__(self):
        super().__init__()
    def run(self):
        arg_err=None
        try:
            self.devz=GCSDevice('C-863')
            self.devz.OpenRS232DaisyChain(comport=8, baudrate=9600)
            chainid=self.devz.dcid
            self.devz.ConnectDaisyChainDevice(3, chainid)
            self.devy=GCSDevice('C-863')
            self.devy.ConnectDaisyChainDevice(2, chainid)
            self.devx=GCSDevice('C-863')
            self.devx.ConnectDaisyChainDevice(1, chainid)
            self.sig_log.emit('All axis connected.')
            self.sig_complete.emit()
        except Exception as arg_err:
            self.sig_log.emit(arg_err)
            self.ErrorWin('Device Connection Error\n See log window for more information.')
    def ErrorWin(self,text):
        self.errormsg=QMessageBox()
        self.errormsg.setIcon(QMessageBox.Critical)
        self.errormsg.setText(text)
        self.errormsg.setStandardButtons(QMessageBox.Ok)
        self.errormsg.setWindowTitle('Error')
        self.errormsg.show()
