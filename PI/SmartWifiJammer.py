from cmath import log
from queue import Empty
from PyQt5.QtWidgets import QMainWindow, QApplication,QComboBox, QLabel, QPushButton, QTableView, QProgressBar, QTextEdit
from PyQt5 import uic, QtGui,QtTest,QtCore
from qt_material import apply_stylesheet
from qt_material import list_themes
import threading
import sys
import time
import csv
import functions as LogicFunctions

#global vars
themeIndex=0
uiThemes=[ 				'dark_yellow.xml',
						'dark_amber.xml',
 					    'dark_blue.xml',
 						'dark_cyan.xml',
 						'dark_lightgreen.xml',	
						'dark_pink.xml',
 						'dark_purple.xml',
 						'dark_red.xml',
 						'dark_teal.xml',]


class UI(QMainWindow):
	
	subProcTermSigal=None
	def __init__(self):
		super(UI,self).__init__()
		self.fileName="../CSV/data-01.csv"
			

		#load UI
		uic.loadUi("../UI/MainWindow.ui",self)

		
		#define Widgets and initialization
		self.label1=self.findChild(QLabel,"label") 
		self.buttonEnableMon=self.findChild(QPushButton,"pushButtonMonEnable")
		self.buttonScanAps=self.findChild(QPushButton,"pushButtonScanAps")
		self.buttonFakeAps=self.findChild(QPushButton,"pushButtonFakeAps")
		self.buttonFilterAps=self.findChild(QPushButton,"pushButtonFilterAps")
		self.buttonJamAps=self.findChild(QPushButton,"pushButtonJamAps")
		self.comboBox1=self.findChild(QComboBox,"comboBox")
		self.tableView1=self.findChild(QTableView,"tableView")
		self.progressBar1=self.findChild(QProgressBar,"progressBar1")
		self.buttonStopJammer=self.findChild(QPushButton,"pushButtonStopJammer")
		self.buttonToggleTheme=self.findChild(QPushButton,"pushButtonToggleTheme")
		self.textEditLogs=self.findChild(QTextEdit,"textEditLogs")
	

		self.model=QtGui.QStandardItemModel(self)
		self.tableView1.setModel(self.model)
		self.tableView1.horizontalHeader().stretchLastSection()
		

		self.controlsEnable(False)#at start of app disable buttons
		self.buttonEnableMon.setEnabled(True)#except EnableMon button
		self.progressBar1.setValue(0)
		self.progressBar1.setAlignment(QtCore.Qt.AlignCenter)
		#not mentioning bakground color here
		self.progressBar1.setStyleSheet("QProgressBar::chunk{;} QProgressBar {color: Black;}")
		#more widgets code here

		#work logic  
		self.buttonEnableMon.clicked.connect(self.clickerPressedEnableMon)
		self.buttonJamAps.clicked.connect(self.clickerPressedJamAps)
		self.comboBox1.addItems(LogicFunctions.getNICnames())
		self.buttonScanAps.clicked.connect(self.clickerPressedScanAps)
		self.buttonFilterAps.clicked.connect(self.clickerPressedFilterAps)
		self.buttonStopJammer.clicked.connect(self.clickerPressedStopJammer)
		self.buttonToggleTheme.clicked.connect(self.clickerPressedToggleTheme)

		
		#show App
		self.show()
		self.setWindowTitle("Smart Wi-Fi Jammer")

		
	

		#clickerMethods
	def clickerPressedEnableMon(self):
		LogicFunctions.enableMonitor(self.comboBox1.currentText())#passing iface name
		isMonEnabled=LogicFunctions.checkMon(self.comboBox1.currentText())
		if(isMonEnabled):
			self.controlsEnable(True)#enable buttons on monitor mode
		self.updateLog()

	def clickerPressedScanAps(self):
		threadProgressBar=threading.Thread(target=self.showProgressBar)
		threadLoadCsv=threading.Thread(target=self.loadCsv)

		threadProgressBar.start()
		LogicFunctions.scanAps(self.comboBox1.currentText())
		QtTest.QTest.qWait(15000)#prevent UI freeze
		threadLoadCsv.start()
		threadLoadCsv.join()
		threadProgressBar.join()
		self.updateLog()
		
					

		
	def clickerPressedJamAps(self):
		self.threadJamAP=[]
		self.ESSIDList=self.getESSIDList()
		self.ChannelList=self.getChannelList()
		#merge upper two lists into dictionary
		self.dictESSID_Channel={self.ESSIDList[i]:self.ChannelList[i] for i in range(len(self.ESSIDList))}
		#for every dictionary item create a thread and pass func jamap with args iface,ESSID,channel
		for ESSID,channel in self.dictESSID_Channel.items():
			self.threadJamAP.append(threading.Thread(target=LogicFunctions.jamAp,args=(self.comboBox1.currentText(),ESSID,channel)))
		
		for th in self.threadJamAP:
			th.start()
			th.join()

		self.updateLog()
		
			



	def clickerPressedFilterAps(self):
		pass
		

	def clickerPressedStopJammer(self):	
		LogicFunctions.stopJammer()
		self.updateLog()

	def clickerPressedToggleTheme(self):
		global themeIndex
		themeIndex+=1
		themeIndex%=9#index not to exceed 8
		apply_stylesheet(app,theme=uiThemes[themeIndex])
		self.updateLog()

		

		
	
	def controlsEnable(self,flag):
		self.buttonEnableMon.setEnabled(flag)
		self.buttonScanAps.setEnabled(flag)
		self.buttonFakeAps.setEnabled(flag)
		self.buttonFilterAps.setEnabled(flag)
		self.buttonJamAps.setEnabled(flag)
		self.buttonStopJammer.setEnabled(flag)
		#self.textEditLogs.setEnabled(flag)

	def loadCsv(self):
		self.model.clear() #clear previous model data to load new
		with open(self.fileName,"r") as fileInput:
			for row in csv.reader(fileInput):
				items= [
					QtGui.QStandardItem(self.field)
					for self.field in row
		
				]
				self.model.appendRow(items)

		#removing useless columns from model		
		self.model.removeColumn(1)
		self.model.removeColumn(1)
		self.model.removeColumn(8)
		self.model.removeColumn(8)
		self.model.removeColumn(10)
				
	


	#NonClicker Methods
	def showProgressBar(self):
			self.controlsEnable(False)#disable control while progressbar is running
			for i in range(1,21):
				self.progressBar1.setValue(i*5)
				time.sleep(1)
			self.controlsEnable(True)#Enable controls
			
	
	def getESSIDList(self):
		ESSIDList=[]
		rows=sorted(set(index.row() for index in
						self.tableView1.selectedIndexes()))
		for row in rows:
			ESSIDList.append(self.model.item(row,9).text())
		return ESSIDList

	def getChannelList(self):
		channelList=[]
		rows=sorted(set(index.row() for index in
						self.tableView1.selectedIndexes()))
		for row in rows:
			channelList.append(self.model.item(row,1).text())
		return channelList

	def updateLog(self):
		self.textEditLogs.setPlainText(LogicFunctions.logString)









#initialize App
app=QApplication(sys.argv)
apply_stylesheet(app,theme=uiThemes[themeIndex])#default theme with index 0
UIWindow=UI()
app.exec_()