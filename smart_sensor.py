import pandas as pd

from sleep_monitor import sleep_monitor
from bio_watch import bio_watch
from seismotracker import seismotracker

# Source: https://archive.ics.uci.edu/ml/datasets/MHEALTH+Dataset
# Source: https://archive.ics.uci.edu/ml/datasets/Dataset+for+ADL+Recognition+with+Wrist-worn+Accelerometer
input_dataset_csv = {'datasets/uic_dataset.csv': 50, 'datasets/hmp_dataset1.csv': 32, 'datasets/hmp_dataset2.csv': 32}

algorithms = {'Bio Watch': bio_watch, 'Sleep Monitor': sleep_monitor, 'SeismoTracker': seismotracker}
measurements = ['Heart Rate(bpm)', 'Breathing Rate(bpm)']

if __name__ == '__main__':
  count = 1
  results = {}

  for dataset, sampling_freq in sorted(input_dataset_csv.items()):
    data = pd.read_csv(dataset).values
    print('\nDataset %d: %s\n========='% (count, dataset))
    print("Number of records:", len(data))

    count = count + 1
    rates = []
    
    for algo, algo_fn in sorted(algorithms.items()):
      print('\n%s:\n' % algo)
      hr, br = algo_fn(data.copy(), sampling_freq)
      rates.append([hr, br])
    res = pd.DataFrame(rates, sorted(algorithms.keys()), measurements)
    results[dataset] = res
    print(res)

  print('\nFinal Results\n=============')
  for ds, result in sorted(results.items()):
    print("\nDataset: %s\n%s" %(ds, result))

