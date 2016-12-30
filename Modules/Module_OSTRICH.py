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

if __name__ == '__main__':
    from Base import ParameterEstimationModuleBaseClass
else:
    from .Base import ParameterEstimationModuleBaseClass

class Module_OSTRICH (ParameterEstimationModuleBaseClass):
    def __init__(self, baseName):
        program = 'ostrichmpi.bat'
        parameters = {}
        ParameterEstimationModuleBaseClass.__init__(self, program, parameters, baseName)
        
    def parseInput(self):
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
        self.printStatus('Saving estimated parameter set')
        shutil.copy(os.path.join(os.path.dirname(__file__), 'OSTRICH', 'OstOutput0.txt'), os.path.join(self.textDirectory, '{0}({1})_PAR.txt'.format(self.baseName, modelData.abaqusMaterial)))
        self.printDone()            
        
    def setParameters(self, args):
        pass
        
    def run(self):
        #self.clearScreen()
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
        
 
    def createArgumentParser(self):
        self.parser = argparse.ArgumentParser(description='Ostrich optimization module')
        populateArgumentParser(self.parser)
        
    def parseArguments(self, args):
        self.modelName = args.name
        self.identity = args.identity
        self.MPI = args.parallel
        self.cores = args.cores
        self.optimizer = args.optimizer

def getVelocityString(velTable):
    accelTime = velTable[-1]/10
    amp = -1
    vString = '((0, {0}), '.format(amp)
    for i in range(len(velTable)-1):
        vString += '({0}, {1}), ({2}, {3}), '.format(velTable[i]-accelTime, amp, velTable[i]+accelTime, amp*-1)
        amp = amp*-1
    vString += '({0}, {1}))'.format(velTable[-1], amp)
    return vString
    
    
def importModelData(modelName):
    global modelData
    modelData = importlib.import_module('Data.Input.'+modelName)
    
def fillTemplate(template, parameters, file):
    with open(os.path.join(os.path.dirname(__file__), 'OSTRICH', template), 'r') as templateFile:
        t = templateFile.read()
        for i in parameters.keys():
            t = t.replace(i, str(parameters[i]))
        with open(os.path.join(os.path.dirname(__file__), 'OSTRICH', file), 'w') as modelFile:
            modelFile.write(t)

def importMaterialData(materialName):
    global material
    material = importlib.import_module('Modules.OSTRICH.materials.'+materialName)
 
def parserHandler(args):
    importModelData(args.name)
    M = Module_OSTRICH(args.name)
    M.parseArguments(args)
    M.parseInput()
    M.run()
    
def populateArgumentParser(parser):
    parser.add_argument('-n', '--name', required=True ,help='Name of the file containing the model data without the extension')
    parser.add_argument('-id', '--identity', help='identification Number')
    parser.add_argument('-p', '--parallel', default=True, help='use parallel processing')
    parser.add_argument('-c', '--cores', default=4, help='number of logical cores to use for parallel processing')
    parser.add_argument('-o', '--optimizer', default='ParticleSwarm', help='optimization algorithm')
    parser.set_defaults(func=parserHandler)
    
    return parser

if __name__ == '__main__':
    pass
    #nonfunctional curently