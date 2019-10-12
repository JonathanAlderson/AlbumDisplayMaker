import random, pickle, os, time, sys
from PIL import Image, ImageDraw
from collections import Counter


class Wall:
    x = 0
    y = 0
    maxX = 0
    maxY = 0
    picturesDone = 0
    picturesOnWall = []
    remaningLocations = []
    freePictures = []  # only for random
    criteria = "mean"
    incrementMode = "vertical"
    sumOfDiffs = 999999999

    def __init__(self,x,y,allPictures):
        self.maxX = x
        self.maxY = y
        self.picturesOnWall = [[0 for i in range(self.maxX)] for j in range(self.maxY)]
        self.remaningPictures = allPictures[:]


    def getDiff(self,picture1,picture2):
        diff = 0
        if(self.criteria == "mean"):
            for i in range(3):
                diff += abs(picture1.meanColour[i]-picture2.meanColour[i])

        elif(self.criteria == "mode"):
            for i in range(3):
                diff += abs(picture1.modeColour[i]-picture2.modeColour[i])

        return diff

    def drawWalls(self):
        thumbnailSize = self.picturesOnWall[0][0].thumbSize
        imageWidth = self.maxX * thumbnailSize
        imageHeight = self.maxY * thumbnailSize
        img = Image.new('RGB', (imageWidth, imageHeight))

        # for every picture on the wall
        for x in range(self.maxX):
            for y in range(self.maxY):
                if(self.picturesOnWall[y][x] != 0): # only 0 when we haven't found an image
                    thisImage = Image.open(self.picturesOnWall[y][x].thumbnail)
                    img.paste(thisImage,(x*thumbnailSize,y*thumbnailSize))
        img.save(str(self.sumOfDiffs) + " x=" + str(self.maxX) + " y=" + str(self.maxY) + " " + self.criteria + " " + self.incrementMode    + '.png')

    def getSumOfDiffs(self):
        totalDiff = 0
        for x in range(self.maxX):
            for y in range(self.maxY):
                thisImage = self.picturesOnWall[y][x]
                closeImages = self.getCloseImages(x,y)

                for closeImage in closeImages:
                    totalDiff += self.getDiff(thisImage,closeImage)

        return totalDiff


    def increment(self):
        # this swipes along the wall
        # in a diagonal fashion
        # keep going up diagonally
        # and when we reach the top, go to the next
        # diagonal row
        if(self.incrementMode == "vertical"):
            self.y += 1
            if(self.y >= self.maxY):
                self.y = 0
                self.x += 1
        elif(self.incrementMode == "diagonal"):
            if(self.x >= self.maxX-1):
                while(self.y < self.maxY):
                    self.y += 1
                    self.x -= 1
                self.x += 1

            if(self.y == 0):
                self.y = self.x + 1
                self.x = 0
                while self.y >= self.maxY:
                    self.x += 1
                    self.y -= 1
            else:
                self.y = self.y - 1
                self.x = self.x + 1
        elif(self.incrementMode == "random"):
            if(len(self.remaningLocations) == 0):
                for i in range(self.maxX):
                    for j in range(self.maxY):
                        self.remaningLocations.append((i,j))

            newPosition = random.choice(self.remaningLocations)
            self.x,self.y = newPosition
            self.remaningLocations.remove(newPosition)

        self.picturesDone += 1


    def getCloseImages(self,x=-1,y=-1):
        # gets all the images already in our little wall
        # if they are 0, then they haven't been filled in yet.
        if(x == -1 and y == -1):
            x = self.x
            y = self.y
        closeImages = []
        if(x > 0):
            if(self.picturesOnWall[y][x-1] != 0):
                closeImages.append(self.picturesOnWall[y][x-1])
        if(x < self.maxX-1):
            if(self.picturesOnWall[y][x+1] != 0):
                closeImages.append(self.picturesOnWall[y][x+1])
        if(y > 0):
            if(self.picturesOnWall[y-1][x] != 0):
                closeImages.append(self.picturesOnWall[y-1][x])
        if(y < self.maxY-1):
            if(self.picturesOnWall[y+1][x] != 0):
                closeImages.append(self.picturesOnWall[y+1][x])

        #print("There are " + str(len(closeImages)) + " close images")
        return closeImages

    def addPictureToWall(self):
        #print("\n\nAdding picture to wall")
        if(self.picturesDone == 0):
            bestMatch = random.choice(self.remaningPictures)
            #print("Random chosen album")
            #print(bestMatch)
        else:
            closePictures = self.getCloseImages()
            bestMatch = ""
            bestDiff = 9999
            for contestentImage in self.remaningPictures:
                diff = 0
                for closeImage in closePictures:
                    diff += self.getDiff(contestentImage,closeImage)
                if(diff < bestDiff):
                    bestDiff = diff
                    bestMatch = contestentImage

        self.picturesOnWall[self.y][self.x] = bestMatch
        self.remaningPictures.remove(bestMatch)

    def makeWall(self,criteria,increment):
        self.incrementMode = increment
        self.criteria = criteria
        self.x = 0
        self.y = 0

        while(self.picturesDone < self.maxX*self.maxY):
            try:
                #print("x: ",self.x," y: ",self.y)
                self.addPictureToWall()
                self.increment()
            except:
                print("Crashing")
                sys.exit(0)
        if(self.incrementMode == "random" or self.incrementMode == "horizontal"):
            self.addPictureToWall()
        self.sumOfDiffs = self.getSumOfDiffs()

class Picture:
    thumbSize = 128
    filename = ""
    thumbnail = ""
    name = ""
    x = 0
    y = 0
    meanColour = [0,0,0]
    modeColour = [0,0,0]
    edgesColour = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    imData = []
    thumbnail = ""
    def __init__(self,filename):
        self.name = filename.split("\\")[-1]
        self.name = self.name.split(".")[0]
        self.filename = filename

    def __str__(self):
        return "Album: " + self.name + " Mean: " + str(self.meanColour) + " Mode: " + str(self.modeColour)

    def getImData(self):
        self.imData = []
        im = Image.open(self.thumbnail)
        width, height = im.size
        for y in range(height):
            for x in range(width):
                pixel = im.getpixel((x,y))
                try:
                    pixel = int(pixel)
                    pixel = (pixel,pixel,pixel)
                except:
                    pass

                self.imData.append(pixel)

    def calcMean(self):
        self.meanColour = [int(sum([i[0] for i in self.imData])/len(self.imData)),
                           int(sum([i[1] for i in self.imData])/len(self.imData)),
                           int(sum([i[2] for i in self.imData])/len(self.imData))]

    def calcMode(self):
        modeList = [str(i[0])+":"+str(i[1])+":"+str(i[2]) for i in self.imData]
        self.modeColour = Counter(modeList).most_common(1)
        allColours = [item[0] for item in self.modeColour]
        allColours = [item.split(":") for item in allColours]
        self.modeColour = [int(sum([int(allColours[i][j])/len(allColours) for i in range(len(allColours))])) for j in range(len(allColours[0]))]


    def getEdges(self):
        pass #TODO

    def makeThumbnail(self):
            im = Image.open(self.filename)
            im.thumbnail((self.thumbSize,self.thumbSize), Image.ANTIALIAS)
            im.save("thumbnails/" + self.name + ".jpeg", "JPEG")
            self.thumbnail = "thumbnails/" + self.name + ".jpeg"




imagesOne = "C:\\Users\\light\\Documents\\MemoryStickBackup\\albumsThatILike"
imagesTwo = "C:\\Users\\light\\Documents\\MemoryStickBackup\\albumsThatILike2"

allPictures = []

wallX = 16
wallY = 7
maxPictures = wallX*wallY


loadPickle = True

if(loadPickle):
    print("Reading Pickle...")
    allPictures = pickle.load( open( "allPictures.p","rb"))
    print("Read Pickle")

else:
    for subdir, dirs, files in os.walk(imagesOne):
        for file in files:
            allPictures.append(Picture(imagesOne + "\\" + file))
    for subdir, dirs, files in os.walk(imagesTwo):
        for file in files:
            allPictures.append(Picture(imagesTwo + "\\" + file))

    toRemove = []
    for i in range(len(allPictures)):
        if(i < maxPictures + len(toRemove)):
            picture = allPictures[i]
            picture.makeThumbnail()
            picture.getImData()
            picture.calcMean()
            picture.calcMode()
            #print(picture)

    for index in toRemove:
        allPictures.remove(allPictures[index])
    print("There were " + str(len(toRemove)) + " errors and " + str(len(allPictures)) + " pictures")

    allPictures = allPictures[:maxPictures]
    pickle.dump(allPictures, open( "allPictures.p", "wb" ) )

for picture in allPictures:
    print(picture)

minimums = {
            "vertical": 9999999,
            "diagonal": 99999,
            "random": 999999 }
walls = []
for i in range(100000):
    print(i)
    for type_for_run in ["vertical","diagonal","random"]:
        walls.append(Wall(wallX,wallY,allPictures))
        walls[-1].makeWall("mean",type_for_run)
        if(walls[-1].sumOfDiffs < minimums[type_for_run]):
            print("New Best for " + type_for_run + "! ",walls[-1].sumOfDiffs)
            minimums[type_for_run] = walls[-1].sumOfDiffs
            walls[-1].drawWalls()
