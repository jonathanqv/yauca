from variables import *
def overwriteParams(ws,parmsCal):
    '''
    #### Run Before running the model
    
    Overwrites ws.params with new params
    '''
    import os
    import gsflow as gsf
    import pandas as pd
    import numpy as np
        
    param_path = os.path.join('input',F"{ws.lower()}.params")
    params = gsf.prms.PrmsParameters.load_from_file(param_path)
    
    parms = pd.read_csv(parmsCal, comment='#')
    for idx,row in parms.iterrows():
        #
        valFile = F"{row.group}-{row.params}.dat"
        pestvalues = np.loadtxt(valFile,ndmin=1)
        params.get_record(row.params).values = pestvalues
    params.write(param_path)

def stats(obsDf,simDf,keyword='test',silent=False):
    import numpy as np
    import pandas as pd

    stDf = pd.DataFrame(columns=['observed','modeled'],index=simDf.index)
    stDf['observed'] = obsDf
    stDf['modeled'] = simDf
    stDf = stDf.dropna()
    
    obs = stDf['observed'].values
    sim = stDf['modeled'].values
    
    NSE = 1-(sum((obs - sim)**2)/sum((obs-obs.mean())**2))
    RMSE = np.sqrt(sum((obs-sim)**2)/len(obs))
    if silent:
        pass
    else:
        print(F"{keyword} | NSE={NSE:.2f} | RMSE={RMSE:.2f}") #r2={r2:.2f} | 
    return NSE, RMSE

def processStatVolume(ws):
    '''
    #### Not used
    
    Process stats dataframe
    #Need to create an output file with observed volumes for Pane
    '''
    import pandas as pd
    import os
        
    statPath = F'output/{ws.lower()}.stat'
    
    with open(statPath,'r') as f: # Opening file and getting number of outputs
        nouts=int(f.readline())
    with open(statPath,'r') as f: # Opening file and getting columns headers
        data = []
        for i in range(1,nouts+2):
            data.append(f.readline())
    colSim = ['-'.join(i.split(' '))[:-1] for i in data[1:]]
    cols = ['idx','year','month','day','hour','minute','second'] 
    cols += colSim

    stat = pd.read_csv(statPath,skiprows=len(colSim)+1,delim_whitespace=True,header=None)
    stat.columns = cols
    stat['date'] = pd.to_datetime(stat[['year','month','day']])
    stat = stat.set_index('date')
    
    # Filtering to export simulated variables as arrays, exporting .sim files
    stat['lake_vol-4'].to_csv('vol_Pane.sim')

def formatReservoir(ws):
    '''
    #### Run just once 
    
    This function formats the observed volumes from Pane
    '''
    print('queso')
    
    import os
    import pandas as pd
    import gsflow as gsf
    from datetime import datetime
    
    # formatting observed values
    ctrl = gsf.ControlFile.load_from_file(f"control/{ws}.control")
    sT = ctrl.get_record('start_time').values
    eT = ctrl.get_record('end_time').values
    start_time = datetime(sT[0],sT[1],sT[2])
    end_time = datetime(eT[0],eT[1],eT[2])
    
    # Formatting Outputs and exporting .obs files
    panePath = os.path.join('obs','Volume_Pane_AutodemaEgasa.csv')
    pane = procRes(panePath,start_time,end_time,'Pane')
    pane.to_csv('obs/vol_Pane.obs')
    
def procRes(dfPath,start_time,end_time,name):
    import pandas as pd
    
    df = pd.read_csv(dfPath,index_col=0,parse_dates=True)
    df = df.loc[start_time:end_time]
    df = df / (0.3048**3) / 43560 # m3 to ft3 to acr-ft
    df.columns = [F"{name}_acr-ft"]
    
    # Checking df length and correcting
    dr = pd.date_range(start_time,end_time)
    if dr.shape[0] == df.shape[0]:
        pass
    else:
        for idx in dr:
            try:
                df.loc[idx]
            except:
                df.loc[idx] = -999
    df = df.sort_index()
    return df

def wb(tc= [' 1']):
    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    import geopandas as gpd
    from matplotlib.lines import Line2D
    import numpy as np
    # Cfs
    interflow = pd.read_csv(os.path.join(outPath,'nsub_subinc_interflow.csv'),index_col=0,parse_dates=True)
    interflow = interflow[tc].sum(axis=1).to_frame()
    interflow.columns = ['interflow']
    gwflow = pd.read_csv(os.path.join(outPath,'nsub_subinc_gwflow.csv'),index_col=0,parse_dates=True)
    gwflow = gwflow[tc].sum(axis=1).to_frame()
    gwflow.columns = ['gwflow']
    sroff = pd.read_csv(os.path.join(outPath,'nsub_subinc_sroff.csv'),index_col=0,parse_dates=True)
    sroff = sroff[tc].sum(axis=1).to_frame()
    sroff.columns = ['sroff']

    cfs = pd.concat([sroff,gwflow,interflow],axis=1)
    fig,ax=plt.subplots(figsize=(9,6))
    cfs.plot(ax=ax)
    ax.set_ylabel('cfs')
    ax.legend()
    plt.show()

    # IN
    recharge = pd.read_csv(os.path.join(outPath,'nsub_subinc_recharge.csv'),index_col=0,parse_dates=True)
    recharge = recharge[tc].sum(axis=1).to_frame()
    recharge.columns = ['recharge']
    precip = pd.read_csv(os.path.join(outPath,'nsub_subinc_precip.csv'),index_col=0,parse_dates=True)
    precip = precip[tc].sum(axis=1).to_frame()
    precip.columns = ['precip']
    actet = pd.read_csv(os.path.join(outPath,'nsub_subinc_actet.csv'),index_col=0,parse_dates=True)
    actet = actet[tc].sum(axis=1).to_frame()
    actet.columns = ['actet']

    inches = pd.concat([precip,actet,recharge],axis=1)
    fig,ax=plt.subplots(figsize=(9,6))
    inches.plot(ax=ax)
    ax.legend()
    ax.set_ylabel('in')
    plt.show()
    
    #FRAC
    capstor = pd.read_csv(os.path.join(outPath,'nsub_subinc_capstor_frac.csv'),index_col=0,parse_dates=True)
    capstor = capstor[tc].mean(axis=1).to_frame()
    capstor.columns = ['capstor']
    sztor = pd.read_csv(os.path.join(outPath,'nsub_subinc_szstor_frac.csv'),index_col=0,parse_dates=True)
    sztor = sztor[tc].mean(axis=1).to_frame()
    sztor.columns = ['sztor']

    frac = pd.concat([sztor,capstor],axis=1)
    fig,ax=plt.subplots(figsize=(9,6))
    frac.plot(ax=ax)
    ax.legend()
    ax.set_ylabel('frac')
    plt.show()
    
    
    # Soil and gw
    
    base = gpd.read_file(os.path.join(auxPath,F'{ws}.gpkg'))
    gwres_stor = pd.read_csv(os.path.join(outPath,'nhru_gwres_stor.csv'),index_col=0,parse_dates=True)
    gwres_in = pd.read_csv(os.path.join(outPath,'nhru_gwres_in.csv'),index_col=0,parse_dates=True)
    slow_stor = pd.read_csv(os.path.join(outPath,'nhru_slow_stor.csv'),index_col=0,parse_dates=True)
    slow_flow = pd.read_csv(os.path.join(outPath,'nhru_slow_flow.csv'),index_col=0,parse_dates=True)
    soil_moist = pd.read_csv(os.path.join(outPath,'nhru_soil_moist.csv'),index_col=0,parse_dates=True)
    soil_to_ssr = pd.read_csv(os.path.join(outPath,'nhru_soil_to_ssr.csv'),index_col=0,parse_dates=True)

    mult = base['zones'].isin([int(i) for i in tc]).astype(int).values
    area = base['area'].values / base['area'].values.sum()
    mult_array = np.reshape(mult.tolist()*gwres_stor.shape[0],gwres_stor.shape)
    area_array = np.reshape(area.tolist()*gwres_stor.shape[0],gwres_stor.shape)
    
    gwres_stor.loc[:,:] = gwres_stor.values * mult_array/sum(mult) * area_array
    gwres_in.loc[:,:] = gwres_in.values * mult_array/sum(mult)*area_array
    slow_stor.loc[:,:] = slow_stor.values * mult_array/sum(mult) * area_array
    slow_flow.loc[:,:] = slow_flow.values * mult_array/sum(mult) * area_array
    soil_moist.loc[:,:] = soil_moist.values * mult_array/sum(mult) * area_array
    soil_to_ssr.loc[:,:] = soil_to_ssr.values * mult_array/sum(mult) * area_array

    
    gwres_stor = gwres_stor.mean(axis=1).to_frame()
    gwres_stor.columns = ['gwres_stor']
    gwres_in = gwres_in.mean(axis=1).to_frame()
    gwres_in.columns = ['gwres_in']
    slow_stor = slow_stor.mean(axis=1).to_frame()
    slow_stor.columns = ['slow_stor']
    slow_flow = slow_flow.mean(axis=1).to_frame()
    slow_flow.columns = ['slow_flow']
    soil_moist = soil_moist.mean(axis=1).to_frame()
    soil_moist.columns = ['soil_moist']
    soil_to_ssr = soil_to_ssr.mean(axis=1).to_frame()
    soil_to_ssr.columns = ['soil_to_ssr']

    fig,ax=plt.subplots(figsize=(9,6))
    soil_to_ssr.plot(ax=ax,color='black')
    ax2 = ax.twinx()
    soil_moist.plot(ax=ax2,color='#47B5FF')
    custom_lines = [Line2D([0], [0], color='black', lw=4),
                    Line2D([0], [0], color='#47B5FF', lw=4)]
    ax2.legend(custom_lines, ['soil_to_ssr', 'soil_moist'])
    ax.set_ylabel('soil_to_ssr')
    ax2.set_ylabel('soil_moist')
    ax.set_title('soil')
    plt.show()

    fig,ax=plt.subplots(figsize=(9,6))
    slow_stor.plot(ax=ax,color='black')
    ax2 = ax.twinx()
    slow_flow.plot(ax=ax2,color='#47B5FF')
    custom_lines = [Line2D([0], [0], color='black', lw=4),
                    Line2D([0], [0], color='#47B5FF', lw=4)]
    ax2.legend(custom_lines, ['slow_stor', 'slow_flow'])
    ax.set_ylabel('slow_stor')
    ax2.set_ylabel('slow_flow')
    ax.set_title('grvty')
    plt.show()
    

    fig,ax=plt.subplots(figsize=(9,6))
    gwres_stor.plot(ax=ax,color='black', label = 'gwres_in')
    ax2 = ax.twinx()
    gwres_in.plot(ax=ax2,color='#47B5FF', label = 'gwres_stor')
    custom_lines = [Line2D([0], [0], color='black', lw=4),
                    Line2D([0], [0], color='#47B5FF', lw=4)]
    ax2.legend(custom_lines, ['gwres_stor', 'gwres_in'])
    ax.set_ylabel('gwres_stor')
    ax2.set_ylabel('gwres_in')
    ax.set_title('GW')
    plt.show()
    

    
# def correct_variable(par,zones,record,new_val):
#     """
#     zones is an array with idx location, generated with numpy.where
#     Used for 1 param for the whole watershed
#     """
#     import numpy as np
#     values = par.get_record(record).values
#     for idx in zones:
#         values[idx]=new_val
#     par.get_record(record).values = values
    
def correct_var(par,zone,record,newval):
    """
    Applies uniform parameter to the designated zone
    
    'par': gsflow.Prms.ParameterData object
    'zone': 2D zones to be modified (1|True modify, 0|False not modify)
    'record': is the string related to the parameter to modify
    'valsDict': dataframe with keys
        For ndim =1
            x, where x is the new value
        For ndim = 2
            {0:x,4:x2}, where x.. is the new value and the keys represent different spaces, like nmonth
    """
    import numpy as np
    par_rc = par.get_record(record)
    values = par_rc.values.copy()
    z_idx = np.where(zone==1)[0]
    if par_rc.ndim == 1:
        for zz_idx in z_idx:
            values[zz_idx]=newval
    elif par_rc.ndim ==2: # changes 2 different dimensions, i.e. nmonth, values
        maxlen = values.shape[0]/zone.shape[0]
        idx_ts = 0
        while idx_ts < maxlen:
            try:
                tg_val = newval[idx_ts]
            except:
                pass
            lb = idx_ts*len(zone) #lowerbound
            ub = (idx_ts+1)*len(zone) # upperbound # not used

            for zz_idx in (lb+z_idx):
                values[zz_idx] = tg_val

            idx_ts +=1
    par.get_record(record).values = values
    
def correct_dist_var(par,record,newval): # For testing
    import numpy as np
    par_rc = par.get_record(record)
    par.get_record(record).values = newval
    
# if __name__ == "__main__":
#     ws='Camana'
#     formatReservoir() # check
#     procOutReservoir() #check
