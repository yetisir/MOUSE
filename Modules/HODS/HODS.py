import os
import sys
import time
import copy
import numpy
import math
import pickle

class DataSet(object):
    def __init__(self, fileName):
        self.fileName = fileName
        print('-'*70)
        print('Initalizing {} Data'.format(fileName))
        print('-'*70)
        
        filePath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'Data', 'Binary', self.fileName+'_DEM.pkl')
        print('\tLoading binary DEM data')
        pickleData = pickle.load(open(filePath, 'rb'))

        print('\tUnpacking block data')
        self.blockData = pickleData[0]
        print('\tUnpacking contact data')
        self.contactData = pickleData[1]
        print('\tUnpacking corner data')
        self.cornerData = pickleData[2]
        print('\tUnpacking zone data')
        self.zoneData = pickleData[3]
        print('\tUnpacking gridpoint data')
        self.gridPointData = pickleData[4]
        print('\tUnpacking domain data')
        self.domainData = pickleData[5]

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
 
class Homogenize(DataSet):
    def __init__(self, centre, radius, fileName):
        DataSet.__init__(self, fileName=fileName)
        
        self.centre = centre
        self.radius = radius
        
            
        self.calculateHomogenizationParameters()
    
    #Boundary Functions
    def blocksOnBoundary(self):
        time = min(self.blockData.keys())
        blocks = []
        for blockIndex in self.blockData[time]:
            blockOut = False
            blockIn = False
            for cornerIndex in self.blockData[time][blockIndex]['corners']:
                gridPointIndex = self.cornerData[time][cornerIndex]['gridPoint']
                gridPoint = self.gridPointData[time][gridPointIndex]
                distance = math.hypot(gridPoint['x'] - self.centre['x'], gridPoint['y'] - self.centre['y'])
                if distance <= self.radius: blockIn = True
                if distance > self.radius: blockOut = True
            if blockIn and blockOut: blocks.append(blockIndex)
        return blocks

    def blocksOutsideBoundary(self):
        time = min(self.blockData.keys())
        blocks = []
        for blockIndex in self.blockData[time]:
            blockIn = False
            for cornerIndex in self.blockData[time][blockIndex]['corners']:
                gridPointIndex = self.cornerData[time][cornerIndex]['gridPoint']
                gridPoint = self.gridPointData[time][gridPointIndex]
                distance = math.hypot(gridPoint['x'] - self.centre['x'], gridPoint['y'] - self.centre['y'])
                if distance <= self.radius: blockIn = True
            if not blockIn: blocks.append(blockIndex)
        return blocks
        
    def blocksInsideBoundary(self):
        time = min(self.blockData.keys())
        blocks = []
        for blockIndex in self.blockData[time]:
            blockOut = False
            for cornerIndex in self.blockData[time][blockIndex]['corners']:
                gridPointIndex = self.cornerData[time][cornerIndex]['gridPoint']
                gridPoint = self.gridPointData[time][gridPointIndex]
                distance = math.hypot(gridPoint['x'] - self.centre['x'], gridPoint['y'] - self.centre['y'])
                if distance > self.radius: blockOut = True
            if not blockOut: blocks.append(blockIndex)
        return blocks
            
    def cornersOutsideBoundary(self):
        time = min(self.blockData.keys())
        corners = []
        for cornerIndex in self.cornerData[time]:
            gridPointIndex = self.cornerData[time][cornerIndex]['gridPoint']
            gridPoint = self.gridPointData[time][gridPointIndex]
            distance = math.hypot(gridPoint['x'] - self.centre['x'], gridPoint['y'] - self.centre['y'])
            if distance > self.radius: corners.append(cornerIndex)
        return corners
        
    def cornersInsideBoundary(self):
        time = min(self.blockData.keys())
        corners = []
        for cornerIndex in blockData[time]:
            gridPointIndex = self.cornerData[time][cornerIndex]['gridPoint']
            gridPoint = self.gridPointData[time][gridPointIndex]
            distance = math.hypot(gridPoint['x'] - self.centre['x'], gridPoint['y'] - self.centre['y'])
            if distance <= self.radius: corners.append(cornerIndex)
        return corners
        
    def contactsOutsideBoundary(self):
        time = min(self.blockData.keys())
        contacts = []
        for contactIndex in self.contactData[time]:
            contact = self.contactData[time][contactIndex]
            distance = math.hypot(contact['x'] - self.centre['x'], contact['y'] - self.centre['y'])
            if distance > self.radius: contacts.append(contactIndex)
        return contacts
        
    def contactsInsideBoundary(self):
        time = min(self.blockData.keys())
        contacts = []
        for contactIndex in self.contactData[time]:
            contact = self.contactData[time][contactIndex]
            distance = math.hypot(contact['x'] - self.centre['x'], contact['y'] - self.centre['y'])
            if distance <= self.radius: contact.append(contactIndex)
        return contacts
    
    #Manipulation Functions
    def orderBlocks(self, blocks, relaventContacts):
        blocks = copy.deepcopy(blocks)
        time = min(self.contactData.keys())
        blockContacts = [self.contactsOnBlocks([block]) for block in blocks]
        newBlocks = [blocks[0]]
        newBlockContacts = [blockContacts[0]]
        blocks.pop(0)
        blockContacts.pop(0)
        tempBlockContacts= []
        i = 0
        numBlocks = len(blocks)
        noSuccess = 0
        while i < numBlocks: 
            j = 0
            success = 0
            while j < len(blockContacts):
                relaventBlockContacts = common.listIntersection(blockContacts[j], relaventContacts)
                if i+1 > len(newBlockContacts):
                    i += -1
                    noSuccess += 1
                elif common.listIntersection(newBlockContacts[i], relaventBlockContacts):
                    success += 1
                    if success > noSuccess:
                        newBlockContacts.append(blockContacts[j])
                        newBlocks.append(blocks[j])
                        blockContacts.pop(j)
                        blocks.pop(j)
                        noSuccess = 0
                        break
                elif noSuccess > len(blockContacts):
                    xDistance = [self.blockData[time][newBlocks[i]]['x'] - self.blockData[time][b]['x'] for b in blocks] 
                    yDistance = [self.blockData[time][newBlocks[i]]['y'] - self.blockData[time][b]['y'] for b in blocks] 
                    distance = [math.hypot(xDistance[z], yDistance[z]) for z in range(len(blocks))]
                    nextBlockIndex = distance.index(min(distance))
                    newBlockContacts.append(blockContacts[nextBlockIndex])
                    newBlocks.append(blocks[nextBlockIndex])
                    blockContacts.pop(nextBlockIndex)
                    blocks.pop(nextBlockIndex)
                    noSuccess = 0
                    break
                j += 1
            i += 1
        return newBlocks
        
    def orderCorners(self, orderedBlocks, corners):
        time = min(self.contactData.keys())
        
        directionSign = 0
        for i in range(len(orderedBlocks)):
            x1 = self.blockData[time][orderedBlocks[i-2]]['x']
            y1 = self.blockData[time][orderedBlocks[i-2]]['y']
            x2 = self.blockData[time][orderedBlocks[i-1]]['x']
            y2 = self.blockData[time][orderedBlocks[i-1]]['y']
            x3 = self.blockData[time][orderedBlocks[i]]['x']
            y3 = self.blockData[time][orderedBlocks[i]]['y']
            xVec1 = x1-x2
            yVec1 = y1-y2
            xVec2 = x3-x2
            yVec2 = y3-y2
            vecAngle = common.angle(xVec1, yVec1, xVec2, yVec2)
            vecSign = xVec1*yVec2-xVec2*yVec1
            directionSign += vecSign
        if directionSign > 0:
            directionSign = -directionSign
            orderedBlocks = orderedBlocks[::-1]
        corners = copy.deepcopy(corners)
        orderedBlocks = copy.deepcopy(orderedBlocks)
        newCorners = []
        
        for i in range(len(orderedBlocks)):
            allBlockCorners = self.blockData[time][orderedBlocks[i]]['corners']
            blockCorners = common.listIntersection(corners, allBlockCorners)           
            orderedBlockCorners = []
            for corner in allBlockCorners:
                if corner in blockCorners:
                    orderedBlockCorners.append(corner)
            blockCorners = orderedBlockCorners
            
            blockDirection = 0
         
            for j in range(len(allBlockCorners)):
                x1 = self.gridPointData[time][self.cornerData[time][allBlockCorners[j-2]]['gridPoint']]['x']
                y1 = self.gridPointData[time][self.cornerData[time][allBlockCorners[j-2]]['gridPoint']]['y']
                x2 = self.gridPointData[time][self.cornerData[time][allBlockCorners[j-1]]['gridPoint']]['x']
                y2 = self.gridPointData[time][self.cornerData[time][allBlockCorners[j-1]]['gridPoint']]['y']
                x3 = self.gridPointData[time][self.cornerData[time][allBlockCorners[j]]['gridPoint']]['x']
                y3 = self.gridPointData[time][self.cornerData[time][allBlockCorners[j]]['gridPoint']]['y']
                xVec1 = x1-x2
                yVec1 = y1-y2
                xVec2 = x3-x2
                yVec2 = y3-y2
                vecAngle = common.angle(xVec1, yVec1, xVec2, yVec2)
                vecSign = xVec1*yVec2-xVec2*yVec1
                blockDirection += vecSign
            if math.copysign(1, blockDirection) != math.copysign(1, directionSign):
                blockCorners = blockCorners[::-1]
                
            previousBlockCorners = self.blockData[time][orderedBlocks[i-1]]['corners']
            startingCornerDistance = -1
            for corner in blockCorners:
                gridPoint = self.cornerData[time][corner]['gridPoint']
                for previousCorner in previousBlockCorners:
                    previousGridPoint = self.cornerData[time][previousCorner]['gridPoint']
                    xDistance = self.gridPointData[time][previousGridPoint]['x'] - self.gridPointData[time][gridPoint]['x']
                    yDistance = self.gridPointData[time][previousGridPoint]['y'] - self.gridPointData[time][gridPoint]['y']
                    distance = math.hypot(xDistance, yDistance)
                    if startingCornerDistance < 0 or distance < startingCornerDistance:
                        startingCornerDistance = distance
                        startingCorner = corner
                    
                    
            index = blockCorners.index(startingCorner)
            blockCorners = blockCorners[index:] + blockCorners[:index]
            newCorners += blockCorners
        return newCorners
        
    def duplicateCorners(self, corners, blocks):
        time = min(self.blockData.keys())
        newCorners = copy.deepcopy(corners)
        allCorners = self.cornersOnBlocks(blocks)
        blockSizes = [self.blockData[time][block]['area'] for block in blocks]
        averageBlockSize = math.sqrt(float(sum(blockSizes))/len(blockSizes))
        for i in range(len(corners)):
            for j in range(len(allCorners)):
                gridPoint1 = self.cornerData[time][corners[i]]['gridPoint']
                gridPoint2 = self.cornerData[time][allCorners[j]]['gridPoint']
                x1 = self.gridPointData[time][gridPoint1]['x']
                y1 = self.gridPointData[time][gridPoint1]['y']
                x2 = self.gridPointData[time][gridPoint2]['x']
                y2 = self.gridPointData[time][gridPoint2]['y']
                if abs(x1-x2)/averageBlockSize <0.01 and abs(y1-y2)/averageBlockSize < 0.01:
                    newCorners.append(allCorners[j])
        return list(set(newCorners))
        
    def singleElementCorners(self):
        time = min(self.blockData.keys())
        blocks = self.blockData[time].keys()
        return self.cornersOnBlocks(blocks)

    #Homogenization Functions
    def calculateHomogenizationParameters(self):
        print('-'*70)
        print('Calculating Homogenization Parameters for {}'.format(self.fileName))
        print('-'*70)
        print('Processing Homogenization Data:')
        print('\tCalculating boundary blocks')
        self.boundaryBlocks = self.blocksOnBoundary()
        print('\tCalculating inside blocks')
        self.insideBlocks = self.blocksInsideBoundary()
        print('\tCalculating outside blocks')
        self.outsideBlocks = self.blocksOutsideBoundary()
        print('\tCalculating inside boundary blocks')
        self.insideBoundaryBlocks = self.boundaryBlocks + self.insideBlocks
        print('\tCalculating boundary contacts')
        self.boundaryContacts = self.contactsBetweenBlocks(self.outsideBlocks, self.boundaryBlocks)
        print('\tCalculating boundary contact corners')
        self.boundaryContactCorners = self.cornersOnContacts(self.boundaryContacts)
        print('\tCalculating boundary contact blocks')
        self.boundaryContactBlocks = self.blocksWithContacts(self.boundaryBlocks, self.boundaryContacts)
        print('\tCalculating outside corners')
        self.outsideCorners = self.cornersOutsideBoundary()
        print('\tCalculating outside contacts')
        self.outsideContacts = self.contactsOutsideBoundary()
        print('\tCalculating boundary block corners')
        self.boundaryBlockCorners = self.cornersOnBlocks(self.boundaryContactBlocks)
        print('\tCalculating boundary corners')
        self.boundaryCorners = common.listIntersection(self.boundaryContactCorners, self.boundaryBlockCorners)
        #print('\tCalculating missing boundary corners')
        #self.allBoundaryCorners = self.duplicateCorners(self.boundaryCorners, self.boundaryContactBlocks)
        self.allBoundaryCorners = self.boundaryCorners
        print('\tCalculating boundary block order')
        self.boundaryBlocksOrdered = self.orderBlocks(self.boundaryContactBlocks, self.outsideContacts)
        print('\tCalculating boundary corner order')
        self.boundaryCornersOrdered = self.orderCorners(self.boundaryBlocksOrdered, self.allBoundaryCorners)

                   
    def stress(self):
        print('Assessing homogenized stresses:')
        sigmaHistory = []
        print('\tAt time ', end='')
        time = min(self.blockData.keys())
        totalArea = common.area(list(zip(self.cornerX(self.boundaryCornersOrdered, time), self.cornerY(self.boundaryCornersOrdered, time))))
        for time in sorted(self.blockData.keys()):
            numString = str(time)+'s'
            print(numString, end='')
            print('\b'*len(numString), end='')
            sys.stdout.flush()
            sigma = numpy.array([[0.,0.],[0.,0.]])
            for blockIndex in self.insideBoundaryBlocks:
                block = self.blockData[time][blockIndex]
                zones = block['zones']
                for zoneIndex in zones:
                    zone = self.zoneData[time][zoneIndex]
                    S11 = zone['S11']
                    S22 = zone['S22']
                    S12 = zone['S12']
                    S = numpy.array([[S11,S12],[S12,S22]])
                    gridPoints = zone['gridPoints']
                    gp = []
                    for gridPoint in gridPoints:
                        gpCoordinates = [self.gridPointData[time][gridPoint][var] for var in ['x', 'y']]
                        gp.append(gpCoordinates)
                    zoneArea = common.triangleArea(gp)
                    sigma += numpy.multiply(zoneArea,S)

                xx = self.cornerX(self.boundaryCornersOrdered, time)
                yy = self.cornerY(self.boundaryCornersOrdered, time)

                #totalArea = common.area(list(zip(self.cornerX(self.boundaryCornersOrdered, time), self.cornerY(self.boundaryCornersOrdered, time))))
            sigmaHistory.append(sigma/totalArea)
        print('')
        print('\tDone')
        self.stressHistory = sigmaHistory
        return sigmaHistory
    
    def strain(self):
        print('Assessing homogenized strains:')
        epsilonHistory = []
        corners = self.boundaryCornersOrdered
        corners.append(corners[0])
        print('\tAt time ', end='')
        for time in sorted(self.blockData.keys()):
            numString = str(time)+'s'
            print(numString, end='')
            print('\b'*len(numString), end='')
            sys.stdout.flush()
            epsilon = numpy.array([[0.,0.],[0.,0.]])
            for i in range(len(corners)-1):
                gridPoint1 = self.gridPointData[time][self.cornerData[time][corners[i]]['gridPoint']]
                gridPoint2 = self.gridPointData[time][self.cornerData[time][corners[i+1]]['gridPoint']]
                dx = gridPoint1['x']-gridPoint2['x']
                dy = gridPoint1['y']-gridPoint2['y']
                dW = math.hypot(dx, dy)
                if dW:
                    n = numpy.array([-dy, dx])/dW
                    u1 = numpy.array([gridPoint1['xDisp'], gridPoint2['yDisp']])
                    u2 = numpy.array([gridPoint1['xDisp'], gridPoint2['yDisp']])
                    u = (u1+u2)/2
                    x = numpy.outer(u, n)
                    epsilon += dW*(x + x.transpose())

            area = sum([self.blockData[time][b]['area'] for b in self.insideBoundaryBlocks])
            
            epsilonHistory.append(epsilon/2/area)
        print('')
        print('\tDone')
        self.strainHistory = epsilonHistory
        return epsilonHistory

    def time(self):
        t = sorted(self.blockData.keys());
        self.timeHistory = t
        return t
        
class common:
    def triangleArea(gp):
        distance = lambda p1,p2: math.hypot(p1[0]-p2[0], p1[1]-p2[1])
        side_a = distance(gp[0], gp[1])
        side_b = distance(gp[1], gp[2])
        side_c = distance(gp[2], gp[0])
        s = 0.5 * (side_a + side_b + side_c)
        return math.sqrt(s * (s - side_a) * (s - side_b) * (s - side_c))
        
    def listIntersection(a, b):
        return list(set(a) & set(b))

    def segments(p):
        return zip(p, p[1:] + [p[0]])
        
    def area(p):
        return 0.5 * abs(sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in common.segments(p)))

    def angle(x1, y1, x2, y2):
        inner_product = x1*x2 + y1*y2
        len1 = math.hypot(x1, y1)
        len2 = math.hypot(x2, y2)
        cosine = inner_product/(len1*len2)
        if abs(cosine) > 1:
            cosine = math.copysign(1, cosine)
        return math.acos(cosine)        
        
        
# def main():
    # pass

    # #test Functions should be here
    
    
    
    
    # # os.system('cls')

    # # clargs = sys.argv
    # # if len(clargs) >= 2:
        # # fileName = clargs[1]
    # # #else: error message
    # # #add other cl args for centre and radius
    # # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))
    # # module = __import__('UDEC.modelData.'+fileName[0:-3]+'_modelData', globals(), locals(), ['*']) #add subroutine to find module in UDEC folder and copy it here if it is not already.
    

    # # for k in dir(module):
        # # locals()[k] = getattr(module, k)
    # # revCentre = {'x':mSize/2, 'y':mSize/2}
    # # revRadius = mSize/2-bSize*2
    
    # # H = Homogenize(revCentre, revRadius, fileName=fileName)
    # # stressHistory = H.stress()
    # # strainHistory = H.strain()
    # # timeHistory = H.time()


# if __name__ == '__main__':
    # main()
