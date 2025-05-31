# The repository

This repository contains solution code for RMK's 2025 data team internship.

## Challenge

[Challenge link](https://rmk.ee/wp-content/uploads/2025/04/test_challenge2025.pdf)

# The result

![solution plot](img/solution.png)

N=20

# The solution

Data was collected from 2. May 2025 to 30. May 2025 by fetching [gps.txt](https://transport.tallinn.ee/gps.txt) at 60 second interval. The time was encoded into filename (UTC time). The collected data is stored in gzipped tar file data/gpsdata.tar.gz.  
  
Data was fetched at one minute interval, so interpolation was needed to determinte the departura and arrival times at bus stops more accurately. The polyline from [tallinna-linn_bus_8.txt](https://transport.tallinn.ee/data/tallinna-linn_bus_8.txt) was used for the interpolation. The final solution interpolated the coordinates to 1 second intervals (linear interpolation). When a bus from specified line number got within tolerance distance from one of the stops, then the departure and corresponding arrival were logged. Only monday to friday samples were considered.  
  
20 departure-arrival pairs were found. These pairs could be used to determine the probability of Rita being late. The probability was evaluated at one second interval. The resulting plot can be seen above. Linear interpolation isn't perfectly accurate, so there's definitely some approximation error involved (maybe up to ~10-20 seconds).  
  
# Files
solve.py - script to solve the task (calculate and display the plot)  
interpolate.py - interpolation specific helper functions  
util.py - utility functions  
visualize.py - code used to visualize interpolation, not part of solution  
gather_data.py - code that was run on a VPS to collect the data  
tltdata.py - code specific to Tallinn's city transport  
data/gpsdata.tar.gz - all 40k gps frames collected   
README.md - you are here  
  
# How to run

```bash
cd data
tar xf gpsdata.tar.gz
cd ..
# using venv recommended
pip install -r requirements.txt
python solve.py
```