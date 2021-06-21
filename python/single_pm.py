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

df_pm = pd.read_csv(filein + '/' + filename)

df_pm['DateTime'] = pd.to_datetime(df_pm['rtctime'])

df_pm = df_pm.set_index('DateTime')

start = '2020-09-14T16'
stop = '2020-09-15T10'

df_pm = df_pm.loc[start:]



# test = df_pm.drop(df_pm['pm25_env'] > 500)

# df_pm = df_pm[df_pm["pm25_env"] < 500]


"###################### Environmental PM Observations ######################"
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
time = df_pm.index.values
start= np.datetime_as_string(time[0], unit= 'h')
stop= np.datetime_as_string(time[-1], unit= 'h')

rain = '2020-09-14T18'
rain = pd.to_datetime(rain, format='%Y-%m-%dT%H')
start = '2020-09-14 16:00 PDT'
stop = '2020-09-15 08:00 PDT'

fig, ax = plt.subplots(3,1, figsize=(16,10))
fig.suptitle(f'UBC PM Sensor Test \n {start}  -  {stop}', fontsize=16, fontweight="bold")
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
ax[0].xaxis.set_major_formatter(xfmt)
ax[0].set_ylabel(r"PM 1 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[0].plot(df_pm.index,df_pm['pm10_env'], color = colors[0], label = "PM01")
# ax[0].axvline(rain, color = 'k', linewidth = 3)
# ax[0].legend()
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_xticklabels([])
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')

ax[1].xaxis.set_major_formatter(xfmt)
ax[1].set_ylabel(r"PM 2.5 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[1].plot(df_pm.index,df_pm['pm25_env'], color = colors[1])
# ax[1].axvline(rain, color = 'k', linewidth = 3)
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_xticklabels([])
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')

ax[2].xaxis.set_major_formatter(xfmt)
ax[2].set_xlabel("Datetime (PDT)", fontsize = label)
ax[2].set_ylabel(r"PM 10 ($\frac{\mu g}{m^3}$)", fontsize = label)
ax[2].plot(df_pm.index,df_pm['pm100_env'], color = colors[2])
# ax[2].axvline(rain, color = 'k', linewidth = 3)
ax[2].tick_params(axis='both', which='major', labelsize=tick_size)
#ax[2].set_xticklabels([])
ax[2].xaxis.grid(color='gray', linestyle='dashed')
ax[2].yaxis.grid(color='gray', linestyle='dashed')

# plt.show()
fig.savefig(save + '/' + filename[0:7], dpi = 250)







