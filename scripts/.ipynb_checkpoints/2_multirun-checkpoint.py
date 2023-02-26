import sys,os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from runutils import multirun
from helpers import stats
from variables import *

# Extra Paths
#._____________________

param_file = F"{ws.lower()}.params"
worker_root = F'../sim/multirun'
run_cmd = F"prms control/{ws}.control"

# Target parameter
#._____________________

param = 'Ssr2gw_rate'
min_lim = 0.01
max_lim = 100
num_workers = 8 #mp.cpu_count()
lims = np.linspace(min_lim,max_lim,8)

# Running
#._____________________

test = multirun(param,min_lim,max_lim,num_workers,simPath,param_file,worker_root,run_cmd)
# testseg = multirun(param,min_lim,max_lim,num_workers,simPath,param_file,worker_root,run_cmd,res=True,
#                    resZone=[0,0,0,0,0,0,0,0,0,0,0,1]) # reservoir mainly

# Opening observations and compare
#._____________________

cols = [' 1'] # Target output segment
station = pd.read_csv(os.path.join(obsPath,'flow_yauca.csv'),index_col=0,parse_dates=True)

for i in range(len(os.listdir(worker_root))):
    wk = F"worker_{i}"
    wp = os.path.join(worker_root,wk,'output',F"nseg_seg_outflow.csv")
    outflow = pd.read_csv(wp,index_col=0,parse_dates=True)
    outflow = outflow[cols]
    outflow.columns = [wk]
    if i == 0:
        odf = outflow
    else:
        odf[wk] = outflow[wk]
    
    stats(station['Flows'],odf[wk],F"{lims[i]:.4f}-{wk}")


# PLOT
#._____________________
[os.remove(F"figs/{i}") for i in os.listdir('figs') if i.endswith('png')]

station[station['Flows']==-999]=np.nan

fig,ax=plt.subplots(figsize=(18,6))
odf.plot(ax=ax,alpha=0.75)
station.plot(ax=ax,color='black')
fig.savefig(F'figs/{param}_multirun.png')
plt.show()

# # PLOT PER YEAR
# #._____________________

# minYear = station.index.min().year
# maxYear = station.index.max().year
# for i in range(minYear,maxYear+1):
#     fig,ax=plt.subplots(figsize = (18,6))
#     odf.loc[str(i)].plot(ax=ax)
#     station.loc[str(i)].plot(ax=ax,color='black')
#     ax.set_title(F'Year {i}')
#     fig.savefig(F'figs/{param}_multirun_year-{i}.png')