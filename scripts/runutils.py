import os, shutil, time
import multiprocessing as mp
import subprocess as sp
import gsflow as gsf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from helpers import correct_var
    
def multirun(param,min_lim,max_lim,num_workers,base_dir,param_file,worker_root,run_cmd,zone):
    # res=False,resZone=[1]
    notebook_dir = os.getcwd()

    procs = []
    worker_dirs = []

    pV = np.linspace(min_lim,max_lim,num_workers)
    
    # clean workers
    for wr in os.listdir(worker_root):
        try:
            shutil.rmtree(os.path.join(worker_root,wr))
        except:
            pass

    for i in range(num_workers):
        print(F"Worker # {i}")
        new_worker_dir = os.path.join(worker_root,F"worker_{i}")
        if os.path.exists(new_worker_dir):
            shutil.rmtree(new_worker_dir)
        shutil.copytree(base_dir,new_worker_dir)
        # Editing
        par_dir = os.path.join(new_worker_dir,'input',param_file)
        par = gsf.prms.PrmsParameters.load_from_file(par_dir)
        
        correct_var(par,zone,param,pV[i])
        
        par.write(par_dir)
        #
        cwd = new_worker_dir
        os.chdir(cwd)
        cmdd = run_cmd.split()
        p = sp.Popen(cmdd)
        #time.sleep(2.0) #? 
        procs.append(p)
        os.chdir(notebook_dir)
        worker_dirs.append(new_worker_dir)
    st = time.time()
    for p in procs:
        p.wait()
    print(F"Elapsed time (s) ----> {time.time() - st}")

def multirunb(param,pV,num_workers,base_dir,param_file,worker_root,run_cmd,zone):
    # res=False,resZone=[1]
    notebook_dir = os.getcwd()

    procs = []
    worker_dirs = []
    
    # clean workers
    for wr in os.listdir(worker_root):
        try:
            shutil.rmtree(os.path.join(worker_root,wr))
        except:
            pass

    for i in range(num_workers):
        print(F"Worker # {i}")
        new_worker_dir = os.path.join(worker_root,F"worker_{i}")
        if os.path.exists(new_worker_dir):
            shutil.rmtree(new_worker_dir)
        shutil.copytree(base_dir,new_worker_dir)
        # Editing
        par_dir = os.path.join(new_worker_dir,'input',param_file)
        par = gsf.prms.PrmsParameters.load_from_file(par_dir)
        
        correct_var(par,zone,param,pV[i])
        
        par.write(par_dir)
        #
        cwd = new_worker_dir
        os.chdir(cwd)
        cmdd = run_cmd.split()
        p = sp.Popen(cmdd)
        #time.sleep(2.0) #? 
        procs.append(p)
        os.chdir(notebook_dir)
        worker_dirs.append(new_worker_dir)
    st = time.time()
    for p in procs:
        p.wait()
    print(F"Elapsed time (s) ----> {time.time() - st}")
    
    
def multirun_lake_gw(min_lim,max_lim,num_workers,base_dir,param_file,worker_root,run_cmd,zone_arr):
    # res=False,resZone=[1]
    notebook_dir = os.getcwd()
    procs = []
    worker_dirs = []

    pV = np.linspace(min_lim,max_lim,num_workers)
    
    # clean workers
    for wr in os.listdir(worker_root):
        try:
            shutil.rmtree(os.path.join(worker_root,wr))
        except:
            pass

    for i in range(num_workers):
        print(F"Worker # {i}")
        new_worker_dir = os.path.join(worker_root,F"worker_{i}")
        if os.path.exists(new_worker_dir):
            shutil.rmtree(new_worker_dir)
        shutil.copytree(base_dir,new_worker_dir)
        # Editing
        par_dir = os.path.join(new_worker_dir,'input',param_file)
        par = gsf.prms.PrmsParameters.load_from_file(par_dir)
        
        correct_var(par,zone_arr,'gw_seep_coef',pV[i])
        correct_var(par,zone_arr,'gwflow_coef',pV[i])
        
        
        par.write(par_dir)
        #
        cwd = new_worker_dir
        os.chdir(cwd)
        cmdd = run_cmd.split()
        p = sp.Popen(cmdd)
        #time.sleep(2.0) #? 
        procs.append(p)
        os.chdir(notebook_dir)
        worker_dirs.append(new_worker_dir)
    st = time.time()
    for p in procs:
        p.wait()
    print(F"Elapsed time (s) ----> {time.time() - st}")

def multirun_wg(num_workers,base_dir,cntrl_file,worker_root,run_cmd):
    # For generation of weather variables #
    notebook_dir = os.getcwd()

    procs = []
    worker_dirs = []
    
    # clean workers
    for wr in os.listdir(worker_root):
        try:
            shutil.rmtree(os.path.join(worker_root,wr))
        except:
            pass
        
    # Define times
    ctrl_dir = os.path.join(base_dir,'control',cntrl_file)
    ctrl = gsf.ControlFile.load_from_file(ctrl_dir,abs_path =True)
    st = ctrl.get_record('start_time').values.tolist() # extracting
    et = ctrl.get_record('end_time').values.tolist()
    st = datetime(*st[0:3]) # converting to datetime
    et = datetime(*et[0:3])
    step = round((et-st).days / num_workers)
    ts = None # dummy variable

    for i in range(num_workers):
        print(F"Worker # {i}")
        new_worker_dir = os.path.join(worker_root,F"worker_{i}")
        shutil.copytree(base_dir,new_worker_dir)
        # Editing
        ctrl_wdir = os.path.join(new_worker_dir,'control',cntrl_file)
        ctrl = gsf.ControlFile.load_from_file(ctrl_wdir,abs_path =False)

        ts = st + timedelta(days=step)
        if i == num_workers-1:
            ctrl.set_values('start_time',[st.year,st.month,st.day,0,0,0])
            ctrl.set_values('end_time',[et.year,et.month,et.day,0,0,0])
        else:
            ctrl.set_values('start_time',[st.year,st.month,st.day,0,0,0])
            ctrl.set_values('end_time',[ts.year,ts.month,ts.day,0,0,0])
        print(ctrl_wdir)
        
        ctrl.write() # Do not need to specify path as it overwrites.
        st = ts + timedelta(days=1)
        #
        cwd = new_worker_dir
        os.chdir(cwd)
        cmdd = run_cmd.split()
        p = sp.Popen(cmdd)
        #time.sleep(2.0) #? 
        procs.append(p)
        os.chdir(notebook_dir)
        worker_dirs.append(new_worker_dir)
    st = time.time()
    for p in procs:
        p.wait()
    print(time.time() - st)

def multirun_merge(worker_root,file):
    timecols = ['year','month','day','hour','minute','second']
    wr = os.listdir(worker_root)
    wr.sort()
    for i in wr:
        # Opening file
        var_path = os.path.join(worker_root,i,file)
        # If it is the first worker stablish a base dataframe
        if i.endswith('0'):
            fv = pd.read_csv(var_path,delim_whitespace=True,skiprows=3,header=None)
            cols =  timecols + np.arange(1,len(fv.columns)-6+1).tolist()
            fv.columns = cols
            fv = fv.set_index(pd.to_datetime(fv[['year','month','day','hour','minute','second']]))
        # Then just concatenate the other workers
        else:
            fvi = pd.read_csv(var_path,delim_whitespace=True,skiprows=3,header=None)
            cols = timecols + np.arange(1,len(fvi.columns)-6+1).tolist()
            fvi.columns = cols
            fvi = fvi.set_index(pd.to_datetime(fvi[['year','month','day','hour','minute','second']]))

            fv = pd.concat([fv,fvi])
    return fv

def multirun_write(outfile,df,var='precip'):
    with open(outfile, 'w') as f:
        f.writelines(F'Generated with multiprocessing by JQ \n')
        f.writelines(F'{var} {len(df.columns)-6} \n')
        f.writelines(F'######################################## \n')
        for idx,row in df.iterrows():
            formattedString = [F"{i:.0f}" for  i in row.values[0:6]] + [F"{i:.4E}" for  i in row.values[6:]]
            f.writelines(' '.join(formattedString) + '\n')
    f.close()
    
def multirun_write_f(outfile,df,var='precip'): # Faster way of writing sacrificing nice formatting
    with open(outfile, 'w') as f:
        f.writelines(F'Generated with multiprocessing by JQ \n')
        f.writelines(F'{var} {len(df.columns)-6} \n')
        f.writelines(F'######################################## \n')
        # for idx,row in df.iterrows():
        #     formattedString = [F"{i:.0f}" for  i in row.values[0:6]] + [F"{i:.4E}" for  i in row.values[6:]]
        #     f.writelines(' '.join(formattedString) + '\n')
    f.close()
    df.to_csv(outfile,mode='a',index=False,header=False,sep=' ')