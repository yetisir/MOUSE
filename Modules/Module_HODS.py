import argparse
import os
import pickle  
import importlib

if __name__ == '__main__':
    from Modules import HomogenizationModuleBaseClass
    from HODS.HODS import Homogenize
else:
    from .Modules import HomogenizationModuleBaseClass
    from .HODS.HODS import Homogenize

class Module_HODS (HomogenizationModuleBaseClass):
    def __init__(self, baseName):
        program = 'python HODS.py'
        parameters = {}
        HomogenizationModuleBaseClass.__init__(self, program, parameters, baseName)
        
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
            
    def setParameters(self, args):
        self.revCentreX = args.revX
        self.revCentreY = args.revY
        self.revRadius = args.revRadius
            
        #TODO: assess these parameters from data
        importModelData(self.baseName[:-5])
        if self.revCentreX == None:
            self.revCentreX = modelData.modelSize/2
        if self.revCentreY == None:
            self.revCentreY = modelData.modelSize/2
        if self.revRadius == None:
            self.revRadius = modelData.modelSize/2-modelData.blockSize*2
        self.revCentre = {'x':self.revCentreX, 'y':self.revCentreY}
        
    def run(self):
        #self.clearScreen()

        H = Homogenize(self.revCentre, self.revRadius, fileName=self.baseName)

        self.stressHistory = H.stress()
        self.strainHistory = H.strain()
        self.timeHistory = H.time()
                
        self.formatOutput()
        
    def createArgumentParser(self):
        self.parser = argparse.ArgumentParser(description='ostrichHomogenize: Homogenizes the specified DEM data')
        populateArgumentParser(self.parser)
        
    def parseArguments(self, args):
        self.modelName = args.name
        self.revCentre = {'x':args.revX, 'y':args.revY}
        self.revRadius = args.revRadius

def importModelData(modelName):
    global modelData
    modelData = importlib.import_module('Data.Input.'+modelName)
 
def parserHandler(args):
    #importModelData(args.name)
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
    parser.add_argument('-x', '--revX', type=float ,help='x coordinate of REV centre')
    parser.add_argument('-y', '--revY', type=float ,help='y coordinate of REV centre')
    parser.add_argument('-r', '--revRadius', type=float ,help='Radius of REV centre')
    parser.set_defaults(func=parserHandler)
    
    return parser

if __name__ == '__main__':
    M = Module_HODS('voronoiGranite(0.0)')
    M.createArgumentParser()
    M.parseArguments(self.parser.parse_args())
    M.run()