import sys
import csv
import numpy as np
import pdf
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QSlider , QColorDialog
from PyQt5.QtCore import QTimer ,Qt
from PyQt5.QtGui import QColor, QIcon , QPen
from pyqtgraph import PlotWidget
from pyqtgraph.graphicsItems import TextItem
from task1 import Ui_MainWindow


class SignalViewerApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the UI

        #pdf
        self.ui.pdfButton.clicked.connect(self.pdf)

        #browse
        self.ui.BrowseButton_1.clicked.connect(self.browse_file_1)
        self.ui.BrowseButton_2.clicked.connect(self.browse_file_2)

        #play/pause
        self.ui.PlayPauseButton_1.clicked.connect(self.toggle_playback_1)
        self.ui.PlayPauseButton_2.clicked.connect(self.toggle_playback_2)

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
        self.ui.SelectColor_1.clicked.connect(self.showColorSelector)
        self.ui.SelectColor_2.clicked.connect(self.showColorSelector)

        #label
        self.ui.SaveButton_1.clicked.connect(self.save_channel_name)
        self.ui.SaveButton_2.clicked.connect(self.save_channel_name)
        
        #plot
        self.plot_widget_1 = self.ui.graph1
        self.plot_widget_2 = self.ui.graph2

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

    # #detect change in selected channel
    # def onChannelChange1(self):
    #     selected_text = self.ui.channelsMenu_1.currentText()
    #     selectedSignalIndex = selected_text[-1]
    #     print(f"selectedSignalIndex: {selectedSignalIndex}")
    
    # def onChannelChange2(self):
    #     selected_text = self.ui.channelsMenu_2.currentText()
    #     selectedSignalIndex = int(selected_text[-1]) + 5
    #     print(f"selectedSignalIndex: {selectedSignalIndex}")
        # Initialize the playing state


    # Color

    def showColorSelector(self):
        # Get the selected channel from the combo box
        selected_channel = self.ui.channelsMenu_1.currentText() if self.ui.graph1.isVisible() else self.ui.channelsMenu_2.currentText()
        
        if selected_channel:
            color_dialog = QColorDialog(self)
            color = color_dialog.getColor()
            if color.isValid():
                # Update the color of the selected channel in the channel_data dictionary
                channel_data = self.get_channel_data(selected_channel)
                channel_data['color'] = color

                # Refresh the plot to apply the new color
                self.switch_channel(self.plot_widget_1 if self.ui.graph1.isVisible() else self.plot_widget_2, self.ui.channelsMenu_1 if self.ui.graph1.isVisible() else self.ui.channelsMenu_2, self.curves_1 if self.ui.graph1.isVisible() else self.curves_2)
            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Color is invalid!')


    # Reset
    def reset_plot(self, graph_frame):
        # Reset the x-axis range for the specified plot
        if graph_frame == self.plot_widget_1:
            self.x_range_1 = [0.0, 10.0]
            self.plot_widget_1.setXRange(*self.x_range_1)
        elif graph_frame == self.plot_widget_2:
            self.x_range_2 = [0.0, 10.0]
            self.plot_widget_2.setXRange(*self.x_range_2)
    # Label
    def save_channel_name(self):
        selected_channel = self.ui.channelsMenu_1.currentText() if self.sender() == self.ui.SaveButton_1 else self.ui.channelsMenu_2.currentText()
        new_channel_name = self.ui.editLabel_1.text() if self.sender() == self.ui.SaveButton_1 else self.ui.editLabel_2.text()
        
        # Update the channel name in the dictionary
        self.rename_channel(selected_channel, new_channel_name)
        
        # Update the channel name in the QComboBox
        if self.sender() == self.ui.SaveButton_1:
            self.ui.channelsMenu_1.setItemText(self.ui.channelsMenu_1.currentIndex(), new_channel_name)
        else:
            self.ui.channelsMenu_2.setItemText(self.ui.channelsMenu_2.currentIndex(), new_channel_name)

    def rename_channel(self, channel_name, new_name):
        if channel_name and new_name:
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
        self.delete_channel(self.plot_widget_1, self.ui.channelsMenu_1, self.curves_1)

    def delete_channel_2(self):
        self.delete_channel(self.plot_widget_2, self.ui.channelsMenu_2, self.curves_2)

    #export pdf
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
                curve = graph_frame.plot(channel_data['time'], channel_data['amplitude'], pen=channel_data['color'])
                graph_frame.setLabel('bottom', text='Time')
                graph_frame.setLabel('left', text='Amplitude')
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

                # Create a PlotDataItem to display the data
                color_index = len(curves_list) % len(self.default_colors)  # Get a color index
                color = self.default_colors[color_index]
                curve = graph_frame.plot(time, amplitude, pen=color)

                # Set labels
                graph_frame.setLabel('bottom', text='Time')
                graph_frame.setLabel('left', text='Amplitude')

                # Append the curve to the specified list
                curves_list.append(curve)

                # Add the channel name to the list
                self.channel_counter += 1
                channel_name = f"Channel {self.channel_counter}"


                # Create a dictionary to store channel data
                channel_data = {
                    'time': time,
                    'amplitude': amplitude,
                    'color': color  # More data will be added here
                }

                # Update the channel data dictionary
                self.channel_data[channel_name] = channel_data

                # Add the channel name to the combo box
                combo_box.addItem(channel_name)  # Update the combo box

                # Start the respective timer to move the x-axis
                if graph_frame == self.plot_widget_1:
                    self.timer_1.start(50)
                elif graph_frame == self.plot_widget_2:
                    self.timer_2.start(50)

        except Exception as e:
            print("Error:", str(e))


    def browse_file(self, graph_frame, curves_list, combo_box ):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles


        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_name:
            self.ui.PlayPauseButton_1.setText("Pause" if graph_frame == self.plot_widget_1 else "Pause")
            playing_port = self.playing_port_1 if graph_frame == self.plot_widget_1 else self.playing_port_2
            playing_port = True
            self.plot_csv_data(file_name, graph_frame, curves_list, combo_box, )


    def browse_file_1(self):
        self.browse_file(self.plot_widget_1, self.curves_1, self.ui.channelsMenu_1)

    def browse_file_2(self):
        self.browse_file(self.plot_widget_2, self.curves_2, self.ui.channelsMenu_2)


    def scroll_graph_1_x(self, value):
    # Calculate the new x-axis range based on the scrollbar's value
      new_x_min = value / 100.0 * 10.0  # Assuming a range of 0-10
      new_x_max = new_x_min

      # Set the updated x-axis range for the first plot
      self.x_range_1 = [new_x_min, new_x_max]
      self.plot_widget_1.setXRange(*self.x_range_1)
     
    def scroll_graph_2_x(self, value):
    # Calculate the new x-axis range based on the scrollbar's value
      new_x_min = value / 100.0 * 10.0  # Assuming a range of 0-10
      new_x_max = new_x_min

      # Set the updated x-axis range for the second plot
      self.x_range_2 = [new_x_min, new_x_max]
      self.plot_widget_2.setXRange(*self.x_range_2)
      

        
    def scroll_graph_1_y(self, value):
    # Calculate the new y-axis range based on the vertical scrollbar's value
      new_y_min = value / 100.0 * 10.0  # Assuming a range of 0-10
      new_y_max = new_y_min + 10.0 * self.zoom_level_1

      # Set the updated y-axis range for the first plot
      self.y_range_1 = [new_y_min, new_y_max]
      self.plot_widget_1.setYRange(*self.y_range_1)
    

    def toggle_playback_1(self):
      # Toggle the playing state
      self.playing_port_1 = not self.playing_port_1
      # Update the text of the "Pause/Resume" button
      if self.playing_port_1:
          self.ui.PlayPauseButton_1.setText("Pause")
      else:
          self.ui.PlayPauseButton_1.setText("Play")
    
    def toggle_playback_2(self):
      # Toggle the playing state
      self.playing_port_2 = not self.playing_port_2
      # Update the text of the "Pause/Resume" button
      if self.playing_port_2:
          self.ui.PlayPauseButton_2.setText("Pause")
      else:
          self.ui.PlayPauseButton_2.setText("Play")

    def update_zoom_1(self, value):
      self.zoom_level_1 = value / 100.0
      # Update the x-axis range of the plots
      self.x_range_1 = [0, 10 * self.zoom_level_1]
      self.plot_widget_1.setXRange(*self.x_range_1) #Current POS

    def update_zoom_2(self, value):
      self.zoom_level_2 = value / 10.0
      # Update the x-axis range of the plots
      self.x_range_2 = [0, 10 * self.zoom_level_2]
      self.plot_widget_2.setXRange(*self.x_range_2)

    def update_playback_speed_1(self, value):
      self.x_range_speed_1 = (value / 300.0) +0.01
    
    def update_playback_speed_2(self, value):
      self.x_range_speed_2 = (value / 300.0) +0.01

    def toggle_visibility_1(self, state):
        pass
# Not Working yet
    # def toggle_visibility_1(self, state):
    #     selected_channel_index = self.ui.channelsMenu_1.currentIndex()  # Get the selected channel index
    #     selected_channel = self.ui.channelsMenu_1.currentText()
        
    #     if selected_channel_index >= 0:
    #         if state == Qt.Checked:
    #             self.curves_1[selected_channel_index].setVisible(True)  # Show the selected channel
    #         else:
    #             self.curves_1[selected_channel_index].setVisible(False)  # Hide the selected channel

    #     # Force a redraw of the plot to reflect the changes
    #     self.plot_widget_1.replot()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalViewerApp()
    window.setWindowTitle("Digital Signal Viewer")
    app.setWindowIcon(QIcon("img/logo.png"))
    window.show()
    sys.exit(app.exec_())
