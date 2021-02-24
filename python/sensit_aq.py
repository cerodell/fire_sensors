#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 21:32:55 2019

@author: rodell
"""
import context
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path
from context import data_dir, root_dir


"######################  Adjust for user/times of interest/plot customization ######################"
##User and file location
user = "rodell"

filein  = str(data_dir) + "/ramp/roof-test/"
save    = str(root_dir) + "/img/"
##Plot customization
label      = 14
fig_size   = 20
tick_size  = 12
title_size = 16


##Time of Interst...Start and Stop in PDT!!!!!!!!!!!!
start     = datetime(2020,9,15,18)   ##Pre: (2019,5,6,15,30)  ##Post: (2019,5,16,00,00)
start_str = start.strftime('%m/%d/%y %H')

stop     = datetime(2020,9,21,9)    ##Pre: (2019,5,7,15,30)  ##Post: (2019,5,21,00,00)
stop_str = stop.strftime('%m/%d/%y %H')



"######################  Read File/ Plot Data ######################"
CO_f, NO_f, NO2_f, O3_f, T_f, RH_f = [], [], [], [], [], []
P_f, G_f, Date_f, pm1_f, pm25_f, pm10_f, str_aq  = [], [], [], [], [], [], []

pathlist = sorted(Path(filein).glob('*.TXT'))
for path in pathlist:
    path_in_str = str(path)
    # print(path_in_str)

    # open SPN file to read and read all lines
    handle = open(path_in_str,'r')
    lines  = handle.readlines() 
    lines  = lines[:-1]  ##this is to remove partially empty data on at the end of the txt file 
    
    #################################################################
    "###################### Read Out / Plot Particulate Matter  ######################"
    #################################################################
    # initialize list of products
    CO, NO, NO2, O3, T, RH = [], [], [], [], [], []
    P, G, Date_Str, pm1, pm25, pm10  = [], [], [], [], [], []
    
    ## read and append data to initialize lists
    for line in lines:
        entries = line.split(',') 
        if(entries[0][0] == 'S'):
            Date_Str.append(str(entries[1]))
            CO.append(float(entries[3]))
            NO.append(float(entries[5]))
            NO2.append(float(entries[7]))
            O3.append(float(entries[9]))
            T.append(float(entries[11]))
            RH.append(float(entries[13]))
            P.append(float(entries[15]))
            G.append(float(entries[17]))
            pm1.append(float(entries[19]))
            pm25.append(float(entries[21]))
            pm10.append(float(entries[23]))


    
    ##Loop and convert list to datetime type list
    Date =[]
    for i in range(len(Date_Str)):
        Date_i = datetime.strptime(Date_Str[i], '%m/%d/%y %H:%M:%S') + timedelta(hours=1, minutes=6)
        # Date_i = Date_i.strftime('%Y%m%dT%H:%M:%S')
        Date.append(Date_i)
        

    Date_f.append(Date)
    CO_f.append(CO)
    NO_f.append(NO)
    NO2_f.append(NO2)
    O3_f.append(O3)
    T_f.append(T)
    RH_f.append(RH)
    P_f.append(P)
    G_f.append(G)
    pm1_f.append(pm1)
    pm25_f.append(pm25)
    pm10_f.append(pm10)
    str_aq.append(path_in_str[-8:-4])   


def flatten(listoflists):
    mylist = [item for sublist in listoflists for item in sublist]
    return np.array(mylist)


CO, NO, NO2, O3 = flatten(CO_f), flatten(NO_f), flatten(NO2_f), flatten(O3_f)
T, RH, P, G, DateTime = flatten(T_f), flatten(RH_f), flatten(P_f), flatten(G_f), flatten(Date_f)
pm1, pm25, pm10  = flatten(pm1_f), flatten(pm25_f), flatten(pm10_f)
df = pd.DataFrame({'CO': CO, 'NO':NO, 'NO2': NO2, 'O3':O3, 'Temp': T, 'RH':RH, 'P': P, 'G':G, \
    'DateTime': DateTime, 'pm1':pm1, 'pm25':pm25, 'pm10':pm10 })

df = df.set_index('DateTime')

df = df.loc[start:]

"######################Plot Molecular Concentrations ######################"
plt.close()
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
fig, ax = plt.subplots(4,1, figsize=(16,10))
fig.suptitle('Molecular Concentrations', fontsize=16, fontweight="bold")

ax[0].set_ylabel("CO ($PPB$)", fontsize = label)
ax[0].plot(df.index, df.CO, color = colors[0])
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_xticklabels([])
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')



ax[1].set_ylabel("NO ($PPB$)", fontsize = label)
ax[1].plot(df.index, df.NO, color = colors[1])
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_xticklabels([])
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')



ax[2].set_ylabel("NO2 ($PPB$)", fontsize = label)
ax[2].plot(df.index, df.NO2, color = colors[2])
ax[2].tick_params(axis='both', which='major', labelsize=tick_size)
ax[2].set_xticklabels([])
ax[2].xaxis.grid(color='gray', linestyle='dashed')
ax[2].yaxis.grid(color='gray', linestyle='dashed')


ax[3].set_ylabel("O3 ($PPB$)", fontsize = label)
ax[3].plot(df.index, df.O3, color = colors[3])
ax[3].tick_params(axis='both', which='major', labelsize=tick_size)
ax[3].xaxis.grid(color='gray', linestyle='dashed')
ax[3].yaxis.grid(color='gray', linestyle='dashed')



fig.savefig(save + 'Mol_All.png')
# plt.close()




"######################Plot Thermodynamic Variables ######################"

fig, ax = plt.subplots(2,1, figsize=(16,10))
fig.suptitle('Thermodynamic Variables', fontsize=16, fontweight="bold")

ax[0].set_ylabel("Temp (\N{DEGREE SIGN}C)", fontsize = label)
ax[0].plot(df.index, df.Temp, color = colors[0])
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_xticklabels([])
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')



ax[1].set_ylabel("RH (%)", fontsize = label)
ax[1].plot(df.index, df.RH, color = colors[2])
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_xticklabels([])
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')


fig.savefig(save + 'Thermo_All.png')

plt.close()







"######################Air Quality Variables ######################"

fig, ax = plt.subplots(3,1, figsize=(16,10))
fig.suptitle('Air Quality Variables', fontsize=16, fontweight="bold")

ax[0].set_ylabel("PM 1 ($\u03BCg/m^3$)", fontsize = label)
ax[0].plot(df.index, df.pm1, color = colors[0])
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_xticklabels([])
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')
ax[0].set_ylim(0,65)



ax[1].set_ylabel("PM 2.5 ($\u03BCg/m^3$)", fontsize = label)
ax[1].plot(df.index, df.pm25, color = colors[1])
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_xticklabels([])
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')
ax[1].set_ylim(0,65)



ax[2].set_xlabel("Datetime (PDT)", fontsize = label)
ax[2].set_ylabel("PM 10 ($\u03BCg/m^3$)", fontsize = label)
ax[2].plot(df.index, df.pm10, color = colors[2])
ax[2].tick_params(axis='both', which='major', labelsize=tick_size)
ax[2].xaxis.grid(color='gray', linestyle='dashed')
ax[2].yaxis.grid(color='gray', linestyle='dashed')
ax[2].set_ylim(0,65)


fig.savefig(save + 'AQ_All.png')
 
plt.close()















