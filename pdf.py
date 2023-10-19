from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QTextEdit, QFileDialog, QScrollBar, QComboBox, QColorDialog, QCheckBox, QSlider
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5 import QtWidgets, uic
from fpdf import FPDF
import pyqtgraph.exporters
import pyqtgraph as pg
import pandas as pd
import statistics
import os
import numpy as np
import main

def Exporter(self):
    FolderPath = QFileDialog.getSaveFileName(None, str('Save the signal file'), None, str("PDF FIles(*.pdf)"))
    try:
        if FolderPath != '':
            # self.check_application()
            pdf = FPDF()

            # for graph1 check first if there is atleast one signal running
            if self.curves_1:
                pdf.add_page()
                # Effective page width
                epw = pdf.w - 2*pdf.l_margin
                # distribute the table on 6 columns
                column_width = epw/6

                pdf.set_font('Arial', 'B', 20)
                pdf.cell(70)
                #        w    h             border  postion allignment 
                pdf.cell(50, 10, 'Signal Viewer Report', 0, 0, 'C')
                pdf.ln(15)
                
                pdf.cell(20, 10, 'Graph 1', 0, 0, 'L')
                pdf.ln(15)

                # iterate through snapshots of graph 1
                x , y = 10 , 50
                for i in range(min(self.snapshot1_counter,3)):
                    #                                                x   y   w    h
                    pdf.image(f'img/graph-1-snapshots/graph{i}.png', x, y, 60, 45)
                    x += 65
                pdf.ln(10)

                if self.snapshot1_counter >= 3:
                    x , y = 10 , 100
                    for i in range(3,min(self.snapshot1_counter,6)):
                        #                                                x   y   w    h
                        pdf.image(f'img/graph-1-snapshots/graph{i}.png', x, y, 60, 45)
                        x += 65
                    pdf.ln(120)
                else:
                    pdf.ln(110)

                pdf.cell(50, 10, 'Statistics data',0,0, 'C')
                pdf.set_font('Arial', 'B', 10)
                pdf.ln(15)

                # Text height is the same as current font size
                text_height = pdf.font_size

                # declare an array of the arrays.  Also we declared the size
                data = [['', 'Max', 'Min', 'Mean', 'Std_Dev', 'Duration']]

                # This loop used to draw the rest of the rows and to get the varibles to fill the table
                for channel_name, channel_values in self.channel_data.items():
                    if channel_values['graph_number'] == 1:
                        current_data = []
                        current_data.append(channel_name)
                        current_data.append(round(np.amax(channel_values['amplitude']), 4))
                        current_data.append(round(np.amin(channel_values['amplitude']), 4))
                        current_data.append(round(np.mean(channel_values['amplitude']), 4))
                        current_data.append(round(np.std(channel_values['amplitude']), 4))
                        current_data.append(round(np.amax(channel_values['time']), 4))
                        data.append(current_data)

                # This 2 loops draw the Table
                for row in data:
                    for datum in row:
                        if datum == row[0]:
                            pdf.set_fill_color(200, 200, 200)
                            pdf.cell(column_width, 3*text_height,str(datum), border=1, fill=True)
                        elif row == data[0]:
                            pdf.set_fill_color(200, 200, 200)
                            pdf.cell(column_width, 3*text_height,str(datum), border=1, fill=True)
                        else:
                            pdf.cell(column_width, 3*text_height,str(datum), border=1)
                    pdf.ln(3*text_height)

            # for graph2 check first if there is atleast one signal running
            if self.curves_2:
                pdf.add_page()
                # Effective page width
                epw = pdf.w - 2*pdf.l_margin
                # distribute the table on 6 columns
                column_width = epw/6

                pdf.set_font('Arial', 'B', 20)
                x , y = 10 , 50

                if not self.curves_1:
                    pdf.cell(70)
                    pdf.cell(50, 10, 'Signal Viewer Report', 0, 0, 'C')
                    pdf.ln(15)
                    y += 10
                
                pdf.cell(15, 10, 'Graph 2', 0, 0, 'L')
                pdf.ln(15)

                # iterate through snapshots of graph 1
                for i in range(min(self.snapshot2_counter,3)):
                    #                                               x   y   w    h
                    pdf.image(f'img/graph-2-snapshots/graph{i}.png', x, y, 60, 45)
                    x += 65
                pdf.ln(10)

                if self.snapshot2_counter >= 3:
                    x , y = 10 , 100
                    if not self.curves_1:
                        y += 10
                    for i in range(3,min(self.snapshot2_counter,6)):
                        #                                                x   y   w    h
                        pdf.image(f'img/graph-2-snapshots/graph{i}.png', x, y, 60, 45)
                        x += 65
                    pdf.ln(120)
                else:
                    pdf.ln(110)

                pdf.cell(50, 10, 'Statistics data',0,0, 'C')
                pdf.set_font('Arial', 'B', 10)
                pdf.ln(15)

                # Text height is the same as current font size
                text_height = pdf.font_size

                # declare an array of the arrays.  Also we declared the size
                data = [['', 'Max', 'Min', 'Mean', 'Std_Dev', 'Duration']]

                # This loop used to draw the rest of the rows and to get the varibles to fill the table
                for channel_name, channel_values in self.channel_data.items():
                    if channel_values['graph_number'] == 2:
                        current_data = []
                        current_data.append(channel_name)
                        current_data.append(round(np.amax(channel_values['amplitude']), 4))
                        current_data.append(round(np.amin(channel_values['amplitude']), 4))
                        current_data.append(round(np.mean(channel_values['amplitude']), 4))
                        current_data.append(round(np.std(channel_values['amplitude']), 4))
                        current_data.append(round(np.amax(channel_values['time']), 4))
                        data.append(current_data)

                # This 2 loops draw the Table
                for row in data:
                    for datum in row:
                        if datum == row[0]:
                            pdf.set_fill_color(200, 200, 200)
                            pdf.cell(column_width, 3*text_height,str(datum), border=1, fill=True)
                        elif row == data[0]:
                            pdf.set_fill_color(200, 200, 200)
                            pdf.cell(column_width, 3*text_height,str(datum), border=1, fill=True)
                        else:
                            pdf.cell(column_width, 3*text_height,str(datum), border=1)
                    pdf.ln(3*text_height)

            # Exporting the Pdf
            pdf.output(str(FolderPath[0]))

            # This message appears when the pdf is EXPORTED
            QtWidgets.QMessageBox.information(self, 'Done', 'PDF has been created successfully!')
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, 'Warning', "Can't Save File!")
