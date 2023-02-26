import os
import multiprocessing as mp
import numpy as np
import pandas as pd
import pyemu

# function added thru PstFrom.add_py_function()
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


def main():

    try:
       os.remove(r'output/nseg_seg_outflow.csv')
    except Exception as e:
       print(r'error removing tmp file:output/nseg_seg_outflow.csv')
    try:
       os.remove(r'output/nseg_seg_outflow.csv')
    except Exception as e:
       print(r'error removing tmp file:output/nseg_seg_outflow.csv')
    pyemu.helpers.apply_list_and_array_pars(arr_par_file='mult2model_info.csv',chunk_len=50)
    overwriteParams('Yauca','paramsYauca.glm2')
    pyemu.os_utils.run(r'prms control/Yauca.control')


if __name__ == '__main__':
    mp.freeze_support()
    main()

