import context
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from context import data_dir, root_dir, img_dir
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from utils.pm import read_ramp


############### INPUTS ###############


file_date = "220515"

########################################

########################### Open RAMP data ##########################

ramp_pathlist = sorted(Path(str(data_dir) + f"/RAMP/").glob(f'{file_date}*.TXT'))
ramp_df = read_ramp(ramp_pathlist)

########################################################################
######################## Open UBC PM data ##########################

ubc_pms = ["%.2d" % i for i in range(1, 7)]
ubc_pms = ["01", "02", "04", "05", "06"]
ubc_pathlist =  np.ravel([sorted(Path(str(data_dir) + f"/UBC-PM-{pm}/").glob(f'20{file_date}*.TXT')) for  pm in ubc_pms])

path = str(ubc_pathlist[0])
print(path)
df = pd.read_csv(path)
del df['rtctime']
df['test'] =  "20" + file_date + "T" + df['millis']
df['test'] = pd.to_datetime(df['test'])
pm_date_range = pd.Timestamp(
        "20" + file_date + "T" + path[-12:-4]
    )
diff = pm_date_range - df['test'][0]
df['datetime'] = df['test'] + diff
df = df.set_index(pd.DatetimeIndex(df['datetime']))


def correct_datetime(path):
  path = str(path)
  print(path)
  df = pd.read_csv(path)
  del df['rtctime']
  df['test'] =  "20" + file_date + "T" + df['millis']
  df['test'] = pd.to_datetime(df['test'])
  pm_date_range = pd.Timestamp(
          "20" + file_date + "T" + path[-12:-4]
      )
  diff = pm_date_range - df['test'][0]
  df['datetime'] = df['test'] + diff
  df = df.set_index(pd.DatetimeIndex(df['datetime']))
  df = df.sort_index()['2022-05-15 14:58:00': '2022-05-15 15:56:00']
  df = df.resample("2Min").mean()

  return df


ubc_dfs = [correct_datetime(path) for path in ubc_pathlist]
########################################################################

hours = pd.Timedelta('0 days 01:07:00')
ramp_df.index = ramp_df.index - hours


# ramp_df = ramp_df.set_index(pd.DatetimeIndex(ramp_df['DateTime_corrected']))

# ramp_df = ramp_df[str(ubc_dfs[0].index[0]) : str(ubc_dfs[0].index[-1])]
ramp_df = ramp_df.sort_index()['2022-05-15 14:58:00': '2022-05-15 15:56:00']
ramp_df = ramp_df.resample("2Min").mean()


fig = plt.figure(figsize=(8, 8))  # (Width, height) in inches.
fig.autofmt_xdate()
ax = fig.add_subplot(1, 1, 1)
for i in range(len(ubc_dfs)):
  ax.plot(ubc_dfs[i].index, ubc_dfs[i]['pm25_env'], label = f'UBC-PM-{ubc_pms[i]}  Mean: {int(ubc_dfs[i]["pm25_env"].mean())}' + r" ($\frac{\mu g}{m^3}$)")
ax.plot(ramp_df.index,ramp_df['pm25'], label = f'RAMP          Mean: {int(ramp_df["pm25"].mean())}' + r" ($\frac{\mu g}{m^3}$)")
xfmt = DateFormatter("%H:%M")
ax.xaxis.set_major_formatter(xfmt)
ax.set_xlabel("Time (HH:MM)", fontsize = 14)
ax.set_ylabel(r"PM 2.5 ($\frac{\mu g}{m^3}$)", fontsize = 14)
ax.tick_params(axis='both', which='major', labelsize=13)
ax.xaxis.grid(color='gray', linestyle='dashed')
ax.yaxis.grid(color='gray', linestyle='dashed')
# ax.set_xlim(pd.Timestamp('2022-05-15 14:58:00'), pd.Timestamp('2022-05-15 15:55:00'))
# plt.legend()
ax.legend(
    loc="upper right",
    # bbox_to_anchor=(0.48, 1.15),
    ncol=1,
    fancybox=True,
    shadow=True,
)
plt.savefig(
    str(img_dir) + f"/ramp-v-ubc-{file_date}.png", dpi=300, bbox_inches="tight"
)


