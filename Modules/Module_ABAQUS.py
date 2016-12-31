#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import pickle
from .Base import ContinuumModuleBaseClass

def importModelData(modelName):
    """Imports the input model parameters and assigns them to a global modelData variable
    
    Args:
        modelName(str): Name of file containing the model data.
        
    Returns:
        None: Assigns model parameters from file to global modelData
        
    """
    global modelData
    modelData = importlib.import_module('Data.Input.'+modelName)
 
def parserHandler(args):
    """Function called after argparse subparser is executed
    
    Args:
        args(argparse.Arguments): arparse parsed command line arguments.
        
    Returns:
        None: initializes ABAQUS Module and runs it
        
    """
    pass
    numSimulations = 0
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'Data', 'Binary')
    for file in os.listdir(path):
        if args.name in file:
            testNumSimulations = int(file[len(args.name)+3])    
            if testNumSimulations > numSimulations:
                numSimulations = testNumSimulations+1
    for i in range(numSimulations):      
        fileName = '{0}({1}.{2})'.format(args.name, 0, i)  
        M = Module_HODS(fileName)
        M.setParameters(args)
        M.run()
    
def populateArgumentParser(parser):
    """Adds arguments to the argument parser
    
    Args:
        parser(argparse.ArgumentParser): empty argparse subparser
        
    Returns:
        argparse.ArgumentParser: same argparse supparser, now populated with arguments
        
    """
    parser.add_argument('-n', '--name', required=True ,help='Name of the file containing the model data without the extension')
    parser.set_defaults(func=parserHandler)
    
    return parser
    
class Module_ABAQUS (ContinuumModuleBaseClass):
    def __init__(self, baseName):
        """Initializes class attributes for homogenization Module
        
        Args:
            baseName (str): Name of model input file
                         
        """
        program = 'abaqus cae nogui=runAbaqus.py'
        parameters = {}
        ContinuumModuleBaseClass.__init__(self, program, parameters, baseName)
        
    def parseInput(self):
        """Parses input file
                        
        Returns:
            struct: returns data in a structured array
            
        """
        return self.loadData()
        
    def formatOutput(self):
        """Formats ABAQUS data into consistent nested lists and writes them to binary file
                        
        Returns:
            None: writes serialized binary data to file
        """
        self.printText('Saving homogenization time history:')
        fileName = self.outputFileName()
        bundle = [self.timeHistory, self.stressHistory, self.strainHistory]
        with open(self.outputFileName(), 'wb') as bundleFile:
            pickle.dump(bundle, bundleFile)
        self.printText('\tDone')
            
    def setParameters(self, revCentreX=None, revCentreY=None, revRadius=None):
        """Sets module parameters
         
        Todo:
            assess revCentreX, revCentreY and revRadius from data rather than from input file
        
        Args:
            parameters(dict): new parameters to be set
                        
        Returns:
            None: Sets module parameters
            
        """
        self.revCentreX = revCentreX
        self.revCentreY = revCentreY
        self.revRadius = revRadius
            
        if revCentreX == None:
            self.revCentreX = modelData.modelSize/2
        if revCentreY == None:
            revCentreY = modelData.modelSize/2
        if revRadius == None:
            revRadius = modelData.modelSize/2-modelData.blockSize*2
        revCentre = {'x':revCentreX, 'y':revCentreY}
        
    def run(self):
        """runs the HODS homogenization Module which creates input files for OSTRICH MOUSE Module
        
        Returns:
            None: MOUSE homogenization data files
            
        """
        pickleData = self.parseInput()
        self.clearScreen()
            
        H = Homogenize(self.revCentre, self.revRadius, pickleData=pickleData)
        self.stressHistory = H.stress()
        self.strainHistory = H.strain()
        self.timeHistory = H.time()
                
        self.formatOutput()
