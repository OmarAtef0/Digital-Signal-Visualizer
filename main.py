import sys
import csv
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QSlider
from PyQt5.QtCore import QTimer
from task1 import Ui_MainWindow
from pyqtgraph import PlotWidget
from PyQt5.QtGui import QPen, QColor 
import numpy as np
from pyqtgraph.graphicsItems import TextItem


class SignalViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the UI

        self.ui.BrowseButton_1.clicked.connect(self.browse_file_1)
        self.ui.BrowseButton_2.clicked.connect(self.browse_file_2)
        self.ui.PlayPauseButton_1.clicked.connect(self.toggle_playback_1)
        self.ui.PlayPauseButton_2.clicked.connect(self.toggle_playback_2)
        #Zoom Range
        self.ui.ZoomSlider_1.valueChanged.connect(self.update_zoom_1)
        self.ui.ZoomSlider_2.valueChanged.connect(self.update_zoom_2)

        self.ui.PlayBackSpeedSlider_1.valueChanged.connect(self.update_playback_speed_1)
        self.ui.PlayBackSpeedSlider_2.valueChanged.connect(self.update_playback_speed_2)

        self.plot_widget_1 = self.ui.Plot_1
        self.plot_widget_2 = self.ui.Plot_2

        self.x_range_speed = 0.05  # Should be done by a slider or button
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

        #Static colors for now, should add a color palette
        self.colors = [QColor(255, 0, 0),  # Red
                       QColor(0, 255, 0),  # Green
                       QColor(0, 0, 255),  # Blue
                       QColor(255, 255, 0),  # Yellow
                       QColor(255, 0, 255)]  # Magenta
        
        # Initialize the playing state
        self.playing_port_1 = False
        self.playing_port_2 = False
        self.zoom_level_1 = 5.0
        self.zoom_level_2 = 5.0

    def update_plot_1(self):
      if not self.playing_port_1:
        return

      # Update the x-axis range for the first plot
      self.x_range_1 = [self.x_range_1[0] + self.x_range_speed, self.x_range_1[1] + self.x_range_speed]
      
      # Set the updated x-axis range for the first plot
      self.plot_widget_1.setXRange(*self.x_range_1)

    def update_plot_2(self):
      if not self.playing_port_2:
        return
      # Update the x-axis range for the second plot
      self.x_range_2 = [self.x_range_2[0] + self.x_range_speed, self.x_range_2[1] + self.x_range_speed]

      # Set the updated x-axis range for the second plot
      self.plot_widget_2.setXRange(*self.x_range_2)

    def plot_csv_data(self, file_name, graph_frame, curves_list):
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
                color_index = len(curves_list) % len(self.colors)  # Get a color index
                color = self.colors[color_index]
                curve = graph_frame.plot(time, amplitude, pen=color)

                # Set labels 
                graph_frame.setLabel('bottom', text='Time')
                graph_frame.setLabel('left', text='Amplitude')

                # Append the curve to the specified list
                curves_list.append(curve)

                # Start the respective timer to move the x-axis
                if graph_frame == self.plot_widget_1:
                    self.timer_1.start(50)  
                elif graph_frame == self.plot_widget_2:
                    self.timer_2.start(50)  

        except Exception as e:
            print("Error:", str(e))

    def browse_file_1(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles


        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_name:
            self.ui.PlayPauseButton_1.setText("Pause")
            self.playing_port_1 = True
            self.plot_csv_data(file_name, self.plot_widget_1, self.curves_1)

    def browse_file_2(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_name:
          self.ui.PlayPauseButton_2.setText("Pause")
          self.playing_port_2 = True
          self.plot_csv_data(file_name, self.plot_widget_2, self.curves_2)

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
      self.x_range_speed = value / 100.0
    
    def update_playback_speed_2(self, value):
      self.x_range_speed = value / 100.0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalViewerApp()
    window.show()
    sys.exit(app.exec_())