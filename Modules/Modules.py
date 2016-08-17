import os
import sys
import pickle


class ModuleBaseClass(object):
    def __init__(self, program, parameters = {}, supressText = False, supressErrors = True):
        self.program = program
        self.parameters = parameters
        
        self.supressText = supressText
        self.supressErrors = supressErrors
        
        topDirectory = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
        dataDirectory =  os.path.join(topDirectory, 'Data')
        self.binaryDirectory = os.path.join(dataDirectory, 'Binary')
        self.textDirectory = os.path.join(dataDirectory, 'Text')

    def printText(self, text):
        if not self.supressText:
            print(text)
        #else save to file
    
    def printTitle(self, title):
        self.printText('-'*70)
        self.printText(title)
        self.printText('-'*70)

    def printSection(self, section):
        self.printText(section)
        
    def printStatus(self, status):
        self.printText('\t{0}'.format(status))

    def printDone(self):
        self.printText('Done')
        
    def clearScreen(self):
        os.system('cls')
        
    def printErrors(self, error):
        if not self.supressErrors:
            self.printText(error)
            
    def saveData(self, data):
        with open(self.outputFileName()) as file:
            pickle.dump(file, data)
        
    def loadData(self):
        with open(self.inputFileName()) as file:
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
            

class DemModuleBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters):
        ModuleBaseClass.__init__(program, parameters)
             
    def inputFileName(self, data):
        pass
            
    def outputFileName(self, data): 
        pass
        

class ParameterEstimationModuleBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters):
        ModuleBaseClass.__init__(program, parameters)
        
            
    def inputFileName(self, data):
        pass
            
    def outputFileName(self, data):
        pass

class ContinuumModuleBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters):
        ModuleBaseClass.__init__(program, parameters)
        
            
    def inputFileName(self, data):
        pass
            
    def outputFileName(self, data):
        pass

class HomogenizationBaseClass(ModuleBaseClass):
    def __init__(self, program, parameters):
        ModuleBaseClass.__init__(program, parameters)
            
    def inputFileName(self, data):
        return 'testIn.pkl'
            
    def outputFileName(self, data):       
        return 'testOut.pkl'


    