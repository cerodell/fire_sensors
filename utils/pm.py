import context
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from context import data_dir, root_dir



def read_ramp(pathlist):
  "######################  Read File/ Plot Data ######################"
  CO_f, NO_f, NO2_f, O3_f, T_f, RH_f = [], [], [], [], [], []
  P_f, G_f, Date_f, pm1_f, pm25_f, pm10_f, str_aq  = [], [], [], [], [], [], []

  # pathlist = sorted(Path(filein).glob('*.TXT'))
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
          if(entries[0][0] == 'D'):
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

  return df


