#copy modelData modules from UDEC to HOMOGENIZE
import os
import sys
import shutil
import time
import psutil
import importlib
import argparse

def main():
    
    pass 
    
def importModelData(modelName):
    global modelData
    modelData = importlib.import_module('Data.Input.'+modelName)
    
def run(modelName, radius=10):
    importModelData(modelName)
    main(radius)
    

def ostrichHandler(args):
    if res.clc_deploy:
        print('Clc deploy')
        
        
    
if __name__ == '__main__':
    os.system('cls')
    parser = argparse.ArgumentParser(description='MOUSE: An Up-Scaling Utility for DEM Simulations')
    #parser.add_argument('-n', '--name', required=True ,help='Name of the file containing the model data without the extension')

    subparsers = parser.add_subparsers()
    
    #TODO: scan subparsers from module files
    
    udecParser = subparsers.add_parser('UDEC')
    from Modules import Module_UDEC
    udecParser = Module_UDEC.populateArgumentParser(udecParser)
    #udecParser.set_defaults(func=udecHandler)
    
    hodsParser = subparsers.add_parser('HODS')
    from Modules import Module_HODS    
    hodsParser = Module_HODS.populateArgumentParser(hodsParser)
    #hodsParser.set_defaults(func=hodsHandler)
    
    ostrichParser = subparsers.add_parser('OSTRICH')
    from Modules import Module_OSTRICH
    ostrichParser = Module_OSTRICH.populateArgumentParser(ostrichParser)
    
    args = parser.parse_args()
    args.func(args)
