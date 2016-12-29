import argparse
import os
import pickle  
import sys
import copy 
import importlib

if __name__ == '__main__':
    from Modules import DemModuleBaseClass
else:
    from .Modules import DemModuleBaseClass

class Module_UDEC(DemModuleBaseClass):
    def __init__(self, baseName):
        program = 'python HODS.py'
        parameters = {}
        DemModuleBaseClass.__init__(self, program, parameters, baseName)

    def inputFileName(self, data):
        return os.path.join(self.inputDirectory, '{0}{1}'.format(self.baseName, '.py'))

    def outputFileName(self): 
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.fileName, '_DEM.pkl'))

    def loadData(self):
        pass
    
    def parseInput(self):
        return self.loadData()
  
    def formatOutput(self):
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
        pass
        
    def getVelocityString(self, velTable):
        accelTime = velTable[-1]/10
        amp = -1
        vString = '((0, {0}), '.format(amp)
        for i in range(len(velTable)-1):
            vString += '({0}, {1}), ({2}, {3}), '.format(velTable[i]-accelTime, amp, velTable[i]+accelTime, amp*-1)
            amp = amp*-1
        vString += '({0}, {1}))'.format(velTable[-1], amp)
        return vString
        
    def getUDECParameters(self):
        #this needs to be redone
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
        #this needs to be redone
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
        
    def createArgumentParser(self):
        self.parser = argparse.ArgumentParser(description='ostrichHomogenize: Homogenizes the specified DEM data')
        populateArgumentParser(self.parser)
        
    def parseArguments(self):
        arguments = self.parser.parse_args()
        self.modelName = arguments.name

def importModelData(modelName):
    global modelData
    modelData = importlib.import_module('Data.Input.'+modelName)
 
def parserHandler(args):
    importModelData(args.name)
    M = Module_UDEC(args.name)
    M.run()
    
def populateArgumentParser(parser):
    parser.add_argument('-n', '--name', required=True ,help='Name of the file containing the model data without the extension')
    parser.set_defaults(func=parserHandler)   
    return parser
    
def fileList(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files
        
def simulationFiles(files, rawPath, compiledPath):
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
    

if __name__ == '__main__':
    M = Module_UDEC('voronoiGranite')
    M.createArgumentParser()
    M.parseArguments()
    M.run()