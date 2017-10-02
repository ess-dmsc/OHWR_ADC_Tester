#  -*- coding: utf-8 -*-

import os
from PyQt4 import QtCore, QtGui, uic
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from DataAnalyser import DataAnalyser

class AdcViewerApp(QtGui.QMainWindow):
	def __init__(self, data_dir):

		#Parent constructor
		super(AdcViewerApp,self).__init__()
		self.ui = None
		self.setup(data_dir)

	def setup(self, data_dir):
		import adc_view
		self.ui = adc_view.Ui_MainWindow()
		self.ui.setupUi(self)
		
		
		self.figure = Figure()
		self.canvas = FigureCanvas(self.figure)
	
		# set the layout
		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.canvas)
		self.ui.plotFrame.setLayout(layout)
		self.ax = self.figure.add_subplot(111)
		y = np.zeros(512)	
		self.timer = QtCore.QTimer()
		self.timer.setSingleShot(False)
		self.timer.timeout.connect(self.on_timer)
		self.timer.start(500)
		self.dataAnalyser = DataAnalyser(udp_port = 65535, True)
	
	#----------------------------------------------------------------------
	def plot_data(self, data):
		self.ax.clear()
		self.ax.plot(data, lw = 3, color = "k")
		self.ax.axis([0, None, 0, 16384])
		self.ax.set_xlabel("Sample #")
		self.ax.set_ylabel("Value")
		self.canvas.draw()
	
	#----------------------------------------------------------------------
	def on_timer(self):
		data = self.dataAnalyser.get_packet()
		if data == None:
			return
		self.ui.timeStamp.setText(str(data["time_stamp"]))
		self.plot_data(data["data"])
		#self.line.set_ydata(data["data"])
	
	def closeEvent(self, event):
		self.timer.stop()
		del self.dataAnalyser
		event.accept()
		

if __name__ == "__main__":
	# Recompile ui
	with open("adc_view.ui") as ui_file:
		with open("adc_view.py","w") as py_ui_file:
			uic.compileUi(ui_file,py_ui_file)

	app = QtGui.QApplication([])
	main_window = AdcViewerApp("ADC demonstrator")
	main_window.show()
	app.exec_()
