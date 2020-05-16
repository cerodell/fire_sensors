"""
Created on May 15th 2020 

@author: rodell
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
from pathlib import Path



"######################  Adjust for user/times of interest/plot customization ######################"
##User and file location
user = "rodell"

filename    = '2020515.TXT'
filein  = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Fire_Sensor/data/'
save    = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Fire_Sensor/Images/Plot/'

##Plot customization
label      = 14
fig_size   = 20
tick_size  = 12
title_size = 16

df_pm = pd.read_csv(filein + filename)

# df_pm["rtctime"] = pd.to_datetime(df_pm["rtctime"])
# df_pm = df_pm.set_index("rtctime")

rtctime = np.array([])
for i in range(len(df_pm['rtctime'])):
    rtc = datetime.strptime(df_pm['rtctime'][i], "%Y-%m-%dT%H:%M:%S")
    rtctime = np.append(rtctime,rtc)

df_pm['rtctime'] = rtctime


"###################### Environmental PM Observations ######################"

fig, ax = plt.subplots(3,1, figsize=(16,10))
fig.suptitle('UBC PM Sensor Test:  ' + filename[0:7], fontsize=16, fontweight="bold")
fig.autofmt_xdate()

xfmt = DateFormatter("%H:%M:%S")
ax[0].xaxis.set_major_formatter(xfmt)
ax[0].set_ylabel(r"PM 1 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[0].plot(df_pm['rtctime'],df_pm['pm10_env'], color = 'r')
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_xticklabels([])
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')

ax[1].xaxis.set_major_formatter(xfmt)
ax[1].set_ylabel(r"PM 2.5 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[1].plot(df_pm['rtctime'],df_pm['pm25_env'], color = 'g')
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_xticklabels([])
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')

ax[2].xaxis.set_major_formatter(xfmt)
ax[2].set_xlabel("Datetime (PDT)", fontsize = label)
ax[2].set_ylabel(r"PM 10 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[2].plot(df_pm['rtctime'],df_pm['pm100_env'], color = 'blue')
ax[2].tick_params(axis='both', which='major', labelsize=tick_size)
#ax[2].set_xticklabels([])
ax[2].xaxis.grid(color='gray', linestyle='dashed')
ax[2].yaxis.grid(color='gray', linestyle='dashed')

plt.show()
fig.savefig(save + "Env_PM/" + filename[0:7])