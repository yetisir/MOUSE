import os
import math
from math import *
from caeModules import *
from odbAccess import *
from parameters import *
import pickle
import subprocess
from vectorMath import *
import time
          
def fWrite(stuff):
    with open('log.txt', 'a') as f:
        f.write(str(stuff)+'\n')
        
def sketchPart(name, gp):
    s = mdb.models['Model-1'].ConstrainedSketch(
        name='__profile__',sheetSize=10.0)
    for i in range(0, len(gp)-1):
        s.Line(point1=(gp[i][0], gp[i][1]), point2=(gp[i+1][0], gp[i+1][1]))
    p = mdb.models['Model-1'].Part(name=name, dimensionality=TWO_D_PLANAR,
                                   type=DEFORMABLE_BODY)
    p.BaseShell(sketch=s)
    del mdb.models['Model-1'].sketches['__profile__']
    
def tabulateVectors(vec1, vec2):
	vecLength = min(len(vec1), len(vec2))
	tabulatedData = []
	for i in range(vecLength):
		tabulatedData.append((vec1[i], vec2[i]))
	return tabulatedData

def tensilePlasticStrain(n, args):
    elasticModulus = args['elasticModulus']
    tLambda = args['tLambda']
    initialTensileYeild = args['initialTensileYeild']

    return (initialTensileYeild*tLambda*math.exp(approxStrain*tLambda)*(1/(approxStrain + 1)**n - 1)*(approxStrain + 1)**n)/elasticModulus - (initialTensileYeild*n*math.exp(approxStrain*tLambda)*(approxStrain + 1)**n)/(elasticModulus*(approxStrain + 1)**(n + 1)) + (initialTensileYeild*n*math.exp(approxStrain*tLambda)*(1/(approxStrain + 1)**n - 1)*(approxStrain + 1)**(n - 1))/elasticModulus + 1

def compressiveBeta(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain):
    peakCompressiveYeild = initialCompressiveYeild+peakCompressiveYeildDiff
    alpha = compressiveAlpha(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain)
    return math.log((2*alpha)/(1+alpha))/peakPlasticStrain
    
def compressiveAlpha(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain):
    peakCompressiveYeild = initialCompressiveYeild+peakCompressiveYeildDiff
    return (2*peakCompressiveYeild-initialCompressiveYeild+2*math.sqrt(peakCompressiveYeild*(peakCompressiveYeild-initialCompressiveYeild)))/initialCompressiveYeild
    
def compressivePlasticStrain(m, args):
    elasticModulus = args['elasticModulus']
    initialCompressiveYeild = args['initialCompressiveYeild']
    peakCompressiveYeildDiff = args['peakCompressiveYeildDiff']
    peakPlasticStrain = args['peakPlasticStrain']
    
    peakCompressiveYeild = initialCompressiveYeild+peakCompressiveYeildDiff
    alpha = compressiveAlpha(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain)
    beta = compressiveBeta(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain)
    
    return -((initialCompressiveYeild*approxStrain*m*(beta*math.exp(-beta*approxStrain)*(alpha - 1) + 2*alpha*beta*math.exp(-2*beta*approxStrain)))/(elasticModulus*(approxStrain*m - 1)) - (initialCompressiveYeild*m*(alpha*math.exp(-2*beta*approxStrain) + math.exp(-beta*approxStrain)*(alpha - 1)))/(elasticModulus*(approxStrain*m - 1)) + (initialCompressiveYeild*approxStrain*m**2*(alpha*math.exp(-2*beta*approxStrain) + math.exp(-beta*approxStrain)*(alpha - 1)))/(elasticModulus*(approxStrain*m - 1)**2) ) + 1

def root(f, args,  limits=[0.0,1.0], tolerance=0.001, samples=10):
    dl = (limits[1]-limits[0])/samples
    n = [limits[0]]
    for i in range(1, samples+1):
        n.append(n[i-1]+dl) 
    i = 1
    while i < samples+1:
        val = f(n[i], args)
        if val < 0 and n[i-1]!=n[i] :
            nRefined = root(f, args, limits=[n[i-1], n[i]], tolerance=tolerance, samples=samples)
            n.append(nRefined)
            break
        if abs(val) < tolerance:
            break
        i += 1
    if i == samples+1:
        nRefined = root(f, args, limits=[n[-2], n[-1]*10], tolerance=tolerance, samples=samples)
        n.append(nRefined)
    return n[-1]    
    
def concreteDamage(elasticModulus, poissonsRatio, dilationAngle, eccentricity, invariantRatio, equibiaxialRatio,  initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain, tLambda, initialTensileYeild, tensileDamageScaling, compressiveDamageScaling):
    materialName = 'Material-1'

    peakCompressiveYeild = initialCompressiveYeild+peakCompressiveYeildDiff
    
    alpha = compressiveAlpha(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain)
    beta = compressiveBeta(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain)

    plasticStrain = divide(range(0, 100), 100/approxStrain)
    
    compressiveYeildStress = multiply(initialCompressiveYeild, subtract(multiply(1+alpha, exp(multiply(-beta, plasticStrain))), multiply(alpha, exp(multiply(-2*beta, plasticStrain)))))
    
    try:
        m = root(compressivePlasticStrain, {'elasticModulus':elasticModulus, 'initialCompressiveYeild':initialCompressiveYeild, 'peakCompressiveYeildDiff':peakCompressiveYeildDiff, 'peakPlasticStrain':peakPlasticStrain})
    except (OverflowError, RuntimeError):
        m = 0.9/approxStrain
    
    compressiveDamage = multiply(m*compressiveDamageScaling, plasticStrain)

    tLambda = -tLambda
    tensileYeildStress = multiply(initialTensileYeild, exp(multiply(tLambda, plasticStrain)))
    n = root(tensilePlasticStrain, {'elasticModulus':elasticModulus, 'tLambda':tLambda, 'initialTensileYeild':initialTensileYeild})
    tensileDamage = subtract(0.95, divide(0.95, power(add(1, plasticStrain), n*tensileDamageScaling))) 
            
    mat = mdb.models['Model-1'].Material(name=materialName)
    mat.Density(table=((density, ), ))
    mat.Elastic(table=((elasticModulus, poissonsRatio), ))

    mat.ConcreteDamagedPlasticity(table=
        ((dilationAngle, eccentricity, equibiaxialRatio, invariantRatio, 0), ))
    mat.concreteDamagedPlasticity.ConcreteCompressionHardening(
        table=(tabulateVectors(compressiveYeildStress, plasticStrain)))
    mat.concreteDamagedPlasticity.ConcreteTensionStiffening(
        table=(tabulateVectors(tensileYeildStress, plasticStrain)))
        
    mat.concreteDamagedPlasticity.ConcreteCompressionDamage(
        table=(tabulateVectors(compressiveDamage, plasticStrain)))
    mat.concreteDamagedPlasticity.ConcreteTensionDamage(
        table=(tabulateVectors(tensileDamage, plasticStrain)))             


def druckerDamage(elasticModulus, poissonsRatio, frictionAngle, flowStressRatio, dilationAngle, initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain, yeildStrain1, yeildStrain2Diff, failureDisplacement):
    materialName = 'Material-1'
    
    peakCompressiveYeild = initialCompressiveYeild+peakCompressiveYeildDiff
    
    alpha = compressiveAlpha(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain)
    beta = compressiveBeta(initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain)

    plasticStrain = divide(range(0, 100), 100/approxStrain)
    compressiveYeildStress = multiply(initialCompressiveYeild, subtract(multiply(1+alpha, exp(multiply(-beta, plasticStrain))), multiply(alpha, exp(multiply(-2*beta, plasticStrain)))))
    
    triaxiality = subtract(divide(range(0, 100), 25), 2)
    yeildStrain2 = yeildStrain2Diff+yeildStrain1
    johnson_D1 = 0
    johnson_D2 = yeildStrain1**3/yeildStrain2**2
    johnson_D3 = 4*math.log(yeildStrain2/yeildStrain1)
    damageInitiationStrain = add(johnson_D1, multiply(johnson_D2, exp(multiply(-johnson_D3, triaxiality))))    
            
    mat = mdb.models['Model-1'].Material(name=materialName)
    mat.Density(table=((density, ), ))
    mat.Elastic(table=((elasticModulus, poissonsRatio), ))

    mat.DruckerPrager(shearCriterion=LINEAR, table=((frictionAngle, flowStressRatio, dilationAngle), ))
    mat.druckerPrager.DruckerPragerHardening(table=(tabulateVectors(compressiveYeildStress, plasticStrain)))
    mat.DuctileDamageInitiation(table=(tabulateVectors(damageInitiationStrain, triaxiality)))
    mat.ductileDamageInitiation.DamageEvolution(type=DISPLACEMENT, table=((failureDisplacement, ), ))		

def assignSection(name, part, location, material):
    mdb.models['Model-1'].HomogeneousSolidSection(name=name, material=material,
                                                  thickness=None)
    p = mdb.models['Model-1'].parts[part]
    f = p.faces
    faces = f.findAt((location, ))
    region = p.Set(faces=faces, name=name)
    p.SectionAssignment(region=region, sectionName=name, offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='',
                        thicknessAssignment=FROM_SECTION)

def meshPart(size, part, location, elementType, elementShape):
    p = mdb.models['Model-1'].parts[part]
    p.seedPart(size=size, deviationFactor=0.1, minSizeFactor=0.1)
    elemType = mesh.ElemType(elemCode=elementType)
    pickedRegions =(p.faces.findAt((location, )), )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType,))
    pickedRegions = p.faces.findAt((location, ))
    p.setMeshControls(regions=pickedRegions, elemShape=elementShape)
    p.generateMesh()

def createInstance(name, part):
    a = mdb.models['Model-1'].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    p = mdb.models['Model-1'].parts[part]
    a.Instance(name=name, part=p, dependent=ON)

# def applyVelocityBoundaryCondition(name, instance, step, location, v):
    # a = mdb.models['Model-1'].rootAssembly
    # edges1 = a.instances[instance].edges.findAt((location, ))
    # region = a.Set(edges=edges1, name=name)
    # # mdb.models['Model-1'].PeriodicAmplitude(name='Amp-1', timeSpan=STEP, 
        # # frequency=pi/simulationTime, start=0.0, a_0=0, data=((0.0, 1.0), ))
    # mdb.models['Model-1'].TabularAmplitude(name='Amp-1', timeSpan=STEP, 
        # smooth=SOLVER_DEFAULT, data=velocityTable)
    # mdb.models['Model-1'].VelocityBC(name=name, createStepName=step, 
        # region=region, v1=v[0], v2=v[1], vr3=v[2], amplitude='Amp-1', 
        # localCsys=None, distributionType=UNIFORM, fieldName='')  
        
def applyVelocityBoundaryCondition(name, instance, step, location, v, velocityAmp):
    a = mdb.models['Model-1'].rootAssembly
    edges1 = a.instances[instance].edges.findAt((location, ))
    region = a.Set(edges=edges1, name=name)
    mdb.models['Model-1'].VelocityBC(name=name, createStepName=step, 
        region=region, v1=v[0], v2=v[1], vr3=v[2], amplitude=velocityAmp, 
        localCsys=None, distributionType=UNIFORM, fieldName='')  

def applyZeroDisplacementBoundaryCondition(name, instance, step, location, u):
    a = mdb.models['Model-1'].rootAssembly
    edges1 = a.instances[instance].edges.findAt((location, ))
    region = a.Set(edges=edges1, name=name)
    mdb.models['Model-1'].DisplacementBC(name=name, createStepName=step, 
        region=region, u1=u[0], u2=u[1], ur3=u[2], amplitude=UNSET, 
        distributionType=UNIFORM, fieldName='', localCsys=None)    
        
def applyDisplacementBoundaryCondition(name, instance, step, location, u, dispAmp):
    a = mdb.models['Model-1'].rootAssembly
    edges1 = a.instances[instance].edges.findAt((location, ))
    region = a.Set(edges=edges1, name=name)
    mdb.models['Model-1'].DisplacementBC(name=name, createStepName=step, 
        region=region, u1=u[0], u2=u[1], ur3=u[2], amplitude=dispAmp, 
        distributionType=UNIFORM, fieldName='', localCsys=None)    
          
# def applyConfiningStress(name, instance, step, location, stress):
    # a = mdb.models['Model-1'].rootAssembly
    # edges1 = a.instances[instance].edges.findAt((location, ))
    # region = a.Surface(side1Edges=edges1, name=name)
    # mdb.models['Model-1'].TabularAmplitude(name='Amp-2', timeSpan=STEP, 
        # smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (5, 1)))
    # mdb.models['Model-1'].Pressure(name=name, createStepName=step, 
        # region=region, distributionType=UNIFORM, field='', magnitude=stress, 
        # amplitude='Amp-2')
        
def applyGeostaticStress(name, instance, location, hStress, K=0.4):
    a = mdb.models['Model-1'].rootAssembly
    faces1 = a.instances[instance].faces.findAt((location, ))
    region = a.Set(faces=faces1, name=name)
    mdb.models['Model-1'].GeostaticStress(name=name, region=region, 
        stressMag1=-hStress/K, vCoord1=0, stressMag2=-hStress/K, vCoord2=10, 
        lateralCoeff1=K, lateralCoeff2=K)   

def applyBoundaryStress(name, instance, step, location, stress, amp):
    a = mdb.models['Model-1'].rootAssembly
    edges1 = a.instances[instance].edges.findAt((location, ))
    region = a.Surface(side1Edges=edges1, name=name)
    

    mdb.models['Model-1'].Pressure(name=name, createStepName=step, 
        region=region, distributionType=UNIFORM, field='', magnitude=stress, 
        amplitude=amp)
        
def applyInitialStress(name, instance, location, cStress):
    a = mdb.models['Model-1'].rootAssembly
    faces1 = a.instances[instance].faces.findAt((location, ))
    region = a.Set(faces=faces1, name=name)
    #pr = 0.3755856
    aStress = -cStress/2#*pr/(1-pr)
    mdb.models['Model-1'].Stress(name=name, region=region, 
        distributionType=UNIFORM, sigma11=-cStress, sigma22=aStress, sigma33=aStress, 
        sigma12=0, sigma13=None, sigma23=None)        
        
def createStaticStep(name, previous):
    mdb.models['Model-1'].StaticStep(name=name, previous=previous, timePeriod=simulationTime,
                                     maxNumInc=1000, initialInc=0.5, minInc=0.001,
                                     maxInc=0.5, matrixSolver=DIRECT,
                                     matrixStorage=UNSYMMETRIC, nlgeom=largeDef)
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(numIntervals=numberOfSteps)

def createExplicitDynamicStep(name, previous):
    mdb.models['Model-1'].ExplicitDynamicsStep(name=name, previous=previous, 
                                                timePeriod=simulationTime, nlgeom=largeDef)
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(numIntervals=numberOfSteps)

def createImplicitDynamicStep(name, previous):
    mdb.models['Model-1'].ImplicitDynamicsStep(name=name, previous=previous, nlgeom=largeDef)
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(numIntervals=numberOfSteps)
                                                
def createGeostaticStep(name, previous):
    mdb.models['Model-1'].GeostaticStep(name=name, previous=previous, nlgeom=largeDef)
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(numIntervals=numberOfSteps)

def applyGravity(magnitude, stepName):
    mdb.models['Model-1'].Gravity(name='Gravity', createStepName=stepName, comp2=magnitude,
                                  distributionType=UNIFORM, field='')
                                  
def applyConfiningStress(confiningStress, amp):
    if confiningStress != 0:
        applyInitialStress('Geostatic', instanceName, sectionLocation, confiningStress)
        
        #applyBoundaryStress('Left', instanceName, 'Step-1', boundaries['Left'], confiningStress)
        applyBoundaryStress('Right', instanceName, 'Step-1', boundaries['Right'], confiningStress, amp)

def buildModel():
    partName = 'Block'
    materialName = 'Material-1'
    sectionName = 'Block'
    steps = ('Initial', 'Step-1', 'Step-2')

    sketchPart(partName, gridPoints)
    
    
    elasticModulus = 1574861000.0
    poissonsRatio = 0.3755856
    dilationAngle = 13.07659
    eccentricity = 0.4249099
    invariantRatio = 0.6474719
    equibiaxialRatio = 1.289982
    initialCompressiveYeild = 52266.98
    peakCompressiveYeildDiff = 3276328.0
    peakPlasticStrain = 0.005485066
    tLambda = 356.7335
    initialTensileYeild = 420270.5
    tensileDamageScaling = 0.6536259
    compressiveDamageScaling = 0.9474579
    concreteDamage(elasticModulus, poissonsRatio, dilationAngle, eccentricity, invariantRatio, equibiaxialRatio,  initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain, tLambda, initialTensileYeild, tensileDamageScaling, compressiveDamageScaling)
    
        
    assignSection(sectionName, partName, sectionLocation, materialName)
    meshPart(meshSize, partName, sectionLocation, elementType, elementShape)
    createInstance(instanceName, partName)
    createExplicitDynamicStep(steps[1],steps[0])
    # createStaticStep(steps[1],steps[0])
   
    # applyDisplacementBoundaryCondition('Bottom', instanceName, steps[0], boundaries['Bottom'],
        # (UNSET, SET, UNSET))
    # applyVelocityBoundaryCondition('vTop', instanceName, steps[1], boundaries['Top'], (UNSET, v, UNSET))
    applyZeroDisplacementBoundaryCondition('dBottom', instanceName, steps[0], boundaries['Bottom'],
        (UNSET, SET, UNSET))
    applyZeroDisplacementBoundaryCondition('dLeft', instanceName, steps[0], boundaries['Left'],
        (SET, UNSET, UNSET))

def getStress(jobName, stepName, instanceName):
    odb = openOdb(jobName+'.odb')
    allElements = odb.rootAssembly.instances[instanceName].elements    
    allFrames = odb.steps[stepName].frames
    
    element = allElements[0]
    stressHistory = [[0 for x in range(3)] for x in range(len(allFrames))] 
    for i in range(len(allFrames)):
        stress = allFrames[i].fieldOutputs['S'].getSubset(position=CENTROID).values[0].data
        stressHistory[i][0] = stress[0]
        stressHistory[i][1] = stress[1]
        stressHistory[i][2] = stress[3]
    odb.close()
    return stressHistory

def getStrain(jobName, stepName, instanceName):
    odb = openOdb(jobName+'.odb')
    allElements = odb.rootAssembly.instances[instanceName].elements    
    allFrames = odb.steps[stepName].frames
    
    element = allElements[0]
    strainHistory = [[0 for x in range(3)] for x in range(len(allFrames))] 
    strainShift = allFrames[0].fieldOutputs['E'].getSubset(position=CENTROID).values[0].data

    for i in range(len(allFrames)):
        strain = allFrames[i].fieldOutputs['E'].getSubset(position=CENTROID).values[0].data
        strainHistory[i][0] = strain[0]#-strainShift[0]
        strainHistory[i][1] = strain[1]#-strainShift[1]
        strainHistory[i][2] = strain[3]#-strainShift[3]
    odb.close()
    return strainHistory
    
def getTime(jobName, stepName, instanceName):
    odb = openOdb(jobName+'.odb')
    allFrames = odb.steps[stepName].frames
    timeHistory = [allFrames[x].frameValue for x in range(len(allFrames))] 
    #for i in range(len(allFrames)):
    #    timeHistory[i] = allFrames[i].frameValue
    odb.close()
    return timeHistory
    
def main():
    #open('log.txt', 'w').close()
    buildModel()
    for i in range(len(confiningStress)):
        mdb.models['Model-1'].TabularAmplitude(name='Amp-3', timeSpan=STEP, 
            smooth=SOLVER_DEFAULT, data= tuple(boundaryStresses[i][0]))
        applyConfiningStress(1, 'Amp-3')
        
        mdb.models['Model-1'].TabularAmplitude(name='Amp-1', timeSpan=STEP, 
            smooth=SOLVER_DEFAULT, data= tuple(boundaryDisplacements[i][0]))
        mdb.models['Model-1'].TabularAmplitude(name='Amp-2', timeSpan=STEP, 
            smooth=SOLVER_DEFAULT, data= tuple(boundaryDisplacements[i][1]))
        #applyDisplacementBoundaryCondition('vRight', instanceName, 'Step-1', boundaries['Right'], (1, UNSET, UNSET), 'Amp-1')
        applyDisplacementBoundaryCondition('vTop', instanceName, 'Step-1', boundaries['Top'], (UNSET, 1, UNSET), 'Amp-2')
        applyInitialStress('confStress', instanceName, sectionLocation, confiningStress[i])

        jobName = 'Job-{0}'.format(i+1)
        mdb.Job(name=jobName, model='Model-1', description='', type=ANALYSIS, atTime=None,
                waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE,
                getMemoryFromAnalysis=True, explicitPrecision=SINGLE,
                nodalOutputPrecision=SINGLE, echoPrint=OFF,
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                scratch='', parallelizationMethodExplicit=DOMAIN, numDomains=1, 
                activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
        mdb.jobs[jobName].submit(consistencyChecking=OFF)
    
        while 1:
            try:
                timeHistory = getTime(jobName, 'Step-1', instanceName)
                stressHistory = getStress(jobName, 'Step-1', instanceName)
                strainHistory = getStrain(jobName, 'Step-1', instanceName)                
                with open('{0}_rawHistory.pkl'.format(jobName), 'wb') as file:
                    pickle.dump(timeHistory, file)
                    pickle.dump(stressHistory, file)
                    pickle.dump(strainHistory, file)
                break
            except:# FileNotFoundError:
                pass


if __name__ == '__main__': 
    attempts = 3
    while attempts >0:
        try:
            main()
            break
        except Exception as e:
            os.system('jclean.bat')
            fWrite(e)
            attempts -= 1
            #write Error Report
            # with open('OstExeOut.txt', 'r') as f:
                # for i in f.readlines():
                    # fWrite(i)
            # try:
                # with open('Job-1.dat', 'r') as f:
                    # for i in f.readlines():
                        # fWrite(i)
                # with open('Job-2.dat', 'r') as f:
                    # for i in f.readlines():
                        # fWrite(i)
                # with open('Job-3.dat', 'r') as f:
                    # for i in f.readlines():
                        # fWrite(i)
            # except:
                # pass