from PIL import Image
from PIL import ImageChops
import fnmatch
import os
import datetime
import shutil


class Screenshot:

    img1 = None
    img2 = None

    picturesDir = "/Users/emoyal/Pictures/"
    pictureType = ".png"
    imgs = dict()

    def __init__(self, fs = True):
        if fs:
            self.imgs = self.collectFSImgs(self.picturesDir)

    def collectFSImgs(self, baseDir):
        dictPics = dict()
        for dirView in fnmatch.filter(os.listdir(baseDir), "*View"):
            if os.path.isdir(os.path.join(baseDir, dirView)):
                screenshotsView = dict()
                for dirDate in fnmatch.filter(os.listdir(os.path.join(baseDir, dirView)), "*-*-*"):
                    if os.path.isdir(os.path.join(baseDir, dirView, dirDate)):
                        screenshotsDate = dict()
                        for filename in fnmatch.filter(os.listdir(os.path.join(baseDir,
                                                       dirView, dirDate)), "*" + self.pictureType):
                            screenshotsDate[filename] = Image.open(os.path.join(baseDir,
                                                                   dirView, dirDate, filename))
                        screenshotsView[dirDate] = screenshotsDate
                dictPics[dirView] = screenshotsView

        #this portion only grabs the images in the tmp directory
        screenshotsTemp = dict()
        for dirView in fnmatch.filter(os.listdir(os.path.join(baseDir, "tmp")), "*View"):
            if os.path.isdir(os.path.join(baseDir, "tmp", dirView)):
                screenshotsView = dict()
                for dirDate in fnmatch.filter(os.listdir(os.path.join(baseDir, "tmp", dirView)), "*-*-*"):
                    if os.path.isdir(os.path.join(os.path.join(baseDir, "tmp", dirView, dirDate))):
                        screenshotsDate = dict()
                        for filename in fnmatch.filter(os.listdir(os.path.join(baseDir,
                                                       "tmp", dirView, dirDate)), "*" + self.pictureType):
                            screenshotsDate[filename] = Image.open(os.path.join(baseDir,
                                                                   "tmp", dirView, dirDate, filename))
                screenshotsView[dirDate] = screenshotsDate
            screenshotsTemp[dirView] = screenshotsView
        dictPics['tmp'] = screenshotsTemp
        return dictPics

    # Identifies exact equality, can't differentiate between the following:
    # image size, image file type, image mode (ie. RGB/L/P/CMYK)
    def equals(self, firstImg, secondImg):
        if firstImg is None or secondImg is None:
            return False
        self.img1 = firstImg
        self.img2 = secondImg
        output = ImageChops.difference(firstImg, secondImg)
        if output.getbbox() != None:
            return False
        else:
            return True

    def store(self, imgLoc = None, diffImg = None, changeImg = None):

        if imgLoc is None and diffImg is None and changeImg is None:
            return False

        try:
            view = imgLoc['View']
            date = imgLoc['Date']
            function = imgLoc['Function']
            if view not in self.imgs:
                self.imgs[view] = dict()
            if date not in self.imgs[view]:
                self.imgs[view][date] = dict()
            self.imgs[view][date][function] = self.imgs['tmp'][view][date][function]
        except:
            raise
        return True

    def saveFS(self):
        today = datetime.datetime.now().date().isoformat()
        try:
            for view in fnmatch.filter(self.imgs, "*View"):
                print(view)
                if not os.path.exists(os.path.join(self.picturesDir, view)):
                    os.mkdir(os.path.join(self.picturesDir, view))
                if not os.path.exists(os.path.join(self.picturesDir, view, today)):
                    os.mkdir(os.path.join(self.picturesDir, view, today))
                for function in self.imgs[view][today]:
                    self.imgs[view][today][function].save(os.path.join(self.picturesDir,
                                                                       view,
                                                                       today,
                                                                       function))
            return True
        except:
            return False

    #pass in the location of the modified img, returns location of original image
    def locateImgForDiff(self, loc):
        #find the oldest date stored and check if it has function, if so return location
        for dateDir in sorted(self.imgs[loc['View']], reverse = True):
            imgReference = self.getImg(loc)
            if imgReference is not None:
                return {'View': loc['View'], 'Date': dateDir, 'Function': loc['Function']}
            else:
                continue
        return None

    def getImg(self, loc, tmp = False):
        view = loc['View']
        date = loc['Date']
        function = loc['Function']
        try:
            if tmp:
                return self.imgs['tmp'][view][date][function]
            return self.imgs[view][date][function]
        except KeyError:
            return None

    # If firstLoc and secondLoc are not provided it will use the last images opened
    # using the equals method, firstLoc must be the original image and secondLoc
    # must be the modified image
    def getDiff(self, color = (0, 150, 255), highlightDiff = True,
                firstLoc = None, secondLoc = None):
        firstImg = None
        secondImg = None

        if (firstLoc is None and secondLoc is None) and (self.img1 is None or self.img2 is None):
            raise UnboundLocalError("The stored images are null and the parameters" +
                                    " do not provide locations to open them")
        if firstLoc is not None and secondLoc is not None:
            try:
                firstImg = self.getImg(firstLoc)
                secondImg = self.getImg(secondLoc, True)
            except (IOError, KeyError, TypeError):
                return None
        else:
            firstImg = self.img1
            secondImg = self.img2

        dif = ImageChops.difference(firstImg, secondImg)

        if dif.getbbox() is None:
            return None

        dif = ImageChops.invert(dif)

        if not highlightDiff:
            return Image.blend(dif, firstImg, 0.2)

        for x in range(dif.size[0]):
            for y in range(dif.size[1]):
                if dif.getpixel((x, y)) == (255, 255, 255, 255):
                    continue
                dif.putpixel((x, y), color)
        return Image.blend(dif, firstImg, 0.2)

    def getChange(self, color = (0, 150, 255), highlightDiff = True,
                  originalLoc = None, modifiedLoc = None):
        originalImg = None
        modifiedImg = None

        if (originalLoc is None and modifiedLoc is None) and (self.img1 is None or self.img2 is None):
            raise UnboundLocalError("The stored images are null and the parameters" +
                                    " do not provide locations to open them")

        if originalLoc is not None and modifiedLoc is not None:
            try:
                originalImg = self.getImg(originalLoc)
                modifiedImg = self.getImg(modifiedLoc, True)
            except (IOError, KeyError, TypeError):
                return None
        else:
            originalImg = self.img1
            modifiedImg = self.img2

        diff = ImageChops.difference(originalImg, modifiedImg)
        if diff.getbbox() is None:
            return None

        invertedOriginal = ImageChops.invert(originalImg)
        mergingImg = invertedOriginal.copy()

        for x in range(mergingImg.size[0]):
            for y in range(mergingImg.size[1]):
                pixel = diff.getpixel((x, y))
                if pixel == (0, 0, 0, 0):
                    continue
                mergingImg.putpixel((x, y), pixel)

        finalDiff = ImageChops.invert(ImageChops.difference(mergingImg, invertedOriginal))

        if not highlightDiff:
            return Image.blend(finalDiff, originalImg, 0.2)

        for x in range(finalDiff.size[0]):
            for y in range(finalDiff.size[1]):
                if finalDiff.getpixel((x, y)) == (255, 255, 255, 255):
                    continue
                finalDiff.putpixel((x, y), color)

        return Image.blend(finalDiff, originalImg, 0.2)

    def cleanupFS(self):
        try:
            path = self.picturesDir + "tmp"
            shutil.rmtree(path)
        except:
            return False
        return True

    def run(self):
        for view in self.imgs['tmp']:
            for date in self.imgs['tmp'][view]:
                for function in self.imgs['tmp'][view][date]:
                    modifiedLoc = {'View': view, 'Date': date, 'Function': function}
                    originalLoc = self.locateImgForDiff(modifiedLoc)
                    diff = None
                    change = None
                    if originalLoc is not None:
                        modifiedImg = self.getImg(modifiedLoc)
                        originalImg = self.getImg(originalLoc)
                        if self.equals(originalImg, modifiedImg):
                            continue
                        diff = self.getDiff()
                        change = self.getChange()
                    self.store(modifiedLoc, diff, change)


#TODO
#Create run function that iterates through tmp directory and creates the diffs then saves them


#Documenting terminal completion
#
#
#
#

#Not used code keeping for concepts that may need later

    # def search(self, loc):
    #     view = loc['View']
    #     date = loc['Date']
    #     function = loc['Function']
    #     try:
    #         img = self.imgs['tmp'][view][date][function]
    #     except KeyError:
    #         raise KeyError("There is no image found at the location provided for the temp image")
    #     for dateDir in self.imgs[view]:
    #         try:
    #             imgReference = self.imgs[view][dateDir][function]
    #         except KeyError:
    #             continue
    #         if img.mode != imgReference.mode:
    #             continue
    #         if self.equals(img, imgReference):
    #             return True
    #     return False

    #method uses filesystem to perform searching, code needs to change
    #in order to implement blob storage query
    # def search(self, fullLoc = None, name = None):
    #     if name is None and fullLoc is None:
    #         raise UnboundLocalError("Both parameters are null please provide at least one parameter")
    #     elif name is not None and fullLoc is None:
    #         loc = self.picturesDir + "tmp/" + name
    #     if fullLoc is not None:
    #         loc = fullLoc
    #
    #     # img = self.exists(loc)
    #     return self.searchImg(img, loc)
    #
    # def searchImg(self, img, loc):
    #     if img is None:
    #         return False
    #     for root, dirnames, filenames in os.walk(self.picturesDir):
    #         for filename in fnmatch.filter(filenames, "*" + self.pictureType):
    #             fileLoc = os.path.join(root, filename)
    #             if fileLoc == loc:
    #                 continue
    #             imgReference = Image.open(fileLoc)
    #             if img.mode != imgReference.mode:
    #                 continue
    #             if self.equals(img, imgReference):
    #                 return True
    #     return False

        #     today = datetime.datetime.now()
        #     path = self.picturesDir + "SomeView/"
        #     if not os.path.exists(path):
        #         os.mkdir(path)
        #     outputPath = path + today.date().isoformat() + "/"
        #     if not os.path.exists(outputPath):
        #         os.mkdir(outputPath)
        #     filename = "{0}_{1}_{2}_{3}".format(today.hour, today.minute,
        #                                         today.second, today.microsecond)
        #     img.save(outputPath + filename + self.pictureType)
        # except IOError:
        #     raise
        # except AttributeError:
        #     raise
        #
        # return True
