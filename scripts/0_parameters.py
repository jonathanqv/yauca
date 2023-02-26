import os, gsflow, shutil
from gsflow.builder import ControlFileDefaults, ControlFileBuilder, PrmsDefaults, ParameterFileBuilder
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from variables import *

cam = PrmsDefaults(f="params-semidist.json")

basePath = os.path.join(auxPath,F'{ws}.gpkg')
base = gpd.read_file(basePath)

#!#! DIMENSIONS #!#!

nhru = base.shape[0]

cam.get_default('nhru').data = nhru
cam.get_default('ngw').data = nhru
cam.get_default('nssr').data = nhru
cam.get_default('nsub').data = base.zones.max()

cam.get_default('nobs').data = 1 # Maybe change when trying to incorporate reservoirs outflows
cam.get_default('nrain').data = 93
cam.get_default('ntemp').data = 94

cam.get_default('ndepl').data = 1
cam.get_default('ndeplval').data = 11

cam.get_default('ndays').data = 366
cam.get_default('nmonths').data = 12

cam.get_default('nsegment').data =  base.zones.max()

cam.add_default("ncascade", data=nhru)
cam.add_default("ncascdgw", data=nhru)

# nlake = 0 # No params
# cam.get_default('nlake').data =  nlake
# cam.get_default('nlake_hrus').data = 1
# cam.get_default('nlakeelev').data = 1
# cam.get_default('nratetbl').data =  1
# cam.get_default('ngate').data =  1
# cam.get_default('nstage').data =  1

# cam.get_default('nexternal').data = 1 #1
# cam.get_default('nwateruse').data = 2 #2

#!#! PARAMETERS #!#!

########################################################### BASIC PHYSICAL ATTRIBUTES ###########################################################
cam.get_default('hru_area').data = np.around(base.area.values / 0.3048**2/43560, 2) # m2 to ft2 to acre
cam.get_default('hru_aspect').data = base.aspect.values
cam.get_default('hru_elev').data = base.elev.values
cam.get_default('hru_lat').data = np.around(base.lat.values,2)
cam.get_default('hru_lon').data = np.around(base.lon.values,2)
cam.get_default('hru_slope').data = base.slope.values
cam.get_default('hru_type').data = base.hru_type.values

########################################################### Measured input ###########################################################
cam.get_default('outlet_sta').data = 1

########################################################### Air temperature and precipitation distribution ###########################################################
cam.get_default('precip_units').data = 0
cam.get_default('temp_units').data = 0

cam.get_default('hru_x').data = np.around(base.x.values,2)
cam.get_default('hru_y').data = np.around(base.y.values,2)

psta_elev = np.loadtxt(os.path.join(auxPath,'psta_elev.dat')).tolist()
cam.get_default('psta_elev').data = psta_elev
psta_x = np.loadtxt(os.path.join(auxPath,'psta_x.dat')).tolist()
cam.get_default('psta_x').data = np.around(psta_x,2)
psta_y = np.loadtxt(os.path.join(auxPath,'psta_y.dat')).tolist()
cam.get_default('psta_y').data = np.around(psta_y,2)
print(len(psta_elev),len(psta_x),len(psta_y))

tsta_elev = np.loadtxt(os.path.join(auxPath,'tsta_elev.dat')).tolist()
cam.get_default('tsta_elev').data = tsta_elev
tsta_x = np.loadtxt(os.path.join(auxPath,'tsta_x.dat')).tolist()
cam.get_default('tsta_x').data = np.around(tsta_x,2)
tsta_y = np.loadtxt(os.path.join(auxPath,'tsta_y.dat')).tolist()
cam.get_default('tsta_y').data = np.around(tsta_y,2)
print(len(tsta_elev),len(tsta_x),len(tsta_y))

cam.get_default('psta_nuse').data = [1]*cam.get_default('nrain').data
cam.get_default('tsta_nuse').data = [1]*cam.get_default('ntemp').data
print(len(cam.get_default('psta_nuse').data))

# IDE
cam.get_default('dist_exp').data = 3.5 #3.5
cam.get_default('ndist_psta').data = cam.get_default('nrain').data
cam.get_default('ndist_tsta').data = cam.get_default('ntemp').data
cam.get_default('prcp_wght_dist').data = [0.75]
cam.get_default('temp_wght_dist').data = [0.75]
cam.get_default('adjust_rain').data = [[0]]
cam.get_default('adjust_snow').data = [0]

########################################################### Potential evapotransporation distribution ###########################################################

hs_krs = np.ones((12,nhru)) * 0.0135
cam.get_default('hs_krs').data = hs_krs.ravel().tolist()

## Evapotranspiration and sublimation ###########################################################
cam.get_default('soil_type').data = base.soil_type.values

########################################################### Interception ###########################################################
cam.get_default('cov_type').data = base.cov_type.values
cam.get_default('covden_sum').data = base.covden_sum.values
cam.get_default('covden_win').data = base.covden_win.values

########################################################### Hortonian surface runoff ###########################################################
cam.get_default('hru_percent_imperv').data = base.percent_imperv.values

########################################################### Streamflow ###########################################################
cam.get_default('hru_segment').data  = base.zones.values
cam.get_default('segment_type').data  = [0,0,0,0,0,0,0,0,0]
sub_order = [0,1,1,3,3,5,6,5,6]
cam.get_default('tosegment').data  = sub_order
#obsin_segment? obsout_segment?
#segment_type , replace inflow?

########################################################### Lake Routing ###########################################################
# nstage, ngate? nratetbl
# Check if groundwater_seep_coef changes if I just focus on the reservoirs I have
# Check lake_seep_elev, , changing elevation changes something? 0 is enough?
# Lake_seg_id?
# Depressions?

# cam.get_default('lake_type').data = [5]*nlake # 3: Flow through, 5: rating table
# cam.get_default('lake_hru_id').data = base.hru_type.values-1 # this works because I only have 1 lake
# #cam.get_default('lake_segment_id').data = [0,0,0,0,0,0,0,0,0,1,0] #!#! Trying with zero as my entire segment is not a lake?

# cam.get_default('elevlake_init').data = [5.1639]*nlake
# init_vol = [132.97E6] #MMC to m3
# cam.get_default('lake_vol_init').data = np.around([i/4046.86/0.3048 for i in init_vol],2) # acre-ft, 1 acre = 4046.86m2
# cam.get_default('ratetbl_lake').data =  [1] # Order does not matter as all are the same

# cam.get_default('K_coef').data = [1,1,1,1,1,1,1,1,1,1,1,24] # 24 for res
# cam.get_default('x_coef').data = [0,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0]

###  rating tables

# cam.get_default('tbl_gate').data =  [0]
# cam.get_default('tbl_stage').data =  [1000]
# cam.get_default('rate_table').data = [[0]]

########################################################### Subbasin parameters ###########################################################
cam.get_default('hru_subbasin').data = base.zones.values
cam.get_default('subbasin_down').data = sub_order


#!#! CLimate by HRU #!#!
ide_dist_params = ['nrain','ntemp','hru_x','hru_y','psta_elev','psta_x','psta_y','tsta_elev','tsta_x','tsta_y',
                   'psta_nuse','tsta_nuse','dist_exp','ndist_psta','ndist_tsta','prcp_wght_dist','temp_wght_dist',
                   'adjust_rain','adjust_snow',
                  'solrad_elev','tmax_adj','tmax_allrain_sta','tmax_allsnow_sta','tmin_adj']
[cam.delete_default(i) for i in ide_dist_params]

# cam.add_default('orad_flag',data=[0],dtype=1,dimension=[['one',1]])

cam.add_default('rain_cbh_adj',data=[1],dtype=2,dimension=[['nmonths',12]])
cam.add_default('snow_cbh_adj',data=[1],dtype=2,dimension=[['nmonths',12]])
cam.add_default('tmax_cbh_adj',data=[1],dtype=2,dimension=[['nmonths',12]])
cam.add_default('tmin_cbh_adj',data=[1],dtype=2,dimension=[['nmonths',12]])

# #!#! Precip 1sta #!#!
# ide_dist_params = ['hru_x','hru_y','psta_elev','psta_x','psta_y','tsta_elev','tsta_x','tsta_y','psta_nuse','tsta_nuse','dist_exp','ndist_psta','ndist_tsta','prcp_wght_dist','temp_wght_dist',
#                    'adjust_rain','adjust_snow',
#                   'solrad_elev','tmax_allrain_sta','tmax_allsnow_sta','ngate','nstage']
# [cam.delete_default(i) for i in ide_dist_params]

#!#! EXPORTING #!#!

pb = ParameterFileBuilder(cam)
params = pb.build()
params.write(os.path.join(inpPath,F'{ws.lower()}.params'))