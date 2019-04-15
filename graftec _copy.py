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

        self.Label  = QLabel('채널 갯수')
        
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
        peaks, _ = find_peaks(x, height=0, distance=50,threshold=0.2)
        fig, ax = plt.subplots()
        # place a text box in upper left in axes coords
        ax.plot(x,C,linewidth=3)
        ax.plot(peaks, x[peaks], "rD", markersize=10)
        plt.title(tile)
        plt.xlabel('Time(ms)')
        plt.ylabel('Degree(°C)')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.6, 0.9, 'max Degree='+str(x[peaks]) ,transform=ax.transAxes, fontsize=14,bbox=props)

    def openCSVClicked(self):
        fname = QFileDialog.getOpenFileName(self)
        with open(fname[0], 'r') as raw:
            reader = csv.reader(raw)

            #csv to list    
            self.data = list(reader)

        #delete non-data raw
        self.data = self.data[17:]
        #convert list to dataframe 
        self.df = pandas.DataFrame(self.data)
        
        a = self.NumChannel.value()

        if a == 1:
            self.data = self.df.loc[2:, 3]
            self.ch_num=self.df.loc[0,3]
            self.idx = 0
        elif a == 0:
            print('숫자가 잘못 입력되었습니다.')
        else:
            self.data = self.df.loc[2:, 3:2+a].values
            self.ch_num=self.df.loc[0,3:3+a].values
            self.idx = a-1
            self.max_num = np.zeros(a)

        ind = 0
        self.deg = np.zeros(np.shape(self.data))
        self.deg= self.deg[:, np.newaxis]
        for d in self.data:
            if self.idx == 0:
                self.deg[ind] = float(str(d).replace("+", ""))
            elif self.idx != 0 and ind !=0:
                for f in np.arange(0, len(self.data[0])):
                    self.deg[ind, f] = float(str(d[f]).replace("+", ""))
            elif self.idx != 0 and ind ==0:
                self.deg = self.deg.reshape(np.shape(self.data))
            ind +=1

        print('Done!!!!')
    def DrawGraphClicked(self):
        col = ['b','g','c','m','y','k']
        max_num = np.max(self.deg,0)
        print(max_num)
        max_val_txt = ''
        for f in np.arange(0, self.idx+1):
            C = col[f%6]
            tile = 'Degree of '+str(self.ch_num[f])
            self.draw_plot(self.deg[1:,f],tile,C)
            max_val_txt+= str(self.ch_num[f])+': ' +str(max_num[f])+'\n'
        if self.idx !=0:
            fig, ax = plt.subplots()
            
            ax.bar(np.arange(0, len(self.data[0])),max_num)
            ax.plot(max_num,'r--',linewidth=5)
            plt.title('max Degree')
            plt.ylabel('Degree(°C)')
            plt.xticks(np.arange(0, len(self.data[0])), self.ch_num)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.4, 0.7, max_val_txt ,transform=ax.transAxes, fontsize=14,bbox=props)

        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
