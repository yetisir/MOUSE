import os
import sys
import time
import copy
import numpy
import math
import pickle

class DataSet(object):
    def __init__(self, dataClass=None, fileName=None, loadBinary=True):
        if fileName:
            self.fileName = fileName
            print('-'*70)
            print('Initalizing {} Data'.format(fileName))
            print('-'*70)

            parse = True
            
            filePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'binaryData', self.fileName+'_binary.dat')
            if loadBinary is True:
                try:
                    print('Attempting to load DEM Data from binary:')
                    dataTime = os.path.getmtime(os.path.join('UDEC', 'compiledData', fileName + '___block.dat'))
                    binTime = os.path.getmtime(filePath)
                    if binTime > dataTime:
                        pickleData = pickle.load(open(filePath, 'rb'))
                        self.blockData = pickleData[0]
                        self.contactData = pickleData[1]
                        self.cornerData = pickleData[2]
                        self.zoneData = pickleData[3]
                        self.gridPointData = pickleData[4]
                        self.domainData = pickleData[5]
                        parse = False
                        print('\tSuccess')
                    else:
                        print('\tFailed... Binary data out of date')
                except:
                    print('\tFailed... Binary data not found')
                    
            if parse is True:
                print('Parsing DEM data from text files:')
                blockFileName = fileName + '___block.dat'
                contactFileName = fileName + '___contact.dat'
                cornerFileName = fileName + '___corner.dat'
                zoneFileName = fileName + '___zone.dat'
                gridPointFileName = fileName + '___gridPoint.dat'
                domainFileName = fileName + '___domain.dat'

                print('\tLoading block data')
                self.blockData = self.parseDataFile(blockFileName)
                print('\tLoading contact data')
                self.contactData = self.parseDataFile(contactFileName)
                print('\tLoading corner data')
                self.cornerData = self.parseDataFile(cornerFileName)
                print('\tLoading zone data')
                self.zoneData = self.parseDataFile(zoneFileName)
                print('\tLoading gridPoint data')
                self.gridPointData = self.parseDataFile(gridPointFileName)
                print('\tLoading domain data')
                self.domainData = self.parseDataFile(domainFileName)
                print('Saving DEM data to binary:')
                pickle.dump([self.blockData, self.contactData, self.cornerData, self.zoneData,
                             self.gridPointData, self.domainData], open(filePath, 'wb'))
                print('\tDone')
        elif dataClass:
            self.blockData = dataClass.blockData
            self.contactData = dataClass.contactData
            self.cornerData = dataClass.cornerData
            self.zoneData = dataClass.zoneData
            self.gridPointData = dataClass.gridPointData
            self.domainData = dataClass.domainData
            self.fileName = dataClass.fileName
        print('')

    def parseDataFile(self, fileName):
        file = open(os.path.join('UDEC', 'compiledData', fileName))
        header = file.readline()[0:-1].split(' ')
        types = file.readline()[0:-1].split(' ')
        data = {}
        timeData = {}
        firstLoop = 1
        while 1:
            record = file.readline()[0:].replace('\n', '').replace('  ', ' ').split(' ')
            record = list(filter(('').__ne__, record))
            if record == []:
                try:
                    data[dictTime] = copy.copy(timeData)
                except UnboundLocalError:
                    pass
                break
            if firstLoop:
                dictTime = float(record[0])
                firstLoop = 0

            time = float(record[0])
            if dictTime != time:
                data[dictTime] = copy.copy(timeData)
                dictTime = time
            recordData = {}
            for i in range(2, len(record)):
                if types[i] == 'i':
                    record[i] = int(record[i])
                elif types[i] == 'f':
                    record[i] = float(record[i])
                elif types[i] == 'l':
                    csv = record[i].split(',')
                    for j in range(len(csv)):
                        csv[j] = int(csv[j])
                    record[i] = csv
                recordData[header[i]] = record[i]
            timeData[int(record[1])] = recordData
            oldRecord = record

        return data

    #Model Parameters
    def limits(self):
        time = min(self.blockData.keys())
        corners = self.cornerData[time].keys()
        x = self.cornerX(corners, time)
        y = self.cornerY(corners, time)
        return [min(x), max(x), min(y), max(y)]

    #Relational Parameters
    def cornersOnContacts(self, contacts):
        time = min(self.contactData.keys())
        corners = []
        for contact in contacts:
            corners += self.contactData[time][contact]['corners']
        return corners

    def zonesInBlocks(self, blocks):
        time = min(self.blockData.keys())
        zones = []
        for block in blocks:
            zones += self.blockData[time][block]['zones']
        return zones

    def cornersOnBlocks(self, blocks):
        time = min(self.blockData.keys())
        corners = []
        for block in blocks:
            corners += self.blockData[time][block]['corners']
        return corners

    def contactsOnBlocks(self, blocks):
        time = min(self.blockData.keys())
        contacts = []
        for block in blocks:
            for contact in self.contactData[time].keys():
                if block in self.contactData[time][contact]['blocks']:
                    contacts.append(contact)
        return contacts

    def contactsBetweenBlocks(self, blocks1, blocks2):
        time = min(self.blockData.keys())
        contacts1 = self.contactsOnBlocks(blocks1)
        contacts2 = self.contactsOnBlocks(blocks2)
        contacts = common.listIntersection(contacts1, contacts2)
        return contacts

    def blocksWithContacts(self, blocks, contacts):
        time = min(self.contactData.keys())
        newBlocks = []
        for contact in contacts:
            for block in self.contactData[time][contact]['blocks']:
                if block in blocks:
                    newBlocks.append(block)
        return list(set(newBlocks))

    def blocksWithCorners(self, blocks, corners):
        time = min(self.cornerData.keys())
        newBlocks = []
        for corner in corners:
            for block in blocks:
                if corner in self.blockData[time][block]['corners']:
                    newBlocks.append(block)
        return list(set(newBlocks))

    #Corner Parameters
    def cornerX(self, corners, time):
        x = []
        for corner in corners:
            x.append(self.gridPointData[time][self.cornerData[time][corner]['gridPoint']]['x'])
        return x

    def cornerY(self, corners, time):
        y = []
        for corner in corners:
            y.append(self.gridPointData[time][self.cornerData[time][corner]['gridPoint']]['y'])
        return y

    #Zone Parameters
    def zoneS11(self, zones, time):
        S11 = []
        for zone in zones:
            S11.append(self.zoneData[time][zone]['S11'])
        return S11

    def zoneS22(self, zones, time):
        S22 = []
        for zone in zones:
            S22.append(self.zoneData[time][zone]['S22'])
        return S22

    def zoneS33(self, zones, time):
        S33 = []
        for zone in zones:
            S33.append(self.zoneData[time][zone]['S33'])
        return S33

    def zoneS12(self, zones, time):
        S12 = []
        for zone in zones:
            S12.append(self.zoneData[time][zone]['S12'])
        return S12
        
def main():

    H = Homogenize(revCentre, revRadius, fileName=fileName)
    stressHistory = H.stress()
    strainHistory = H.strain()
    timeHistory = H.time()


if __name__ == '__main__':
    main()
