# JAMES SCHOLAR PROJECT CS101  - SPRING 2026

| Distribution of Crashes | Distribution of Crashes % |
| :---: | :---: |
| ![Distribution of Crashes with and without control device](assets/fig1.png) | ![Distribution of Crashes with and without control device percentages](assets/fig2.png) |
## Overview
Part of the project seeks to determine whether traffic control devices were effective
in deterring traffic accidents in Chicago, which traffic control devices were most effective, and 
whether the traffic device condition matters. This part of the project looks at the 
`“TRAFFIC_CONTROL_DEVICE”` and `“DEVICE_CONDITION”` columns.

## How to Run
1. Setup virtual environment.
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Open JSrcommon.ipynb or run 
```shell
python main.py
```

## Conclusions
### Data
Data Conclusions – Chicago traffic crash data is from between dates  March 3, 2013, and March 16, 2026
1. In **4.61%** of cases, there was no report on the presence or absence of traffic control devices.
2. After removing reports of crashes where the presence or absence of traffic control devices is unknown,
**58.9%** of the reported traffic crashes in Chicago occurred in areas without traffic control devices,
compared with **41.1%** in areas with devices.
3. If traffic device signals are present at the crash site, the data show that traffic signals and
stop/flashers are the most common traffic control devices. The logarithmic scale shows that some device
types occur at orders of magnitude more frequently than others.

### Comments
1. The Seaborn library gives users a lot of control over plotting. However, additional control means that 
there is additional work to make the plot look nice.
2. The Altair plotting library is the easiest to use once users get accustomed to the API. It
centers the graph automatically, eliminating the need for the programmer to run trial-and-error tests.
