#!/usr/bin/env python


import numpy as np
import re
import os
import argparse
import json

class configuration_generator:
    
    def __init__(self,base_config="config.ini"):
        self._baseLines=[]
        with open(base_config)as f:
            for line in f.readlines():
                self._baseLines.append(line)
        self._context=None


    def get_pattern_field(self,name):
        return r"^" + str(name)+r"\W*=\W*(.+)\W*$"
        
    def update_data_dir(self,settings,line):
        datadir=settings["dataDir"]
        pattern=r"^datadir =(.*)$"
        m=re.match(pattern,line)
        if m is not None:
                line=f"datadir = {datadir}\n"
        return line
    
    def update_result_dir(self,settings,line):
        datadir=settings["results"]
        pattern=r"^resultdir =(.*)$"
        m=re.match(pattern,line)
        if m is not None:
                line=f"resultdir = {datadir}\n"
        return line

    def update_context(self,line):
        pattern=r"^\[(.*)\]$"
        m=re.match(pattern,line)
        if m is not None:
            self._context=m[1]
    
    def update_field(self,name,value,line):
        pattern=self.get_pattern_field(name)
        m=re.match(pattern,line)
        if m is not None:
            line=f"{name} = {value}\n"
        return line
    
    def update_md_test(self,settings,line):
        nProcessors=settings["nProcessors"]
        for grade in ["easy","hard"]:
            if self._context==f"mdtest-{grade}":
                nFiles=int(settings["mdtest"][f"{grade}"]["nFiles"]/nProcessors)
                line=self.update_field("n",nFiles,line)
        return line

    def update_ior_easy(self,settings,line):

        def get_block_size(settings):
            fileSize=settings["ior"]["easy"]["fileSize"]
            nProcessors=settings["nProcessors"]
            blockSize=int(fileSize*2**10/nProcessors)

            if blockSize % 2 != 0:
                blockSize=blockSize-1
            return blockSize    
        
        if self._context==f"ior-easy":
            blockSize=get_block_size(settings)
            
            line=self.update_field("blockSize",f"{blockSize}m",line)
    
        return line
    def update_ior_hard(self,settings,line):
        
        def get_n_segments(settings):
             blockSize=47008
             fileSize=settings["ior"]["hard"]["fileSize"]
             nProcessors=settings["nProcessors"]
             nSegments=int(fileSize*2**30/(blockSize)/nProcessors)
             return nSegments
        
        if self._context==f"ior-hard":
            nSegments=get_n_segments(settings)
            
            line=self.update_field("segmentCount",nSegments,line)
    
        return line
    
    def _generateLines(self,settings):
        lines2=[]
        for line in self._baseLines:
            self.update_context(line)
            line=self.update_data_dir(settings,line)
            line=self.update_result_dir(settings,line)

            line=self.update_md_test(settings,line)
            line=self.update_ior_easy(settings,line)
            line=self.update_ior_hard(settings,line)
            
            lines2.append(line)
        return lines2

    def save(self,filename,settings):
        lines=self._generateLines(settings)
        with open(filename,"w") as f:
            for line in lines:
                f.write(line)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate configuration files for io500 from a json file. Will create datafiles directory and setup the striping as well')
    parser.add_argument('settings', type=str,
                    help='json file containing the settings')
    parser.add_argument('--output', type=str, default="config.ini",
                    help='Output config file. Defaults to config.ini')
    parser.add_argument('--template', type=str, default="configBase.ini",
                    help='Base config file to use as a template. Defaults to configBase.ini')
    
    
    args = parser.parse_args()


    settings_file=args.settings
    output_config_file=args.output

    print(settings_file)
    print(output_config_file)

    
    with open(settings_file) as f:
        settings=json.load(f)
    
    
    g=configuration_generator(base_config=args.template)
    g.save(output_config_file,settings)


