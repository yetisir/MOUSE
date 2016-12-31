#! /usr/bin/python
# -*- coding: utf-8 -*-

__version__ = "0.3"
__author__ = "M. Yetisir"
__copyright__ = "Copyright 2016"
__credits__ = ["M. Yetisir", "R. Gracie", "M. Dusseault"]
__license__ = "GPL"
__maintainer__ = "M. Yetisir"
__email__ = "yetisir@gmail.com"
__status__ = "Development"

"""MOUSE: (M)odular aut(O)mated (U)p-(S)caling softwar(E)

This software represents the implementation of the up-scaling framework 
described in the thesis entitled 'Up-Scaling DEM Simulations of Discontinua' 
written by M. Yetisir for the University of Waterloo in fulfillment of his thesis 
requirement for the degree of Master of Applied Science in Civil Engineering.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""
import os
import sys
import shutil
import time
import psutil
import importlib
import argparse
import textwrap

   
def createParser():
    """Creates an argparse parser object for MOUSE and imports argparse subparsers for each MOUSE Module
    
    Todo:
        Scan subparsers from module files and import in order to remove hard-coded dependance
        
    Note:
        Currenlty subparser imports are hard-coded in
    
    Returns:
        argparse.ArgumentParser: the main argument parser for MOUSE populated with all required subparsers form modules.
            
    """
    parser = argparse.ArgumentParser(description='MOUSE: An Up-Scaling Utility for DEM Simulations')
    subparsers = parser.add_subparsers()
     
    udecParser = subparsers.add_parser('UDEC')
    from Modules import Module_UDEC
    udecParser = Module_UDEC.populateArgumentParser(udecParser)
    
    hodsParser = subparsers.add_parser('HODS')
    from Modules import Module_HODS    
    hodsParser = Module_HODS.populateArgumentParser(hodsParser)
    
    ostrichParser = subparsers.add_parser('OSTRICH')
    from Modules import Module_OSTRICH
    ostrichParser = Module_OSTRICH.populateArgumentParser(ostrichParser)
    
    abaqusParser = subparsers.add_parser('ABAQUS')
    from Modules import Module_ABAQUS
    abaqusParser = Module_ABAQUS.populateArgumentParser(abaqusParser)
    
    return parser
        
class SplashScreen(object):
    """Creates the splash screen and interface for MOUSE

    This class allows for the generation of an introduction screen for MOUSE. Here, a collection of printing methods are created in order to provide an environment for creating a consistent splash screen and interface. 
    
    Attributes:
        boxWidth (int): Character width of text box for splash screen
        textWidth (int): Character width of text area for splash screen
        padWidth (int): Character width of text area for padding on splash screen
        
    """        
    
    def __init__(self, boxWidth=55, textWidth=70, padWidth=15):
        """Initializes class attributes and displayes splash screen
        
        Args:
            boxWidth (int, optional): Character width of text box for splash screen
            textWidth (int, optional): Character width of text area for splash screen
            padWidth (int, optional): Character width of text area for padding on splash screen
                
        """
        self.boxWidth = boxWidth
        self.textWidth = textWidth
        self.padWidth = padWidth
        os.system('cls')
        self.printSplash()
    
    def printSplash(self):
        """Clears the console and prints the splash screen to the console

        Returns:
            None:Splash screen printed on console
            
        Todo:
            Import Modules and stuses from module files rather than hard coding them into this method
                
        """        
        os.system('cls')
        
        print()
        self.printCentre('M O U S E: Version {0}'.format(__version__))
        self.printBoxLine()
        self.printInBox('(M)odular aut(O)mated (U)p-(S)caling softwar(E)')
        self.printInBox('')
        self.printInBox('An Up-Scaling Utility for DEM Simulations')
        self.printBoxLine()
        
        introductionString = 'This software represents the implementation of the up-scaling framework described in the thesis entitled \'Up-Scaling DEM Simulations of Discontinua\' written by M. Yetisir for the University of Waterloo in fulfillment of his thesis requirement for the degree of Master of Applied Science in Civil Engineering.'
        wrappedIntroductionString = textwrap.wrap(introductionString, self.boxWidth-2)
        for line in wrappedIntroductionString:
            self.printInBox(line)
        self.printInBox('')
        self.printInBox('Copyright \N{COPYRIGHT SIGN}: M. Yetisir 2016' )
        self.printBoxLine()

        self.printInBox('Available Modules:')
        self.printInBox('')        
        self.printModule('UDEC', 'Installed')#
        self.printModule('HODS', 'Installed')#
        self.printModule('ABAQUS', 'Installed')#
        self.printModule('OSTRICH', 'Installed')#
        self.printBoxLine()
        print()
        
    def printFullLine(self):
        """Prints a horizontal line across the text width of the console
        
        Returns:
            None:Prints a horizontal dashed line of length self.textWidth on the console
                
        """       
        self.printCentre(self.textWidth*'-')

    def printBoxLine(self):
        """Prints a horizontal line for the box in the centre of the console
        
        Returns:
            None:Prints a centred horizontal dashed line of length self.boxWidth on the console
                
        """       
        self.printCentre(self.boxWidth*'-')
        
    def printCentre(self, text):
        """Prints text in the centre of the console
        
        Args:
            text(str): text to be printed in the centre of the console
    
        Returns:
            None:Prints str to the centre of the console
                
        """       
        print(text.center(self.textWidth))
        
    def printInBox(self, text):
        """Prints text in the centre of the box
        
        Args:
            text(str): text to be printed in the centre of the box
            
        Returns:
            None:Prints a horizontal dashed line of length self.textWidth on the console
                
        """       
        self.printCentre('|{0}|'.format(text.center(self.boxWidth-2)).center(self.textWidth))

    def printModule(self, module, status):
        """Prints module and installation status in the splash box
        
        Args:
            module(str): name of the module
            status(str): module status [installed, available, unavailable]
            
        Returns:
            None:Prints the module name with the status in the splash box
                
        """       
        self.printInBox('{0}{1}'.format(module.ljust(self.padWidth, '.'), status.rjust(self.padWidth, '.')))        
        
if __name__ == '__main__':
    M = SplashScreen(boxWidth=55, textWidth=70, padWidth=15)
    parser = createParser()
    args = parser.parse_args()
    if len(sys.argv) <= 1:
        parser.print_usage()
    else:
        args.func(args)
