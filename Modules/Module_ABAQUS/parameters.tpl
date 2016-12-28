mName = $$mName
sName = $$sName

abaqusMaterial = $$abaqusMaterial
    
gridPoints = [[0, 0], [$$mSize, 0], [$$mSize, $$mSize], [0, $$mSize], [0, 0]]

sectionLocation = ($$mSize/2, $$mSize/2, 0.0)

simulationTime = $$sTime
numberOfSteps = $$nSteps

confiningStress = $$confStress

density = $$rho
approxStrain = $$approxStrain

boundaryDisplacements = $$boundaryDisplacements
boundaryStresses = $$boundaryStresses
relevantMeasurements = $$relVars

try:
    from abaqusConstants import *
        
    elementType = CPE4R
    elementShape = QUAD
    meshSize = $$mSize

    instanceName = 'BLOCK-1'

    boundaries = {'Bottom': ($$mSize/2, 0.0, 0.0), 'Top':($$mSize/2, $$mSize, 0.0), 'Left':(0.0, $$mSize/2, 0.0), 'Right':($$mSize, $$mSize/2, 0.0)}

    # steps = ('Initial', 'Step-1', 'Step-2')
    v = $$vel
    vNames = (('Bottom', ), ('Top', ), ('Left', ), ('Right', ))
    velocityTable = $$vString

    largeDef=OFF
except ImportError: pass