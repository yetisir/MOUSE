import os
os.system('jclean.bat')
os.system('abaqus cae nogui=runAbaqus.py')
os.system('python interpolateData.py')
