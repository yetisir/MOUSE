from Modules import HomogenizationModuleBaseClass
from HODS_Module.HODS import Homogenize
import argparse
import os
import pickle

class HODS_Module (HomogenizationModuleBaseClass):
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
        self.parser = argparse.ArgumentParser(description='ostrichHomogenize: Homogenizes the specified DEM data')
        self.parser.add_argument('-n', '--name', required=True ,help='Name of the file containing the model data without the extension')
        self.parser.add_argument('-x', '--revX', type=float ,help='x coordinate of REV centre')
        self.parser.add_argument('-y', '--revY', type=float ,help='y coordinate of REV centre')
        self.parser.add_argument('-r', '--revRadius', type=float ,help='Radius of REV centre')
        self.parser.add_argument('-i', '--interpolate', dest='interpolate', help='Interpolate Stress and strain data', action='store_true')
        self.parser.add_argument('-ni', '--no-interpolate', dest='interpolate', help='Dont interpolate Stress and strain data', action='store_false')
        self.parser.set_defaults(interpolate=False)
        
    def parseArguments(self):
        arguments = self.parser.parse_args()
        self.modelName = arguments.name
        self.revCentre = {'x':arguments.revX, 'y':arguments.revY}
        self.revRadius = arguments.revRadius
        self.interpolate = arguments.interpolate
    
if __name__ == '__main__':
    M = HODS_Module('voronoiGranite(0.0)')
    M.createArgumentParser()
    M.parseArguments()
    M.run()
