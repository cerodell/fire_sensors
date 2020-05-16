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

filename    = '2020514.TXT'
filein  = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Fire_Sensor/data/'
save    = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Fire_Sensor/Images/'

##Plot customization
label      = 14
fig_size   = 20
tick_size  = 12
title_size = 16

df_pm = pd.read_csv(filein + filename)

