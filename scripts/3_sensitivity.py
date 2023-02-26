import os, shutil, pyemu
import gsflow as gsf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
from pathlib import Path
from variables import *

parmsCal = parmsSEN
# Paths
#._________________________

baseModelPath = os.path.join(pestPath,'base')
tmpModPath = os.path.join(pestPath,'tmp')
multirunPath = os.path.join(pestPath,'multirun')

pstFilePath = os.path.join(tmpModPath,pstFile)
basePath = os.path.join(auxPath,F'{ws}.gpkg')

# Defining watershed zones
#._________________________

base = gpd.read_file(basePath)
base['zones_cal'] = 1#base.zone

zones = base['zones_cal'].values

# idxLK = [10,11,12] # Reservoir zone
# idxWs = [i for i in range(1,base.zones.max()) if i not in idxLK] # SantaRosa Zones
# base.loc[~base['zones_cal'].isin(idxWs),'zones_cal'] = 0
# base.loc[base['zones_cal'].isin(idxWs),'zones_cal'] = 1

# Defining segment zones
#._________________________

zones_seg = base['zones'].unique()
zones_seg = zones_seg/zones_seg
# zones_seg = list(range(1,base.zones.max()+1))
# for i in range(len(zones_seg)):
#     if zones_seg[i] in idxLK:
#         zones_seg[i] = 0
#     else:
#         zones_seg[i] = 1
# zones_seg = np.array(zones_seg)

# Cleaning base model path
#._________________________

if os.path.isdir(baseModelPath):
    shutil.rmtree(baseModelPath)
    shutil.copytree(simPath,baseModelPath)
else:
    shutil.copytree(simPath,baseModelPath)

# Cleaning multirun
#._________________________

[os.system(F"rm -rf {os.path.join(multirunPath,i)}") for i in os.listdir(multirunPath)]
 
# Copying helpers, params and opening parms
#._________________________

parms = pd.read_csv(parmsCal)
shutil.copy(parmsCal,os.path.join(baseModelPath))# copying parms to calibrate into base
shutil.copy('helpers.py',os.path.join(baseModelPath))

# Loading PRMS parameters
#._________________________

param_path = os.path.join(baseModelPath,'input',f"{ws.lower()}.params")
params = gsf.prms.PrmsParameters.load_from_file(param_path)


# Creating PEST  files
#._________________________

pf = pyemu.utils.PstFrom(baseModelPath,tmpModPath,zero_based=False,echo=False,remove_existing=True)

# Adding parameters to PEST
#._________________________

for idx,row in parms.iterrows():
    print(row.params)
    valFile = F"{row.group}-{row.params}.dat"
    valPath = os.path.join(tmpModPath,valFile)
    paramVal = params.get_record(row.params).values
    dim = paramVal.shape[0]
    with open(valPath, 'w') as f:
        np.savetxt(f, paramVal,fmt="%12.6E")
    if dim ==1:
        z = np.array([[1]])
        nzones = 1
        par = pf.add_parameters(valFile,par_style='d',transform=row['PARTRANS'],
                par_type="constant",
                par_name_base=F"{row.group}-{row.params}",pargp=row.params,#row.group+"_gr",
                lower_bound=row['min'],upper_bound=row['max'], # Bounds?
                ult_lbound=row['min'],ult_ubound=row['max'])
    elif row['group'] == 'stream':
        zone_seg_array = np.reshape(zones_seg,(paramVal.shape[0],1))
        nzones = np.unique(zone_seg_array).shape[0] # -1 because we do not account for 0
        par = pf.add_parameters(valFile,par_style='d',transform=row['PARTRANS'],
                                par_type="zone",zone_array=zone_seg_array,
                                par_name_base=F"{row.group}-{row.params}",pargp=row.params,#row.group+"_gr",
                                lower_bound=row['min'],upper_bound=row['max'], # Bounds?
                                ult_lbound=row['min'],ult_ubound=row['max'],initial_value=row['default'])
    else:
        zone_array = np.reshape(zones,(paramVal.shape[0],1))
        nzones = np.unique(zone_array).shape[0]
        par = pf.add_parameters(valFile,par_style='d',transform=row['PARTRANS'],
                                par_type="zone",zone_array=zone_array,
                                par_name_base=F"{row.group}-{row.params}",pargp=row.params,#row.group+"_gr",
                                lower_bound=row['min'],upper_bound=row['max'], # Bounds?
                                ult_lbound=row['min'],ult_ubound=row['max'],initial_value=row['default'])
    
    #init_vals = np.random.normal(loc=row.default,scale=row.default/100,size=nzones)
    init_vals = np.ones(nzones)*row['default'] #6.43844e+11
    init_vals[init_vals>row['max']] = row['max']
    init_vals[init_vals<row['min']] = row['min']
    par.loc[:,'parval1'] = init_vals
    
# Adding observations to PEST
#._________________________

statFile=F'output/nseg_seg_outflow.csv'
ob = pf.add_observations(statFile,ofile_sep=',',ofile_skip=1,prefix='yauca_flow',obsgp='ya_flow',
                        includes_header=False,index_cols=0,use_cols=[1]) # List index -1? because index is 0

# Removing outputs to avoid reading previous outputs
#._________________________

pf.tmp_files.append(statFile)

# Adding pre-proc func
#._________________________

pf.add_py_function("helpers.py",F"overwriteParams('{ws}','{parmsCal}')",is_pre_cmd=True)

# Adding comand run model
#._________________________

command = F'prms control/{ws}.control'
pf.mod_sys_cmds.append(command)

# Building pest
#._________________________

pst = pf.build_pst(pstFile,version=2,update=False)

# Setting up observed values and weights
#._________________________

obsFlowPath = os.path.join(obsPath,'flow_yauca.csv')
obsFlow = pd.read_csv(obsFlowPath,index_col=0,parse_dates=True)
obsFlow['weight'] = 1
obsFlow.loc[obsFlow['Flows']==-999,'weight']=0
#obsSantaRosa.loc['2015':,'weight'] = 0 # onnly if there is a weird date
#obsSantaRosa = obsSantaRosa.set_index((obsSantaRosa.index-obsSantaRosa.index[0]).days + 1)
pst.observation_data.loc[:,'weight'] = obsFlow.loc[pst.observation_data.idx0.values.astype('str'),'weight'].values # 
pst.observation_data.loc[:,'obsval'] = obsFlow.loc[pst.observation_data.idx0.values.astype('str'),'Flows'].values # 

# Draw samples
#.________________________

# pe = pf.draw(num_reals=100,scale_offset=False) # specsim for grid?
# pe.enforce()
# pe.to_binary(os.path.join(tmpModPath,"prior.jcb"))
# pst.pestpp_options = {}
# pst.pestpp_options["ies_parameter_ensemble"] = "prior.jcb"

# Some pest configs
#.________________________

# pst.parameter_data.loc[:,'parchglim'] = 'relative'
# for idx,row in parms.iterrows():
#     print(row.PARTRANS,row.PARCHGLIM)

#pst.parameter_groups.loc[:,'dermthd'] = 'best_fit'

# Setting up for multirun
#.________________________

noptm = 10
pst.control_data.noptmax = noptm

# Running pestpp-sen
#.________________________

pst.pestpp_options["gsa_method"] = "sobol"
pst.pestpp_options["gsa_sobol_samples"] = 100
pst.pestpp_options["gsa_sobol_par_dist"] = "unif"

# Writing pest
#.________________________

pst.write(pstFilePath,version=1)
#4.66905e+11

master_root = os.path.join(pestPath,"multirun",'master')
worker_root = os.path.join(pestPath,"multirun")
pyemu.os_utils.start_workers(tmpModPath,"pestpp-sen",pstFile,num_workers=8,
                             master_dir=master_root,worker_root=worker_root,
                             port=4269)


# SCHUR https://github.com/pypest/pyemu/blob/407fbba29a566c22a028c82b72c6b8b1cebd1ec6/examples/Schurexample_freyberg.ipynb

#MF thesis https://github.com/oscarfasanchez/Thesis_mf6_pest/tree/master/09_Python