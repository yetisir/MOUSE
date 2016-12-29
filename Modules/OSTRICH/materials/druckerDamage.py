ostrichParameters = {   
                            'elasticModulus':{          'init':1.7e9,    'low':1e9,      'high':10e9},
                            'poissonsRatio':{           'init':0.2,     'low':0.15,     'high':0.45},
                            'frictionAngle':{           'init':55,      'low':30,       'high':60}, 
                            'flowStressRatio':{         'init':0.86,     'low':0.78,     'high':1},
                            'dilationAngle':{           'init':10,      'low':5,        'high':50},
                            'initialCompressiveYeild':{ 'init':31e3,     'low':1e3,    'high':100e3},
                            'peakCompressiveYeildDiff':{'init':1.5e6,     'low':0.5e6,    'high':5e6},
                            'peakPlasticStrain':{       'init':13e-3,   'low':5e-3,        'high':50e-3},
                            'yeildStrain1':{            'init':12e-6,    'low':5e-6,   'high':100e-6},
                            'yeildStrain2':{            'init':214e-3,    'low':10e-3,   'high':1000e-3},
                            'failureDisplacement':{     'init':0.8,     'low':0,        'high':2}}
 
                
abaqusTemplate = '''
    elasticModulus = $elasticModulus
    poissonsRatio = $poissonsRatio
    frictionAngle = $frictionAngle
    flowStressRatio = $flowStressRatio
    dilationAngle = $dilationAngle
    initialCompressiveYeild = $initialCompressiveYeild
    peakCompressiveYeildDiff = $peakCompressiveYeildDiff
    peakPlasticStrain = $peakPlasticStrain
    yeildStrain1 = $yeildStrain1
    yeildStrain2Diff = $yeildStrain2
    failureDisplacement = $failureDisplacement
    druckerDamage(elasticModulus, poissonsRatio, frictionAngle, flowStressRatio, dilationAngle, initialCompressiveYeild, peakCompressiveYeildDiff, peakPlasticStrain, yeildStrain1, yeildStrain2Diff, failureDisplacement)
    '''
