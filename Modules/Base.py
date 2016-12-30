#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import pickle

class ModuleBaseClass(object):
    """Creates a base class containing common module methods and attributes

    A base module class is implemented here to provide a framework containing required methods and attributes for the MOUSE modules to inherit. The module class contains methods pertaining to I/O routines associated with the module so that each module that is written behaves in a consistent manner and to avoid reimplementation of certain methods.  
    
    Attributes:
        program (str): String containing name of module software executable file. 
        parameters (dict): Dictionary of command line parameters as keys and corresponding arguments as entries
        suppressText (bool): Suppreses text output from modules if True
        suppressErrors (bool): Suppress error output from modules if True
        baseName (str): Name of model input file
        binaryDirectory(str): Directory in which MOUSE binary data is located
        textDirectory(str): Directory in which MOUSE text data is located
        inputDirectory(str): Directory in which MOUSE input data is located
        outputDirectory(str): Directory in which MOUSE output data is located
    """        
    def __init__(self, program, baseName, parameters = {}, suppressText = False, suppressErrors = True):
        """Initializes class attributes for base module
        
        Args:
            program (str): String containing name of module software executable file. 
            baseName (str): Name of model input file
            parameters (dict): Dictionary of command line parameters as keys and corresponding arguments as entries
            suppressText (bool): Suppreses text output from modules if True
            suppressErrors (bool): Suppress error output from modules if True
                
      """
        self.program = program
        self.parameters = parameters
        
        self.suppressText = suppressText
        self.suppressErrors = suppressErrors
        
        self.baseName = baseName
        topDirectory = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
        dataDirectory =  os.path.join(topDirectory, 'Data')
        self.binaryDirectory = os.path.join(dataDirectory, 'Binary')
        self.textDirectory = os.path.join(dataDirectory, 'Text')
        self.inputDirectory = os.path.join(dataDirectory, 'Input')
        self.outputDirectory = os.path.join(dataDirectory, 'Output')

    def printText(self, text, end='\n'):
        """Prints text to console if not suppressed
        
        Note:
            All text printed to the console should be routed through this function rather than using the built-in print() function. Using this function allows for easy suppression and piping of output.
            
        Todo:
            If text suppression is on, route output to file.
    
        Args:
            text (str): text to be printed to console
            end (str, optional): character to be appended to end of print line
            
        Returns:
            None: text printed to the console
                
        """
        if not self.suppressText:
            print(text, end=end, flush=True)
        #else save to file
    
    def printTitle(self, title):
        """Prints a title to console. 
        
        Titles are displayed with horizontal lines printed above and below the text and are alligned with the left side of the console.
        
        Args:
            title (str): title to be printed to console
             
        Returns:
            None: title printed to the console
               
        """
        self.printText('')
        self.printText('-'*70)
        self.printText(title)
        self.printText('-'*70)

    def printSection(self, section):
        """Prints a section name to console. 
        
        Sections are displayed alligned to the left side of the console.
        
        Args:
            section (str): section name to be printed to console
            
        Returns:
            None: section name printed to the console
                
        """
        self.printText(section)
        
    def printStatus(self, status):
        """Prints a status to console. 

        Statuses are displayed proceeding a tab and are follwed by ellipses with no new line character at the end of the print line. 

        Note:
        The no new line character at the end of the print line allows the printDone() method to print 'Done' at the end of the ellipses after some arbitrary code execution. It is recommended that these two methods always be used together
        
        Args:
            status (str): status to be printed to console
            
        Returns:
            None: status printed to the console
                
        """       
        self.printText('\t{0}...'.format(status), end='')

    def printDone(self):
        """Prints 'Done' to console. 
              
        Note:
        It is recommended that this method be used in conjunction with printStatus()

        Args:
            status (str): status to be printed to console
        
        Returns:
            None: 'Done' printed to the console
                
        """       
        self.printText('Done')
        
    def clearScreen(self):
        """Clears all text from the console. 

        Returns:
        None: Clears all text from the console
            
        """       
        os.system('cls')
        
    def printErrors(self, error):
        """Prints error to console if not suppressed
        
        Note:
            All errors caught should be routed through this function. Using this function allows for easy suppression and piping of output.
 
        Args:
            error (str): error to be printed to console
            
        Returns:
            None: error printed to the console
                
        """
        if not self.suppressErrors:
            self.printText(error)
            
    def saveData(self, data):
        """Saves module data as binary using the pickle serialization module
    
        Args:
            data (any): Module data to be serialized and stored in file
            
        Returns:
            None: serialized data in binary file in specified binaryDirectory
                
        """
        with open(self.outputFileName(), 'wb') as file:
            pickle.dump(data, file)
        
    def loadData(self):
        """Loads module data from binary using the pickle serialization module
    
        Args:
            data (any): Module data to be serialized and stored in file
            
        Returns:
            None: serialized data in binary file in specified binaryDirectory
                
        """
        with open(self.inputFileName(), 'rb') as file:
            print(self.inputFileName())
            return pickle.load(file)
        
    def updateParameters(self, parameters):
        """Updates the parameter attribute so that the modul can be run with a different parameter set without being re-instantiated
    
        Args:
            parameters (dict): dictionary of new parameters
            
        Returns:
            None: updates the parameter attribute
                
        """
        self.parameters = parameters

    def commandLineArguments(self):
        """converts the parameters dictionary to a string which can be passed to the command line when running the specified program.
    
        Returns:
            str: string to be passed to command line
                
        """
        arguments = ''
        for i in self.parameters:
            arguments += '{0} {1}'.format(i, self.parameters[i])
        return arguments
        
    def run(self):
        """runs specified program with specified parameters
    
        Returns:
            None: runs specified program with specified parameters
                
        """
        self.parseInput()
        command = '{0} {1}'.format(program, commandLineArguments)
        os.system(command)
        self.formatOutput()

class DemModuleBaseClass(ModuleBaseClass):
    """Creates a base class for the DEM modules containing common methods and attributes

    A base dem module class is implemented here, inheriting from the module base class to provide a framework containing required methods and attributes for the DEM modules to inherit. The module class contains methods pertaining to I/O routines associated with the module so that each module that is written behaves in a consistent manner and to avoid reimplementation of certain methods.  
    
    Attributes:
        type (str): Type of module 
    """        
    def __init__(self, program, parameters, baseName):
        """Initializes class attributes for DEM Module
        
        Args:
            program (str): String containing name of module software executable file. 
            baseName (str): Name of model input file
            parameters (dict): Dictionary of command line parameters as keys and corresponding arguments as entries
            
        """
        ModuleBaseClass.__init__(self, program, baseName, parameters)
        self.type = 'DEM'
             
    def inputFileName(self):
        """Returns full path of input binary data
                        
        Returns:
            str: full path of input binary data
        """
        return ''
            
    def outputFileName(self): 
        """Returns full path of output binary data
                        
        Returns:
            str: full path of output binary data
        """
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.baseName, '_DEM.pkl'))
        

class ParameterEstimationModuleBaseClass(ModuleBaseClass):
    """Creates a base class for the parameter estimation modules containing common methods and attributes

    A base parameter estimation module class is implemented here, inheriting from the module base class to provide a framework containing required methods and attributes for the parameter estimation modules to inherit. The module class contains methods pertaining to I/O routines associated with the module so that each module that is written behaves in a consistent manner and to avoid reimplementation of certain methods.  
    
    Attributes:
        type (str): Type of module 
    """        
    def __init__(self, program, parameters, baseName):
        """Initializes class attributes for parameter estimation Module
        
        Args:
            program (str): String containing name of module software executable file. 
            baseName (str): Name of model input file
            parameters (dict): Dictionary of command line parameters as keys and corresponding arguments as entries
            
        """
        ModuleBaseClass.__init__(self, program, baseName, parameters)      
            
    def inputFileName(self):
        """Returns full path of input binary data
                        
        Returns:
            str: full path of input binary data
        """
        pass
            
    def outputFileName(self):
        """Returns full path of output binary data
                        
        Returns:
            str: full path of output binary data
        """
        return os.path.join(self.textDirectory, '{0}{1}'.format(self.baseName, '_DEM.pkl'))

class ContinuumModuleBaseClass(ModuleBaseClass):
    """Creates a base class for the continuum model modules containing common methods and attributes

    A base continuum model module class is implemented here, inheriting from the module base class to provide a framework containing required methods and attributes for the continuum model modules to inherit. The module class contains methods pertaining to I/O routines associated with the module so that each module that is written behaves in a consistent manner and to avoid reimplementation of certain methods.  
    
    Attributes:
        type (str): Type of module 
    """        
    def __init__(self, program, parameters, baseName):
        """Initializes class attributes for continuum model Module
        
        Args:
            program (str): String containing name of module software executable file. 
            baseName (str): Name of model input file
            parameters (dict): Dictionary of command line parameters as keys and corresponding arguments as entries
            
        """
        ModuleBaseClass.__init__(self, program, baseName, parameters)
            
    def inputFileName(self):
        """Returns full path of input binary data
                        
        Returns:
            str: full path of input binary data
        """
        pass
            
    def outputFileName(self):
        """Returns full path of output binary data
                        
        Returns:
            str: full path of output binary data
        """
        pass

class HomogenizationModuleBaseClass(ModuleBaseClass):
    """Creates a base class for the homogenization modules containing common methods and attributes

    A base homogenization module class is implemented here, inheriting from the module base class to provide a framework containing required methods and attributes for the homogenization modules to inherit. The module class contains methods pertaining to I/O routines associated with the module so that each module that is written behaves in a consistent manner and to avoid reimplementation of certain methods.  
    
    Attributes:
        type (str): Type of module 
    """        
    def __init__(self, program, parameters, baseName):
        """Initializes class attributes for homogenization Module
        
        Args:
            program (str): String containing name of module software executable file. 
            baseName (str): Name of model input file
            parameters (dict): Dictionary of command line parameters as keys and corresponding arguments as entries
            
        """
        ModuleBaseClass.__init__(self, program, baseName, parameters)
        self.type = 'Homogenization'
        
            
    def inputFileName(self):
        """Gets full path of input binary data
                        
        Returns:
            str: full path of input binary data
        """
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.baseName, '_DEM.pkl'))
            
    def outputFileName(self):       
        """Returns full path of output binary data
                        
        Returns:
            str: full path of output binary data
        """
        return os.path.join(self.binaryDirectory, '{0}{1}'.format(self.baseName, '_HOM.pkl'))


    
