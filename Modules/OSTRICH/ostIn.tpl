#Configuration File for Ostrich Program

ProgramType $$pType

BeginFilePairs    
runAbaqus.temp.tpl	runAbaqus.py
EndFilePairs

ModelExecutable    simulationData.bat

ModelSubdir model

BeginParams
#parameter	init.	low	    high	tx_in   tx_ost	tx_out
$$ostrichParameters
EndParams

BeginObservations
#observation	value		weight	file		keyword		line	column
$$ostrichObservations
EndObservations

BeginLevMar
InitialLambda    10.0
LambdaScaleFactor    1.1
MoveLimit    0.1
AlgorithmConvergenceValue    0.01
LambdaPhiRatio    0.3
LambdaRelReduction    0.01
MaxLambdas    10
MaxIterations    20
EndLevMar

BeginParticleSwarm
SwarmSize  24
NumGenerations  100
ConstrictionFactor  1.00
CognitiveParam  2.00
SocialParam  2.00
InertiaWeight  1.20
InertiaReductionRate 0.1
EndParticleSwarm

BeginAPPSO
SwarmSize  24
NumGenerations  100
ConstrictionFactor  1.00
CognitiveParam  2.00
SocialParam  2.00
InertiaWeight  1.20
InertiaReductionRate 0.1
EndAPPSO

BeginParallelDDSAlg
PerturbationValue 0.2
MaxIterations 1000
UseRandomParamValues
UseOpt standard
EndParallelDDSAlg

BeginDDSAlg
PerturbationValue 0.2
MaxIterations 1000
UseRandomParamValues
EndDDSAlg

BeginMathAndStats
Default
Confidence
Sensitivity
EndMathAndStats

BeginExtraFiles
parameters.py
interpolateData.py
simulationData.py
vectorMath.py
jclean.bat
EndExtraFiles

