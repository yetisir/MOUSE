import argparse
import os
import pickle
if __name__ == '__main__':
    from Base import ContinuumModuleBaseClass
else:
    from .Base import ContinuumModuleBaseClass

class Module_ABAQUS (ContinuumModuleBaseClass):
    def __init__(self, baseName):
        program = 'abaqus cae nogui=runAbaqus.py'
        parameters = {}
        ContinuumModuleBaseClass.__init__(self, program, parameters, baseName)
        
    def parseInput(self):
        return self.loadData()
        
    def formatOutput(self):
        self.printText('Saving homogenization time history:')
        #fileName = '{0}({1}.{2})'.format(modelData.modelName, parameterizationRun, cStressIndex)
        fileName = self.outputFileName()
        bundle = [self.timeHistory, self.stressHistory, self.strainHistory]
        with open(self.outputFileName(), 'wb') as bundleFile:
            pickle.dump(bundle, bundleFile)
        self.printText('\tDone')
            
    def setParameters(self, revCentreX=None, revCentreY=None, revRadius=None):
        self.revCentreX = revCentreX
        self.revCentreY = revCentreY
        self.revRadius = revRadius
            
        #TODO: assess these parameters from data
        if revCentreX == None:
            self.revCentreX = modelData.modelSize/2
        if revCentreY == None:
            revCentreY = modelData.modelSize/2
        if revRadius == None:
            revRadius = modelData.modelSize/2-modelData.blockSize*2
        revCentre = {'x':revCentreX, 'y':revCentreY}
        
    def run(self):
        pickleData = self.parseInput()
        self.clearScreen()
            
        H = Homogenize(self.revCentre, self.revRadius, pickleData=pickleData)
        self.stressHistory = H.stress()
        self.strainHistory = H.strain()
        self.timeHistory = H.time()
                
        self.formatOutput()
        
    def createArgumentParser(self):
        self.parser = argparse.ArgumentParser(description='abaqus')
        #populateArgumentParser(self.parser)
        
    def parseArguments(self):
        arguments = self.parser.parse_args()
        self.modelName = arguments.name
        
def importModelData(modelName):
    global modelData
    modelData = importlib.import_module('Data.Input.'+modelName)
 
def parserHandler(args):
    #importModelData(args.name)
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
    parser.add_argument('-n', '--name', required=True ,help='Name of the file containing the model data without the extension')
    parser.set_defaults(func=parserHandler)
    
    return parser
    
if __name__ == '__main__':
    pass
    #not currently functional
