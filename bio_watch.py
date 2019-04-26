import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import scipy.fftpack
import scipy as sp
from scipy.stats import zscore
import pandas as pd
from scipy.signal import butter, lfilter
from scipy import signal
import warnings
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")
style.use('ggplot')

input_file_path = "HMP_Dataset/Liedown_bed/Accelerometer-2011-06-02-17-21-57-liedown_bed-m1.txt"
sampling_frequency = 32
average_filter_window_duration_hr = int((1/7)*sampling_frequency)
average_filter_window_duration_br = int((40/60)*sampling_frequency)
T = 1/sampling_frequency

def normalize(data):
  for i in range(0, 3):
    data[:,i] = sp.stats.zscore(data[:,i])  
  return data

def apply_average_filter(data, window):
  for i in range(0, 3):
    data[:,i] = np.array(pd.Series(data[:,i]).rolling(window=window).mean())
  return data

def plot(data, title):
  N = len(data)
  y = np.linspace(0, sampling_frequency, N)
  plt.plot(y, data)

  plt.title(title)
  plt.ylabel('ACCELERATION Ax (m/s^2)')
  plt.xlabel('TIME (s)')
  plt.draw()
  plt.pause(5)
  plt.close()

def butter_bandpass(lowcut, highcut, fs, order):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b, a = butter(order, [low, high], btype='band')
  return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
  b, a = butter_bandpass(lowcut, highcut, fs, order)
  y = lfilter(b, a, data)
  return y

def apply_bandpass_butterworth_filter(data, low_cutoff_freq, high_cutoff_freq):
  order = 2
  y = butter_bandpass_filter(data, low_cutoff_freq, high_cutoff_freq, sampling_frequency, order)
  return y

def aggregate_components(data):
  return np.array(list(map(lambda c: np.sqrt(np.sum(np.square(c))) , data)), dtype=np.float64)

def fft(acc_data, f_low, f_high):
  acc_data = acc_data[~np.isnan(acc_data)]
  acc_data = sp.signal.detrend(acc_data)
  N = len(acc_data)

  fft_data = sp.fftpack.fft(acc_data)
  f = np.linspace(0, sampling_frequency, N)

  plt.plot(f[:N // 2], np.abs(fft_data)[:N // 2] * 1 / N)
  plt.xlabel('Frequency in Hertz [Hz]')
  plt.ylabel('Magnitude')
  plt.title('FFT')
  plt.draw()
  plt.pause(5)
  plt.close()

  max_amp = 0
  max_index = 0
  index = 0
  for c in fft_data:
    if f[index] < f_low or f[index] > f_high:
      index = index + 1
      continue;
    real = np.real(c)
    img = np.imag(c)
    amp = np.sqrt(real*real + img*img)
    if max_amp < amp:
      max_amp = amp
      max_index = index
    index = index + 1

  return max_amp, f[max_index]

def calculate_breathing_rate(normalized_data):
  smooth_data = apply_average_filter(normalized_data, average_filter_window_duration_br)
  plot(smooth_data[:,0], 'Smoothened Accelerometer Data')

  amp_to_freq = {}
  breathing_low_freq = 0.13
  breathing_high_freq = 0.66
  print('Max Amplitude within 0.13 and 0.66 Hz frequency:')
  br_x_amp, br_x_f = fft(smooth_data[:,0], breathing_low_freq, breathing_high_freq)
  amp_to_freq[br_x_amp] = br_x_f
  print('X-Axis:', br_x_amp)
  br_y_amp, br_y_f = fft(smooth_data[:,1], breathing_low_freq, breathing_high_freq)
  amp_to_freq[br_y_amp] = br_y_f
  print('Y-Axis:', br_y_amp)
  br_z_amp, br_z_f = fft(smooth_data[:,2], breathing_low_freq, breathing_high_freq)
  amp_to_freq[br_z_amp] = br_z_f
  print('Z-Axis:', br_z_amp)
  br_max_amp = max([br_x_amp, br_y_amp, br_z_amp])

  print("Max amplitude chosen:", br_max_amp)
  print("Frequency of chosen amplitude:", amp_to_freq[br_max_amp])
  print("Respiratory Rate (bpm):", 60*amp_to_freq[br_max_amp])

def calculate_heart_rate(normalized_data):
  smooth_data = apply_average_filter(normalized_data, average_filter_window_duration_hr)
  smooth_data = np.array(list(filter(lambda row: np.isfinite(np.sum(row)), smooth_data)), dtype=np.float64)
  plot(smooth_data[:,0], 'Smoothened Accelerometer Data')

  high_cutoff_freq = 4
  low_cutoff_freq = 11
  bandpass1_data = apply_bandpass_butterworth_filter(smooth_data, low_cutoff_freq, high_cutoff_freq)
  plot(bandpass1_data[:,0], 'Bandpass-1 Accelerometer Data')

  aggregated_data = aggregate_components(bandpass1_data)

  high_cutoff_freq = 2.5
  low_cutoff_freq = 0.66
  bandpass2_data = apply_bandpass_butterworth_filter(aggregated_data, low_cutoff_freq, high_cutoff_freq)
  plot(bandpass2_data, 'Bandpass-2 Accelerometer Data')

  max_amp, max_freq = fft(bandpass2_data, 0.66, 2.5)
  print('Max Amplitude:', max_amp)
  print('Max Frequency:', max_freq)
  print('Heart Rate (bpm):', 60*max_freq)
  return

if __name__ == '__main__':
  data = np.loadtxt(input_file_path)
  plot(data[:,0], 'Raw Accelerometer Data')
  print("Number of records:", len(data))

  normalized_data = normalize(data)
  plot(normalized_data[:,0], 'Normalized Accelerometer Data')

  calculate_heart_rate(normalized_data)
  calculate_breathing_rate(normalized_data)


