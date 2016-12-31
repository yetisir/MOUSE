#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import pickle  
import importlib
import statistics
import numpy
import shutil
import time
import psutil
import sys
from .Base import ParameterEstimationModuleBaseClass

    
def importModelData(modelName):
    """Imports the input model parameters and assigns them to a global modelData variable
    
    Args:
        modelName(str): Name of file containing the model data.
        
    Returns:
        None: Assigns model parameters from file to global modelData
        
    """
    global modelData
    modelData = importlib.import_module('Data.Input.'+modelName)
    
def importMaterialData(materialName):
    """Imports the material parameters and assigns them to a global material variable
    
    Args:
        material(str): Name of file containing the model data.
        
    Returns:
        None: Assigns model parameters from file to global material
        
    """
    global material
    material = importlib.import_module('Modules.OSTRICH.materials.'+materialName)
 
def fillTemplate(template, parameters, file):
    """fills a template file with variable parameters
    
    Args:
        template(str): file path to template file
        parameters(dict): dictionary of parameters and corresponding values
        file(str): destination file path for filled template

    Returns:
        None: saves filled template to file
        
    """
    with open(os.path.join(os.path.dirname(__file__), 'OSTRICH', template), 'r') as templateFile:
        t = templateFile.read()
        for i in parameters.keys():
            t = t.replace(i, str(parameters[i]))
        with open(os.path.join(os.path.dirname(__file__), 'OSTRICH', file), 'w') as modelFile:
            modelFile.write(t)

def getVelocityString(velTable):
    """Generates a table of relative velocities (from -1 to 1) for the simulation in a linear string format for ABAQUS
    
    Args:
        velTable(list of float): times at which the velocity changes from negative to positive
                    
    Returns:
        str: table of relative velocities (-1 to 1) in ABAQUS format
        
    """
    accelTime = velTable[-1]/10
    amp = -1
    vString = '((0, {0}), '.format(amp)
    for i in range(len(velTable)-1):
        vString += '({0}, {1}), ({2}, {3}), '.format(velTable[i]-accelTime, amp, velTable[i]+accelTime, amp*-1)
        amp = amp*-1
    vString += '({0}, {1}))'.format(velTable[-1], amp)
    return vString

def parserHandler(args):
    """Function called after argparse subparser is executed
    
    Args:
        args(argparse.Arguments): arparse parsed command line arguments.
        
    Returns:
        None: initializes UDEC Module and runs it
        
    """
    importModelData(args.name)
    M = Module_OSTRICH(args.name)
    M.parseArguments(args)
    M.parseInput()
    M.run()
    
def populateArgumentParser(parser):
    """Adds arguments to the argument parser
    
    Args:
        parser(argparse.ArgumentParser): empty argparse subparser
        
    Returns:
        argparse.ArgumentParser: same argparse supparser, now populated with arguments
        
    """
    parser.add_argument('-n', '--name', required=True ,help='Name of the file containing the model data without the extension')
    parser.add_argument('-id', '--identity', help='identification Number')
    parser.add_argument('-p', '--parallel', default=True, help='use parallel processing')
    parser.add_argument('-c', '--cores', default=4, help='number of logical cores to use for parallel processing')
    parser.add_argument('-o', '--optimizer', default='ParticleSwarm', help='optimization algorithm')
    parser.set_defaults(func=parserHandler)
    
    return parser
    
class Module_OSTRICH (ParameterEstimationModuleBaseClass):
    """Creates the OSTRICH interface for MOUSE

    This class allows for the generation of the usage of UDEC through the MOUSE framework. As of current, there is still no capacity for full automation due to UDEC API limitations. As such, a batch UDEC script is generated which can then be called in UDEC with one command.
    
    Attributes:
        identity(int): for repeat trials, a different identity can be assigned to each game
        MPI(bool): OSTRICH uses parallel processing if True
        cores(int): number of logical cores to be used for optimization
        optimizer(str): optimization algorithm to use. List can be found in OSTRICH Documentation    
    """        
    def __init__(self, baseName):
        """Initializes class attributes for parameter estimation Module
        
        Args:
            baseName (str): Name of model input file
                         
        """
        program = 'ostrichmpi.bat'
        parameters = {}
        ParameterEstimationModuleBaseClass.__init__(self, program, parameters, baseName)
        
    def parseInput(self):
        """Parses input file
                        
        Returns:
            None: creates Ostrich input files
            
        """
        self.printTitle('Generating OSTRICH Input Files for {0}'.format(self.baseName))
        self.printSection('Filling in Model Templates')
        self.printStatus('Creating model parameter file')
        fillTemplate('parameters.tpl', self.getModelParameters(), 'parameters.py')
        self.printDone()
        self.printStatus('Creating OSTRICH input parameter file')
        fillTemplate('ostIn.tpl', self.getOstrichParameters(), 'ostIn.txt')
        self.printDone()
        self.printStatus('Creating model template file')
        fillTemplate('runAbaqus.tpl', self.getModelConstants(), 'runAbaqus.temp.tpl') 
        self.printDone()
    
    def formatOutput(self):
        """Formats parameter estimation data for MOUSE
                        
        Returns:
            None: Copies OSTRICH output files to output directory
        """
        self.printStatus('Saving estimated parameter set')
        shutil.copy(os.path.join(os.path.dirname(__file__), 'OSTRICH', 'OstOutput0.txt'), os.path.join(self.textDirectory, '{0}({1})_PAR.txt'.format(self.baseName, modelData.abaqusMaterial)))
        self.printDone()            
        
    def setParameters(self, args):
        """Sets module parameters
        
        Args:
            parameters(dict): new parameters to be set
                        
        Returns:
            None: Sets module parameters
            
        """
        pass
        
    def run(self):
        """runs the OSTRICH Module which creates input files for OSTRICH, then runs OSTRICH
        
        Returns:
            None: OSTRICH data files
            
        """
        self.printTitle('Running OSTRICH Optimization Software')
        self.printSection('Initializing OSTRICH')
        os.chdir(os.path.join(os.path.dirname(__file__), 'OSTRICH'))
        self.printStatus('Cleaning up OSTRICH mess from previous run')
        os.system('cleanup.bat')
        for j in range(len(modelData.confiningStress)):
            open(os.path.join('fittedHistory', '{0}({1}.{2})_{3}_fittedHistory.pkl'.format(modelData.modelName, 0, j, modelData.abaqusMaterial)), 'w').close()
        self.printDone()
        self.printStatus('Initializing OSTRICH' )
        self.printDone()
        if self.MPI:
            print('Running OSTRICH MPI\n\tProgress...', end='')
            os.system('mpirun.bat >NUL 2>OstErrors.log')
            while 1: 
                try:
                    with open('OstStatus0.txt', 'r') as file:
                        lines = file.readlines()
                        comp = int(float(lines[2][18:-1]))
                        numString = '{0}%'.format(comp)
                        print(numString, end='')
                        print('\b'*len(numString), end='')
                        sys.stdout.flush()
                        if comp == 100:
                            print('100%')
                            print('\tComputing parameter statistics...', end='')
                            sys.stdout.flush()
                            while 1:
                                runningProcesses = psutil.pids()
                                br = True
                                for k in runningProcesses:
                                    try:
                                        if psutil.Process(k).name() == 'OstrichMPI.exe':
                                            br = False
                                    except:
                                        pass
                                if br:
                                    break
                            print('\tDone')        
                            print('Shutting Down OSTRICH\n\tProgress...', end='')
                            sys.stdout.flush()
                            sleepTime = 10
                            for k in range(sleepTime):
                                time.sleep(1)
                                numString = '{0}%'.format(int(k/sleepTime*100))
                                print(numString, end='')
                                print('\b'*len(numString), end='')
                                sys.stdout.flush()
                            print('100%')
                            break
                except (FileNotFoundError, IndexError, PermissionError):
                    pass
                time.sleep(1)
        else:
            print('Running Serial OSTRICH')
            os.system('ostrich.exe')
            print('\tDone')
            print('Shutting Down OSTRICH...')
            print('\Done')
      
        self.formatOutput()
     
        os.system('cleanup.bat')
        os.chdir(os.pardir)
        os.chdir(os.pardir)
        
 
    def getModelParameters(self):
        """Returns abaqus model input parameters
        
        Todo:
            move towards a  more object oriented method of handling data
                        
        Returns:
            dict: dictionary of abaqus input parameters
        """

        parameters =  {'$$mSize': modelData.modelSize,
                                '$$mName': '\''+modelData.modelName+'\'',
                                '$$sName': ['{0}({1}.{2})'.format(modelData.modelName, 0, x) for x in range(len(modelData.confiningStress))],
                                '$$nSteps': modelData.numberOfSteps,
                                '$$rho': modelData.rho,
                                '$$confStress': [x for x in modelData.confiningStress], #***********************************************************fix for different confining stresses!!!!!
                                '$$approxStrain': modelData.velocity*modelData.simulationTime/modelData.modelSize,
                                '$$vel':modelData.velocity,
                                '$$sTime':modelData.simulationTime,
                                '$$vString':getVelocityString([modelData.simulationTime]),
                                '$$boundaryDisplacements': self.getBoundaryDisplacements(),
                                '$$boundaryStresses': self.getBoundaryStresses(),
                                '$$relVars': modelData.relevantMeasurements, 
                                '$$abaqusMaterial':'\''+modelData.abaqusMaterial+'\''}
        return parameters

    def getOstrichParameters(self, frontBias=1):
        """Returns OSTRICH parameters
        
        Todo:
            move towards a  more object oriented method of handling data
                        
        Returns:
            dict: dictionary of udec parameters
            
        """
        importMaterialData (modelData.abaqusMaterial)
        ostrichParametersText = '' 
        ostrichParameters = material.ostrichParameters.keys()
        for parameter in ostrichParameters:
                p = material.ostrichParameters[parameter]
                newRecord = '$' + parameter + '\t' + str(p['init']) + '\t' + str(p['low']) + '\t' +str(p['high']) +'\tnone\tnone\tnone\n'
                ostrichParametersText += newRecord
     
        observations = ''
        obsNo = 0
        for k in range(len(modelData.confiningStress)):
            with open(os.path.join(self.binaryDirectory, '{0}({1}.{2})_HOM.pkl'.format(self.baseName, 0, k)), 'rb') as bundleFile:
                bundle = pickle.load(bundleFile)
                timeHistory = bundle[0]
                stressHistory = bundle[1]
                strainHistory = bundle[2]
            averageS11 = statistics.mean([x[0, 0] for x in stressHistory])
            averageS22 = statistics.mean([x[1, 1] for x in stressHistory])
            averageS12 = statistics.mean([x[0, 1] for x in stressHistory])
            averageLE11 = statistics.mean([x[0, 0] for x in strainHistory])
            averageLE22 = statistics.mean([x[1, 1] for x in strainHistory])
            averageLE12 = statistics.mean([x[0, 1] for x in strainHistory])
            averageS = (averageS11+averageS12+averageS22)/3
            averageLE = (averageLE11+averageLE12+averageLE22)/3
            
            numObservations = len(timeHistory) + 1
            #TODO: add weightings so strain and stress can be used together
            for i in range(1, numObservations):
                for j in range(len(modelData.relevantMeasurements)):
                    if modelData.relevantMeasurements[j] == 'S11':
                        o = stressHistory[i-1][0, 0]
                        c = 2
                        # w = 1/averageS
                        w = 1
                    elif modelData.relevantMeasurements[j] == 'S22':
                        o = stressHistory[i-1][1, 1]
                        c = 3
                        # w = 1/averageS
                        w = 1
                    elif modelData.relevantMeasurements[j] == 'S12':
                        o = stressHistory[i-1][0, 1]
                        c = 4
                        # w = 1/averageS
                        w = 1
                    elif modelData.relevantMeasurements[j] == 'LE11':
                        o = strainHistory[i-1][0, 0]
                        c = 5
                        # w = 1/averageLE
                        w = 1
                    elif modelData.relevantMeasurements[j] == 'LE22':
                        o = strainHistory[i-1][1, 1]
                        c = 6
                        # w = 1/averageLE
                        w = 1
                    elif modelData.relevantMeasurements[j] == 'LE12':
                        o = strainHistory[i-1][0, 1]
                        c = 7
                        # w = 1/averageLE
                        w = 1
                    if str(o) != str(numpy.NaN):
                        l = k*(numObservations-1)+ i 
                        #obsNo = k*(numObservations-1)*len(modelData.relevantMeasurements) + (i-1)*len(modelData.relevantMeasurements) + (j +1)
                        obsNo += 1
                        bias = frontBias
                        w = w*((1-bias)/numObservations*i+bias)
                        newObservation = 'obs{} \t\t{:10f} \t{} \toutput.dat \tOST_NULL \t{} \t\t{}\n'.format(obsNo, o, w, l, c)
                        observations += newObservation

        parameters = {'$$ostrichParameters':ostrichParametersText, 
                      '$$ostrichObservations':observations,
                      '$$pType':self.optimizer}

        return parameters
    
    def getModelConstants(self):
        parameters = material.ostrichParameters
        for parameter in material.ostrichParameters:
            parameters[parameter] = parameter

        parameters['$$$materialDef'] = material.abaqusTemplate
        return parameters
    
    def getBoundaryDisplacements(self):
        displacements = []
        for k in range(len(modelData.confiningStress)):
            with open(os.path.join(self.binaryDirectory, '{0}({1}.{2})_HOM.pkl'.format(self.baseName, 0, k)), 'rb') as bundleFile:
                bundle = pickle.load(bundleFile)
                timeHistory = bundle[0]
                stressHistory = bundle[1]
                strainHistory = bundle[2]
            LE11 = [x[0,0] for x in strainHistory]
            LE22 = [x[1,1] for x in strainHistory]
            
            U1 = [x*modelData.modelSize for x in LE11]
            U2 = [x*modelData.modelSize for x in LE22]

            v1Tuple = [(timeHistory[i], U1[i]) for i in range(len(timeHistory))]
            v2Tuple = [(timeHistory[i], U2[i]) for i in range(len(timeHistory))]
            displacements.append((v1Tuple, v2Tuple))
        return displacements

    def getBoundaryStresses(self):
        stresses = []
        for k in range(len(modelData.confiningStress)):
            with open(os.path.join(self.binaryDirectory, '{0}({1}.{2})_HOM.pkl'.format(self.baseName, 0, k)), 'rb') as bundleFile:
                bundle = pickle.load(bundleFile)
                timeHistory = bundle[0]
                stressHistory = bundle[1]
                strainHistory = bundle[2]
            S11 = [-x[0,0] for x in stressHistory]
            S22 = [-x[1,1] for x in stressHistory]
            
            S1Tuple = [(timeHistory[i], S11[i]) for i in range(len(timeHistory))]
            S2Tuple = [(timeHistory[i], S22[i]) for i in range(len(timeHistory))]
            stresses.append((S1Tuple, S2Tuple))
        return stresses
