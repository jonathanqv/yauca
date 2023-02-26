import os,shutil,gsflow, time
from gsflow import ParameterRecord as pr
import pandas as pd
import numpy as np
import geopandas as gpd
from variables import *
from run import run
import subprocess as sp

modRunPath = '/mnt/d/5_Watershed'
scriptsDir = os.path.abspath('.')

nworkers = 16 # 8 Models at a time

# CREATE 1 folder for each worker which is each SSP and model, maybe create a batch list of this before the first iteration
# Run in batch and copy outputs with and elseif or if stream or lake for copying outputs, for lakes stats file and for streams segments outflows


def base_setup():

    models = {'stream':['base']}
    for modtype in models.keys():
        for mod in models[modtype]:        
            # Defining paths
            # .___________________
            modPath = os.path.abspath(F'../sim/{mod}')
            ccPath = os.path.abspath(F'../sim/cc/{mod}')
            outPath = os.path.join(ccPath,'output')

            # Copying model and cleaning outputs
            # .___________________

            shutil.copytree(modPath,ccPath,dirs_exist_ok=True)
            shutil.rmtree(outPath)
            os.mkdir(outPath)

            # Modyfing control file
            # .___________________
            ctrlPath = os.path.join(ccPath,'control',F'{ws}.control')
            ctrl = gsflow.ControlFile.load_from_file(ctrlPath,abs_path=False)

            # ctrl.set_values("start_time", values=[2017,1,1,0,0,0]) # Same as the initial time
            ctrl.set_values("end_time", values=[2100,12,31,0,0,0])

            ctrl.set_values("precip_day", values=['./input/precip_cc.cbh'])
            ctrl.set_values("tmax_day", values=['./input/tmax_cc.cbh'])
            ctrl.set_values("tmin_day", values=['./input/tmin_cc.cbh'])

            ctrl.set_values("water_use_flag", values=[0])
            ctrl.set_values("lake_transferON_OFF", values=[0])
            ctrl.set_values("segment_transferON_OFF", values=[0])
            ctrl.set_values("external_transferON_OFF", values=[0])
            ctrl.set_values("nsubOutON_OFF", values=[0])
            ctrl.set_values("csvON_OFF", values=[0])
            if modtype == 'lake':
                ctrl.set_values("statsON_OFF", values=[1])
                ctrl.set_values("nsegmentOutON_OFF", values=[0])
                # Remove stat lake transfer variables
                stats_vals = lake_stats
                stats_vals.remove('total_lake_transfer')
                stats_elem = ['1']*len(stats_vals)
                ctrl.set_values("statsON_OFF", values=[1])                    # Format?
                ctrl.set_values("stat_var_file", values=[F'./output/{ws.lower()}.stat'])
                ctrl.set_values("nstatVars", values=[len(stats_vals)])
                ctrl.set_values("statVar_element", values=stats_elem) # which lake id
                ctrl.set_values("statVar_names", values=stats_vals)
            elif modtype == 'stream':
                ctrl.set_values("statsON_OFF", values=[0])
                ctrl.set_values("nsegmentOutON_OFF", values=[1])

            ctrl.write()

            # Modyfing parameter file
            # .___________________
            paramPath = os.path.join(ccPath,'input',F'{ws.lower()}.params')
            par = gsflow.prms.PrmsParameters.load_from_file(paramPath)

            par.set_values('nwateruse',[0])
            par.set_values('nexternal',[0])

            par.write(paramPath)

            # Data File
            # .___________________
            # Need to change dates in data file
            dataPath = os.path.join(ccPath,'input',F'{ws.lower()}.data')
            datafile = gsflow.prms.PrmsData.load_from_file(dataPath)
            data_data = datafile.data_df
            dataND = pd.DataFrame(columns = data_data.columns) # creating dataframe for climate change
            dr = pd.date_range('2017/1/1','2100/12/31')
            dataND['Date'] = dr
            dataND['Year'] = dr.year
            dataND['Month'] = dr.month
            dataND['Day'] = dr.day
            dataND['Hour'] = 0; dataND['Minute'] = 0; dataND['Second'] = 0
            if 'gate_ht_0' in data_data.columns:
                dataND['gate_ht_0'] = 0.0; dataND['lake_elev_0'] = 0.0;
            newDataCC = pd.concat([data_data,dataND])
            prmsDataCC = gsflow.prms.PrmsData(newDataCC,header='Climate Change file prepared by JQ')
            prmsDataCC.write(dataPath)
                        
def running():
    ccBasePath = '../sim/cc'
    ccDataPath = '/mnt/d/5_Watershed/climate_change' #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
    mrBasePath = '../sim/multirun'
    ccPath = os.path.join(modRunPath,'7_cc-bc',ws) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
    ccOutPath = os.path.join(modRunPath,'8_cc_outputs-bc',ws) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!)
    bases = os.listdir(ccBasePath)
    for bss in bases: # Calibrated folders
    #  Creating output folder in SSD if it does not exist
    #.____________________________
        bssOutPath = os.path.join(ccOutPath,bss)
        if os.path.isdir(bssOutPath):
            shutil.rmtree(bssOutPath)
            os.mkdir(bssOutPath)
        else:
            os.mkdir(bssOutPath)
    # Getting a list of CC models
    #.____________________________
        modsmr = []
        ccmods = os.listdir(ccDataPath) # Climate change folders with data
        for ccmod in ccmods:
            ccmodPath = os.path.join(ccDataPath,ccmod)
            for ssp in os.listdir(ccmodPath): # SSP MODELS TO RUN
                if ssp in ['ssp126','ssp245','ssp370','ssp585']: #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
                    modsmr.append(F"{ssp}_{ccmod}")
    # Defining workers and batches
    #._____________________________
    
        nbatch = len(modsmr)//nworkers
        if len(modsmr)/nworkers > nbatch:
            nbatch+=1
        print(F"There are {nbatch} batches")
    # Running and selecting batches
    #._____________________________
        for i in range(nbatch):
            [shutil.rmtree(os.path.join(mrBasePath,i)) for i in os.listdir(mrBasePath)] # cleaning multirun
            
            procs = []
            if nworkers*(i+1) > len(modsmr):
                trgt_mods = modsmr[i*nworkers:len(modsmr)]
            else:
                trgt_mods = modsmr[i*nworkers:nworkers*(i+1)]
    # Formating climate change model and scenario variables
    #._____________________________
            for sspPath in trgt_mods:
                ssp = sspPath.split('_')[-2]
                ccmod = sspPath.split('_')[-1]
                print(F"{bss} - Batch #{i+1} - {ssp} - {ccmod}")
    # Creating multiruns
    #._____________________________  
                bPath = os.path.join(ccBasePath,bss)
                mrPath = os.path.join(mrBasePath,F'{bss}_{i+1}_{ssp}_{ccmod}')
                shutil.copytree(bPath,mrPath,dirs_exist_ok=True)            
                    
    # Merging data for this batch and creating .cbh files
    #._____________________________
                baseDataPath = os.path.join(mrPath,'input')
                
                variables = ['precip','tmax','tmin']
                for vrb in variables:
                    # Copying var files
                    cbhFilePath = os.path.join(ccPath,F"{ssp}_{ccmod}_{vrb}_bc.cbh") #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
                    newInpFilePath = os.path.join(baseDataPath,F"{vrb}_cc.cbh") #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
                    shutil.copyfile(cbhFilePath, newInpFilePath) #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
                    
    # Creating multirun
    #._____________________________
                
                os.chdir(mrPath)
                p = sp.Popen(run_cmd.split())
                procs.append(p)
                os.chdir(scriptsDir)

            st = time.time()
            for p in procs:
                p.wait()
            print(F"BATCH #{i+1} Elapsed time (s) ----> {time.time() - st}")
    # Copying outputfiles
    #._____________________________
            for sspPath in trgt_mods:
                ssp = sspPath.split('_')[-2]
                ccmod = sspPath.split('_')[-1]
                mrOutPath = os.path.join(mrBasePath,F'{bss}_{i+1}_{ssp}_{ccmod}','output')
                #Copying files
                if True in ['nseg' in i for i in os.listdir(mrOutPath)]:
                    cpFCC = os.path.join(mrOutPath,'nseg_seg_outflow.csv')
                    cpFCCSdd = os.path.join(bssOutPath,F'{ssp}_{ccmod}_outflow.csv')
                    shutil.copy(cpFCC,cpFCCSdd)
                else: # For lakes
                    cpFCC = os.path.join(mrOutPath,F'{ws.lower()}.stat')
                    cpFCCSdd = os.path.join(bssOutPath,F'{ssp}_{ccmod}_stat.csv')
                    shutil.copy(cpFCC,cpFCCSdd)
    [shutil.rmtree(os.path.join(mrBasePath,i)) for i in os.listdir(mrBasePath)] # cleaning multirun  #!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!
            
if __name__ == "__main__":
    base_setup()
    running()