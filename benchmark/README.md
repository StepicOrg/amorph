# Benchmarking
Package for collecting metrics from different patching methods.

Collect stats and plot them on charts and heatmaps with `report.py`
```
usage: report.py [-h] [--limit LIMIT] data save

positional arguments:
  data           Path to CSV data file
  save           Path to save reports into

optional arguments:
  -h, --help     show this help message and exit
  --limit LIMIT  Number of samples to process
```

Dump patches in human/machine readable formats with `dump.py`
```
usage: dump.py [-h] [--method METHOD] [--limit LIMIT] [--format {csv,json}]
               data save

positional arguments:
  data                 Path to CSV data file
  save                 Path to save dump in

optional arguments:
  -h, --help           show this help message and exit
  --method METHOD      Method for patching
  --limit LIMIT        Number of samples to process
  --format {csv,json}  Dump format
```
