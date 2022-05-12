"""
Created on May 15th 2020 

@author: rodell
"""
import context
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
from pathlib import Path
from context import data_dir, save_dir



"######################  Adjust for user/times of interest/plot customization ######################"
##User and file location
user = "rodell"

filename    = '2020912.TXT'
filein  = str(data_dir)
save    = str(save_dir)

##Plot customization
label      = 14
fig_size   = 20
tick_size  = 12
title_size = 16

df_pm01 = pd.read_csv(filein + "/UBC-PM-01/" + filename)
# df_pm02 = pd.read_csv(filein + "/UBC-PM-02/" + filename)

# df_pm["rtctime"] = pd.to_datetime(df_pm["rtctime"])
# df_pm = df_pm.set_index("rtctime")

# def timekepper(df_pm):
#     rtctime = np.array([])
#     for i in range(len(df_pm['rtctime'])):
#         rtc = datetime.strptime(df_pm['rtctime'][i], "%Y-%m-%dT%H:%M:%S")
#         rtctime = np.append(rtctime,rtc)
#     return rtctime

rtctime = np.array([])
for i in range(len(df_pm01['rtctime'])):
    rtc = datetime.strptime(df_pm01['rtctime'][i], "%Y-%m-%dT%H:%M:%S")
    rtctime = np.append(rtctime,rtc)
df_pm01['rtctime'] = rtctime

rtctime = np.array([])
for i in range(len(df_pm02['rtctime'])):
    rtc = datetime.strptime(df_pm02['rtctime'][i], "%Y-%m-%dT%H:%M:%S")
    rtctime = np.append(rtctime,rtc)
df_pm02['rtctime'] = rtctime


"###################### Environmental PM Observations ######################"

fig, ax = plt.subplots(3,1, figsize=(16,10))
fig.suptitle('UBC PM Sensor Test:  ' + filename[0:7], fontsize=16, fontweight="bold")
fig.autofmt_xdate()

xfmt = DateFormatter("%H:%M:%S")
ax[0].xaxis.set_major_formatter(xfmt)
ax[0].set_ylabel(r"PM 1 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[0].plot(df_pm01['rtctime'],df_pm01['pm10_env'], color = 'r', label = "PM01")
# ax[0].plot(df_pm02['rtctime'],df_pm02['pm10_env'], color = 'b', label = "PM02")
ax[0].legend()
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_xticklabels([])
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')

ax[1].xaxis.set_major_formatter(xfmt)
ax[1].set_ylabel(r"PM 2.5 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[1].plot(df_pm01['rtctime'],df_pm01['pm25_env'], color = 'r')
# ax[1].plot(df_pm02['rtctime'],df_pm02['pm25_env'], color = 'b')
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_xticklabels([])
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')

ax[2].xaxis.set_major_formatter(xfmt)
ax[2].set_xlabel("Datetime (PDT)", fontsize = label)
ax[2].set_ylabel(r"PM 10 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[2].plot(df_pm01['rtctime'],df_pm01['pm100_env'], color = 'r')
# ax[2].plot(df_pm02['rtctime'],df_pm02['pm100_env'], color = 'b')
ax[2].tick_params(axis='both', which='major', labelsize=tick_size)
#ax[2].set_xticklabels([])
ax[2].xaxis.grid(color='gray', linestyle='dashed')
ax[2].yaxis.grid(color='gray', linestyle='dashed')

plt.show()
fig.savefig(save + "/Env_PM/" + filename[0:7])




# fig = plt.figure(figsize=(14, 6))
# fig.suptitle("Counts/liter of particles of size XX um", fontsize=16)
# ax = fig.add_subplot(1, 1, 1)
# var_list = list(df_final)[6:37]
# for var in var_list:
#   ax.plot(df_final.index,df_final[var], lw = 2.0, label = var[:-2])
# ax.set_ylabel('Counts/liter')
# ax.set_xlabel('Time (MM-DD HH)')
# ax.legend(
#   bbox_to_anchor=(1.2, 1.2),
# )