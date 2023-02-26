import os
ws = 'Yauca'
ctrlPath = os.path.abspath(F'../sim/base/control')
inpPath = os.path.abspath(F'../sim/base/input')
outPath = os.path.abspath(F'../sim/base/output')
obsPath = os.path.abspath(F'../sim/base/obs')
simPath = os.path.abspath(F'../sim/base')
auxPath = os.path.abspath(F'../data')
pestPath = os.path.abspath(F'../sim/pest')
multirunPath = os.path.abspath(F'../sim/multirun')

run_cmd = F"prms_m control/{ws}.control"

parmsSEN = F'params.sen'
parmsIES = F'params.ies'
parmsGLM1 = F'params.glm1'
parmsGLM2 = F'params.glm2'
pstFile = F'{ws.lower()}.pst'

lake_stats = ['lake_inflow','lake_outflow','lake_interflow','lake_lateral_inflow','lake_outcfs', # CFS # outflow (evap+seepage), outcfs (streamflow leaving)
              'lake_gwflow','lake_2gw','lake_seep_in', # CFS # gwflow (gwflow into lake), 2gw (seepage out),  seep_in (seeps in, dominated by lake_elev...)
              'lake_precip', 'lake_evap','elevlake', # Cfs and m
              'lake_stream_in','lake_sroff', # CFS
              'lake_vol','lake_invol','lake_outvol', # acre-ft
              'total_lake_transfer']  # CFS
#lakein_gwflow # acre-inch
basin_stats=['basin_ppt','basin_actet','basin_cfs','basin_runoff_ratio', # General flows
             'basin_sroff','basin_hortonian','basin_dunnian','basin_slowflow','basin_gwflow',# To streams,not using fast as don't using PFR
             'basin_infil','basin_recharge', # Capillary and groundwater 
             'basin_soil_moist','basin_slstor','basin_gwstor', # capillary, gravity-reservor (slow storage), gw
             'basin_sm2gvr','basin_soil_to_gw','basin_sz2gw' # cap-grv,cap-gw,grv-gw
            ]

sub_stats = ['subinc_precip','subinc_actet', # IN
             'sub_cfs','subinc_sroff','subinc_interflow','subinc_gwflow', # CFS
             'subinc_recharge', # IN
             'subinc_capstor_frac','subinc_szstor_frac', # Fraction
             'sub_inq','subinc_deltastor','subinc_stor','subinc_wb' # Extra features
             ]#

seg_stats = ['seg_inflow','seg_outflow','seg_upstream_inflow',
             'seg_lateral_inflow',
             'seginc_sroff','seginc_ssflow','seginc_gwflow']

basinEPSG = {'Yauca':32718,
            'Camana':32718,
            'Ocona':32718,
            'Quilca':32719,
            'Tambo':32719}


#'segment_gain'