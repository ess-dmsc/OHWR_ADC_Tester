#  -*- coding: utf-8 -*-

import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPainter, QColor, QBrush
import PyQt5.QtWidgets as QtWidgets
import PyQt5.uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar
from matplotlib.figure import Figure
from DataAnalyser import DataAnalyser
from pathlib import Path
import copy

########################################################################
class StatsTableCtrl:
    def __init__(self, headers, statsTable):
        self.statsTable = statsTable
        self.statsTable.setColumnCount(len(headers))
        self.statsTable.setHorizontalHeaderLabels(headers)
        self.headers = headers
        self.key_list = []
        self.key_value_dict = {}

    def setStatsDict(self, statsDict):
        for key in self.key_value_dict:
            self.key_value_dict[key]["value"] = ""
            self.key_value_dict[key]["status"] = True
        for key in statsDict:
            if key == "data":
                data_list = statsDict[key]
                for item in data_list:
                    for data_key in item:
                        if (data_key != "data"):
                            if not data_key in self.key_value_dict:
                                self.key_list.append(data_key)
                                self.statsTable.setRowCount(len(self.key_list))
                                self.statsTable.setItem(len(self.key_list) - 1, 0, QtWidgets.QTableWidgetItem(data_key))
                            self.key_value_dict[data_key] = {"value": item[data_key], "status":True, "errors":""}
            else:
                if not key in self.key_value_dict:
                    self.key_list.append(key)
                    self.statsTable.setRowCount(len(self.key_list))
                    self.statsTable.setItem(len(self.key_list) - 1, 0, QtWidgets.QTableWidgetItem(key))
                self.key_value_dict[key] = copy.deepcopy(statsDict[key])
        for i, key in enumerate(self.key_list):
            error_item = QtWidgets.QTableWidgetItem(str(self.key_value_dict[key]["errors"]))
            self.statsTable.setItem(i, 2, error_item)
            value_item = QtWidgets.QTableWidgetItem(str(self.key_value_dict[key]["value"]))
            if (not self.key_value_dict[key]["status"]):
                value_item.setBackground(QBrush(QColor(255, 0, 0)))
            self.statsTable.setItem(i, 1, value_item)

        #index1 = self.createIndex(0, 0)
        #index2 = self.createIndex(self.rowCount() -1 , self.columnCount() - 1)
        #self.dataChanged.emit(index1, index1, [])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if (role == QtCore.Qt.DisplayRole):
            if (index.column() == 0):
                return self.key_list[index.row()]
            elif (index.column() == 1):
                return self.key_value_dict[self.key_list[index.row()]]["value"]
            elif(index.column() == 2):
                return self.key_value_dict[self.key_list[index.row()]]["errors"]
        return QtCore.QVariant()

class PlotCtrl:
    def __init__(self, plotFrame):
        self.plotFrame = plotFrame
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavToolbar(self.canvas, self.plotFrame)
        self.toolbar.setVisible(False)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        plotFrame.setLayout(layout)
        self.axes = []
        self.plot_map = {}
        self.data_map = {}
        self.setup_all()

    def enable_toolbar(self, enable):
        self.toolbar.setVisible(bool(enable))

    def clear_figure(self):
        self.figure.clear()

    def setup_all(self):
        self.clear_figure()
        ax1 = self.figure.add_subplot(111)
        self.axes = [ax1, ]
        self.plot_map = {0: ax1, 1: ax1, 2:ax1, 3:ax1}

    def setup_12(self):
        self.clear_figure()
        ax1 = self.figure.add_subplot(111)
        self.axes = [ax1, ]
        self.plot_map = {0: ax1, 1: ax1}

    def setup_34(self):
        self.clear_figure()
        ax1 = self.figure.add_subplot(111)
        self.axes = [ax1, ]
        self.plot_map = {2: ax1, 3: ax1}

    def setup_12_and_34(self):
        self.clear_figure()
        ax1 = self.figure.add_subplot(211)
        ax2 = self.figure.add_subplot(212)
        self.axes = [ax1, ax2]
        self.plot_map = {0: ax1, 1: ax1, 2: ax2, 3: ax2}

    def plot(self, data):
        for item in data:
            channel_no = None
            timestamp = 0
            for key in item:
                if "channel" in key:
                    channel_no = item[key]
                elif "timestamp" in key:
                    timestamp = item[key]
                self.data_map[channel_no] = {"data":item["data"], "ts":timestamp}
        for ax in self.axes:
            ax.clear()
        for ch_no in self.data_map:
            if ch_no in self.plot_map:
                self.plot_map[ch_no].plot(self.data_map[ch_no]["data"], label = "Channel {}".format(ch_no + 1), lw = 3)
                ts_text = "Ch {} TS: {}".format(ch_no + 1, self.data_map[ch_no]["ts"])
                self.plot_map[ch_no].annotate(ts_text, xy=(0,0), xytext=(0.1, 0.6 - 0.2 * (ch_no % 2)), textcoords='axes fraction')
        for ax in self.axes:
            ax.legend()
            ax.axis([0, None, 0, 16384])
            ax.set_xlabel("Sample #")
            ax.set_ylabel("Value")
        self.canvas.draw()


class AdcViewerApp(QtWidgets.QMainWindow):
    def __init__(self, data_dir):
        #Parent constructor
        super(AdcViewerApp,self).__init__()
        self.ui = None
        self.setup(data_dir)

    def setup(self, data_dir):
        import adc_view
        self.ui = adc_view.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.channelsSelector.addItems(["All in one", "Ch 1 & 2", "Ch 3 & 4", "1 & 2 and 3 & 4"])
        self.ui.channelsSelector.currentIndexChanged.connect(self.on_channels_select)

        self.ui.rateComboBox.addItems(["0.5 Hz", "1 Hz", "10 Hz"])
        self.ui.rateComboBox.currentIndexChanged.connect(self.on_rate_select)

        self.ui.startButton.clicked.connect(self.on_start_button)
        self.ui.stopButton.clicked.connect(self.on_stop_button)
        self.ui.stopOnErrorCheckBox.clicked.connect(self.on_stop_select)

        self.setUpTable()

        self.plotCtrl = PlotCtrl(self.ui.plotFrame)

        # set the layout
        self.queryTimer = QtCore.QTimer()
        self.queryTimer.setSingleShot(False)
        self.queryTimer.timeout.connect(self.on_query_for_packet)
        self.queryTimer.start(50)

        self.requestTimer = QtCore.QTimer()
        self.requestTimer.setSingleShot(False)
        self.requestTimer.timeout.connect(self.on_request_timer)
        self.request_delay = 2000
        self.requestTimer.start(self.request_delay)
        self.ui.startButton.setEnabled(False)
        self.stop_on_error = False

        self.dataAnalyser = DataAnalyser(udp_port = 65535, use_thread = True)

    def on_channels_select(self, index):
        select_list = [self.plotCtrl.setup_all, self.plotCtrl.setup_12, self.plotCtrl.setup_34, self.plotCtrl.setup_12_and_34]
        select_list[index]()

    def on_rate_select(self, index):
        rate_list = [2000, 1000, 100]
        self.request_delay = rate_list[index]
        self.requestTimer.setInterval(self.request_delay)

    def on_stop_select(self, index):
        self.stop_on_error = bool(index)

    def on_stop_button(self):
        self.stop_it()

    def stop_it(self):
        self.requestTimer.stop()
        self.queryTimer.stop()
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.plotCtrl.enable_toolbar(True)

    def on_start_button(self):
        self.queryTimer.start(50)
        self.requestTimer.start(self.request_delay)
        self.ui.startButton.setEnabled(False)
        self.ui.stopButton.setEnabled(True)
        self.plotCtrl.enable_toolbar(False)

    def setUpTable(self):
        self.tableCtrl = StatsTableCtrl(["Stat", "Value", "Errors"], self.ui.statsTable)

    #----------------------------------------------------------------------
    def on_request_timer(self):
        self.dataAnalyser.request_packet()

    #----------------------------------------------------------------------
    def on_query_for_packet(self):
        data = self.dataAnalyser.get_packet()
        if data == None:
            return
        if (len(data["data"]) > 0):
            self.plotCtrl.plot(data["data"])
        self.tableCtrl.setStatsDict(data)
        if (self.stop_on_error):
            for key in data:
                if ("status" in data[key]):
                    if (not data[key]["status"]):
                        self.stop_it()

    def closeEvent(self, event):
        self.requestTimer.stop()
        self.queryTimer.stop()
        del self.dataAnalyser
        event.accept()


if __name__ == "__main__":
    # Recompile ui
    ui_file_path = Path("adc_view.ui")
    if ui_file_path.exists():
        with open(str(ui_file_path)) as ui_file:
            with open("adc_view.py", "w") as py_ui_file:
                PyQt5.uic.compileUi(ui_file, py_ui_file)

    app = QtWidgets.QApplication([])
    main_window = AdcViewerApp("ADC demonstrator")
    main_window.show()
    app.exec_()
