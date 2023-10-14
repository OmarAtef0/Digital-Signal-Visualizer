import sys
import csv
import pdf
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QSlider , QColorDialog, QAction, QTextEdit
from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtGui import QColor, QIcon, QCursor, QKeySequence
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

        #play/pause
        self.ui.PlayPauseButton_1.clicked.connect(self.toggle_playback_1)
        self.ui.PlayPauseButton_2.clicked.connect(self.toggle_playback_2)
        self.ui.PlayPauseButton_3.clicked.connect(self.toggle_playback_3)

        # Reset
        self.ui.ResetButton_1.clicked.connect(self.reset_plot)
        self.ui.ResetButton_2.clicked.connect(self.reset_plot)
        self.ui.ResetButton_1.clicked.connect(lambda: self.reset_plot(self.plot_widget_1))
        self.ui.ResetButton_2.clicked.connect(lambda: self.reset_plot(self.plot_widget_2))

        # scroll
        self.ui.HorizontalScrollBar_1.valueChanged.connect(self.scroll_graph_1_x)
        self.ui.VerticalScrollBar_1.valueChanged.connect(self.scroll_graph_1_y)
        self.ui.HorizontalScrollBar_2.valueChanged.connect(self.scroll_graph_2_x)

        #show/hide
        self.ui.ShowHide_1.stateChanged.connect(self.toggle_visibility_1)
        
        #zoom
        self.ui.ZoomSlider_1.valueChanged.connect(self.update_zoom_1)
        self.ui.ZoomSlider_2.valueChanged.connect(self.update_zoom_2)

        #speed
        self.ui.SpeedSlider_1.valueChanged.connect(self.update_playback_speed_1)
        self.ui.SpeedSlider_2.valueChanged.connect(self.update_playback_speed_2)

        #color
        self.ui.SelectColor_1.clicked.connect(lambda: self.showColorSelector(for_plot_1=True))
        self.ui.SelectColor_2.clicked.connect(lambda: self.showColorSelector(for_plot_1=False))

        #label
        self.ui.SaveButton_1.clicked.connect(self.save_channel_name)
        self.ui.SaveButton_2.clicked.connect(self.save_channel_name)
        
        #plot
        self.plot_widget_1 = self.ui.graph1
        self.plot_widget_2 = self.ui.graph2
        
        #Icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "logo.png")
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)

        #channels
        self.ui.channelsMenu_1.currentIndexChanged.connect(self.select_channel_1)
        self.ui.channelsMenu_2.currentIndexChanged.connect(self.select_channel_2)

        self.x_range_speed_1 = 0.05  # Should be done by a slider or button
        self.x_range_speed_2 = 0.05  # Should be done by a slider or button
        self.x_range_1 = [0.0, 10.0]  # Initial x-axis range for plot_widget_1
        self.x_range_2 = [0.0, 10.0]   # Initial x-axis range for plot_widget_2
        self.plot_widget_1.setMouseEnabled(x=False, y=False)
        self.plot_widget_2.setMouseEnabled(x=False, y=False)

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

        # Default Colors
        self.default_colors = [QColor(255, 0, 0),  # Red
                       QColor(0, 255, 0),  # Green
                       QColor(0, 0, 255),  # Blue
                       QColor(255, 255, 0),  # Yellow
                       QColor(255, 0, 255)]  # Magenta
        
        self.playing_port_1 = False 
        self.playing_port_2 = False
        self.zoom_level_1 = 5.0
        self.zoom_level_2 = 5.0

        #Delete Button 
        self.ui.deleteButton_1.clicked.connect(self.delete_channel_1)
        self.ui.deleteButton_2.clicked.connect(self.delete_channel_2)

        #Linking Plots 
        self.linked = False
        self.ui.linkButton.clicked.connect(self.toggle_link_plots)
        self.ui.SpeedSlider_3.valueChanged.connect(self.update_both_plots_speed)
        self.ui.ZoomSlider_3.valueChanged.connect(self.update_both_plots_zoom)
        self.ui.PlayPauseButton_3.setDisabled(True)
        self.ui.SpeedSlider_3.setDisabled(True)
        self.ui.ZoomSlider_3.setDisabled(True)
        
        ######Shortcuts########
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

    #Linking
    def toggle_link_plots(self):
        if not self.linked:
            self.playing_port_1 = True
            self.playing_port_2 = True
            # Calculate minimum x-axis range
            min_x_range = min(self.x_range_1, self.x_range_2)
            
            # Calculate minimum zoom level
            min_zoom_level = min(self.zoom_level_1, self.zoom_level_2)
            
            # Calculate minimum speed
            min_x_range_speed = min(self.x_range_speed_1, self.x_range_speed_2)
            
            # Update both plots with the minimum values
            self.x_range_1 = min_x_range
            self.x_range_2 = min_x_range
            self.zoom_level_1 = min_zoom_level
            self.zoom_level_2 = min_zoom_level
            self.x_range_speed_1 = min_x_range_speed
            self.x_range_speed_2 = min_x_range_speed
            
            # Set the linked state
            self.linked = True
            self.ui.linkButton.setText("Unlink")
            # Enable PlayPauseButton_3, SpeedSlider_3, and ZoomSlider_3
            self.ui.PlayPauseButton_3.setText("Pause")
            self.ui.PlayPauseButton_3.setEnabled(True)
            self.ui.SpeedSlider_3.setEnabled(True)
            self.ui.ZoomSlider_3.setEnabled(True)

        else:
            # Toggle the linked state back to unlinked
            self.linked = False
            self.ui.linkButton.setText("Link")
            # Disable PlayPauseButton_3, SpeedSlider_3, and ZoomSlider_3
            self.ui.PlayPauseButton_3.setText("Play")
            self.ui.PlayPauseButton_3.setDisabled(True)
            self.ui.SpeedSlider_3.setDisabled(True)
            self.ui.ZoomSlider_3.setDisabled(True)

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

    def update_both_plots_speed(self, value):
        # Update speed for both plots
        self.x_range_speed_1 = value / 100.0
        self.x_range_speed_2 = value / 100.0

    def update_both_plots_zoom(self, value):
      # Update zoom level for both plots
      self.zoom_level_1 = value / 4
      self.zoom_level_2 = value / 4
      self.x_range_1 = [0, 10 * self.zoom_level_1]
      self.x_range_2 = [0, 10 * self.zoom_level_2]
      self.plot_widget_1.setXRange(*self.x_range_1) 
      self.plot_widget_2.setXRange(*self.x_range_2)

    # Color
    def showColorSelector(self, for_plot_1=True):
        # Get the selected channel from the combo box
        selected_channel = self.ui.channelsMenu_1.currentText() if for_plot_1 else self.ui.channelsMenu_2.currentText()
        
        if selected_channel:
            color_dialog = QColorDialog(self)
            color = color_dialog.getColor()
            if color.isValid():
                # Update the color of the selected channel in the channel_data dictionary
                channel_data = self.get_channel_data(selected_channel)
                channel_data['color'] = color

                # Refresh the plot to apply the new color
                graph = self.plot_widget_1 if for_plot_1 else self.plot_widget_2
                channels_menu = self.ui.channelsMenu_1 if for_plot_1 else self.ui.channelsMenu_2
                curves = self.curves_1 if for_plot_1 else self.curves_2
                self.switch_channel(graph, channels_menu, curves)
            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Color is invalid!')

    # Reset
    def reset_plot(self, graph_frame):
      # Reset the x-axis range for the specified plot
        if graph_frame == self.plot_widget_1:
            self.x_range_1 = [0.0, 10.0]
            self.plot_widget_1.setXRange(*self.x_range_1)
            self.ui.SpeedSlider_1.setValue(4)
            self.ui.ZoomSlider_1.setValue(4)
        elif graph_frame == self.plot_widget_2:
            self.x_range_2 = [0.0, 10.0]
            self.plot_widget_2.setXRange(*self.x_range_2)
            self.ui.SpeedSlider_2.setValue(4)
            self.ui.ZoomSlider_2.setValue(4)

    # Label
    def save_channel_name(self):
        if self.sender() == self.ui.SaveButton_1:
            selected_channel = self.ui.channelsMenu_1.currentText()
            new_channel_name = self.ui.editLabel_1.text()
        else:
            selected_channel = self.ui.channelsMenu_2.currentText()
            new_channel_name = self.ui.editLabel_2.text()
        
        if new_channel_name in self.channel_data.keys():
                QtWidgets.QMessageBox.warning(self, 'Warning', 'This name is already taken!')
        else:
            # Update the channel name in the dictionary
            self.rename_channel(selected_channel, new_channel_name)
            
            # Update the channel name in the QComboBox
            if self.sender() == self.ui.SaveButton_1:
                self.ui.channelsMenu_1.setItemText(self.ui.channelsMenu_1.currentIndex(), new_channel_name)
            else:
                self.ui.channelsMenu_2.setItemText(self.ui.channelsMenu_2.currentIndex(), new_channel_name)

        # remove text in editlabel
        self.ui.editLabel_1.clear()
        self.ui.editLabel_2.clear()

    def rename_channel(self, channel_name, new_name):
        if channel_name and new_name:
            if new_name in self.channel_data.keys():
                QtWidgets.QMessageBox.warning(self, 'Warning', 'This name is already taken!')
            else:
                # Update the channel name in the combo box
                index_1 = self.ui.channelsMenu_1.findText(channel_name)
                if index_1 >= 0:
                    self.ui.channelsMenu_1.setItemText(index_1, new_name)
                index_2 = self.ui.channelsMenu_2.findText(channel_name)
                if index_2 >= 0:
                    self.ui.channelsMenu_2.setItemText(index_2, new_name)

                # Update the channel name in the data
                if channel_name in self.channel_data:
                    channel_data = self.channel_data[channel_name]
                    self.channel_data[new_name] = channel_data
                    del self.channel_data[channel_name]

    #Delete
    def delete_channel(self, graph_frame, combo_box, curves_list):
        selected_channel = combo_box.currentText()
        if selected_channel:
            # Remove the curve from the plot
            graph_frame.removeItem(curves_list[-1])
            # Remove the curve from the list
            curves_list.pop()
            # Remove the channel from the dictionary
            self.channel_data.pop(selected_channel)
            # Remove the channel from the combo box
            combo_box.removeItem(combo_box.currentIndex())

    def delete_channel_1(self):
        if self.curves_1:
            self.delete_channel(self.plot_widget_1, self.ui.channelsMenu_1, self.curves_1)
            if not self.curves_1:
                self.toggle_playback_1()

    def delete_channel_2(self):
        if self.curves_2:
            self.delete_channel(self.plot_widget_2, self.ui.channelsMenu_2, self.curves_2)
            if not self.curves_2:
                self.toggle_playback_2()

    def pdf(self):
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

    def switch_channel(self, graph_frame, combo_box, curves_list):
        selected_channel = combo_box.currentText()
        if selected_channel:
            channel_data = self.get_channel_data(selected_channel)

            graph_frame.clear()
            graph_frame.setLabel('bottom', text='Time')
            graph_frame.setLabel('left', text='Amplitude')

            curve = graph_frame.plot(channel_data['time'], channel_data['amplitude'], name = selected_channel,  pen=channel_data['color'])
            graph_frame.showGrid(x=True, y=True)
            graph_frame.addLegend()

            curves_list.clear()
            curves_list.append(curve)

    def select_channel_1(self, index):
        self.switch_channel(self.plot_widget_1, self.ui.channelsMenu_1, self.curves_1)

    def select_channel_2(self, index):
        self.switch_channel(self.plot_widget_2, self.ui.channelsMenu_2, self.curves_2)

    def get_channel_data(self, channel_name):
        if channel_name in self.channel_data:
            return self.channel_data[channel_name]
        else:
            return None  # Return None if the channel is not found

    def plot_csv_data(self, file_name, graph_frame, curves_list, combo_box, ):
        try:
            with open(file_name, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)

                # Detect whether the first row is a header (contains titles)
                has_header = csv.Sniffer().has_header(csv_file.read(1024))
                csv_file.seek(0)  # Reset the file pointer

                if has_header:
                    next(csv_reader)  # Skip the header row if it exists

                time = []
                amplitude = []

                # Set labels
                graph_frame.setLabel('bottom', text='Time')
                graph_frame.setLabel('left', text='Amplitude')

                for row in csv_reader:
                    time.append(float(row[0]))
                    amplitude.append(float(row[1]))

                # Clear existing data if it's the first plot
                if graph_frame == self.plot_widget_1 and self.is_first_plot_1:
                    graph_frame.clear()
                    self.is_first_plot_1 = False
                elif graph_frame == self.plot_widget_2 and self.is_first_plot_2:
                    graph_frame.clear()
                    self.is_first_plot_2 = False

                # Add the channel name to the list
                self.channel_counter += 1
                channel_name = f"Channel {self.channel_counter}"

                # Create a PlotDataItem to display the data
                color_index = len(curves_list) % len(self.default_colors)  
                color = self.default_colors[color_index]
                curve = graph_frame.plot(time, amplitude, name = channel_name,  pen = color)
                graph_frame.showGrid(x=True, y=True)
                graph_frame.addLegend()

                # Append the curve to the specified list
                curves_list.append(curve)

                graph_number = 0
                # Start the respective timer to move the x-axis
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
    
                # Create a dictionary to store channel data
                signal_data = {
                    'time': time,
                    'amplitude': amplitude,
                    'color': color,  # More data will be added here
                    'graph_number': graph_number,
                    'visible': True
                }

                # Update the channel data dictionary
                self.channel_data[channel_name] = signal_data

                # Add the channel name to the combo box
                combo_box.addItem(channel_name)  

        except Exception as e:
            print("Error:", str(e))

    def browse_file(self, graph_frame, curves_list, combo_box):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_name:
            playing_port = self.playing_port_1 if graph_frame == self.plot_widget_1 else self.playing_port_2
            if playing_port:
                # If it was playing, toggle the state to "Pause" when browsing
                self.toggle_playback_1() if graph_frame == self.plot_widget_1 else self.toggle_playback_2()
            self.plot_csv_data(file_name, graph_frame, curves_list, combo_box)

    def browse_file_1(self):
        self.browse_file(self.plot_widget_1, self.curves_1, self.ui.channelsMenu_1)

    def browse_file_2(self):
        self.browse_file(self.plot_widget_2, self.curves_2, self.ui.channelsMenu_2)

    def scroll_graph_1_x(self, value):
      # Calculate the new x-axis range based on the scrollbar's value
      scroll_window = self.x_range_1[1] - self.x_range_1[0]
      new_x_min = value / 100.0 * (scroll_window)
      new_x_max = new_x_min + scroll_window
      # Ensure the new_x_min doesn't go below zero
      if new_x_min < 0:
        new_x_min = 0  
        new_x_max = scroll_window

      # Set the updated x-axis range for the first plot
      self.x_range_1 = [new_x_min, new_x_max]
      self.plot_widget_1.setXRange(*self.x_range_1)

    def scroll_graph_2_x(self, value):
    # Calculate the new x-axis range based on the scrollbar's value
      scroll_window = self.x_range_2[1] - self.x_range_2[0]
      new_x_min = value / 100.0 * (scroll_window)
      new_x_max = new_x_min + scroll_window

      # Ensure the new_x_min doesn't go below zero
      if new_x_min < 0:
        new_x_min = 0
        new_x_max = scroll_window

      # Set the updated x-axis range for the first plot
      self.x_range_2 = [new_x_min, new_x_max]
      self.plot_widget_2.setXRange(*self.x_range_2)

    def scroll_graph_1_y(self, value):
        y_min = 0.0  # Minimum value for the Y-axis range
        
        signal_y_max = 1  # Maximum value for the signal range

        # Calculate the step size
        step_size = 0.1

        # Calculate the new_y_min and new_y_max based on the scrollbar value
        new_y_min = y_min + value * step_size
        new_y_max = new_y_min + signal_y_max

        # Set the updated viewable Y-axis range for the first plot
        self.plot_widget_1.setYRange(new_y_min, new_y_max)

    def toggle_playback_1(self):
      # Update the text of the "Pause/Resume" button
      self.playing_port_1 = not self.playing_port_1
      self.update_playback_button(self.playing_port_1, self.ui.PlayPauseButton_1)

      if not self.curves_1:
        self.playing_port_1 = False
        self.ui.PlayPauseButton_1.setText("Play")

    def toggle_playback_2(self):
      self.playing_port_2 = not self.playing_port_2
      self.update_playback_button(self.playing_port_2, self.ui.PlayPauseButton_2)
      
      if not self.curves_2:
        self.playing_port_2 = False
        self.ui.PlayPauseButton_2.setText("Play")

    def toggle_playback_3(self):
      self.playing_port_1 = not self.playing_port_1
      self.playing_port_2 = not self.playing_port_2
      self.update_playback_button(self.playing_port_2, self.ui.PlayPauseButton_3)

    def update_playback_button(self, playing, button):
        if playing:
            button.setText("Pause")
        else:
            button.setText("Play")

    def update_zoom_1(self, value):
      self.zoom_level_1 = value / 4
      # Update the x-axis range of the plots
      self.x_range_1 = [0, 10 * self.zoom_level_1]
      self.plot_widget_1.setXRange(*self.x_range_1) 

    def update_zoom_2(self, value):
      self.zoom_level_2 = value / 4
      # Update the x-axis range of the plots
      self.x_range_2 = [0, 10 * self.zoom_level_2]
      self.plot_widget_2.setXRange(*self.x_range_2)

    def update_playback_speed_1(self, value):
      self.x_range_speed_1 = (value / 100.0) +0.01

    def update_playback_speed_2(self, value):
      self.x_range_speed_2 = (value / 100.0) +0.01

    def toggle_visibility_1(self):
        selected_channel = self.ui.channelsMenu_1.currentText()
        self.plot_widget_1.clear()

        if self.ui.ShowHide_1.isChecked():
            self.channel_data[selected_channel]['visible'] = True
        else:
            self.channel_data[selected_channel]['visible'] = False

        # Force a redraw of the plot to reflect the changes
        for signal_name , signal in self.channel_data.items():
            print("signal name : ",signal_name,"  ", signal['visible'])
            if signal['visible'] == True:
                curve = self.plot_widget_1.plot(signal['time'], signal['amplitude'], pen=signal['color'])
                self.curves_1.append(curve)

    def toggle_visibility_2(self):
        selected_channel = self.ui.channelsMenu_2.currentText()
        self.plot_widget_2.clear()

        if self.ui.ShowHide_2.isChecked():
            self.channel_data[selected_channel]['visible'] = True
        else:
            self.channel_data[selected_channel]['visible'] = False

        # Force a redraw of the plot to reflect the changes
        for signal_name , signal in self.channel_data.items():
            print("signal name : ",signal_name,"  ", signal['visible'])
            if signal['visible'] == True:
                curve = self.plot_widget_2.plot(signal['time'], signal['amplitude'], pen=signal['color'])
                self.curves_2.append(curve)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalViewerApp()
    window.setWindowTitle("Digital Signal Viewer")
    app.setWindowIcon(QIcon("img/logo.png"))
    window.resize(1100,850)
    window.show()
    sys.exit(app.exec_())
