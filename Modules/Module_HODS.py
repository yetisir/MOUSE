#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import pickle  
import importlib
from .Base import HomogenizationModuleBaseClass
from .HODS.HODS import Homogenize


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
        None: initializes HODS Module and runs it
        
    """
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
    parser.add_argument('-x', '--revX', type=float ,help='x coordinate of REV centre')
    parser.add_argument('-y', '--revY', type=float ,help='y coordinate of REV centre')
    parser.add_argument('-r', '--revRadius', type=float ,help='Radius of REV centre')
    parser.set_defaults(func=parserHandler)
    return parser
    
class Module_HODS (HomogenizationModuleBaseClass):
    """Creates the HODS model interface for MOUSE

    This class allows for the generation of the usage of HODS through the MOUSE framework. Because HODS was also written in python, a direct link can be established between the programs rather than relying on I/O protols.
    
    Attributes:
        stressHistory (nested list of float): List of homogenized stress tensor history
        strainHistory (nested list of float): List of homogenized strain tensor history 
        timeHistory (list of float): List of simulation time steps
        revCentreX(float): x position of centre of REV
        revCentreY(float): y position of centre of REV
        revRadius(float): radius of REV
    """        
    
    def __init__(self, baseName):
        """Initializes class attributes for homogenization Module
        
        Args:
            baseName (str): Name of model input file
                         
        """
        program = 'python HODS.py'
        parameters = {}
        HomogenizationModuleBaseClass.__init__(self, program, parameters, baseName)
        
    def parseInput(self):
        """Parses input file
                        
        Returns:
            struct: returns data in a structured array
            
        """
        return self.loadData()
        
    def formatOutput(self):
        """Formats Homogenization data into consistent nested lists and writes them to binary file
                        
        Returns:
            None: writes serialized binary data to file
        """
        self.printText('Saving homogenization time history:')

        with open(os.path.join(self.textDirectory, '{0}_HOM.txt'.format(self.baseName)), 'w') as file:
            file.write('time S11 S22 S12 LE11 LE22 LE12\n')
            S11History = [x[0,0] for x in self.stressHistory]
            S22History = [x[1,1] for x in self.stressHistory]
            S12History = [x[0,1] for x in self.stressHistory]
            LE11History = [x[0,0] for x in self.strainHistory]
            LE22History = [x[1,1] for x in self.strainHistory]
            LE12History = [x[0,1] for x in self.strainHistory]

            for i in range(len(self.stressHistory)):
                LE11 = LE11History[i]                 
                LE22 = LE22History[i]
                LE12 = LE12History[i]
                S11 = S11History[i]
                S22 = S22History[i]
                S12 = S12History[i]
                self.stressHistory[i][0,0] = S11
                self.stressHistory[i][1,1] = S22
                self.stressHistory[i][1,0] = S12
                self.stressHistory[i][0,1] = S12
                self.strainHistory[i][0,0] = LE11
                self.strainHistory[i][1,1] = LE22
                self.strainHistory[i][1,0] = LE12
                self.strainHistory[i][0,1] = LE12

                time = self.timeHistory[i]
                record = [time, S11, S22, S12, LE11, LE22, LE12]
                record = ' '.join(map(str, record))
                file.write(record + '\n')

        bundle = [self.timeHistory, self.stressHistory, self.strainHistory]

        fileName = self.outputFileName()
        bundle = [self.timeHistory, self.stressHistory, self.strainHistory]
        self.saveData(bundle)
        
        self.printText('\tDone')
            
    def setParameters(self, args):
        """Sets module parameters
         
        Todo:
            assess revCentreX, revCentreY and revRadius from data rather than from input file
        
        Args:
            parameters(dict): new parameters to be set
                        
        Returns:
            None: Sets module parameters
            
        """
        self.revCentreX = args.revX
        self.revCentreY = args.revY
        self.revRadius = args.revRadius
            
        importModelData(self.baseName[:-5])
        if self.revCentreX == None:
            self.revCentreX = modelData.modelSize/2
        if self.revCentreY == None:
            self.revCentreY = modelData.modelSize/2
        if self.revRadius == None:
            self.revRadius = modelData.modelSize/2-modelData.blockSize*2
        self.revCentre = {'x':self.revCentreX, 'y':self.revCentreY}
        
    def run(self):
        """runs the HODS homogenization Module which creates input files for OSTRICH MOUSE Module
        
        Returns:
            None: MOUSE homogenization data files
            
        """
        H = Homogenize(self.revCentre, self.revRadius, fileName=self.baseName)

        self.stressHistory = H.stress()
        self.strainHistory = H.strain()
        self.timeHistory = H.time()
                
        self.formatOutput()
