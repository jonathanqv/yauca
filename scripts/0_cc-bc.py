import os, shutil, fiona, gsflow, time
from gsflow import ParameterRecord as pr
from osgeo import gdal
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import subprocess as sp
from variables import *
from run import run
from runutils import multirun_write_f

cbhExtension = 'day' # For base files #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
nworkers = 16 #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!

# PATHS
# .___________

scriptsDir = os.path.abspath('.')
Path = '/mnt/c/Users/lrbk/Documents/CSM/Proyects/5_Watershed'
boundPath = os.path.join(Path,'2_GIS','2_Processed',ws,F'basin{ws}.gpkg')
demPath = os.path.join(Path,'2_GIS','1_Base',F'dem_{basinEPSG[ws]}.tif')
ccDataPath = '/mnt/d/5_Watershed/climate_change' #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!

winCcPath = F'/mnt/d/5_Watershed/7_cc-bc/{ws}' #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!

# Opening base and bounds
#.______________

basePath = os.path.join(auxPath,F'{ws}.gpkg')
base = gpd.read_file(basePath)
bound = gpd.read_file(boundPath,layer=F'basin{ws}')

# Creating list with models
#.______________

modsmr = []

ccmods = os.listdir(ccDataPath)
for ccmod in ccmods:
    ccmodPath = os.path.join(ccDataPath,ccmod)
    for ssp in os.listdir(ccmodPath):
        if ssp in ['ssp126','ssp245','ssp370','ssp585']: ####################################### TO FILTER SSP
            sspPath = os.path.join(ccmodPath,ssp)
            modsmr.append(sspPath)

# Creating list with models
#.______________

nbatch = len(modsmr)//nworkers
if len(modsmr)/nworkers > nbatch:
    nbatch+=1
print(F"There are {nbatch} batches")
for i in range(nbatch):
    print(F"Batch #{i+1}")
    procs = []
    if nworkers*(i+1) > len(modsmr):
        trgt_mods = modsmr[i*nworkers:len(modsmr)]
    else:
        trgt_mods = modsmr[i*nworkers:nworkers*(i+1)]
    for sspPath in trgt_mods:
        ssp = sspPath.split('/')[-1]
        ccmod = sspPath.split('/')[-2]
        
        print(ssp,ccmod)
# Processing batches
#.______________

        coordsPath = os.path.join(sspPath,'coordinatespr.csv')
        cd = pd.read_csv(coordsPath,index_col=0)
        cd = gpd.GeoDataFrame(cd, geometry=gpd.points_from_xy(cd.Longitude, cd.Latitude))
        cd = cd.set_crs(epsg=4326)
        cd = cd.to_crs(epsg=bound.crs.to_epsg())
        
        # Filtering points
        cd_filt = cd[cd.within(bound.buffer(30000).unary_union)]

# Copying base model
#.__________________

        baseSimPath = os.path.join('..','sim','base')
        ccSimPath = os.path.join('..','sim','cc',F'{ssp}_{ccmod}')
        shutil.copytree(baseSimPath,ccSimPath,dirs_exist_ok=True)
        
        # MORE PATHS
        inpPath = os.path.join(ccSimPath,'input')
        
# Creating Data File
#.______________________
        data_pr = pd.read_parquet(os.path.join(sspPath,'pr_bc.parquet.gz')) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
        data_tmax = pd.read_parquet(os.path.join(sspPath,'tasmax_bc.parquet.gz')) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
        data_tmin = pd.read_parquet(os.path.join(sspPath,'tasmin_bc.parquet.gz')) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!

        data_pr = data_pr[cd_filt.index] #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
        data_pr = data_pr/25.4 # mm to inches # bias corrected ones are in mm and C #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
        data_tmax = data_tmax[cd_filt.index] #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
        data_tmax = (data_tmax * 9/5) +32 #C to F #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
        data_tmin = data_tmin[cd_filt.index] #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
        data_tmin = (data_tmin * 9/5) +32 #C to F #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!

        data_pr.columns = [F"precip_{ix}" for ix,jx in enumerate(data_pr.columns)]
        data_tmax.columns = [F"tmax_{ix}" for ix,jx in enumerate(data_tmax.columns)]
        data_tmin.columns = [F"tmin_{ix}" for ix,jx in enumerate(data_tmin.columns)]
        merged = pd.concat([data_tmax,data_tmin,data_pr],axis=1)

        cols = merged.columns

        merged['year'] = merged.index.year
        merged['month'] = merged.index.month
        merged['day'] = merged.index.day
        merged['hour'] = merged.index.hour
        merged['minute'] = merged.index.minute
        merged['second'] = merged.index.second
        merged['hour'] = 0 # To fix hour =12

        merged = merged[['year','month','day','hour','minute','second'] + cols.tolist()]

        merged.to_parquet(os.path.join(winCcPath,F'{ssp}_{ccmod}_data.parquet.gz'),compression='gzip')
        merged['Date'] = merged.index
        prms_data = gsflow.prms.PrmsData(data_df=merged,header=F'{ws} PRMS climate change data')
        prms_data.write(os.path.join(inpPath,F'{ssp}_{ccmod}.data'))
# Getting elevation, x, and y coordinates for each point in the climate change model 
#.______________________

        dataset = gdal.Open(demPath)
        band = dataset.GetRasterBand(1)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        transform = dataset.GetGeoTransform()
        xOrigin = transform[0]
        yOrigin = transform[3]
        pixelWidth = transform[1]
        pixelHeight = -transform[5]
        data = band.ReadAsArray()

        elevation = []
        for idx,row in cd_filt.iterrows():
            x = row.geometry.x
            y = row.geometry.y
            col = int((x - xOrigin) / pixelWidth)
            row = int((yOrigin - y ) / pixelHeight)
            elevation.append(data[row][col])
        # cd_filt['Elevation'] = elevation

        dataset = None

        x = cd_filt.geometry.x.values
        y = cd_filt.geometry.y.values

# Modyfing control file
#.______________________
        ctrlPath = os.path.join(ccSimPath,'control',F'{ws}.control')
        ctrl = gsflow.ControlFile.load_from_file(ctrlPath,abs_path=False)
        
        ctrl.set_values("start_time", values=[2017,1,1,0,0,0])
        ctrl.set_values("end_time", values=[2100,12,31,0,0,0])
        ctrl.set_values("data_file", values=[F'./input/{ssp}_{ccmod}.data'])
        
        ctrl.set_values("model_mode", values=["WRITE_CLIMATE"])
        ctrl.set_values("precip_module", values=['ide_dist'])   #'ide_dist'
        ctrl.set_values("temp_module", values=['ide_dist']) #'ide_dist'
        
        [ctrl.remove_record(i) for i in ['precip_day','tmax_day','tmin_day']]   
        
        ctrl.write()
        
# Modyfing parameter file
#.______________________

        paramPath = os.path.join(ccSimPath,'input',F'{ws.lower()}.params')
        par = gsflow.prms.PrmsParameters.load_from_file(paramPath)
        
        nhru = par.get_record('nhru').values
        
        nexternal = 0
        nwateruse = 0
        nrain = data_pr.shape[1]
        ntemp = data_tmax.shape[1]
        psta_elev = elevation
        psta_x = x
        psta_y = y
        tsta_elev = elevation
        tsta_x = x
        tsta_y = y
        psta_nuse = nrain
        tsta_nuse = ntemp

        ndist_psta = nrain
        ndist_tsta = ntemp

        par.set_values('nexternal',[nexternal])
        par.set_values('nwateruse',[nwateruse])
        par.set_values('ndist_psta',[ndist_psta])
        par.set_values('ndist_tsta',[ndist_tsta])

        new_pardel = [pr('nrain',[nrain]),
                      pr('ntemp',[ntemp]),
                      pr('hru_x',np.around(base.x.values,2),[['nhru',nhru]],2),
                      pr('hru_y',np.around(base.y.values,2),[['nhru',nhru]],2),
                      pr('dist_exp',[3.5],[['one',1]],2),
                      pr('prcp_wght_dist',[0.75],[['one',1]],2),
                      pr('temp_wght_dist',[0.75],[['one',1]],2),
                      pr('ndist_psta',[nrain],[['one',1]],1),
                      pr('ndist_tsta',[ntemp],[['one',1]],1),
                      pr('tmax_allsnow_sta',[32],[['one',1]],2),
                      pr('solrad_elev',[2300],[['one',1]],2),
                      pr('tmax_adj',[0],[['one',1]],2),
                      pr('tmin_adj',[0],[['one',1]],2),
                      pr('tmax_allrain_sta',[38],[['one',1]],2),
                      pr('tmax_allsnow_sta',[32],[['one',1]],2)
                     ]
        [par.add_record_object(i) for i in new_pardel]
        
        cbh_pars = ['rain_cbh_adj','snow_cbh_adj','tmax_cbh_adj','tmin_cbh_adj']
        [par.remove_record(i) for i in cbh_pars]
        
        par.set_values('nobs',[0])
        par.set_values('outlet_sta',[0])

        par.set_values('dist_exp',[3.5])

        new_pars = [pr('psta_elev',elevation,[['nrain',nrain]],2),
                    pr('psta_x',psta_x,[['nrain',nrain]],2),
                    pr('psta_y',psta_y,[['nrain',nrain]],2),
                    pr('tsta_elev',tsta_elev,[['ntemp',ntemp]],2),
                    pr('tsta_x',tsta_x,[['ntemp',ntemp]],2),
                    pr('tsta_y',tsta_y,[['ntemp',ntemp]],2),
                    #OTHERS
                    pr('adjmix_rain',[1],[['one',1]],2),
                    pr('adjust_rain',[0],[['one',1]],2),
                    pr('adjust_snow',[0],[['one',1]],2),
                    pr('adjust_rain',[0],[['one',1]],2),
                    pr('psta_nuse',[1]*nrain,[['nrain',ntemp]],1),
                    pr('tsta_nuse',[1]*ntemp,[['ntemp',ntemp]],1),
                   ]
        [par.remove_record(i.name) for i in new_pars if i in par.parameters_list] # Remove because we are also changing dimensions
        [par.add_record_object(i) for i in new_pars] # Add

        par.write(paramPath)
        
# Parallel running per batch
#.________________________
        os.chdir(ccSimPath)
        p = sp.Popen(run_cmd.split())
        procs.append(p)
        os.chdir(scriptsDir)
        
    st = time.time()
    for p in procs:
        p.wait()
    print(F"Elapsed time (s) ----> {time.time() - st}")
        
        
# Storing data as parquet files
#.________________________
    print("Saving variables data as parquet")
    variables = ['precip','tmax','tmin']
    
    for sspPath in trgt_mods:
        ssp = sspPath.split('/')[-1]
        ccmod = sspPath.split('/')[-2]
        ccSimPath = os.path.join('..','sim','cc',F'{ssp}_{ccmod}')

        for v in variables:
            start = time.time() #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!

            vPath = os.path.join(ccSimPath,F"{v}.day")
            dfVar = gsflow.prms.PrmsDay(vPath).dataframe
            dfVarPath = os.path.join(winCcPath,F"{ssp}_{ccmod}_{v}.parquet.gz")
            dfVar.to_parquet(dfVarPath,compression='gzip')

            # Writing data file #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            baseDataFile = os.path.join('..','data',F"{v}.{cbhExtension}")# Opening base data file #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            baseData = gsflow.prms.PrmsDay(baseDataFile).dataframe #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew = pd.concat([baseData,dfVar]) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            # Writing df #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            timecols = ['year','month','day','hour','minute','second'] #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            cols =  timecols + dfnew.columns.tolist() #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew['year'] = dfnew.index.year #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew['month'] = dfnew.index.month #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew['day'] = dfnew.index.day #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew['hour'] = dfnew.index.hour #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew['minute'] = dfnew.index.minute #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew['second'] = dfnew.index.second #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            dfnew = dfnew[cols] #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            print(F"Writing {ssp} {ccmod} {v} bc") #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            multirun_write_f(os.path.join(winCcPath,F"{ssp}_{ccmod}_{v}_bc.cbh"),dfnew,var=v) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!        
            print(F"Time to run variable {ssp} {ccmod} {v} bc is {(time.time() - start)/60} min") #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            
    print(os.listdir('../sim/cc'))
    shutil.rmtree('../sim/cc/')
    
    if not os.path.isdir('../sim/cc/'):
        os.mkdir('../sim/cc/')        
        
# # Running the model
# #.______________________

#         start_time = time.time()
#         run(ccSimPath)
#         print(F"{ssp}_{ccmod} - DONE! --- {time.time() - start_time} seconds --- ")
        

# # Copying files and cleaning outputs
# #.______________________

#         shutil.copy(os.path.join(ccSimPath,'precip.day'), os.path.join(winCcPath,F'{ssp}_{ccmod}_precip.cbh'))
#         shutil.copy(os.path.join(ccSimPath,'tmax.day'), os.path.join(winCcPath,F'{ssp}_{ccmod}_tmax.cbh'))
#         shutil.copy(os.path.join(ccSimPath,'tmin.day'), os.path.join(winCcPath,F'{ssp}_{ccmod}_tmin.cbh'))


#         [os.remove(os.path.join(ccSimPath,i)) for i in os.listdir(ccSimPath) if i.endswith('.day')]
