import os,gsflow
import pandas as pd
import numpy as np
import geopandas as gpd
from variables import *

# Opening and loadin Parameter File
#._____________________

paramPath = os.path.join(inpPath,F'{ws.lower()}.params')
par = gsflow.prms.PrmsParameters.load_from_file(paramPath)

# Assigning dimension variables
#._____________________

nhru = par.get_record('nhru').values.item()
nseg = par.get_record('nsegment').values.item()

# Opening base feature
#._____________________

base = gpd.read_file(os.path.join(auxPath,F"{ws}.gpkg"))

# _1sta
#._____________________

# basin_tsta = gsflow.ParameterRecord("basin_tsta",[1],dimensions=[['one',1]],datatype=1)
# par.add_record_object(basin_tsta)
# hru_psta = gsflow.ParameterRecord("hru_psta",[1]*nhru,dimensions=[['nhru',nhru]],datatype=1)
# par.add_record_object(hru_psta)

# rain_adj_vals = list(base.elev.values/3141 * (base.zones>5).values)*12
# rain_adj = gsflow.ParameterRecord("rain_adj",rain_adj_vals,dimensions=[['nhru',nhru],['nmonths',12]],datatype=2)
# par.add_record_object(rain_adj)
# snow_adj = gsflow.ParameterRecord("snow_adj",[1]*nhru*12,dimensions=[['nhru',nhru],['nmonths',12]],datatype=2)
# par.add_record_object(snow_adj)


# hru_tsta = gsflow.ParameterRecord("hru_tsta",[1]*nhru,dimensions=[['nhru',nhru]],datatype=1)
# par.add_record_object(hru_tsta)
# max_missing = gsflow.ParameterRecord("max_missing",[0],dimensions=[['one',1]],datatype=1)
# par.add_record_object(max_missing)
# tmax_adj = gsflow.ParameterRecord("tmax_adj",[0]*nhru*12,dimensions=[['nhru',nhru],['nmonths',12]],datatype=2)
# par.add_record_object(tmax_adj)
# tmin_adj = gsflow.ParameterRecord("tmin_adj",[0]*nhru*12,dimensions=[['nhru',nhru],['nmonths',12]],datatype=2)
# par.add_record_object(tmin_adj)
# tmax_lapse = gsflow.ParameterRecord("tmax_lapse",[3]*nhru*12,dimensions=[['nhru',nhru],['nmonths',12]],datatype=2)
# par.add_record_object(tmax_lapse)
# tmin_lapse = gsflow.ParameterRecord("tmin_lapse",[3]*nhru*12,dimensions=[['nhru',nhru],['nmonths',12]],datatype=2)
# par.add_record_object(tmin_lapse)

# tsta_elev = gsflow.ParameterRecord("tsta_elev",[3141],dimensions=[['ntemp',1]],datatype=2)
# par.add_record_object(tsta_elev)
# psta_elev = gsflow.ParameterRecord("psta_elev",[3141],dimensions=[['nrain',1]],datatype=2)
# par.add_record_object(psta_elev)

# Assigning new values
#._____________________

par.get_record('gwstor_init').values = np.zeros(nhru)

# par.get_record('carea_max').values = np.ones(nhru)*0.6
# par.get_record('gwflow_coef').values = np.ones(nhru)*0.4
# ar.get_record('gwstor_init').values = np.zeros(nhru)
# par.get_record('gwstor_min').values = np.zeros(nhru)*0.21430
# par.get_record('slowcoef_lin').values = np.ones(nhru)
# par.get_record('soil_rechr_max_frac').values = np.ones(nhru)*0.8

# GLM outputs
#.____________________

par.get_record('gwflow_coef').values = np.zeros(nhru)
par.get_record('carea_max').values = np.ones(nhru)*0.781780312500

# par.get_record('soil_moist_max').values = np.ones(nhru)*12.000000		#*0.0001#7.696047
# par.get_record('soil_rechr_max_frac').values = np.ones(nhru)*0.802872
# par.get_record('slowcoef_lin').values = np.ones(nhru)*0.126012	
# par.get_record('ssr2gw_rate').values = np.ones(nhru)*0.098557


par.get_record('ssr2gw_exp').values = np.ones(nhru)*1.419570
par.get_record('ssr2gw_rate').values = np.ones(nhru)*0.126906
par.get_record('K_coef').values = np.ones(nseg)*5.7


# Writing File
#._____________________

par.write(paramPath)
