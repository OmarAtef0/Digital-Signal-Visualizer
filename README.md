# DSP_task_1
# Multi-Port Multi-Channel Signal Viewer Application

## Overview

This desktop application is developed using Python and Qt to provide a multi-port, multi-channel signal viewer with various features. It allows users to browse and display different medical signals such as **ECG**, **EMG**, **EEG**, etc., and provides tools for signal manipulation, synchronization, and report generation.

## Features

### Dual Graphs

- The application contains two identical graphs, each with its own controls.
- Users can open different signals in each graph.
- The graphs can operate independently or be linked via a UI button.
- When linked, both graphs display the same time frames, signal speed, and viewport (zoom and pan).
- If unlinked, each graph can run signals independently.

### Cine Mode

- Signals open in cine mode, displaying the signals as they change over time, similar to ICU monitors.
- Users can rewind signals, stop them, or start them again from the beginning.

### Signal Manipulation

Users can manipulate the running signals with various UI elements:

- Change signal color.
- Add labels/titles to each signal.
- Show/hide signals.
- Control/customize the cine speed.
- Zoom in/out.
- Pause/play/rewind (on/off).
- Scroll and pan the signal in any direction (left, top, right, bottom).
- Moving signals between graphs.

The application enforces boundary conditions to prevent scrolling or panning beyond signal limits.

### Exporting and Reporting

- Users can construct a report with one or more snapshots of the graphs.
- The report includes data statistics for the displayed signals.
- Data statistics can include mean, standard deviation, duration, minimum, and maximum values for each signal.
- The report is generated as a PDF file with organized tables and layouts.

## How to run the program

To run the application, follow these steps:

1. Ensure you have Python and the required libraries (PyQt, NumPy, pyqtgraph) installed.
2. Clone or download this repository.
3. Run the Python code to launch the application.

## Team Members
Hazem Rafaat
Ahmed Khaled
Omar Atef
Ibrahim Emad
