import os
import argparse
import importlib

def getVelocityString(velTable):
    accelTime = velTable[-1]/10
    amp = -1
    vString = '((0, {0}), '.format(amp)
    for i in range(len(velTable)-1):
        vString += '({0}, {1}), ({2}, {3}), '.format(velTable[i]-accelTime, amp, velTable[i]+accelTime, amp*-1)
        amp = amp*-1
    vString += '({0}, {1}))'.format(velTable[-1], amp)
    return vString

def getUDECParameters():
    rangeOffset = modelData.blockSize/1000
    bRange = '{0},{1} {0},{2}'.format(-rangeOffset, modelData.modelSize+rangeOffset, rangeOffset)
    tRange = '{0},{1} {2},{1}'.format(-rangeOffset, modelData.modelSize+rangeOffset, modelData.modelSize-rangeOffset)
    lRange = '{0},{1} {0},{2}'.format(-rangeOffset, rangeOffset, modelData.modelSize+rangeOffset)
    rRange = '{0},{1} {2},{1}'.format(modelData.modelSize-rangeOffset, modelData.modelSize+rangeOffset, -rangeOffset)
    UDECParameters = {
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
    return UDECParameters

def createUDECModelFiles(UDECParameters):
    fileNames = []
    for i in range(len(modelData.simulationTime)):
        UDECParameters['$sTime'] = float(modelData.simulationTime[i])
        UDECParameters['$vTable'] = getVelocityString(modelData.velocityTable[i])
        UDECParameters['$vel'] = modelData.velocity[i]
        for j in range(len(modelData.confiningStress)):
            UDECParameters['$cStress'] = int(-modelData.confiningStress[j])
            UDECParameters['$mName'] = '\''+modelData.modelName+'('+str(i)+'.'+str(j)+')'+'\''      
            with open('UDECModel.tpl', 'r') as templateFile:
                template = templateFile.read()
                for k in UDECParameters.keys():
                    template = template.replace(k, str(UDECParameters[k]))
                fileNames.append('{0}({1}.{2})_Model.dat'.format(modelData.modelName, i, j))
                with open(fileNames[-1], 'w') as modelFile:
                    modelFile.write(template)
                    
    with open('{0}(batchrun).dat'.format(modelData.modelName), 'w') as modelFile:
        batchrun = []
        for i in range(len(fileNames)):
            batchrun.append('new\n')
            batchrun.append('call \'{}\'\n'.format(os.path.join(os.getcwd(), fileNames[i])))
        modelFile.writelines(batchrun)   

def importModelData(modelName):
    global modelData
    modelData = importlib.import_module('modelData.'+modelName)

def run(modelName, ):
    importModelData(modelName)
    main()

def main():
    createUDECModelFiles(getUDECParameters()) 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='createOstrichInput: Creates the Neccessary Input files to Run OSTIRCH')
    parser.add_argument('-n', '--name', required=True, help='Name of the file containing the model data without the extension')

    args = parser.parse_args()
    modelName = args.name
    
    importModelData(modelName)
    main()
 