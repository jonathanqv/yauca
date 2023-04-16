import os
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from variables import *
from helpers import stats, wb
from matplotlib import rc
from Figures import ReportFigures
rf = ReportFigures()
rf.set_style(width='double', height='tall')
rc('text', usetex=True)
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
class postproc():
    def __init__(self,wsu,prefix='',stream=''):
        self.wsu = wsu
        self.stream = stream
        self.prefix = prefix
    def read_stats(self,stat_vals,statPath):
        base = ['idx','year','month','day','hour','minute','second']
        stat = pd.read_csv(statPath,skiprows=len(stat_vals)+1,delim_whitespace=True,header=None)
        stat.columns = base + stat_vals
        stat['date'] = pd.to_datetime(stat[['year','month','day']])
        stat = stat.set_index('date')
        stat = stat.sort_index()
        self.stat = stat
        return self.stat
    def read_streamflow(self,outPath,subDict):
        strflowPath = os.path.join(outPath,'nseg_seg_outflow.csv')
        strflow = pd.read_csv(strflowPath,index_col=0,parse_dates=True)
        col = list(subDict.keys())[0]
        strflow = strflow[[col]]
        self.model_strflow = strflow
        return self.model_strflow
    def volume_obs(self,volPath):
        obs_vol = pd.read_csv(volPath,index_col=0,parse_dates=True)
        obs_vol[obs_vol == -999]=np.nan
        obs_vol.columns = ['observed']
        obs_vol = obs_vol.sort_index()
        self.obs_vol = obs_vol
        return self.obs_vol
    def streamflow_obs(self,strmPath):
        obs_strm = pd.read_csv(strmPath,index_col=0,parse_dates=True)
        obs_strm[obs_strm == -999]=np.nan
        obs_strm.columns = ['observed']
        obs_strm = obs_strm.sort_index()
        self.obs_strm = obs_strm
        return self.obs_strm
    def evap_obs(self,evapPath,crop=[]):
        obs_evap = pd.read_csv(evapPath,index_col=0,parse_dates=True)
        obs_evap[obs_evap == -999]=np.nan
        obs_evap.columns = ['observed']
        obs_evap = obs_evap.sort_index()
        if len(crop)==1:
            obs_evap=obs_evap.loc[crop[0]:]
        elif len(crop)==2:
            obs_evap=obs_evap.loc[crop[0]:crop[1]]
        self.obs_evap = obs_evap
        return self.obs_evap
    def stream_plot(self,outPath,subDict,legT,colors=['#554994','#4FA095','#F2D388','#874C62']):
        subs = list(subDict.values())
        for leg in legT:
            # Openning datasets
            # .______________
            for l in leg:
                exec(F"{l} = pd.read_csv(os.path.join(outPath,'nseg_{l}.csv'),index_col=0,parse_dates=True)")
                exec(F"{l} = {l}[list(subDict.keys())]")
                new_cols = []
                for col in locals()[l]:
                    new_cols.append(subDict[col])
                exec(F"{l}.columns = new_cols")        #     if i == len(subs)-1:
            # Plotting
            # .______________
            if len(subs) == 1:
                fig,ax=plt.subplots(figsize=(12,4))
                toexec = [F"locals()['{leg[l]}'][[subs[0]]].plot(ax=ax,color=colors[{l}])" for l in range(len(leg))]  
                for te in toexec:
                    exec(te)
                ax.set_xlabel('Date')
                ax.set_ylabel('cfs')
                ax.grid(color='black',alpha=0.5)
                ax.set_title(subs[0])
                ax.legend(leg)
            else:
                fig,ax=plt.subplots(figsize=(12,3*len(subs)),nrows=len(subs))
                for i in range(len(subs)):
                    toexec = [F"locals()['{leg[l]}'][[subs[{i}]]].plot(ax=ax[{i}],color=colors[{l}])" for l in range(len(leg))]    
                    for te in toexec:
                        exec(te)
                    if i == len(subs)-1:
                        ax[i].set_xlabel('Date')
                    else:
                        ax[i].set_xlabel('')
                    ax[i].set_ylabel('cfs')
                    ax[i].grid(color='black',alpha=0.5)
                    ax[i].set_title(subs[i])
                    ax[i].legend(leg)
                
    def lake_plot(self,colors=['#554994','#4FA095','#F2D388','#874C62']):
        legT = [['elevlake'], # ft
                ['lake_stream_in'], # cfs
               ['lake_precip','lake_evap'], # cfs
               ['lake_sroff','lake_interflow','lake_gwflow'],# Lateral inflow
               ['lake_lateral_inflow','lake_seep_in'], # infow
               ['lake_2gw','lake_evap'], # outflow
               ['lake_outflow','lake_inflow']] 
        for leg in legT:
            fig,ax=plt.subplots(figsize=(12,4),nrows=1)
            for i in range(len(leg)):
                exec(F"self.stat.{leg[i]}.plot(ax=ax,color=colors[{i}])")
                # ylabel
                if leg[i] == 'elevlake':
                    ax.set_ylabel('ft')
                else:
                    ax.set_ylabel('cfs')
            ax.set_xlabel('Date')
            ax.legend(leg)
            ax.grid(color='black',alpha=0.5)
    def subbasin_plot(self,outPath,subDict,colors=['#554994','#4FA095','#F2D388','#874C62']):
        subs = list(subDict.values())

        legT = [['subinc_precip','subinc_actet'], # inches
                ['sub_cfs','subinc_interflow','subinc_sroff','subinc_gwflow'], # cfs
                ['subinc_recharge'], # in
                ['subinc_capstor_frac','subinc_szstor_frac'], # %
                ['sub_inq']] # CFS
        legT_Units = ['in','cfs','in','%','cfs']

        idx_ylabel = 0
        for leg in legT:
            # Openning datasets
            # .______________
            for l in leg:
                exec(F"{l} = pd.read_csv(os.path.join(outPath,'nsub_{l}.csv'),index_col=0,parse_dates=True)")
                # Filtering
                locals()[l] = locals()[l][subDict.keys()]
                # Selecting columns
                new_cols = []
                for col in locals()[l]:
                    new_cols.append(subDict[col])
                exec(F"{l}.columns = new_cols")        #     if i == len(subs)-1:
            # Plotting
            # .______________
            fig,ax=plt.subplots(figsize=(12,3*len(subs)),nrows=len(subs))
            for i in range(len(subs)):
                toexec = [F"locals()['{leg[l]}'][[subs[{i}]]].plot(ax=ax[{i}],color=colors[{l}])" for l in range(len(leg))]    
                for te in toexec:
                    try:
                        exec(te)
                    except:
                        print(F"error: {te}")
                if i == len(subs)-1:
                    ax[i].set_xlabel('Date')
                else:
                    ax[i].set_xlabel('')
                ax[i].set_ylabel(legT_Units[idx_ylabel])
                ax[i].grid(color='black',alpha=0.5)
                ax[i].set_title(subs[i])
                ax[i].legend(leg)
            idx_ylabel +=1
    def strm_cal_plot(self,colors=['red','black']):
        self.model_strflow.columns = ['simulated']
        self.obs_strm.columns = ['observed']
        strflowDf = self.model_strflow.join(self.obs_strm)
        
        fig,ax=plt.subplots(figsize= (12,3))
        strflowDf.simulated.plot(ax=ax,color=colors[0],linestyle='--')
        strflowDf.observed.plot(ax=ax,color=colors[1])
        NSE,RMSE = stats(strflowDf[['observed']],strflowDf[['simulated']]) #statistics
        ax.set_xlabel('Date')
        ax.set_ylabel(F'{self.stream} streamgage (cfs)')
        ax.legend()
        ax.grid(color='black',alpha=0.5)
        ax.text(0.1, 0.75, F'NSE={NSE:.2f}\nRMSE={RMSE:.2f}', fontsize=12,transform=ax.transAxes)
        fig.savefig(F'figs_rep/{self.prefix}_streamflow_daily.png',transparent=True,bbox_inches='tight', dpi=300)
        
        
        strflowDf_ym = strflowDf.groupby(strflowDf.index.year).sum()
        fig,ax=plt.subplots(figsize= (12,3))
        strflowDf_ym.plot.bar(ax=ax,color=colors)
        ax.set_xlabel('Date')
        ax.set_ylabel(F'{self.stream} streamgage yearly\ncumulative volume (ft$^3$)')
        ax.legend()
        ax.grid(color='black',alpha=0.5)

        
    def vol_cal_plot(self,colors=['#379237','#153462']):
        mod_vol = self.stat[['lake_vol']]
        mod_vol.columns = ['model']
        lakeVolDf = mod_vol.join(self.obs_vol)
        # Plot daily
        #.________________________
        fig,ax=plt.subplots(figsize= (12,3))
        lakeVolDf.model.plot(ax=ax,color=colors[0],linestyle='--')
        lakeVolDf.observed.plot(ax=ax,color=colors[1])
        NSE,RMSE = stats(lakeVolDf[['observed']],lakeVolDf[['model']]) #statistics
        ax.set_xlabel('Date')
        ax.set_ylabel(F'{self.wsu} reservoir volume (acr-ft)')
        ax.legend()
        ax.grid(color='black',alpha=0.5)
        fig.savefig(F'figs_rep/{self.prefix}_vol_daily.png',transparent=True,bbox_inches='tight', dpi=300)
        # Plot yearly monthly accumulated
        #.________________________
        lakeVolDf_ym = lakeVolDf.groupby(lakeVolDf.index.year).sum()

        fig,ax=plt.subplots(figsize= (12,3))
        lakeVolDf_ym.plot.bar(ax=ax,color=colors)
        ax.set_xlabel('Date')
        ax.set_ylabel(F'{self.wsu} reservoir yearly\ncumulative volume (acr-ft)')
        ax.legend()
        ax.grid(color='black',alpha=0.5)
        # ax.text(5, 4.5, F'NSE={NSE:.2f}\nRMSE={RMSE:.2f}', fontsize=15)
        # fig.savefig(F'figs_rep/{self.prefix}_vol_yearly.png',transparent=True,bbox_inches='tight', dpi=300)
        
    def lake_evap_cal_plot(self,area_ij,colors=['red','black']):
        """
        needs backup, stat and obs, plotting mainly
        """
        mod_evap = (self.stat.lake_evap * 1000 * 86400 * 0.30348**3 / area_ij).to_frame() # CFS to mm
        mod_evap.columns = ['model']
        lakeEvapDf = mod_evap.join(self.obs_evap)
        # Plot daily
        #.________________________
        fig,ax=plt.subplots(figsize= (12,3))
        lakeEvapDf.observed.plot(ax=ax,color=colors[0])
        lakeEvapDf.model.plot(ax=ax,color=colors[1],linestyle='--')
        ax.set_xlabel('Date')
        ax.set_ylabel(F'{self.wsu} reservoir evaporation (mm)')
        ax.legend()
        ax.grid(color='black',alpha=0.5)
        fig.savefig(F'figs_rep/{self.prefix}_et_daily.png',transparent=True,bbox_inches='tight', dpi=300)
        # Plot monthly
        #.________________________
        lakeEvapDf_mm = lakeEvapDf.groupby(pd.PeriodIndex(lakeEvapDf.index, freq="M")).mean()

        fig,ax=plt.subplots(figsize= (12,3))
        lakeEvapDf_mm.observed.plot(ax=ax,color=colors[0])
        lakeEvapDf_mm.model.plot(ax=ax,color=colors[1],linestyle='--')
        ax.set_xlabel('Date')
        ax.set_ylabel(F'{self.wsu} reservoir monthly\nmean evaporation (mm)')
        ax.legend()
        ax.grid(color='black',alpha=0.5)
        fig.savefig(F'figs_rep/{self.prefix}_et_monthly.png',transparent=True,bbox_inches='tight', dpi=300)
        # Plot yearly monthly mean
        #.________________________
        lakeEvapDf_ym = lakeEvapDf.groupby(lakeEvapDf.index.month).mean()
        NSE,RMSE = stats(lakeEvapDf_ym.observed.to_frame(),lakeEvapDf_ym.model.to_frame()) #statistics

        fig,ax=plt.subplots(figsize= (12,3))
        lakeEvapDf_ym.observed.plot(ax=ax,color=colors[0])
        lakeEvapDf_ym.model.plot(ax=ax,color=colors[1],linestyle='--')
        ax.set_xlabel('Date')
        ax.set_ylabel(F'{self.wsu} reservoir yearly\nmean evaporation (mm)')
        ax.set_xticks(range(1,13),['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dic'])
        ax.legend()
        ax.grid(color='black',alpha=0.5)
        ax.text(5, 4.5, F'NSE={NSE:.2f}\nRMSE={RMSE:.2f}', fontsize=15)
        fig.savefig(F'figs_rep/{self.prefix}_et_yearly.png',transparent=True,bbox_inches='tight', dpi=300)