import sys
import csv
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QTimer
from task1 import Ui_MainWindow

class SignalViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # Set up the UI
        self.ui.BrowseButton.clicked.connect(self.browse_file_1)
        self.ui.BrowseButton_2.clicked.connect(self.browse_file_2)

        self.plot_widget_1 = self.ui.Plot_3
        self.plot_widget_2 = self.ui.Plot_2

        self.x_range_speed = 0.04  # Should be a done by bar or button
        self.x_range_1 = [0, 10]  # Initial x-axis range for plot_widget_1
        self.x_range_2 = [0, 10]  # Initial x-axis range for plot_widget_2

        self.timer_1 = QTimer(self)
        self.timer_1.timeout.connect(self.update_plot_1)

        self.timer_2 = QTimer(self)
        self.timer_2.timeout.connect(self.update_plot_2)

        self.is_first_plot_1 = True
        self.is_first_plot_2 = True

    def update_plot_1(self):
        # Update the x-axis range for the first plot
        self.x_range_1 = [self.x_range_1[0] + self.x_range_speed, self.x_range_1[1] + self.x_range_speed]

        # Set the updated x-axis range for the first plot
        self.plot_widget_1.setXRange(*self.x_range_1)

    def update_plot_2(self):
        # Update the x-axis range for the second plot
        self.x_range_2 = [self.x_range_2[0] + self.x_range_speed, self.x_range_2[1] + self.x_range_speed]

        # Set the updated x-axis range for the second plot
        self.plot_widget_2.setXRange(*self.x_range_2)

    def plot_csv_data(self, file_name, graph_frame):
        try:

            graph_frame.clear()

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
                curve = graph_frame.plot(time, amplitude, pen=(0, 255, 250))

                # Set labels 
                graph_frame.setLabel('bottom', text='Time')
                graph_frame.setLabel('left', text='Amplitude')

                # Start the respective timer to move the x-axis
                if graph_frame == self.plot_widget_1:
                    self.timer_1.start(50)  
                elif graph_frame == self.plot_widget_2:
                    self.timer_2.start(50)  

        except Exception as e:
            print("Error:", str(e))

    def browse_file_1(self):
        self.browse_file(self.plot_widget_1)

    def browse_file_2(self):
        self.browse_file(self.plot_widget_2)

    def browse_file(self, plot_widget):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_name:
            self.plot_csv_data(file_name, plot_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignalViewerApp()
    window.show()
    sys.exit(app.exec_())
