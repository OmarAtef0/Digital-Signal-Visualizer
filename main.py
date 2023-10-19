import sys
import csv
import pdf
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QSlider , QColorDialog, QAction, QTextEdit
from PyQt5.QtCore import QTimer,Qt, QPointF
from PyQt5.QtGui import QColor, QIcon, QCursor, QKeySequence
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar, QDialog, QVBoxLayout
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from task1 import Ui_MainWindow
import os
class SignalViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set up the UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  

        #pdf
        self.ui.pdfButton.clicked.connect(self.pdf)

        #browse
        self.ui.BrowseButton_1.clicked.connect(self.browse_file_1)
        self.ui.BrowseButton_2.clicked.connect(self.browse_file_2)
        # self.ui.BrowseButton_2.clicked.connect(self.show_popup)

        #play/pause
        self.ui.PlayPauseButton_1.clicked.connect(self.toggle_playback_1)
        self.ui.PlayPauseButton_2.clicked.connect(self.toggle_playback_2)
        self.ui.PlayPauseButton_3.clicked.connect(self.toggle_playback_3)

        # Reset
        self.ui.ResetButton_1.clicked.connect(lambda: self.reset_plot(for_plot_1=True))
        self.ui.ResetButton_2.clicked.connect(lambda: self.reset_plot(for_plot_1=False))
        self.ui.ResetButton_3.clicked.connect(lambda: self.reset_plot(for_plot_1=True))

        #show/hide
        self.ui.ShowHide_1.stateChanged.connect(self.toggle_visibility_1)
        self.ui.ShowHide_2.stateChanged.connect(self.toggle_visibility_2)

        #speed
        self.ui.SpeedSlider_1.valueChanged.connect(self.update_playback_speed_1)
        self.ui.SpeedSlider_2.valueChanged.connect(self.update_playback_speed_2)

        #color
        self.ui.SelectColor_1.clicked.connect(lambda: self.showColorSelector(for_plot_1=True))
        self.ui.SelectColor_2.clicked.connect(lambda: self.showColorSelector(for_plot_1=False))

        #label
        self.ui.SaveButton_1.clicked.connect(lambda: self.save_channel_name(for_plot_1=True))
        self.ui.SaveButton_2.clicked.connect(lambda: self.save_channel_name(for_plot_1=False))
        
        #plot
        self.plot_widget_1 = self.ui.graph1
        self.plot_widget_2 = self.ui.graph2

        #channels
        self.ui.channelsMenu_1.currentIndexChanged.connect(lambda: self.switch_channel(for_plot_1=True))
        self.ui.channelsMenu_2.currentIndexChanged.connect(lambda: self.switch_channel(for_plot_1=False))

        #x-range
        self.x_range_speed_1 = 0.05  
        self.x_range_speed_2 = 0.05  
        self.x_range_1 = [0.0, 10.0]  
        self.x_range_2 = [0.0, 10.0]   

        #mouse
        self.plot_widget_1.setMouseEnabled(x=False, y=False)
        self.plot_widget_2.setMouseEnabled(x=False, y=False)

        #timers
        self.timer_1 = QTimer(self)
        self.timer_1.timeout.connect(self.update_plot_1)

        self.timer_2 = QTimer(self)
        self.timer_2.timeout.connect(self.update_plot_2)

        self.is_first_plot_1 = True
        self.is_first_plot_2 = True

        # Lists to store curves for each plot widget
        self.curves_1 = []
        self.curves_2 = []

        # Dict to store channel data (time, color, amplitude, etc..)
        self.channel_data = {}
        self.channel_counter = 0
        self.snapshot1_counter = 0
        self.snapshot2_counter = 0
        self.zoom_level_1 = 5.0
        self.zoom_level_2 = 5.0
        self.playing_port_1 = False 
        self.playing_port_2 = False

        # Default Colors
        self.default_colors = [QColor(255, 0, 0),  # Red
                       QColor(0, 255, 0),  # Green
                       QColor(0, 0, 255),  # Blue
                       QColor(255, 255, 0),  # Yellow
                       QColor(255, 0, 255)]  # Magenta
    
        #Delete Button 
        self.ui.deleteButton_1.clicked.connect(self.delete_channel_1)
        self.ui.deleteButton_2.clicked.connect(self.delete_channel_2)

        #Snapshot Button 
        self.ui.snapshot_1.clicked.connect(self.snapshot1)
        self.ui.snapshot_2.clicked.connect(self.snapshot2)

        #Linking Plots 
        self.linked = False
        self.ui.linkButton.clicked.connect(self.toggle_link_plots)
        self.ui.SpeedSlider_3.valueChanged.connect(self.update_playback_speed_3)
        self.ui.PlayPauseButton_3.setDisabled(True)
        self.ui.SpeedSlider_3.setDisabled(True)
        self.ui.ResetButton_3.setDisabled(True)
        
        #------------Shortcuts-----------------------------------------------------

        #Snapshot Button Shortcut
        self.snap1_button_shortcut = QKeySequence("Ctrl+S")
        self.snap1_action = QAction(self)
        self.snap1_action.setShortcut(self.snap1_button_shortcut)
        self.snap1_action.triggered.connect(self.snapshot1)
        self.addAction(self.snap1_action)

        self.snap2_button_shortcut = QKeySequence("Ctrl+D")
        self.snap2_action = QAction(self)
        self.snap2_action.setShortcut(self.snap2_button_shortcut)
        self.snap2_action.triggered.connect(self.snapshot2)
        self.addAction(self.snap2_action)

        #Delete Snapshot Shortcut
        self.snap1_delete_shortcut = QKeySequence("Shift+Ctrl+S")
        self.snap1_delete_action = QAction(self)
        self.snap1_delete_action.setShortcut(self.snap1_delete_shortcut)
        self.snap1_delete_action.triggered.connect(self.snapshot1_delete)
        self.addAction(self.snap1_delete_action)

        self.snap2_delete_shortcut = QKeySequence("Shift+Ctrl+D")
        self.snap2_delete_action = QAction(self)
        self.snap2_delete_action.setShortcut(self.snap2_delete_shortcut)
        self.snap2_delete_action.triggered.connect(self.snapshot2_delete)
        self.addAction(self.snap2_delete_action)

        #Link Button Shortcut
        self.link_button_shortcut = QKeySequence("Ctrl+L")
        self.link_action = QAction(self)
        self.link_action.setShortcut(self.link_button_shortcut)
        self.link_action.triggered.connect(self.toggle_link_plots)
        self.addAction(self.link_action)

        #Browse File Shortcut
        self.browse_file_1_shortcut = QKeySequence("Ctrl+N")
        self.browse_file_1_action = QAction(self)
        self.browse_file_1_action.setShortcut(self.browse_file_1_shortcut)
        self.browse_file_1_action.triggered.connect(self.browse_file_1)
        self.addAction(self.browse_file_1_action)
        
        self.browse_file_2_shortcut = QKeySequence("Ctrl+Shift+N")
        self.browse_file_2_action = QAction(self)
        self.browse_file_2_action.setShortcut(self.browse_file_2_shortcut)
        self.browse_file_2_action.triggered.connect(self.browse_file_2)
        self.addAction(self.browse_file_2_action)

        #Play Pause Button Shortcut
        self.play_pause_1_shortcut = QKeySequence("Space")
        self.play_pause_1_action = QAction(self)
        self.play_pause_1_action.setShortcut(self.play_pause_1_shortcut)
        self.play_pause_1_action.triggered.connect(self.toggle_playback_1)
        self.addAction(self.play_pause_1_action)

        self.play_pause_2_shortcut = QKeySequence("Ctrl+Space")
        self.play_pause_2_action = QAction(self)
        self.play_pause_2_action.setShortcut(self.play_pause_2_shortcut)
        self.play_pause_2_action.triggered.connect(self.toggle_playback_2)
        self.addAction(self.play_pause_2_action)

        #scroll bars
        self.ui.HorizontalScrollBar_1.valueChanged.connect(self.scroll_graph_1_x)
        self.ui.HorizontalScrollBar_2.valueChanged.connect(self.scroll_graph_2_x)
        self.ui.VerticalScrollBar_1.valueChanged.connect(self.scroll_graph_1_y)
        self.ui.VerticalScrollBar_2.valueChanged.connect(self.scroll_graph_2_y)
        
        self.ui.VerticalScrollBar_1.setRange(-80,80)
        self.ui.VerticalScrollBar_2.setRange(-80,80)
        self.ui.VerticalScrollBar_1.setSingleStep(10)
        self.ui.VerticalScrollBar_2.setSingleStep(5)

        self.warn1 = False
        self.warn2 = False

        self.MaxX = 0
        self.MaxY = 0
        self.MinX = 0
        self.MinY = 0

        #drag and drop 
        self.ui.Move_1.clicked.connect(self.move_to2)
        self.ui.Move_2.clicked.connect(self.move_to1)

    def move_to2(self):
        selected_channel = self.ui.channelsMenu_1.currentText() 
        print(selected_channel)

        if selected_channel == "All Channels":
            QtWidgets.QMessageBox.warning(self, 'Warning', 'You cannot move all channels at once')
        else:
            self.channel_data[selected_channel]['graph_number'] = 2

            index_1 = self.ui.channelsMenu_1.findText(selected_channel)
            self.ui.channelsMenu_1.removeItem(index_1)
            self.ui.channelsMenu_1.setCurrentIndex(0)
            
            self.ui.channelsMenu_2.addItem(selected_channel)
            self.ui.channelsMenu_2.setCurrentIndex(0)

            self.timer_2.start(100)
            self.ui.PlayPauseButton_2.setText("Pause")
            self.playing_port_2 = True

            if self.ui.channelsMenu_1.count() == 1:
                self.playing_port_1 = False
                self.ui.PlayPauseButton_1.setText("Play")

            self.redraw1()
            self.redraw2()

    def move_to1(self):
        selected_channel = self.ui.channelsMenu_2.currentText() 
        print(selected_channel)
        
        if selected_channel == "All Channels":
            QtWidgets.QMessageBox.warning(self, 'Warning', 'You cannot move all channels at once')
        else:
            self.channel_data[selected_channel]['graph_number'] = 1

            index_2 = self.ui.channelsMenu_2.findText(selected_channel)
            self.ui.channelsMenu_2.removeItem(index_2)
            self.ui.channelsMenu_2.setCurrentIndex(0)
            
            self.ui.channelsMenu_1.addItem(selected_channel)
            self.ui.channelsMenu_1.addItem(selected_channel)
            self.ui.channelsMenu_1.setCurrentIndex(0)

            self.timer_1.start(100)
            self.ui.PlayPauseButton_1.setText("Pause")
            self.playing_port_1 = True

            if self.ui.channelsMenu_2.count() == 1:
                self.playing_port_2 = False
                self.ui.PlayPauseButton_2.setText("Play")

            self.redraw1()
            self.redraw2()

    def snapshot1(self):
        if not self.curves_1:
            return
        if self.warn1:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'You can take only 6 snapshots!')
            return

        ex = pg.exporters.ImageExporter(self.ui.graph1.plotItem)
        ex.export(f'img/graph-1-snapshots/graph{self.snapshot1_counter}.png')
        print(f"snapshot1 : {self.snapshot1_counter} TAKEN")
        if self.snapshot1_counter < 6: 
            self.snapshot1_counter += 1
        if self.snapshot1_counter == 6:
            self.warn1 = True
    
    def snapshot2(self):
        if not self.curves_2:
            return
        if self.warn2:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'You can take only 6 snapshots!')
            return
        
        ex = pg.exporters.ImageExporter(self.ui.graph2.plotItem)
        ex.export(f'img/graph-2-snapshots/graph{self.snapshot2_counter}.png')
        print(f"snapshot2 : {self.snapshot2_counter} TAKEN")
        if self.snapshot2_counter < 6: 
            self.snapshot2_counter += 1
        if self.snapshot2_counter == 6:
            self.warn2 = True
    
    def snapshot1_delete(self):
        self.warn1 = False
        print(f"delete {self.snapshot1_counter-1}")
        if self.snapshot1_counter > 0:
            self.snapshot1_counter -= 1
            os.remove(f'img/graph-1-snapshots/graph{self.snapshot1_counter}.png')
        
    def snapshot2_delete(self):
        self.warn2 = False
        print(f"delete {self.snapshot2_counter-1}")
        if self.snapshot2_counter > 0:
            self.snapshot2_counter -= 1
            os.remove(f'img/graph-2-snapshots/graph{self.snapshot2_counter}.png')
            
    def scroll_graph_1_x(self, value):
    # Calculate the new x-axis range based on the scrollbar's value
      scroll_window = self.x_range_1[1] - self.x_range_1[0]
      x_min = value / 100.0 * (scroll_window)
      x_max = x_min + scroll_window
      # Ensure the x_min doesn't go below zero
      if x_min < 0:
        x_min = 0  
        x_max = scroll_window

      # Set the updated x-axis range for the first plot
      self.x_range_1 = [x_min, x_max]
      self.plot_widget_1.setXRange(*self.x_range_1)

      if self.linked:
        self.x_range_2 = self.x_range_1
        self.plot_widget_2.setXRange(*self.x_range_2)
     
    def scroll_graph_2_x(self, value):
        scroll_window = self.x_range_2[1] - self.x_range_2[0]
        x_min = value / 100.0 * (scroll_window)
        x_max = x_min + scroll_window

        # Ensure the x_min doesn't go below zero
        if x_min < 0:
            x_min = 0
            x_max = scroll_window

        # Set the updated x-axis range for the first plot
        self.x_range_2 = [x_min, x_max]
        self.plot_widget_2.setXRange(*self.x_range_2)

        if self.linked:
            self.x_range_1 = self.x_range_2
            self.plot_widget_1.setXRange(*self.x_range_1)
      
    def scroll_graph_1_y(self, value):
      self.find_limits(True)
      min_y = self.MinY + value / 100
      max_y = self.MaxY + value / 100  
      self.plot_widget_1.setYRange(min_y, max_y)

      if self.linked:
        self.plot_widget_2.setYRange(min_y, max_y)
    
    def scroll_graph_2_y(self, value):
      self.find_limits(False)
      min_y = self.MinY + value/100
      max_y = self.MaxY + value/100  
      self.plot_widget_2.setYRange(min_y, max_y)

      if self.linked:
        self.plot_widget_1.setYRange(min_y, max_y)

    def find_limits(self,for_plot_1=True):
        if for_plot_1:
            graph_number = 1
        else:
            graph_number = 2

        for signal_name , signal in self.channel_data.items():
                if signal['visible'] == True and signal['graph_number'] == graph_number:
                    if max(signal['time']) > self.MaxX:
                        self.MaxX = max(signal['time'])

                    if min(signal['time']) < self.MinX:
                        self.MinX = min(signal['time'])

                    if max(signal['amplitude']) > self.MaxY:
                        self.MaxY = max(signal['amplitude'])

                    if min(signal['amplitude']) < self.MinY:
                        self.MinY = min(signal['amplitude'])

    def redraw1(self):
        self.plot_widget_1.clear()
        self.find_limits(True)
        if self.ui.channelsMenu_1.currentText() == "All Channels":
            for signal_name , signal in self.channel_data.items():
                if signal['visible'] == True and signal['graph_number'] == 1:
                    curve = self.plot_widget_1.plot(signal['time'], signal['amplitude'], pen=signal['color'], name=signal_name)
                    self.curves_1.append(curve)
        else:
            signal = self.get_channel_data(self.ui.channelsMenu_1.currentText())
            if signal['visible'] == True and signal['graph_number'] == 1:
                curve = self.plot_widget_1.plot(signal['time'], signal['amplitude'], pen=signal['color'], name=self.ui.channelsMenu_1.currentText())
                self.curves_1.append(curve)
                
        self.plot_widget_1.plotItem.setLimits(xMin=self.MinX-0.5, xMax=self.MaxX+0.5, yMin=self.MinY-0.5, yMax=self.MaxY+0.5)
        self.plot_widget_1.setLabel('bottom', text='Time')
        self.plot_widget_1.setLabel('left', text='Amplitude')
        self.plot_widget_1.showGrid(x=True, y=True)
        self.plot_widget_1.addLegend()
    
    def redraw2(self):
        self.plot_widget_2.clear()
        self.find_limits(False)
        if self.ui.channelsMenu_2.currentText() == "All Channels":
            for signal_name , signal in self.channel_data.items():
                if signal['visible'] == True and signal['graph_number'] == 2:
                    curve = self.plot_widget_2.plot(signal['time'], signal['amplitude'], pen=signal['color'], name=signal_name)
                    self.curves_2.append(curve)
        else:
            signal = self.get_channel_data(self.ui.channelsMenu_2.currentText())
            if signal['visible'] == True and signal['graph_number'] == 2:
                curve = self.plot_widget_2.plot(signal['time'], signal['amplitude'], pen=signal['color'], name=self.ui.channelsMenu_2.currentText())
                self.curves_2.append(curve)
            
        self.plot_widget_2.plotItem.setLimits(xMin=self.MinX-0.5, xMax=self.MaxX+0.5, yMin=self.MinY-0.5, yMax=self.MaxY+0.5)
        self.plot_widget_2.setLabel('bottom', text='Time')
        self.plot_widget_2.setLabel('left', text='Amplitude')
        self.plot_widget_2.showGrid(x=True, y=True)
        self.plot_widget_2.addLegend()

    #Linking
    def toggle_link_plots(self):
        if not self.curves_1 or not self.curves_2:
            return

        if not self.linked:
            min_x_range = min(self.x_range_1, self.x_range_2)
            min_zoom_level = min(self.zoom_level_1, self.zoom_level_2)
            min_x_range_speed = min(self.x_range_speed_1, self.x_range_speed_2)
            
            # Update both plots with the minimum values
            self.x_range_1 = min_x_range
            self.x_range_2 = min_x_range
            self.zoom_level_1 = min_zoom_level
            self.zoom_level_2 = min_zoom_level
            self.x_range_speed_1 = min_x_range_speed
            self.x_range_speed_2 = min_x_range_speed
            
            # Set the linked state
            if not self.playing_port_1:
                self.toggle_playback_1()
            if not self.playing_port_2:
                self.toggle_playback_2()

            self.linked = True
            self.ui.linkButton.setText("Unlink")
            self.ui.PlayPauseButton_3.setText("Pause")
            self.ui.PlayPauseButton_3.setEnabled(True)
            self.ui.ResetButton_3.setEnabled(True)
            self.ui.SpeedSlider_3.setEnabled(True)
            
        else:
            # Toggle the linked state back to unlinked
            self.linked = False
            self.ui.linkButton.setText("Link")
            self.ui.PlayPauseButton_3.setText("Play")
            self.ui.PlayPauseButton_3.setDisabled(True)
            self.ui.SpeedSlider_3.setDisabled(True)

            if self.playing_port_1:
                self.ui.PlayPauseButton_1.setText("Pause") 
                self.ui.PlayPauseButton_2.setText("Pause") 
            else:
                self.ui.PlayPauseButton_1.setText("Play") 
                self.ui.PlayPauseButton_2.setText("Play") 

        # Enable or disable ControlPanel_1 and ControlPanel_2 as needed
        self.ui.ControlPanel_1.setDisabled(self.linked)
        self.ui.ControlPanel_2.setDisabled(self.linked)
        self.ui.PlayPauseButton_1.setDisabled(self.linked)
        self.ui.PlayPauseButton_2.setDisabled(self.linked)

        btn_active = """
        QPushButton {
            background-color: rgb(0, 85, 255);
            color: rgb(255, 255, 255);
            border-radius: 5px;
        }
        
        QPushButton:hover {
            background-color: rgb(0, 50, 150);
        }"""

        btn_inactive = """
        QPushButton {
            background-color: rgba(0, 85, 255,0.7);
            color: rgb(255, 255, 255);
            border-radius: 5px;
        }
        """

        if self.linked:
            self.ui.PlayPauseButton_1.setStyleSheet(btn_inactive)
            self.ui.PlayPauseButton_2.setStyleSheet(btn_inactive)
            self.ui.PlayPauseButton_3.setStyleSheet(btn_active)
        else:
            self.ui.PlayPauseButton_1.setStyleSheet(btn_active)
            self.ui.PlayPauseButton_2.setStyleSheet(btn_active)
            self.ui.PlayPauseButton_3.setStyleSheet(btn_inactive)

    # Color
    def showColorSelector(self, for_plot_1=True):
        if for_plot_1:
            selected_channel = self.ui.channelsMenu_1.currentText() 
        else:
            selected_channel = self.ui.channelsMenu_2.currentText()
        
        if selected_channel:
            color_dialog = QColorDialog(self)
            color = color_dialog.getColor()
            if color.isValid():
                channel_data = self.get_channel_data(selected_channel)
                channel_data['color'] = color

                # Refresh the plot to apply the new color
                if for_plot_1:
                    self.redraw1()
                else: 
                    self.redraw2()
            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Color is invalid!')

    # Reset
    def reset_plot(self, for_plot_1=True):
        if self.linked:
            self.x_range_1 = [0.0, 10.0]
            self.ui.VerticalScrollBar_1.setValue(0)
            self.ui.HorizontalScrollBar_1.setValue(0)
            self.plot_widget_1.setXRange(*self.x_range_1)
            self.x_range_speed_1 = 0.05
            self.ui.SpeedSlider_1.setValue(4)
            self.update_playback_speed_1(self.ui.SpeedSlider_1.value())
            self.redraw1()

            self.x_range_2 = [0.0, 10.0]
            self.ui.VerticalScrollBar_2.setValue(0)
            self.ui.HorizontalScrollBar_2.setValue(0)
            self.plot_widget_2.setXRange(*self.x_range_2)
            self.x_range_speed_2 = 0.05
            self.ui.SpeedSlider_2.setValue(4)
            self.update_playback_speed_2(self.ui.SpeedSlider_2.value())
            self.redraw2()
        elif for_plot_1:
            self.x_range_1 = [0.0, 10.0]
            self.x_range_speed_1 = 0.05
            self.ui.SpeedSlider_1.setValue(4)
            self.update_playback_speed_1(self.ui.SpeedSlider_1.value())
            self.plot_widget_1.setXRange(*self.x_range_1)
            self.ui.VerticalScrollBar_1.setValue(0)
            self.ui.HorizontalScrollBar_1.setValue(0)
            self.redraw1()
        elif not for_plot_1:
            self.x_range_2 = [0.0, 10.0]
            self.x_range_speed_2 = 0.05
            self.ui.SpeedSlider_2.setValue(4)
            self.update_playback_speed_2(self.ui.SpeedSlider_2.value())
            self.plot_widget_2.setXRange(*self.x_range_2)
            self.ui.VerticalScrollBar_2.setValue(0)
            self.ui.HorizontalScrollBar_2.setValue(0)
            self.redraw2()

    def save_channel_name(self, for_plot_1=True):
        if for_plot_1:
            selected_channel = self.ui.channelsMenu_1.currentText()
            new_name = self.ui.editLabel_1.text()
            self.ui.editLabel_1.clear()
        else:
            selected_channel = self.ui.channelsMenu_2.currentText()
            new_name = self.ui.editLabel_2.text()
            self.ui.editLabel_2.clear()
        
        if new_name in self.channel_data.keys():
            QtWidgets.QMessageBox.warning(self, 'Warning', 'This name is already taken!')
        elif not new_name:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Invalid Name!')
        else:
            # Update the channel name in the data
            if selected_channel in self.channel_data:
                channel_data = self.channel_data[selected_channel]
                self.channel_data[new_name] = channel_data
                del self.channel_data[selected_channel]

            # Update the channel name in the combo box & replot
            if for_plot_1:
                index_1 = self.ui.channelsMenu_1.findText(selected_channel)
                self.ui.channelsMenu_1.setItemText(index_1, new_name)
                self.redraw1()
            else:
                index_2 = self.ui.channelsMenu_2.findText(selected_channel)
                self.ui.channelsMenu_2.setItemText(index_2, new_name)
                self.redraw2()

    def delete_channel(self, graph_frame, combo_box, curves_list):
        selected_channel = combo_box.currentText()

        if self.channel_data[selected_channel]:
            graph_frame.removeItem(curves_list[-1])
            curves_list.pop()
            self.channel_data.pop(selected_channel)
            combo_box.removeItem(combo_box.currentIndex())

    def delete_channel_1(self):
        if self.curves_1:
            self.delete_channel(self.plot_widget_1, self.ui.channelsMenu_1, self.curves_1)

        if self.ui.channelsMenu_1.count() == 1:
            self.playing_port_1 = False
            self.ui.PlayPauseButton_1.setText("Play")

    def delete_channel_2(self):
        if self.curves_2:
            self.delete_channel(self.plot_widget_2, self.ui.channelsMenu_2, self.curves_2)

        if self.ui.channelsMenu_2.count() == 1:
            self.playing_port_2 = False
            self.ui.PlayPauseButton_2.setText("Play")

    def pdf(self):
        if self.snapshot1_counter == 0 and self.snapshot2_counter == 0:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'You must take atleast one snapshot!')
        elif not self.curves_1 and not self.curves_2:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'You have to plot a signal first!')
            return
        
        pdf.Exporter(self)

    def update_plot_1(self):
      if not self.playing_port_1:
        return
      # Update the x-axis range for the first plot
      self.x_range_1 = [self.x_range_1[0] + self.x_range_speed_1, self.x_range_1[1] + self.x_range_speed_1]
      # Set the updated x-axis range for the first plot
      self.plot_widget_1.setXRange(*self.x_range_1)

    def update_plot_2(self):
      if not self.playing_port_2:
        return
      # Update the x-axis range for the second plot
      self.x_range_2 = [self.x_range_2[0] + self.x_range_speed_2, self.x_range_2[1] + self.x_range_speed_2]
      # Set the updated x-axis range for the second plot
      self.plot_widget_2.setXRange(*self.x_range_2)

    def switch_channel(self, for_plot_1=True):
        if for_plot_1:
            self.redraw1()
            selected_channel = self.ui.channelsMenu_1.currentText()
            if selected_channel == "All Channels":
                self.ui.SelectColor_1.setDisabled(True)
                self.ui.editLabel_1.setDisabled(True)
                self.ui.SaveButton_1.setDisabled(True)
                self.ui.Move_1.setDisabled(True)
                self.ui.deleteButton_1.setDisabled(True)
            else:
                self.ui.SelectColor_1.setEnabled(True)
                self.ui.editLabel_1.setEnabled(True)
                self.ui.SaveButton_1.setEnabled(True)
                self.ui.Move_1.setEnabled(True)
                self.ui.deleteButton_1.setEnabled(True)

        else:
            self.redraw2()
            selected_channel = self.ui.channelsMenu_2.currentText()
            if selected_channel == "All Channels":
                self.ui.SelectColor_2.setDisabled(True)
                self.ui.editLabel_2.setDisabled(True)
                self.ui.SaveButton_2.setDisabled(True)
                self.ui.Move_2.setDisabled(True)
                self.ui.deleteButton_2.setDisabled(True)

            else:
                self.ui.SelectColor_2.setEnabled(True)
                self.ui.editLabel_2.setEnabled(True)
                self.ui.SaveButton_2.setEnabled(True)
                self.ui.Move_2.setEnabled(True)
                self.ui.deleteButton_2.setEnabled(True)
        
    def get_channel_data(self, channel_name):
        if channel_name in self.channel_data:
            return self.channel_data[channel_name]
        else:
            return None  

    def plot_csv_data(self, file_name, graph_frame, curves_list, combo_box, ):
        try:
            with open(file_name, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)

                # Detect whether the first row is a header (contains titles)
                has_header = csv.Sniffer().has_header(csv_file.read(1024))

                # Reset the file pointer
                csv_file.seek(0)  
                
                # Skip the header row if it exists
                if has_header:
                    next(csv_reader)  

                time = []
                amplitude = []

                for row in csv_reader:
                    time.append(float(row[0]))
                    amplitude.append(float(row[1]))

                graph_number = 0
                if graph_frame == self.plot_widget_1:
                    self.timer_1.start(100)
                    self.ui.PlayPauseButton_1.setText("Pause")
                    self.playing_port_1 = True
                    graph_number = 1
                elif graph_frame == self.plot_widget_2:
                    self.timer_2.start(100)
                    self.ui.PlayPauseButton_2.setText("Pause")
                    self.playing_port_2 = True
                    graph_number = 2
    
                # get color
                color_index = len(curves_list) % len(self.default_colors)  
                color = self.default_colors[color_index]

                # get channel name
                self.channel_counter += 1
                channel_name = f"Channel {self.channel_counter}"

                signal_data = {
                    'time': time,
                    'amplitude': amplitude,
                    'color': color,  
                    'graph_number': graph_number,
                    'visible': True
                }

                # Update the channel data dictionary
                self.channel_data[channel_name] = signal_data
                # Add the channel name to the combo box
                combo_box.addItem(channel_name) 
                
                index = combo_box.findText(channel_name)
                combo_box.setCurrentIndex(index)

                if graph_number == 1:
                    self.redraw1()
                else:
                    self.redraw2()
                
        except Exception as e:
            print("Error:", str(e))

    def browse_file(self, graph_frame, curves_list, combo_box, playing_port):
        if self.linked:
            return

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", )

        if file_name:
            if playing_port:
                # If it was playing, toggle the state to "Pause" when browsing
                self.toggle_playback_1() if graph_frame == self.plot_widget_1 else self.toggle_playback_2()
            self.plot_csv_data(file_name, graph_frame, curves_list, combo_box)

    def browse_file_1(self):
        self.browse_file(self.plot_widget_1, self.curves_1, self.ui.channelsMenu_1,self.playing_port_1)

    def browse_file_2(self):
        self.browse_file(self.plot_widget_2, self.curves_2, self.ui.channelsMenu_2,self.playing_port_2)

    def toggle_playback_1(self):
        if not self.linked:
            if self.ui.channelsMenu_1.count() == 1:
                self.playing_port_1 = False
                self.ui.PlayPauseButton_1.setText("Play")
                return

            if self.playing_port_1:
                self.ui.PlayPauseButton_1.setText("Play")
            else:
                self.ui.PlayPauseButton_1.setText("Pause")
            
            self.playing_port_1 = not self.playing_port_1
            
    def toggle_playback_2(self):
        if not self.linked:
            if self.ui.channelsMenu_2.count() == 1:
                self.playing_port_2 = False
                self.ui.PlayPauseButton_2.setText("Play")
                return
            
            if self.playing_port_2:
                self.ui.PlayPauseButton_2.setText("Play")
            else:
                self.ui.PlayPauseButton_2.setText("Pause")

            self.playing_port_2 = not self.playing_port_2
            
    def toggle_playback_3(self):
        self.playing_port_1 = not self.playing_port_1
        self.playing_port_2 = not self.playing_port_2

        if self.playing_port_2:
            self.ui.PlayPauseButton_3.setText("Pause")
        else:
            self.ui.PlayPauseButton_3.setText("Play")

    def update_playback_speed_1(self, value):
      self.x_range_speed_1 = (value / 100.0) + 0.1

    def update_playback_speed_2(self, value):
      self.x_range_speed_2 = (value / 100.0) + 0.1 

    def update_playback_speed_3(self, value):
        self.x_range_speed_2 = self.x_range_speed_1 
        self.update_playback_speed_1(value)
        self.update_playback_speed_2(value)

    def toggle_visibility_1(self):
        selected_channel = self.ui.channelsMenu_1.currentText()

        if selected_channel == "All Channels":
            for _ , signal in self.channel_data.items():
                signal['visible'] = not signal['visible']
        else:
            self.channel_data[selected_channel]['visible'] = not self.channel_data[selected_channel]['visible']

        self.redraw1()

    def toggle_visibility_2(self):
        selected_channel = self.ui.channelsMenu_2.currentText()

        if selected_channel == "All Channels":
            for _ , signal in self.channel_data.items():
                signal['visible'] = not signal['visible']
        else:
            self.channel_data[selected_channel]['visible'] = not self.channel_data[selected_channel]['visible']

        self.redraw2()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalViewerApp()
    window.setWindowTitle("Digital Signal Viewer")
    app.setWindowIcon(QIcon("img/logo.png"))
    window.resize(1250,900)
    window.show()
    sys.exit(app.exec_())