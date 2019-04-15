import sys
import csv
import pandas

import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from scipy.signal import find_peaks

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(200, 200, 250, 100)
        self.setWindowTitle("온도 디스플레이 프로그램 v0.1")
        self.setWindowIcon(QIcon('icon.png'))

        self.NumChannel  = QSpinBox(self)
        self.NumChannel.setValue(1)
        self.openCSVbutton = QPushButton("CSV 열기")
        self.openCSVbutton.clicked.connect(self.openCSVClicked)
        self.DrawGraphbutton  = QPushButton("그래프 그리기")
        self.DrawGraphbutton.clicked.connect(self.DrawGraphClicked)

        self.Label  = QLabel('test 장비 갯수')
        
        # Middle Layout
        MiddleLayout = QVBoxLayout()
        MiddleLayout.addWidget(self.Label)
        MiddleLayout.addStretch(1)

        # Right Layout
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.NumChannel)
        rightLayout.addWidget(self.openCSVbutton)
        rightLayout.addWidget(self.DrawGraphbutton)
        rightLayout.addStretch(1)

        layout = QHBoxLayout()
        
        layout.addLayout(MiddleLayout)
        layout.addLayout(rightLayout)
        
        layout.setStretchFactor(MiddleLayout, 1)
        layout.setStretchFactor(rightLayout, 1)

        self.setLayout(layout)
    def draw_plot(self,x,tile,C):
        peaks, _ = find_peaks(x, height=0, distance=200, threshold=0.2, prominence=10)
        fig, ax = plt.subplots()
        # place a text box in upper left in axes coords
        ax.plot(x, C, linewidth=3)
        ax.plot(peaks, x[peaks], "rD", markersize=10)
        plt.title(tile)
        plt.xlabel('Time(ms)')
        plt.ylabel('Degree(°C)')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.7)
        ax.text(0.5, 0.6, 'max Degree=' + str(float(x[peaks])) + ' °C', transform=ax.transAxes, fontsize=14, bbox=props)

    def openCSVClicked(self):
        plt.close('all')
        fname = QFileDialog.getOpenFileName(self)
        try:
            with open(fname[0], 'r') as raw:
                reader = csv.reader(raw)

                # csv to list
                self.data = list(reader)

            a = self.NumChannel.value()

            if a == 1:
                # delete non-data raw
                self.data = self.data[18:]
                # convert list to dataframe
                self.df = pandas.DataFrame(self.data)

                self.data = self.df.loc[2:, 3:8].values
                self.ch_num = ['4cm', '7cm', '10cm', '13cm', '16cm', '19cm']
                self.idx = 5
            elif a != 1 or a != 2:
                QMessageBox.about(self, "message", "숫자가 잘못 입력되었습니다.")
            else:
                # delete non-data raw
                self.data = self.data[24:]
                # convert list to dataframe
                self.df = pandas.DataFrame(self.data).values

                self.data = self.df.loc[2:, 3:14]
                self.ch_num = ['div1_4cm', 'div1_7cm', 'div1_10cm', 'div1_13cm', 'div1_16cm', 'div1_19cm',
                               'div2_4cm', 'div2_7cm', 'div2_10cm', 'div2_13cm', 'div2_16cm', 'div2_19cm']
                self.idx = 11
            ind = 0
            self.deg = np.zeros(np.shape(self.data))
            for d in self.data:
                for f in np.arange(0, len(self.data[0])):
                    self.deg[ind, f] = float(str(d[f]).replace("+", ""))
                ind += 1
            QMessageBox.about(self, "message", "CSV 파일을 성공적으로 읽었습니다")
        except:
            QMessageBox.about(self, "E", "에러 발생")

    def DrawGraphClicked(self):
        col = ['b','g','c','m','y','k']
        max_num = np.max(self.deg,0)
        print(max_num)
        max_val_txt = ''
        for f in np.arange(0, self.idx+1):
            C = col[f%6]
            tile = 'Degree of '+str(self.ch_num[f])
            self.draw_plot(self.deg[1:,f],tile,C)
            if f != self.idx:
                max_val_txt += str(self.ch_num[f]) + ': ' + str(max_num[f]) + '°C \n'
            else:
                max_val_txt += str(self.ch_num[f]) + ': ' + str(max_num[f]) + '°C'
        if self.idx !=0:
            fig, ax = plt.subplots()
            
            ax.bar(np.arange(0, len(self.data[0])),max_num)
            ax.plot(max_num,'r--',linewidth=5)
            plt.title('max Degree')
            plt.ylabel('Degree(°C)')
            plt.xticks(np.arange(0, len(self.data[0])), self.ch_num)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            ax.text(0.4, 0.6, max_val_txt ,transform=ax.transAxes, fontsize=14,bbox=props)

        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
