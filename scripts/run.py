import os,time
import subprocess as sp
from variables import *

# Defining base paths
#.____________________
def run(simPath):
    procs = []
    basePath = os.getcwd()
    os.chdir(simPath)

    run_cmd = F"prms_m control/{ws}.control"
    cmdd = run_cmd.split()
    p = sp.Popen(cmdd)
    procs.append(p)
    os.chdir(basePath)

    st = time.time()
    for p in procs:
        p.wait()
    print(F"Elapsed time (s) ----> {time.time() - st}")