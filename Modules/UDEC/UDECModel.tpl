def modelParameters
	modelName = $mName
	simulationTime = $sTime
	numberOfSteps = $nSteps
end	
modelParameters

config
round $round
edge $edge
block 0,0 0,$mSize $mSize,$mSize $mSize,0
vor edge $bSize iterations $vIterations round $vRound seed $vSeed
 jdelete
gen edge $meshSize
group zone 'User:Rocks'
;zone model elastic density $rho bulk $bulk shear $shear
zone model mohr density $rho bulk $bulk shear $shear friction $rFriction cohesion $rCohesion tension $rTension range group 'User:Rocks'
group joint 'User:Joints'
joint model area jks $jks jkn $jkn jfriction $jFriction jcohesion $jCohesion jtension $jTension jdilation $jDilation range group 'User:Joints'
set jcondf joint model area jks=$jks jkn=$jkn jfriction=$jFriction jcohesion=$jCohesion jtension=$jTension jdilation=$jDilation
table 1 delete
table 1 $vTable

;*****Bottom Boundary
boundary yvelocity 0 range $bRange

;*****Left Boundary
;boundary xvelocity 0 range $lRange
boundary stress $cStress 0 0 range $lRange

;*****Right Boundary
;boundary xvelocity 0 history=table 1 range $rRange
boundary stress $cStress 0 0 range $rRange

;*****Top Boundary
boundary yvelocity $vel history=table 1 range $tRange

fraction $timeFraction
damping auto
set ovtol $round
set skip_error on

call cycleModel.fis
