#! /usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import pickle  
import sys
import copy 
import importlib
from .Base import DemModuleBaseClass

    
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
        None: initializes UDEC Module and runs it
        
    """
    importModelData(args.name)
    M = Module_UDEC(args.name)
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
    
def fileList(path):
    """Gets list of all files in a given directory
    
    Args:
        path(str): directory to get file list from
        
    Returns:
        list of str: List of file names in directory
        
    """
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files
        
def simulationFiles(files, rawPath, compiledPath):
    """Isolates files that contain UDEC simulation Data
    
    Args:
        files(list of str): List of files to be searched
        rawPath(str): directory in which the raw UDEC data is contained
        compiledPath(str): directory in which the compiled UDEC data is contained
        
    Returns:
        list of str: List of simulation files without file extension
        
    """
    simulations = []
    compiledFiles = fileList(compiledPath)
    for file in files:
        index = file.rfind('.')
        simulationName = file[:index]
        extension = file[index+1:]
        if 'dat' in extension and len(extension) > 3:
            if file[:file.rfind('.dat')+4] in compiledFiles:
                rTime = os.path.getmtime(os.path.join(rawPath, file))
                cTime = os.path.getmtime(os.path.join(compiledPath, file[:file.rfind('.dat')+4]))
                if rTime > cTime:
                    simulations.append(simulationName)
            else:
                simulations.append(simulationName)
    simulations = list(set(simulations))
    simulations.sort()
    return simulations

def compileFiles(simulations, files, rawPath, compiledPath):
    """compiles the raw UDEC data files for each timestep into one file
    
    Args:
        simulations(list of str): List of simulations names
        files(list of str): List of files to be compiled
        rawPath(str): directory in which the raw UDEC data is contained
        compiledPath(str): directory in which the compiled UDEC data is contained
        
    Returns:
        None: saves compiled data to file.
        
    """
        
    for simulation in simulations:
        print('\t{0}...'.format(simulation), end='')
        sys.stdout.flush()
        simulationFiles = []
        for file in files:
            if 'dat' not in str(file[-3:]) and simulation in file:
                simulationFiles.append(file)
        with open(os.path.join(compiledPath, '{0}.dat'.format(simulation)), 'w') as fout:
            with open(os.path.join(rawPath, simulationFiles[0]), 'r') as fin:
                fout.writelines(fin.readlines()[:2])
            for simulationFile in simulationFiles:
                with open(os.path.join(rawPath, simulationFile), 'r') as fin:
                    fout.writelines(fin.readlines()[2:])
        print('Done')    

def parseDataFile(fileName):
    """Parses raw DEM data from tab delimited text tile into nested python dictionary
    
    The raw DEM Data is considered to be comprised of six distinct types: block data, contact data, corner data, domain data, grid point data, and zone data. Here, each block, contact, corner, domain, grid point, and zone is assigned a unique 7-digit numeric identifier (assuming here that the number of components in the system does not exceed 10 million) by which the associated data can be accessed. The same identifier may be repeated for different data types.Each DEM data hash table has three levels of nesting. The first level keys are the simulation times, which returns the second level of hash tables. The second level keys are the component identifiers, which returns a third level hash table. In this third level, the component attributes can be accessed using the attribute name as the key. 
    
    Args:
        fileName(str): name of data file to be parsed
        
    Returns:
        nested DEM dict: Tripple nested dictionary of DEM data
        
    """
    absPath = os.path.dirname(os.path.realpath(__file__))
    file = open(os.path.join(absPath, 'UDEC', 'compiledData', fileName))
    header = file.readline()[0:-1].split(' ')
    types = file.readline()[0:-1].split(' ')
    data = {}
    timeData = {}
    firstLoop = 1
    while 1:
        record = file.readline()[0:].replace('\n', '').replace('  ', ' ').split(' ')
        record = list(filter(('').__ne__, record))
        if record == []:
            try:
                data[dictTime] = copy.copy(timeData)
            except UnboundLocalError:
                pass
            break
        if firstLoop:
            dictTime = float(record[0])
            firstLoop = 0

        time = float(record[0])
        if dictTime != time:
            data[dictTime] = copy.copy(timeData)
            dictTime = time
        recordData = {}
        for i in range(2, len(record)):
            if types[i] == 'i':
                record[i] = int(record[i])
            elif types[i] == 'f':
                record[i] = float(record[i])
            elif types[i] == 'l':
                csv = record[i].split(',')
                for j in range(len(csv)):
                    csv[j] = int(csv[j])
                record[i] = csv
            recordData[header[i]] = record[i]
        timeData[int(record[1])] = recordData
        oldRecord = record
    return data
    
class Module_UDEC(DemModuleBaseClass):
    """Creates the UDEC model interface for MOUSE

    This class allows for the generation of the usage of UDEC through the MOUSE framework. As of current, there is still no capacity for full automation due to UDEC API limitations. As such, a batch UDEC script is generated which can then be called in UDEC with one command.
    
    Attributes:
        fileName (str): name of simulation data file
        UDECParameters (dict): Dictionary of UDEC parameters as keys and the associated value as dictionary values
        
    """        
    
    def __init__(self, baseName):
        """Initializes class attributes for homogenization Module
        
        Args:
            baseName (str): Name of model input file
                         
        """
        program = 'python HODS.py'
        parameters = {}
        DemModuleBaseClass.__init__(self, program, parameters, baseName)

    def inputFileName(self):
        """Overloads the default input settings to import python data
                        
        Returns:
            str: full path of input python data
        """
        return os.path.join(self.inputDirectory, '{0}{1}'.format(self.baseName, '.py'))

    def outputFileName(self): 
        """Overloads the default input settings to export
                        
        Returns:
            None: writes serialized binary data to file

        """
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.fileName, '_DEM.pkl'))

    def parseInput(self):
        """Parses input file
                        
        Returns:
            struct: returns data in a structured array
            
        """
        return self.loadData()
  
    def formatOutput(self):
        """Formats DEM data into consistent nested hash tables and writes them to binary file
                        
        Returns:
            None: writes serialized binary data to file
        """
        self.printTitle('Compiling All UDEC Data Files')
        absPath = os.path.dirname(os.path.realpath(__file__))
        rawPath = os.path.join(absPath, 'UDEC', 'rawData')
        compiledPath = os.path.join(absPath, 'UDEC', 'compiledData')
        self.printStatus('Getting list of files in data directory')
        filesInDirectory = fileList(rawPath)
        self.printDone()
        self.printStatus('Isolating files for compilation')
        simulations = simulationFiles(filesInDirectory, rawPath, compiledPath)
        self.printDone()
        self.printStatus('Compiling data files')
        compileFiles(simulations, filesInDirectory, rawPath, compiledPath)
        self.printDone()

        numSimulations = 0
        for file in filesInDirectory:
            if self.baseName in file:
                testNumSimulations = int(file[len(self.baseName)+3])    
                if testNumSimulations > numSimulations:
                    numSimulations = testNumSimulations+1
                    
        for i in range(numSimulations):
            self.fileName = '{0}({1}.{2})'.format(self.baseName, 0, i)
            self.printTitle('Parsing {0} DEM data from text files'.format(self.fileName))
            blockFileName = '{0}___block.dat'.format(self.fileName)
            contactFileName = '{0}___contact.dat'.format(self.fileName)
            cornerFileName = '{0}___corner.dat'.format(self.fileName)
            zoneFileName = '{0}___zone.dat'.format(self.fileName)
            gridPointFileName = '{0}___gridPoint.dat'.format(self.fileName)
            domainFileName = '{0}___domain.dat'.format(self.fileName)
           
            self.printStatus('Loading block data')
            blockData = parseDataFile(blockFileName)
            self.printDone()
            self.printStatus('Loading contact data')
            contactData = parseDataFile(contactFileName)
            self.printDone()
            self.printStatus('Loading corner data')
            cornerData = parseDataFile(cornerFileName)
            self.printDone()
            self.printStatus('Loading zone data')
            zoneData = parseDataFile(zoneFileName)
            self.printDone()
            self.printStatus('Loading gridPoint data')
            gridPointData = parseDataFile(gridPointFileName)
            self.printDone()
            self.printStatus('Loading domain data')
            domainData = parseDataFile(domainFileName)
            self.printDone()
            self.printStatus('Saving DEM data to binary')
            self.saveData([blockData, contactData, cornerData, zoneData,
                         gridPointData, domainData])
            self.printDone()
            
    def setParameters(self):
        """Sets module parameters
        
        Args:
            parameters(dict): new parameters to be set
                        
        Returns:
            None: Sets module parameters
            
        """
        pass
        
    def getVelocityString(self, velTable):
        """Generates a table of relative velocities (from -1 to 1) for the simulation in a linear string format for UDEC
        
        Args:
            velTable(list of float): times at which the velocity changes from negative to positive
                        
        Returns:
            str: table of relative velocities (-1 to 1) in UDEC format
            
        """
        accelTime = velTable[-1]/10
        amp = -1
        vString = '((0, {0}), '.format(amp)
        for i in range(len(velTable)-1):
            vString += '({0}, {1}), ({2}, {3}), '.format(velTable[i]-accelTime, amp, velTable[i]+accelTime, amp*-1)
            amp = amp*-1
        vString += '({0}, {1}))'.format(velTable[-1], amp)
        return vString
        
    def getUDECParameters(self):
        """Returns UDEC parameters
        
        Todo:
            move towards a  more object oriented method of handling data
                        
        Returns:
            dict: dictionary of udec parameters
            
        """
        rangeOffset = modelData.blockSize/1000
        bRange = '{0},{1} {0},{2}'.format(-rangeOffset, modelData.modelSize+rangeOffset, rangeOffset)
        tRange = '{0},{1} {2},{1}'.format(-rangeOffset, modelData.modelSize+rangeOffset, modelData.modelSize-rangeOffset)
        lRange = '{0},{1} {0},{2}'.format(-rangeOffset, rangeOffset, modelData.modelSize+rangeOffset)
        rRange = '{0},{1} {2},{1}'.format(modelData.modelSize-rangeOffset, modelData.modelSize+rangeOffset, -rangeOffset)
        self.UDECParameters = {
            '$nSteps': modelData.numberOfSteps, #depending on the number of contacts, the memory is exceeded with too many steps. future iteration of cycleModel.fis shall write to file after each step rather than after all steps to reduce the memory load. 
            '$mSize': modelData.modelSize,
            '$bSize': modelData.blockSize,
            '$meshSize': modelData.meshSize,
            '$round': float(modelData.blockSize)/10,
            '$vRound': float(modelData.blockSize)/20,
            '$vIterations': modelData.voronoiIterations,
            '$edge': float(modelData.blockSize)/50,
            '$vSeed': modelData.voronoiSeed,
            '$rho': modelData.rho,
            '$bulk': modelData.E/(3*(1-2*modelData.nu)),
            '$shear': modelData.E/(2*(1+modelData.nu)),
            '$jks': modelData.jks,
            '$jkn': modelData.jkn,
            '$jFriction': modelData.jFriction,
            '$jCohesion': modelData.jCohesion,
            '$jTension': modelData.jTension,
            '$jDilation': modelData.jDilation,
            '$rFriction': modelData.rFriction,
            '$rCohesion': modelData.rCohesion,
            '$rTension': modelData.rTension,
            '$rDilation': modelData.rDilation,
            '$bRange': bRange,
            '$tRange': tRange,
            '$lRange': lRange,
            '$rRange': rRange,
            '$timeFraction':modelData.timeStepFraction}
            
    def createInputFiles(self):
        """Creates Input files for UDEC and a batch file to run them all
        
        Todo:
            move towards a  more object oriented method of handling data
                        
        Returns:
            None: creates UDEC input files and corresponding batch file
            
        """
        fileNames = []
        self.printTitle('Creating Input Files for UDEC')
        self.printStatus('Collecting required UDEC parameters')
        self.getUDECParameters()
        self.printDone()
        self.printStatus('Filling in templates')
        self.UDECParameters['$sTime'] = float(modelData.simulationTime)
        self.UDECParameters['$vTable'] = self.getVelocityString([modelData.simulationTime])
        self.UDECParameters['$vel'] = modelData.velocity
        for j in range(len(modelData.confiningStress)):
            self.UDECParameters['$cStress'] = int(-modelData.confiningStress[j])
            self.UDECParameters['$mName'] = '\''+modelData.modelName+'('+'0'+'.'+str(j)+')'+'\''      
            with open(os.path.join(os.path.dirname(__file__),'UDEC', 'UDECModel.tpl'), 'r') as templateFile:
                template = templateFile.read()
                for k in self.UDECParameters.keys():
                    template = template.replace(k, str(self.UDECParameters[k]))
                fileNames.append('{0}({1}.{2})_Model.dat'.format(modelData.modelName, 0, j))
                with open(os.path.join(os.path.dirname(__file__),'UDEC',fileNames[-1]), 'w') as modelFile:
                    modelFile.write(template)
        self.printDone()
        self.printStatus('Generating UDEC batchrun script')
        with open(os.path.join(os.path.dirname(__file__),'UDEC','{0}(batchrun).dat'.format(modelData.modelName)), 'w') as modelFile:
            batchrun = []
            for i in range(len(fileNames)):
                batchrun.append('new\n')
                batchrun.append('call \'{}\'\n'.format(os.path.join(os.getcwd(), fileNames[i])))
            modelFile.writelines(batchrun)   
        self.printDone()
        
    def run(self):
        """runs the UDEC Module which creates input files for UDEC, then opens UDEC to allow the user to run UDEC, then compiles the UDEC output to MOUSE compatible output.
        
        Returns:
            None: MOUSE DEM data files
            
        """
        self.parseInput()
        self.createInputFiles()
        
        self.printTitle('Conducting UDEC Simulations')
        self.printSection('Automated UDEC functionality not available yet. UDEC has to be run manually by calling the batch file that was just generated. Please press Enter and Type the following once UDEC initializes \n\n\t \'call {0}(batchrun).dat\' \n\nWhen the UDEC simulations are complete, please type \'quit\' in order to continue'.format(modelData.modelName))
        input()
        currentDir = os.getcwd()
        os.chdir('Modules/UDEC')
        os.system('UDEC.lnk"')
        os.chdir('../..')
        self.formatOutput()

