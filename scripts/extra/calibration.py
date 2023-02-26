import os, shutil, pyemu
from variables import *

# PATHS
#.________________________

baseModelPath = os.path.join(pestPath,'base')
tmpModPath = os.path.join(pestPath,'tmp')
multirunPath = os.path.join(pestPath,'multirun')

pstFilePath = os.path.join(tmpModPath,pstFile)

# Loading pst file
#.________________________
pst = pyemu.Pst(pstFilePath)

# For sensitivity
#.________________________

#pst.pestpp_options["gsa_method"] = "sobol"
#pst.pestpp_options["rand_seed"] = 358183147
#pst.pestpp_options["gsa_sobol_samples"] = 1
#pst.pestpp_options["gsa_sobol_par_dist"] = "unif"

# For a single run
#.________________________

# pst.control_data.noptmax = 0
# pst.write(pstFilePath,version=2) # 
# pyemu.os_utils.run(F"pestpp-ies {pstFile}",cwd=tmpModPath)
# #pyemu.os_utils.run(F"pestpp-sen {pstFile}",cwd=tmpModPath)

# Run Parallel
#.________________________ 

master_root = os.path.join(pestPath,"multirun",'master')
worker_root = os.path.join(pestPath,"multirun")
pyemu.os_utils.start_workers(tmpModPath,"pestpp-glm",pstFile,num_workers=8,
                             master_dir=master_root,worker_root=worker_root,
                             port=4269)
