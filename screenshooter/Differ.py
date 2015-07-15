from PIL import Image
from PIL import ImageChops
import datetime


class Differ:

    img1 = None
    img2 = None

    imgs = dict()

    def __init__(self):
        pass

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

        view = imgLoc['View']
        date = imgLoc['Date']
        function = imgLoc['Function']
        today = datetime.datetime.now().date().isoformat()

        try:
            if view not in self.imgs:
                self.imgs[view] = dict()
            if today not in self.imgs[view]:
                self.imgs[view][today] = dict()
            self.imgs[view][today]["new" + function] = self.imgs['tmp'][view][date][function]
        except KeyError:
            del self.imgs[view][today]["new" + function]
            return False

        if diffImg is not None or changeImg is not None:
            try:
                imgName = function.partition('.')
                if diffImg is not None:
                    diffName = "new" + imgName[0] + "Diff.png"
                    self.imgs[view][today][diffName] = diffImg
                if changeImg is not None:
                    changeName = "new" + imgName[0] + "Change.png"
                    self.imgs[view][today][changeName] = changeImg
            except KeyError:
                #Not sure if still executes under single try if only one fails
                try:
                    del self.imgs[view][today][diffName]
                except KeyError:
                    pass
                try:
                    del self.imgs[view][today][changeName]
                except KeyError:
                    pass
                del self.imgs[view][today][function]
                return False

        return True

    #pass in the location of the modified img, returns location of original image
    def locateImgForDiff(self, loc):
        #find the oldest date stored and check if it has function, if so return location
        try:
            for dateDir in sorted(self.imgs[loc['View']], reverse = True):
                if dateDir == datetime.datetime.now().date().isoformat():
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

    # If originalLoc and modifiedLoc are not provided it will use the last images opened
    # using the equals method, originalLoc must be the original image and modifiedLoc
    # must be the modified image
    def getDiff(self, color = (0, 150, 255), highlightDiff = True,
                originalLoc = None, modifiedLoc = None):
        firstImg = None
        secondImg = None

        if (originalLoc is None and modifiedLoc is None) and (self.img1 is None or self.img2 is None):
            raise UnboundLocalError("The stored images are null and the parameters" +
                                    " do not provide locations to open them")
        if originalLoc is not None and modifiedLoc is not None:
            try:
                firstImg = self.getImg(originalLoc)
                secondImg = self.getImg(modifiedLoc, True)
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

    def run(self):
        for view in self.imgs['tmp']:
            for date in self.imgs['tmp'][view]:
                for function in self.imgs['tmp'][view][date]:
                    modifiedLoc = {'View': view, 'Date': date, 'Function': function}
                    originalLoc = self.locateImgForDiff(modifiedLoc)
                    diff = None
                    change = None
                    if originalLoc is not None:
                        modifiedImg = self.getImg(modifiedLoc, True)
                        originalImg = self.getImg(originalLoc)
                        if self.equals(originalImg, modifiedImg):
                            continue
                        diff = self.getDiff()
                        change = self.getChange()
                    self.store(modifiedLoc, diff, change)
        return True
