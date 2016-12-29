import os
import sys
import pickle


class ModuleBaseClass(object):
    def __init__(self, program, baseName, parameters = {}, suppressText = False, suppressErrors = True):
        self.program = program
        self.parameters = parameters
        
        self.suppressText = suppressText
        self.suppressErrors = suppressErrors
        
        self.baseName = baseName
        topDirectory = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
        dataDirectory =  os.path.join(topDirectory, 'Data')
        self.binaryDirectory = os.path.join(dataDirectory, 'Binary')
        self.textDirectory = os.path.join(dataDirectory, 'Text')
        self.inputDirectory = os.path.join(dataDirectory, 'Input')
        self.outputDirectory = os.path.join(dataDirectory, 'Output')

    def printText(self, text, end='\n'):
        if not self.suppressText:
            print(text, end=end, flush=True)
        #else save to file
    
    def printTitle(self, title):
        self.printText('')
        self.printText('-'*70)
        self.printText(title)
        self.printText('-'*70)

    def printSection(self, section):
        self.printText(section)
        
    def printStatus(self, status):
        self.printText('\t{0}...'.format(status), end='')

    def printDone(self):
        self.printText('Done')
        
    def clearScreen(self):
        os.system('cls')
        
    def printErrors(self, error):
        if not self.suppressErrors:
            self.printText(error)
            
    def saveData(self, data):
        with open(self.outputFileName(), 'wb') as file:
            pickle.dump(data, file)
        
    def loadData(self):
        with open(self.inputFileName(), 'rb') as file:
            print(self.inputFileName())
            return pickle.load(file)
        
    def updateParameters(self, parameters):
        self.parameters = parameters

    def commandLineArguments(self):
        arguments = ''
        for i in self.parameters:
            arguments += '{0} {1}'.format(i, self.parameters[i])
        return arguments
        
    def run(self):
        self.parseInput()
        command = '{0} {1}'.format(program, commandLineArguments)
        os.system(command)
        self.formatOutput()
        
    def createArgumentParser(self):
        pass
        
    def parseArguments(self):
        pass 

    def inputFileName(self):
        pass
            
    def outputFileName(self):
        pass
            
    def setParameters(self):
        pass

class DemModuleBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters, baseName):
        ModuleBaseClass.__init__(self, program, baseName, parameters)
        self.type = 'DEM'
             
    def inputFileName(self, data):
        return None
            
    def outputFileName(self): 
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.baseName, '_DEM.pkl'))
        

class ParameterEstimationModuleBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters, baseName):
        ModuleBaseClass.__init__(self, program, baseName, parameters)
        
            
    def inputFileName(self, data):
        pass
            
    def outputFileName(self, data):
        pass

class ContinuumModuleBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters, baseName):
        ModuleBaseClass.__init__(self, program, baseName, parameters)
            
    def inputFileName(self, data):
        pass
            
    def outputFileName(self, data):
        pass

class HomogenizationModuleBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters, baseName):
        ModuleBaseClass.__init__(self, program, baseName, parameters)
        self.type = 'Homogenization'
        
            
    def inputFileName(self):
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.baseName, '_DEM.pkl'))
            
    def outputFileName(self):       
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.baseName, '_HOM.pkl'))


    
