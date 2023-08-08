import reframe as rfm
import reframe.utility.sanity as sn
import os 
import re
import json

'''
io500 Input/Output test

The 'settings.json' file contains the configurations of the particular io500 tests,
including the number of processors to use. All file size units are in GiB and aggregated 
over all processors. Both ior and metadata tests are performed.
'''

@rfm.simple_test
class io500(rfm.RegressionTest):

    lang = parameter(['cpp'])
    valid_systems = ['cirrus:compute']
    valid_prog_environs = ['gnu']
    
    settings= parameter(["settings.json"])
    #settings=parameter(["settings_rdfaas.yaml"])
    
    def __init__(self,**kwds):
        
        super().__init__()

       

        self.executable_opts = ['config.ini']

        self.env_vars = {"OMP_NUM_THREADS": str(self.num_cpus_per_task)}

        #self.prerun_cmds  = ['source create_striped_dirs.sh']
        self.time_limit = '24h'
        self.build_system = 'Make'
        #self.build_system.ftn="ftn"
        self.modules = [ "openmpi" ,"python/3.9.13","gcc"]
        self.executable="io500/io500"
        self.prerun_cmds  = ['source generate_config.sh']

        def extract_perf(name):
            return sn.extractsingle(r'\[RESULT\]\s+' + name + r'\s+(\d+\.?\d*)\s+', self.stdout, 1, float)

        self.perf_patterns = {
             'ior-easy-read': extract_perf("ior-easy-read"),
             'ior-easy-write': extract_perf("ior-easy-write"),
             'ior-hard-write': extract_perf("ior-hard-write"),
             'ior-hard-read': extract_perf("ior-hard-read"),
             'mdtest-easy-write': extract_perf("mdtest-easy-write"),
             'mdtest-hard-write': extract_perf("mdtest-hard-write"),
             'mdtest-easy-stat': extract_perf("mdtest-easy-stat"),
             'mdtest-hard-stat': extract_perf("mdtest-hard-stat")
        }



        # self.set_references_per_node()

        #self.reference = {
        #        'cirrus:compute': {
        #        'ior-easy-read': ( 0.9, -0.4, 0.4 ,'GiB/s'),
        #            }
        #            }

        self.env_vars["SETTINGS_JSON"]=self.settings


    @run_before('run')
    def setup_run(self):

        with open(os.path.join(self.stagedir,self.settings)) as f:
            self.settings_json=json.load(f)
        self.num_tasks = self.settings_json["nProcessors"]
        self.num_tasks_per_node = 36
        self.num_cpus_per_task = 1
        

    @sanity_function
    def assert_io500(self):
        return sn.assert_found(r'Bandwidth', self.stdout)
    