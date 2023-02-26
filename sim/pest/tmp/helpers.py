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
    
    parms = pd.read_csv(parmsCal)
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
    
# if __name__ == "__main__":
#     ws='Camana'
#     formatReservoir() # check
#     procOutReservoir() #check
