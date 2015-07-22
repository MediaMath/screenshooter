from PIL import Image
from PIL import ImageChops
import datetime
import screenshooter.config as config


class Differ:
    def __init__(self):
        self.imgs = dict()
        self.diff = None
        self.originalImg = None
        self.modifiedImg = None

    # Identifies exact equality, can't differentiate between the following:
    # image size, image file type, image mode (ie. RGB/L/P/CMYK)
    def equals(self, firstImg, secondImg):
        if firstImg is None or secondImg is None:
            return False
        self.originalImg = firstImg
        self.modifiedImg = secondImg
        self.diff = ImageChops.difference(firstImg, secondImg)
        if self.diff.getbbox() != None:
            return False
        else:
            self.diff = None
            return True

    def storeScreenshot(self, imgLoc):
        if imgLoc is None:
            return False

        view = imgLoc['View']
        date = imgLoc['Date']
        function = imgLoc['Function']

        try:
            if view not in self.imgs:
                self.imgs[view] = dict()
            if date not in self.imgs[view]:
                self.imgs[view][date] = dict()
            self.imgs[view][date]["new" + function] = self.imgs['tmp'][view][date][function]
        except KeyError:
            del self.imgs[view][date]["new" + function]
            return False
        return True

    def storeDiff(self, imgLoc, diffImg):
        if diffImg is None:
            return False

        view = imgLoc['View']
        date = imgLoc['Date']
        imgName = imgLoc['Function'].partition('.')

        diffName = "new" + imgName[0] + "Diff.png"
        self.imgs[view][date][diffName] = diffImg
        return True

    def storeChange(self, imgLoc, changeImg):
        if changeImg is None:
            return False

        view = imgLoc['View']
        date = imgLoc['Date']
        imgName = imgLoc['Function'].partition('.')

        changeName = "new" + imgName[0] + "Change.png"
        self.imgs[view][date][changeName] = changeImg

        return True

    def store(self, imgLoc = None, diffImg = None, changeImg = None):

        if imgLoc is None and diffImg is None and changeImg is None:
            return False

        if self.storeScreenshot(imgLoc):
            self.storeDiff(imgLoc, diffImg)
            self.storeChange(imgLoc, changeImg)
        else:
            return False

        return True

    #pass in the location of the modified img, returns location of original image
    def locateImgForDiff(self, loc):
        #find the oldest date stored and check if it has function, if so return location
        today = datetime.datetime.now().date().isoformat()
        try:
            for dateDir in sorted(self.imgs[loc['View']], reverse = True):
                if dateDir == today:
                    continue
                loc['Date'] = dateDir
                imgReference = self.getImg(loc)
                if imgReference is not None:
                    return {'View': loc['View'], 'Date': dateDir, 'Function': loc['Function']}
                else:
                    continue
        except KeyError:
            pass
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

    def sanitizeForDiff(self, originalLoc, modifiedLoc):
        if (originalLoc is None and modifiedLoc is None) and (self.originalImg is None or self.modifiedImg is None):
            raise UnboundLocalError("The stored images are null and the parameters" +
                                    " do not provide locations to open them")
        if originalLoc is not None and modifiedLoc is not None:
            try:
                self.originalImg = self.getImg(originalLoc)
                self.modifiedImg = self.getImg(modifiedLoc, True)
                self.diff = ImageChops.difference(self.originalImg, self.modifiedImg)
                if self.diff.getbbox() is None:
                    return None
                return self.diff
            except (IOError, KeyError, TypeError):
                return None
        else:
            return self.diff

    # If originalLoc and modifiedLoc are not provided it will use the last images opened
    # using the equals method. OriginalLoc must be the original image and modifiedLoc
    # must be the modified image
    def getDiff(self, originalLoc = None, modifiedLoc = None):

        dif = self.sanitizeForDiff(originalLoc, modifiedLoc)

        if dif is None:
            return None

        color = config.highlightColor

        dif = ImageChops.invert(dif)

        if not color:
            return Image.blend(dif, self.originalImg, 0.2)

        width = dif.size[0]
        height = dif.size[1]
        pixel = dif.load()
        for x in range(width):
            for y in range(height):
                if pixel[x, y] == (255, 255, 255, 255):
                    continue
                pixel[x, y] = color

        return Image.blend(dif, self.originalImg, 0.2)

    def subtractPixels(self, first, second):
        return tuple([abs(first[0] - second[0]), abs(first[1] - second[1]), abs(first[2] - second[2]), abs(first[3] - second[3])])

    def getChange(self, originalLoc = None, modifiedLoc = None):

        diff = self.sanitizeForDiff(originalLoc, modifiedLoc)

        if diff is None:
            return None

        color = config.highlightColor

        mergingImg = ImageChops.invert(self.originalImg)

        width = mergingImg.size[0]
        height = mergingImg.size[1]

        diffPixels = diff.load()
        mergePixel = mergingImg.load()

        for x in range(width):
            for y in range(height):
                diffPixel = diffPixels[x, y]
                if diffPixel != (0, 0, 0, 0):
                    if self.subtractPixels(diffPixel, mergePixel[x, y]) == (0, 0, 0, 0):
                        mergePixel[x, y] = (255, 255, 255, 255)
                    else:
                        if color is None:
                            continue
                        mergePixel[x, y] = color
                else:
                    mergePixel[x, y] = (255, 255, 255, 255)

        return Image.blend(mergingImg, self.originalImg, 0.2)

    def run(self):
        diffFlag = config.runDiff
        changeFlag = config.runChange
        for view in self.imgs['tmp']:
            for date in self.imgs['tmp'][view]:
                for function in self.imgs['tmp'][view][date]:
                    modifiedLoc = {'View': view, 'Date': date, 'Function': function}
                    originalLoc = self.locateImgForDiff(modifiedLoc)
                    diff = None
                    change = None
                    if originalLoc:
                        modifiedImg = self.getImg(modifiedLoc, True)
                        originalImg = self.getImg(originalLoc)
                        if self.equals(originalImg, modifiedImg):
                            continue
                        if diffFlag:
                            diff = self.getDiff()
                        if changeFlag:
                            change = self.getChange()
                    self.store(modifiedLoc, diff, change)
        return True
