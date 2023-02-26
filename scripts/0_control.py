import os, gsflow, shutil
from gsflow.builder import ControlFileDefaults, ControlFileBuilder, PrmsDefaults
import geopandas as gpd
import pandas as pd
import numpy as np
from variables import *

ctrl = gsflow.ControlFile(records_list=[])

## Simulation execution
ctrl.header = [F'Control File - {ws} watershed']
ctrl.add_record("executable_desc", values=[F'PRMS5 - {ws}'])
ctrl.add_record("executable_model", values=[F'prms']) # prms was added to environment variables
ctrl.add_record("model_mode", values=['PRMS5']) #WRITE_CLIMATE, PRMS5
ctrl.add_record("start_time", values=[2014,1,1,0,0,0])
ctrl.add_record("end_time", values=[2016,12,31,0,0,0]) # 2016,12,31,0,0,0
#ctrl.add_record("prms_warmup", values=[2])
ctrl.add_record("data_file", values=[F'./input/{ws.lower()}.data']) # Could be multiple
ctrl.add_record("param_file", values=[F'./input/{ws.lower()}.params']) # Could be multiple #,'./input/groundwater_cascade.param'
ctrl.add_record("model_output_file", values=[F'./output/{ws.lower()}.out'])

## Module section
#ctrl.add_record("precip_module", values=['precip_1sta'])
ctrl.add_record("precip_module", values=['ide_dist'])   #'ide_dist'
ctrl.add_record("temp_module", values=['ide_dist']) #'ide_dist'
ctrl.add_record("et_module", values=['potet_hs'])
ctrl.add_record("solrad_module", values=['ddsolrad'])
ctrl.add_record("srunoff_module", values=['srunoff_smidx'])
#ctrl.add_record("strmflow_module", values=['strmflow_in_out'])
ctrl.add_record("strmflow_module", values=['muskingum'])
ctrl.add_record("transp_module", values=['transp_tindex'])
ctrl.add_record("soilzone_aet_flag", values=[1])
ctrl.add_record("subbasin_flag", values=[1]) ##!!##!!
ctrl.add_record('cascade_flag',values=[2])
ctrl.add_record('cascadegw_flag',values=[2])
## Water use inputs
# ctrl.add_record("water_use_flag", values=[1])
# ctrl.add_record("lake_transferON_OFF", values=[0])
# ctrl.add_record("lake_transfer_file", values=['./input/lake.transfer'])
# ctrl.add_record("segment_transferON_OFF", values=[1])
# ctrl.add_record("segment_transfer_file", values=['./input/segment_empty.transfer'])
# ctrl.add_record("external_transferON_OFF", values=[1])
# ctrl.add_record("external_transfer_file", values=['./input/external.transfer'])

## Debug Options
ctrl.add_record("parameter_check_flag", values=[1])
ctrl.add_record("print_debug", values=[-1]) #1 for water balances

# ## Statistic variables
# stats_vals = ['lake_inflow','lake_outflow','lake_interflow','lake_lateral_inflow',
#               'lake_gwflow','lake_precip','lake_seep_in','elevlake',
#               'lake_stream_in','lake_2gw','lake_sroff',
#               'lake_evap','lake_outcfs',
#               'lake_vol','lake_invol','lake_outvol'] # acre-ft,'total_lake_transfer','total_lake_gain'
# stats_vals = ['lake_vol']
# stats_elem = ['1']*len(stats_vals)
ctrl.add_record("statsON_OFF", values=[0])                    # Format?
# ctrl.add_record("stat_var_file", values=[F'./output/{ws.lower()}.stat'])
# ctrl.add_record("nstatVars", values=[len(stats_vals)])
# ctrl.add_record("statVar_element", values=stats_elem)#values=["4"] * len(stats_vals)
# ctrl.add_record("statVar_names", values=stats_vals)
# ## Initial conditions
# ctrl.add_record("init_vars_from_file", values=[0])
# ctrl.add_record("save_vars_to_file", values=[0])

## nHru Summary
stats_nhru = [] # lake_transfer , 'hru_ppt','tmaxf','tminf'
ctrl.add_record("nhruOutON_OFF", values=[0])
ctrl.add_record("nhruOutBaseFileName", values=['./output/nhru_'])
ctrl.add_record("nhruOut_format", values=[4])
ctrl.add_record("nhruOut_freq", values=[1]) # or 3 for monthly daily
ctrl.add_record("nhruOutNcol", values=[0])
ctrl.add_record("nhruOutVars", values=[len(stats_nhru)])
ctrl.add_record("nhruOutVar_names", values=stats_nhru) #'hru_streamflow_out','sroff', 'hortonian flow', 'dunnian flow','pref_flow','pref_flow_infil','slow_flow','ssres_flow' 

## nsub Summary
stats_nsub = ['subinc_precip','subinc_actet','subinc_sroff','subinc_interflow',
              'subinc_capstor_frac','subinc_recharge',
             'subinc_gwflow','sub_cfs','sub_inq','subinc_deltastor','subinc_stor',
             'subinc_wb']#,'subinc_szstor_frac'
ctrl.add_record("nsubOutON_OFF", values=[1])
ctrl.add_record("nsubOutBaseFileName", values=['./output/nsub_'])
ctrl.add_record("nsubOutVars", values=[len(stats_nsub)])
ctrl.add_record("nsubOutVar_names", values=stats_nsub)
ctrl.add_record("nsubOut_format", values=[1])
ctrl.add_record("nsubOut_freq", values=[1])

## nsegment Summary
stats_seg = ['seg_inflow','seg_outflow','seg_upstream_inflow',
            'strm_seg_in','seg_lateral_inflow','seginc_gwflow',
            'seginc_ssflow','seginc_sroff']#,'segment_gain','segment_transfer'
ctrl.add_record("nsegmentOutON_OFF", values=[1])
ctrl.add_record("nsegmentOutBaseFileName", values=['./output/nseg_'])
ctrl.add_record("nsegmentOutVars", values=[len(stats_seg)])
ctrl.add_record("nsegmentOutVar_names", values=stats_seg)
ctrl.add_record("nsegmentOut_format", values=[1])
ctrl.add_record("nsegmentOut_freq", values=[1])

## PRMS summary
ctrl.add_record("csvON_OFF", values=[1])
ctrl.add_record("csv_output_file", values=[F'./output/{ws.lower()}.csv'])

## Climate by HRU
ctrl.set_values("precip_module", values=['climate_hru'])
ctrl.set_values("temp_module", values=['climate_hru'])
ctrl.add_record("precip_day", values=['./input/precip.day'])
ctrl.add_record("tmax_day", values=['./input/tmax.day'])
ctrl.add_record("tmin_day", values=['./input/tmin.day'])

ctrl.write(os.path.join(ctrlPath,F'{ws}.control'))
