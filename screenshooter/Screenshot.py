from PIL import Image
from PIL import ImageChops


class Screenshot:

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
        try:
            imgRevert = self.imgs[view][date][function]
        except:
            pass

        try:
            if view not in self.imgs:
                self.imgs[view] = dict()
            if date not in self.imgs[view]:
                self.imgs[view][date] = dict()
            self.imgs[view][date][function] = self.imgs['tmp'][view][date][function]
        except:
            if imgRevert is None:
                del self.imgs[view][date][function]
            else:
                self.imgs[view][date][function] = imgRevert
            return False

        if diffImg is not None or changeImg is not None:
            try:
                imgName = function.partition('.')
                if diffImg is not None:
                    diffName = imgName[0] + "Diff.png"
                    self.imgs[view][date][diffName] = diffImg
                if changeImg is not None:
                    changeName = imgName[0] + "Change.png"
                    self.imgs[view][date][changeName] = changeImg
            except:
                #Not sure if still executes under single try if only one fails
                try:
                    del self.imgs[view][date][diffName]
                except KeyError:
                    pass
                try:
                    del self.imgs[view][date][changeName]
                except KeyError:
                    pass
                self.imgs[view][date][function] = imgRevert
                return False

        return True

    #pass in the location of the modified img, returns location of original image
    def locateImgForDiff(self, loc):
        #find the oldest date stored and check if it has function, if so return location
        for dateDir in sorted(self.imgs[loc['View']], reverse = True):
            loc['Date'] = dateDir
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
    #         loc = config.baseImageDir + "tmp/" + name
    #     if fullLoc is not None:
    #         loc = fullLoc
    #
    #     # img = self.exists(loc)
    #     return self.searchImg(img, loc)
    #
    # def searchImg(self, img, loc):
    #     if img is None:
    #         return False
    #     for root, dirnames, filenames in os.walk(config.baseImageDir):
    #         for filename in fnmatch.filter(filenames, "*" + config.pictureType):
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
        #     path = config.baseImageDir + "SomeView/"
        #     if not os.path.exists(path):
        #         os.mkdir(path)
        #     outputPath = path + today.date().isoformat() + "/"
        #     if not os.path.exists(outputPath):
        #         os.mkdir(outputPath)
        #     filename = "{0}_{1}_{2}_{3}".format(today.hour, today.minute,
        #                                         today.second, today.microsecond)
        #     img.save(outputPath + filename + config.pictureType)
        # except IOError:
        #     raise
        # except AttributeError:
        #     raise
        #
        # return True
