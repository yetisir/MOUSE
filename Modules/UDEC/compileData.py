import os
import sys


def fileList(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files

def simulationFiles(files, rawPath, compiledPath):
    simulations = []
    compiledFiles = fileList(compiledPath)
    for file in files:
        index = file.rfind('.')
        simulationName = file[:index]
        extension = file[index+1:]
        if 'dat' in extension and len(extension) > 3:
            if file[:file.rfind('.dat')+4] in compiledFiles:
                rTime = os.path.getmtime(os.path.join(rawPath, file))
                cTime = os.path.getmtime(os.path.join(compiledPath, file[:file.rfind('.dat')+4]))
                if rTime > cTime:
                    simulations.append(simulationName)
            else:
                simulations.append(simulationName)
    simulations = list(set(simulations))
    simulations.sort()
    return simulations
    
def compileFiles(simulations, files, rawPath, compiledPath):
    print('Compiling data files for...')
    for simulation in simulations:
        print('\t{0}...'.format(simulation), end='')
        sys.stdout.flush()
        simulationFiles = []
        for file in files:
            if 'dat' not in str(file[-3:]) and simulation in file:
                simulationFiles.append(file)
        with open(os.path.join(compiledPath, '{0}.dat'.format(simulation)), 'w') as fout:
            with open(os.path.join(rawPath, simulationFiles[0]), 'r') as fin:
                fout.writelines(fin.readlines()[:2])
            for simulationFile in simulationFiles:
                with open(os.path.join(rawPath, simulationFile), 'r') as fin:
                    fout.writelines(fin.readlines()[2:])
        print('Done')    

    
def run():
    main()

def main():
    print('*'*70)
    print('Compiling UDEC Data Files')
    print('*'*70)
    rawPath = 'rawData'
    compiledPath = 'compiledData'
    print('Getting list of files in data directory...')
    filesInDirectory = fileList('rawData')
    print('\tDone')
    print('Isolating files for compilation...')
    simulations = simulationFiles(filesInDirectory, rawPath, compiledPath)
    print('\tDone')
    if simulations:
        compileFiles(simulations, filesInDirectory, rawPath, compiledPath)
    else:
        print('No uncompiled rawData files found.')

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='createOstrichInput: Creates the Neccessary Input files to Run OSTIRCH')
    # parser.add_argument('-n', '--name', required=True, help='Name of the file containing the model data without the extension')

    # args = parser.parse_args()
    # modelName = args.name
    
    main()
 