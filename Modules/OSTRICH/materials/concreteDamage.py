ostrichParameters = {
                                'elasticModulus':{'init':5e9, 'low':1e9, 'high':20e9},
                                'poissonsRatio':{'init':0.2, 'low':0.15, 'high':0.45},
                                'dilationAngle':{'init':10, 'low':5, 'high':15},
                                'eccentricity':{'init':0.1, 'low':0.01, 'high':0.5},
                                'invariantRatio':{'init':0.67, 'low':0.51, 'high':1},
                                'equibiaxialRatio':{'init':1.16, 'low':1.05, 'high':1.3},
                                'initialCompressiveYeild':{'init':50e3, 'low':1e3, 'high':100e3},
                                'peakCompressiveYeildDiff':{'init':1.5e6, 'low':0.5e6, 'high':5e6},
                                'peakPlasticStrain':{'init':15e-3, 'low':5e-3, 'high':50e-3}, 
                                'tLambda':{'init':220, 'low':50, 'high':500},
                                'initialTensileYeild':{'init':100e3, 'low':50e3, 'high':500e3},
                                'tensileDamageScaling':{'init':0.8, 'low':0.4, 'high':0.95},
                                'compressiveDamageScaling':{'init':0.8, 'low':0.4, 'high':0.95}
                                }

abaqusTemplate = '''
    elasticModulus = $elasticModulus
    poissonsRatio = $poissonsRatio
    dilationAngle = $dilationAngle
    eccentricity = $eccentricity
    invariantRatio = $invariantRatio
    equibiaxialRatio = $equibiaxialRatio
    initialCompressiveYeild = $initialCompressiveYeild
    peakCompressiveYeildDiff = $peakCompressiveYeildDiff
    peakPlasticStrain = $peakPlasticStrain
    tLambda = $tLambda
    initialTensileYeild = $initialTensileYeild
    tensileDamageScaling = $tensileDamageScaling
    compressiveDamageScaling = $compressiveDamageScaling
    concreteDamage(elasticModulus, poissonsRatio, dilationAngle, eccentricity, invariantRatio, equibiaxialRatio,  initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain, tLambda, initialTensileYeild, tensileDamageScaling, compressiveDamageScaling)
    '''