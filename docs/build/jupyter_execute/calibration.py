#!/usr/bin/env python
# coding: utf-8

# # Performance
# In a laboratory setting, we compared the low-cost UBC AQ sensors to a [GRIMM](https://www.grimm-aerosol.com/products-en/dust-monitors/the-dust-decoder/11-d/) OPC sensor (Model: 1.109).  We produced air-borne salt particles as a measurand by feeding salt solutions with known molar concentrations into an atomizer. After the atomizer made the air-borne salt particles, they traveled through an adjustable filter (enabling concentrations control) and into a 22L glass chamber containing the UBC AQ sensors (Fig 1). The Grimm OPC sensor pulled air from the glass chamber to sample the salt concentrations simultaneously. There was an exhaust port to maintain persistent salt concentration levels and a small fan within the glass chamber to mix the air. 
# <br>
# <br>
# <img src="_static/img/chamber.jpeg" alt="chamber" width="300"/>
# <br>
# <br>

# Lets dive in.

# In[1]:


import context
import pickle
import numpy as np
import pandas as pd
from functools import reduce
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.offsetbox import AnchoredText
import matplotlib.pylab as pylab
import sklearn
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from scipy import stats

from datetime import datetime, timedelta
from pathlib import Path
from context import data_dir, save_dir

# Back pratices but this keeps the notebook clean when displaying on html
import warnings
warnings.filterwarnings("ignore")


# 
# ## Import OPC data!
# UBC AQ data was one minute averaged to match the GRIMM sample rate.

# In[2]:



## define date of interest
date_of_int = '20210430' # options 20210430 or 20210502


def prepare_df(ubc_pm, date_of_int):
  """
  Function cleans UBC OPCs data by removing duplicate headers and dropping error values. 
  Once cleaned takes 1 min avg of data to match GRIM sample rate.
  """
  df = pd.read_csv(str(data_dir) + ubc_pm + date_of_int + '.TXT')
  df = df.drop(df[df.rtctime == 'rtctime'].index)
  df = df[~df['pm10_env'].str.contains('Rec')]
  time = pd.to_datetime(df['rtctime'])
  df.index = pd.DatetimeIndex(pd.to_datetime(df['rtctime']))
  df = df.drop(['rtctime'], axis=1)
  df = df.astype(float)
  df = df[df['pm10_env'] < 4000]
  df = df[df['pm25_env'] < 4000]
  df = df[df['pm100_env'] < 4000]

  df = df.resample('1Min').mean()

  col = ubc_pm.strip('/').replace('-','_')
  new_name = {}
  for name in list(df):
    new_name.update({name : col+'_'+name} )
  df = df.rename(new_name, axis='columns')

  return df


# Open the ubc opcs

# In[3]:



ubc_list = [prepare_df(f"/UBC-PM-0{i}/", date_of_int) for i in range(1,6)]
df_ubc = reduce(lambda x, y: pd.merge(x, y, on='rtctime'), ubc_list)
df_ubc.columns = df_ubc.columns.str.replace('_y', '')


# Open the grim opc

# In[4]:


def open_grimm(date_of_int, min_ubc):
  try:
    df_grim = pd.read_csv(str(data_dir) + f'/GRIM/{date_of_int}.csv')
    df_grim['date & time'] = pd.to_datetime(df_grim['date & time'])
  except:
    pathlist = sorted(Path(str(data_dir) + '/2021_OPCintercomparison/').glob(f'{date_of_int}*'))
    sheets = ['PM values', 'Count values', 'Mass values', 'Log values']
    df_grim = [pd.read_excel(f'{pathlist[0]}/{pathlist[0].stem}_sample01.xlsx', sheet_name= sheet, skiprows=4, engine='openpyxl') for sheet in sheets]
    df_grim = reduce(lambda x, y: pd.merge(x, y, on='date & time'), df_grim)
    df_grim['date & time'] = pd.to_datetime(df_grim['date & time'], dayfirst=True)
    df_grim.to_csv(str(data_dir) + f'/GRIM/{date_of_int}.csv', index=False)


  df_grim['date & time'] = df_grim['date & time'].dt.round('1min')  
  df_grim = df_grim.set_index('date & time')
  df_grim = df_grim.join(min_ubc, how='outer')
  df_grim = df_grim.dropna()
  return df_grim

min_ubc = np.argmin([len(ubc_list[i]) for i in range(len(ubc_list))])
df_grim = open_grimm(date_of_int, ubc_list[min_ubc])


# Merge UBC dfs with Grimm df and print first five rows 

# In[5]:


df_final = pd.merge(left=df_grim, right=df_ubc, left_index=True, right_index=True, how='left')
df_final.columns = df_final.columns.str.replace('_y', '')
df_final.head()


# Define default font sizes for ploting

# In[6]:


params = {
         'xtick.labelsize':14,
         'ytick.labelsize': 14,
          'axes.labelsize':14,

         }

pylab.rcParams.update(params)


# ### Plot PM 1.0 

# In[7]:



colors = plt.rcParams['axes.prop_cycle'].by_key()['color']


fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
fig.suptitle(r"PM 1.0 ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(2, 1, 2)
ax.plot(df_final.index,df_final['PM1 [ug/m3]'], lw = 4.0, label = 'GRIMM', color = colors[0])
ax.plot(df_final.index,df_final['UBC_PM_01_pm10_env'], label = 'UBC-PM-01', color = colors[1])
# ax.plot(df_final.index,df_final['UBC_PM_02_pm10_env'], label = 'UBC-PM-02', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_03_pm10_env'], label = 'UBC-PM-03', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_04_pm10_env'], label = 'UBC-PM-04', color = colors[3])
ax.plot(df_final.index,df_final['UBC_PM_05_pm10_env'], label = 'UBC-PM-05', color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel('Time (MM-DD HH)')
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 2.44),
    ncol=6,
    fancybox=True,
    shadow=True,
)
ax = fig.add_subplot(2, 2, 1)
size = 6
ax.scatter(df_final['PM1 [ug/m3]'], df_final['PM1 [ug/m3]'], s=size, color = colors[0])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_01_pm10_env'], s=size, color = colors[1])
# ax.scatter(df_grim['PM1 [ug/m3]'], df_final['UBC_PM_02_pm10_env'], s=size, color = colors[2])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_03_pm10_env'], s=size, color = colors[2])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_04_pm10_env'], s=size, color = colors[3])
ax.scatter(df_final['PM1 [ug/m3]'], df_final['UBC_PM_05_pm10_env'], s=size, color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')

ax = fig.add_subplot(2, 2, 2)
bins = 20
alpha = 0.6
ax.hist(df_final['PM1 [ug/m3]'],bins,alpha = alpha, color = colors[0], zorder = 10)
ax.hist(df_final['UBC_PM_01_pm10_env'],bins, alpha = alpha, color = colors[1])
# ax.hist(df_final['UBC_PM_02_pm10_env'],bins, alpha = alpha,color = colors[2])
ax.hist(df_final['UBC_PM_03_pm10_env'],bins, alpha = alpha, color = colors[2])
ax.hist(df_final['UBC_PM_04_pm10_env'],bins, alpha = alpha,color = colors[3])
ax.hist(df_final['UBC_PM_05_pm10_env'],bins, alpha = alpha, color = colors[4])
ax.set_ylabel('Count')
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')


# Figure shows time series comparison of the measured PM 1.0 contractions of four UBC AQ Sensors [UBC-PM-01 (orange), UBC-PM-03 (green), UBC-PM-04 (red), UBC-PM-05 (blue)] and the GRIM sensor [GRIMM (blue)]. The time series shows one minute averaged PM 1.0 contractions incremented from 2021-04-30 09:27:00 unitl 2021-04-30 21:36:00. 

# ### Plot PM 2.5 

# In[8]:




fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
fig.suptitle(r"PM 2.5 ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(2, 1, 2)
ax.plot(df_final.index,df_final['PM2.5 [ug/m3]'], lw = 4.0, label = 'GRIMM', color = colors[0])
ax.plot(df_final.index,df_final['UBC_PM_01_pm25_env'], label = 'UBC-PM-01', color = colors[1])
# ax.plot(df_final.index,df_final['UBC_PM_02_pm10_env'], label = 'UBC-PM-02', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_03_pm25_env'], label = 'UBC-PM-03', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_04_pm25_env'], label = 'UBC-PM-04', color = colors[3])
ax.plot(df_final.index,df_final['UBC_PM_05_pm25_env'], label = 'UBC-PM-05', color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel('Time (MM-DD HH)')
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 2.44),
    ncol=6,
    fancybox=True,
    shadow=True,
)
ax = fig.add_subplot(2, 2, 1)
size = 6
ax.scatter(df_final['PM2.5 [ug/m3]'], df_final['PM2.5 [ug/m3]'], s=size, color = colors[0])
ax.scatter(df_final['PM2.5 [ug/m3]'], df_final['UBC_PM_01_pm25_env'], s=size, color = colors[1])
# ax.scatter(df_grim['PM2.5 [ug/m3]'], df_final['UBC_PM_02_pm25_env'], s=size, color = colors[2])
ax.scatter(df_final['PM2.5 [ug/m3]'], df_final['UBC_PM_03_pm25_env'], s=size, color = colors[2])
ax.scatter(df_final['PM2.5 [ug/m3]'], df_final['UBC_PM_04_pm25_env'], s=size, color = colors[3])
ax.scatter(df_final['PM2.5 [ug/m3]'], df_final['UBC_PM_05_pm25_env'], s=size, color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')

ax = fig.add_subplot(2, 2, 2)
bins = 20
alpha = 0.6
ax.hist(df_final['PM2.5 [ug/m3]'],bins,alpha = alpha, color = colors[0], zorder = 10)
ax.hist(df_final['UBC_PM_01_pm25_env'],bins, alpha = alpha, color = colors[1])
# ax.hist(df_final['UBC_PM_02_pm25_env'],bins, alpha = alpha,color = colors[2])
ax.hist(df_final['UBC_PM_03_pm25_env'],bins, alpha = alpha, color = colors[2])
ax.hist(df_final['UBC_PM_04_pm25_env'],bins, alpha = alpha,color = colors[4])
ax.hist(df_final['UBC_PM_05_pm25_env'],bins, alpha = alpha, color = colors[5])
ax.set_ylabel('Count')
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')


# Figure shows time series comparison of the measured PM 2.5 contractions of four UBC AQ Sensors [UBC-PM-01 (orange), UBC-PM-03 (green), UBC-PM-04 (red), UBC-PM-05 (blue)] and the GRIM sensor [GRIMM (blue)]. The time series shows one minute averaged PM 1.0 contractions incremented from 2021-04-30 09:27:00 unitl 2021-04-30 21:36:00. 

# ### Plot PM 10 

# In[9]:



fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
fig.suptitle(r"PM 10 ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(2, 1, 2)
ax.plot(df_final.index,df_final['PM10 [ug/m3]'], lw = 4.0, label = 'GRIMM', color = colors[0])
ax.plot(df_final.index,df_final['UBC_PM_01_pm100_env'], label = 'UBC-PM-01', color = colors[1])
# ax.plot(df_final.index,df_final['UBC_PM_02_pm100_env'], label = 'UBC-PM-02', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_03_pm100_env'], label = 'UBC-PM-03', color = colors[2])
ax.plot(df_final.index,df_final['UBC_PM_04_pm100_env'], label = 'UBC-PM-04', color = colors[3])
ax.plot(df_final.index,df_final['UBC_PM_05_pm100_env'], label = 'UBC-PM-05', color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel('Time (MM-DD HH)')
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 2.44),
    ncol=6,
    fancybox=True,
    shadow=True,
)
ax = fig.add_subplot(2, 2, 1)
size = 6
ax.scatter(df_final['PM10 [ug/m3]'], df_final['PM10 [ug/m3]'], s=size, color = colors[0])
ax.scatter(df_final['PM10 [ug/m3]'], df_final['UBC_PM_01_pm100_env'], s=size, color = colors[1])
# ax.scatter(df_grim['PM10 [ug/m3]'], df_final['UBC_PM_02_pm100_env'], s=size, color = colors[2])
ax.scatter(df_final['PM10 [ug/m3]'], df_final['UBC_PM_03_pm100_env'], s=size, color = colors[2])
ax.scatter(df_final['PM10 [ug/m3]'], df_final['UBC_PM_04_pm100_env'], s=size, color = colors[3])
ax.scatter(df_final['PM10 [ug/m3]'], df_final['UBC_PM_05_pm100_env'], s=size, color = colors[4])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')

ax = fig.add_subplot(2, 2, 2)
bins = 20
alpha = 0.6
ax.hist(df_final['PM10 [ug/m3]'],bins,alpha = alpha, color = colors[0], zorder = 10)
ax.hist(df_final['UBC_PM_01_pm100_env'],bins, alpha = alpha, color = colors[1])
# ax.hist(df_final['UBC_PM_02_pm10_env'],bins, alpha = alpha,color = colors[2])
ax.hist(df_final['UBC_PM_03_pm100_env'],bins, alpha = alpha, color = colors[2])
ax.hist(df_final['UBC_PM_04_pm100_env'],bins, alpha = alpha,color = colors[3])
ax.hist(df_final['UBC_PM_05_pm100_env'],bins, alpha = alpha, color = colors[4])
ax.set_ylabel('Count')
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')


# Figure shows time series comparison of the measured PM 10 contractions of four UBC AQ Sensors [UBC-PM-01 (orange), UBC-PM-03 (green), UBC-PM-04 (red), UBC-PM-05 (blue)] and the GRIM sensor [GRIMM (blue)]. The time series shows one minute averaged PM 1.0 contractions incremented from 2021-04-30 09:27:00 unitl 2021-04-30 21:36:00. 

# ## Preliminary Results
# We see the UBC-AQ sensors are performing marginally well at PM 1.0 concentrations. However,  the UBC-AQ sensors are grossly over-predicting the concentration levels of PM 2.5 and 10. Let's figure out why this is happening. 

# ### Plot time series PM 1.0, 2.5 and 10 from the GRIMM sensor.

# In[10]:


fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
alpha = 0.7

fig.suptitle(r"GRIMM PM [1, 2.5, 10] ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(2, 1, 2)
ax.plot(df_final.index,df_final['PM1 [ug/m3]'], lw = 4.0, label = 'PM1', alpha = alpha,color = colors[0])
ax.plot(df_final.index,df_final['PM2.5 [ug/m3]'], lw = 4.0, label = 'PM2.5',alpha = alpha, color = colors[1])
ax.plot(df_final.index,df_final['PM10 [ug/m3]'], lw = 4.0, label = 'PM10', alpha = alpha,color = colors[2])

ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel('Time (MM-DD HH)')
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 2.44),
    ncol=6,
    fancybox=True,
    shadow=True,
)
ax = fig.add_subplot(2, 2, 1)
size = 6
ax.scatter(df_final['PM1 [ug/m3]'],df_final['PM1 [ug/m3]'], s=size, alpha = alpha,color = colors[0])
ax.scatter(df_final['PM2.5 [ug/m3]'], df_final['PM2.5 [ug/m3]'], s=size,alpha = alpha, color = colors[1])
ax.scatter(df_final['PM10 [ug/m3]'], df_final['PM10 [ug/m3]'], s=size, alpha = alpha,color = colors[2])

ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')

ax = fig.add_subplot(2, 2, 2)
bins = 20
ax.hist(df_final['PM1 [ug/m3]'],bins,alpha = alpha, color = colors[0], zorder = 10)
ax.hist(df_final['PM2.5 [ug/m3]'],bins,alpha = alpha, color = colors[1], zorder = 10)
ax.hist(df_final['PM10 [ug/m3]'],bins,alpha = alpha, color = colors[2], zorder = 10)

ax.set_ylabel('Count')
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')


# The figure shows a comparison of the  GRIMM sensor PM [1, 2.5, 10]. 

# ### Plot counts of particle sizes averaged over time.

# In[11]:



var_list = list(df_final)[6:37]
var_labels = [var[:-2] for var in var_list]
df_final_mean = df_final[var_list].mean()

fig = plt.figure(figsize=(14, 6))
fig.suptitle("Time averaged counts/liter of particles of size XX um", fontsize=16)
ax = fig.add_subplot(1, 1, 1)
ax.bar(var_labels,df_final_mean)
ax.set_ylabel('Counts/liter')
ax.set_xlabel('Particles of size XX um')
ax.set_xticklabels(var_labels, rotation=70, ha='right')


# The figure shows time averaged counts/liter of particles of size XX um. 
# <br>
# <br>

# We see all air-borne salt particles are 0.7 um or lower, with the majority of size 0.3 um, meaning there should be no deviation in PM concentration for PM 1.0 2.5 and 10 values as they measure the particle size smaller than their respective values. Comparing the GRIMM measured PM [1.0, 2.5, 10] supports this as they are all effectively equal. 
# <br>
# <br>
# We infer that our UBC-PM sensors aren't sensitive enough to delineate clusters of small practical from larger particles. As a result, we see high concentration values in the PM 2.5 and 10. 

# ## Calibration
# We will test a multilayer perceptron (MLP) with a relu active function to determine the weights bias to correct inaccuracies of our UBC PM sensors.
# ### Correct PM 1.0 with an MLP
# First, subset dataframe and normalize

# In[12]:


pm = '2.5' 
pm_u = pm.replace('.', '')
ubc_pm = 'UBC_PM_03_pm'
keep_vars = [f'PM{pm} [ug/m3]', f'{ubc_pm}{pm_u}_env']
df = df_final.drop(columns=[col for col in df_final if col not in keep_vars])
df[f'{ubc_pm}{pm_u}_env2'] = df[f'{ubc_pm}{pm_u}_env']
df.tail()


# Normalize data and print

# In[13]:


scaler = MinMaxScaler()
scaled = scaler.fit_transform(df)

# split up data
y = scaled[:,0]
x = scaled[:,1:]

try:
  # load mlp
  with open(str(data_dir)+f'/mlps/{ubc_pm}{pm_u}.pkl', 'rb') as fid:
      model = pickle.load(fid)
  print(f'found mpl for {ubc_pm}{pm_u}')
except:
  print(f'can not find mpl for {ubc_pm}{pm_u}, building...')
  nhn = 8 
  hidden_layers = 2
  model = MLPRegressor(
      hidden_layer_sizes=(nhn, hidden_layers),
      verbose=False,
      max_iter=1500,
      early_stopping=True,
      validation_fraction=0.2 ,
      batch_size=32,
      solver="adam" ,
      activation="relu",
      learning_rate_init=0.0001,
  )

  model.fit(x, y)  # train the model
  # save the mlp
  with open(str(data_dir)+f'/mlps/{ubc_pm}{pm_u}.pkl', 'wb') as fid:
      pickle.dump(model, fid)    


# Open a dataset from another days comparisons of the GRIMM v UBC-PMs

# In[14]:


# open all ubc_pm datafiles into a list
ubc_list = [prepare_df(f"/UBC-PM-0{i}/", '20210502') for i in range(1,6)]
## combine them to one dataframe
df_ubc = reduce(lambda x, y: pd.merge(x, y, on='rtctime'), ubc_list)
## drop odd character header added when combining
df_ubc.columns = df_ubc.columns.str.replace('_y', '')
## find the ubc dataframe with the lowest time stapms
min_ubc = np.argmin([len(ubc_list[i]) for i in range(len(ubc_list))])
## open the GRIMM dataset and restrict time to smallest ubc pm timeseries
df_grim = open_grimm('20210502', ubc_list[min_ubc])
## combine all the ubc pm dataframes with the grimm dataframe
df_final2 = pd.merge(left=df_grim, right=df_ubc, left_index=True, right_index=True, how='left')
## drop odd character header added when combining
df_final2.columns = df_final2.columns.str.replace('_y', '')
## drop the last 30 mins for this datafile as the sensors were removed form the glass chamber but still sampling
df_final2 = df_final2[:'2021-05-02T18:50']


# reduce dataframe to be only a few variable of interest..print last 5 rows

# In[15]:


keep_vars = [f'PM{pm} [ug/m3]', f'{ubc_pm}{pm_u}_env']
df2 = df_final2.drop(columns=[col for col in df_final2 if col not in keep_vars])
df2[f'{ubc_pm}{pm_u}_env2'] = df2[f'{ubc_pm}{pm_u}_env']
df2.tail()


# Normalize this reduce dataframe and use our mlp model to correct to grimm

# In[16]:


scaler2 = MinMaxScaler()
scaled2 = scaler2.fit_transform(df2)

# split up data
y2 = scaled2[:,0]
x2 = scaled2[:,1:]
y_predict = model.predict(
    x2
) 


# Inverse transform or "unnormalize" data

# In[17]:


y_predict  = np.column_stack((y_predict,x2))
unscaled = scaler.inverse_transform(y_predict)
df_final2[f'{ubc_pm}{pm_u}_cor'] = unscaled[:,0]


# Plot corrected UBC PM 2.5 

# In[18]:



r2value_cor = round(
    stats.pearsonr(df_final2[f'PM{pm} [ug/m3]'].values, df_final2[f'{ubc_pm}{pm_u}_cor'].values)[0], 2
)
r2value = round(
    stats.pearsonr(df_final2[f'PM{pm} [ug/m3]'].values, df_final2[f'{ubc_pm}{pm_u}_env'].values)[0], 2
)
rmse_cor = str(
    round(
        mean_squared_error(
            df_final2[f'PM{pm} [ug/m3]'].values, df_final2[f'{ubc_pm}{pm_u}_cor'].values, squared=False
        ),
        2,
    )
)
rmse = str(
    round(
        mean_squared_error(
            df_final2[f'PM{pm} [ug/m3]'].values, df_final2[f'{ubc_pm}{pm_u}_env'].values, squared=False
        ),
        2,
    )
)
anchored_text = AnchoredText(
    "UBC-PM-03:        " + r"$r$ " + f"{r2value} rmse: {rmse}" + " \nUBC-PM-03 Cor:  " + r"$r$ " + f"{r2value_cor} rmse: {rmse_cor}"  ,
    loc="upper left",
    prop={"size": 12, "zorder": 10},
)


fig = plt.figure(figsize=(14, 12))
fig.autofmt_xdate()
xfmt = DateFormatter("%m-%d %H:00")
fig.suptitle(r"PM 2.5 ($\frac{\mu g}{m^3}$)", fontsize=16)
ax = fig.add_subplot(2, 1, 2)
ax.plot(df_final2.index,df_final2[f'PM{pm} [ug/m3]'].values, lw = 4.0, label = 'GRIMM', color = colors[0])
ax.plot(df_final2.index,df_final2[f'{ubc_pm}{pm_u}_cor'], label = 'UBC-PM-03 Corrected', color = colors[1])
ax.plot(df_final2.index,df_final2[f'{ubc_pm}{pm_u}_env'].values, label = 'UBC-PM-03', color = colors[2])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel('Time (MM-DD HH)')
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 2.44),
    ncol=6,
    fancybox=True,
    shadow=True,
)
ax = fig.add_subplot(2, 2, 1)
size = 6
ax.scatter(df_final2[f'PM{pm} [ug/m3]'], df_final2[f'PM{pm} [ug/m3]'], s=size, color = colors[0])
ax.scatter(df_final2[f'PM{pm} [ug/m3]'], df_final2[f'{ubc_pm}{pm_u}_cor'], s=size, color = colors[1])
ax.scatter(df_final2[f'PM{pm} [ug/m3]'], df_final2[f'{ubc_pm}{pm_u}_env'], s=size, color = colors[2])
ax.set_ylabel(r'$\frac{\mu g}{m^3}$', rotation=0)
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')
ax.add_artist(anchored_text)

ax = fig.add_subplot(2, 2, 2)
bins = 20
alpha = 0.6
ax.hist(df_final2[f'PM{pm} [ug/m3]'],bins,alpha = alpha, color = colors[0], zorder = 10)
ax.hist(df_final2[f'{ubc_pm}{pm_u}_cor'],bins, alpha = alpha, color = colors[1])
ax.hist(df_final2[f'{ubc_pm}{pm_u}_env'],bins, alpha = alpha, color = colors[2])

ax.set_ylabel('Count')
ax.set_xlabel(r'$\frac{\mu g}{m^3}$')


# In[ ]:




