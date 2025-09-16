# The MIT License (MIT)
#
# Copyright (c) 2017 Niklas Rosenstein
# Copyright (c) 2025 Jackson Baloun
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import myo #registered as myo-python on pycharm
from ctypes import *
cdll.LoadLibrary(r"C:\Users\User_Example\Downloads\myo-sdk-win-0.9.0\myo-sdk-win-0.9.0\bin\myo32.dll") #Replace User_Example with your computer's username
from matplotlib import pyplot as plt #package on pycharm
from collections import deque
from threading import Lock, Thread
import numpy as np #package on pycharm
import csv
import pandas as pd #package on pycharm
import math

def fig_open(fig):
    return plt.fignum_exists(fig.number)


class Collector(myo.DeviceListener):

  def __init__(self, n):
    self.n = n
    self.lock = Lock()

    #creating arrays for display and for export later. queue is used for display and is updated,
    #while the logs are exported at the end via export_to_csv func.

    self.emg_data_queue = deque(maxlen=n)
    self.full_emg_log = []

    self.accel_data_queue = deque(maxlen=n)
    self.full_accel_log = []

    self.gyro_data_queue = deque(maxlen=n)
    self.full_gyro_log = []

    self.data = [self.full_emg_log, self.full_accel_log, self.full_gyro_log]
    self.filename = ['emg_log.csv', 'accel_log.csv', 'gyro_log.csv']

    #filename and data array are created to make csv export easier.

  def get_emg_data(self):
    with self.lock:
      #print('got emg data')
      return list(self.emg_data_queue)

  def get_accel_data(self):
    with self.lock:
      #print('got accel data')
      return list(self.accel_data_queue)

  def get_gyro_data(self):
    with self.lock:
      #print('got gyro data')
      return list(self.gyro_data_queue)

  # myo.DeviceListener

  def on_connected(self, event):
    event.device.stream_emg(True)
    print('Device Connected!')

  def on_emg(self, event):
    with self.lock:
      self.emg_data_queue.append((event.timestamp, event.emg))
      self.full_emg_log.append((event.timestamp, event.emg))
    #Device is constantly collecting emg data, and returns the data every time it is called. Self.lock is always true while program is running.

  def on_orientation(self, event):
    with self.lock:
      '''
      print(event.orientation)
      print(event.acceleration)
      print(event.gyroscope)
      
      '''
      self.accel_data_queue.append((event.timestamp, np.array([event.acceleration.x, event.acceleration.y, event.acceleration.z])))
      self.full_accel_log.append((event.timestamp, np.array([event.acceleration.x, event.acceleration.y, event.acceleration.z])))

      self.gyro_data_queue.append((event.timestamp, np.array([event.gyroscope.x, event.gyroscope.y, event.gyroscope.z])))
      self.full_gyro_log.append((event.timestamp, np.array([event.gyroscope.x, event.gyroscope.y, event.gyroscope.z])))

    #Again, self.lock is always true while running. Constant use of on_orientation for collection of acceleration and gyroscopic data
          
  def export_to_csv(self):
    with self.lock:
        data = [self.full_emg_log, self.full_accel_log, self.full_gyro_log]
        filename = ['emg_log.csv', 'accel_log.csv', 'gyro_log.csv']
        for x in range(len(data)):
            timestamps = []
            values = []
            for timestamp, datapt in data[x]:
                timestamps.append(timestamp)
                values.append(datapt)

            if x == 1 or x == 2:
                values = values
                '''
                values_new = []
                for i in values:
                    values_new.append(list(i))
                values = np.array(values_new)
                '''
            else:
                values = np.array(values)
            timestamps = np.array(timestamps)
            timestamps = (timestamps - timestamps[0]) / 1000
            len_data_wo_timestamp = (len(values[0]))
            df = pd.DataFrame(values, columns=[f"{'Sensor '}_{i}" for i in range(len_data_wo_timestamp)])
            df.insert(0, 'timestamp_ms', timestamps)
            df.to_csv(filename[x], index=False)
        #From my understanding, to_csv saves the CSV file wherever the .py file is saved. Did not get a chance to test this theory.

class Plot(object):

  def __init__(self, listener):
    self.n = listener.n
    self.listener = listener

    self.fig_emg = plt.figure(num='EMG Data')
    self.fig_accel = plt.figure(num='Acceleration Data')
    self.fig_gyro = plt.figure(num='Gyro Data')

    #creates 3 figures to chart

    self.figures = [self.fig_emg, self.fig_accel, self.fig_gyro]

    self.axes_emg = [self.fig_emg.add_subplot(int('81' + str(i))) for i in range(1, 9)]
    [(ax.set_ylim([-100, 100])) for ax in self.axes_emg] #Changing set.ylim changes the bounds of the graph in the y-axis
    self.graphs_emg = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes_emg]

    #sets up the rows in accordance with the data channels to be received

    self.axes_accel = [self.fig_accel.add_subplot(int('31' + str(i))) for i in range(1, 4)]
    [(ax.set_ylim([-3, 3])) for ax in self.axes_accel]
    self.graphs_accel = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes_accel]

    self.axes_gyro = [self.fig_gyro.add_subplot(int('31' + str(i))) for i in range(1, 4)]
    [(ax.set_ylim([-180, 180])) for ax in self.axes_gyro]
    self.graphs_gyro = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes_gyro]

    plt.ion()

  def update_plot_emg(self):
      emg_data = self.listener.get_emg_data()
      emg_data = np.array([x[1] for x in emg_data]).T
      for g, data in zip(self.graphs_emg, emg_data):
          if len(data) < self.n:
              # Fill the left side with zeroes.
              data = np.concatenate([np.zeros(self.n - len(data)), data])
          g.set_ydata(data)
      self.fig_emg.canvas.draw_idle()

  def update_plot_accel(self):
      accel_data = self.listener.get_accel_data()
      accel_data = np.array([x[1] for x in accel_data]).T
      for g, data in zip(self.graphs_accel, accel_data):
          if len(data) < self.n:
              # Fill the left side with zeroes.
              data = np.concatenate([np.zeros(self.n - len(data)), data])
          g.set_ydata(data)
      self.fig_accel.canvas.draw_idle()

  def update_plot_gyro(self):
    gyro_data = self.listener.get_gyro_data()
    gyro_data = np.array([x[1] for x in gyro_data]).T
    for g, data in zip(self.graphs_gyro, gyro_data):
      if len(data) < self.n:
        # Fill the left side with zeroes.
        data = np.concatenate([np.zeros(self.n - len(data)), data])
      g.set_ydata(data)
    self.fig_gyro.canvas.draw_idle()

  def main(self):
    while any(fig_open(fig) for fig in self.figures):
      if fig_open(self.figures[2]):
          self.update_plot_gyro()
      if fig_open(self.figures[0]):
          self.update_plot_emg()
      if fig_open(self.figures[1]):
          self.update_plot_accel()
    #runs continuously. Ensures that closing one figure to allow for smoother completion of other charts does not stall the program.

      plt.pause(1.0 / 30)
    print("Plotting and data collection finished.")



def main():
  myo.init()
  hub = myo.Hub()
  listener = Collector(512) #The value 512 refers to the frequency of the device. Adjusting up or down can change the quantity of data available.
  try:
    with hub.run_in_background(listener.on_event):
      Plot(listener).main()
  finally:
      listener.export_to_csv()
      print('Wrote data to csv files!')




if __name__ == '__main__':

  main()

