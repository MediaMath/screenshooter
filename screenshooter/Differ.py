from PIL import Image
from PIL import ImageChops
import datetime
import screenshooter.config as config
import screenshooter.saves


class Differ:
    """
    Differ is a service that allows the diffing of images.
    """

    def __init__(self):
        self.imgs = dict()
        self.diff = None
        self.originalImg = None
        self.modifiedImg = None
        self.archiveTime = None
        self.imgType = config.pictureType

    def equals(self, firstImg, secondImg):
        """
        Identifies if firstImg and secondImg are identical to each other.

        Args:
          firstImg: a PIL image object of the original image
          secondImg: a PIL image object of the modified image

        Returns:
          A boolean stating whether or not the two images are identical, True means they are
          identical.
        """
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

    def archiveImgs(self, imgLoc):
        """
        Archive the image given by imgLoc and it's corresponding diff and change images.

        Args:
          imgLoc: a dictionary representing the location of the image within the multi-dimensional
            dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
        """
        view = imgLoc['View']
        date = imgLoc['Date']
        function = imgLoc['Function']

        if self.archiveTime is None:
            self.archiveTime = datetime.datetime.now().isoformat()
        if self.archiveTime not in self.imgs[view]:
            self.imgs[view][self.archiveTime] = dict()
        self.imgs[view][self.archiveTime]["new" + function] = self.imgs[view][date][function]
        imgName = function.partition('.')
        if imgName[0] + "Diff" + self.imgType in self.imgs[view][date]:
            self.imgs[view][self.archiveTime]["new" + imgName[0] + "Diff.png"] = self.imgs[view][date][imgName[0] + "Diff" + self.imgType]
        if imgName[0] + "Change" + self.imgType in self.imgs[view][date]:
            self.imgs[view][self.archiveTime]["new" + imgName[0] + "Change.png"] = self.imgs[view][date][imgName[0] + "Change" + self.imgType]

    def storeScreenshot(self, imgLoc):
        """
        Moves the screenshot from it's temporary location in the multi-dimensional dictionary to a portion
        where it will actually be saved.

        Args:
          imgLoc: a dictionary representing the location of the image within the multi-dimensional
            dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """
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
            if function in self.imgs[view][date]:
                self.archiveImgs(imgLoc)
            self.imgs[view][date]["new" + function] = self.imgs['tmp'][view][date][function]
        except KeyError:
            del self.imgs[view][date]["new" + function]
            return False
        return True

    def storeDiff(self, imgLoc, diffImg):
        """
        Adds the diff image to the multi-dimensional dictionary so it can be saved.

        Args:
          imgLoc: a dictionary representing the location of the image that was used to create the diff image within
            the multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          diffImg: a PIL image object of the diff image

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """
        if diffImg is None:
            return False

        view = imgLoc['View']
        date = imgLoc['Date']
        imgName = imgLoc['Function'].partition('.')

        diffName = "new" + imgName[0] + "Diff" + self.imgType
        self.imgs[view][date][diffName] = diffImg
        return True

    def storeChange(self, imgLoc, changeImg):
        """
        Adds the change image to the multi-dimensional dictionary so it can be saved.

        Args:
          imgLoc: a dictionary representing the location of the image that was used to create the change image within
            the multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          changeImg: a PIL image object of the diff image

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """
        if changeImg is None:
            return False

        view = imgLoc['View']
        date = imgLoc['Date']
        imgName = imgLoc['Function'].partition('.')

        changeName = "new" + imgName[0] + "Change" + self.imgType
        self.imgs[view][date][changeName] = changeImg

        return True

    def store(self, imgLoc = None, diffImg = None, changeImg = None):
        """
        Adds the screenshot and it's corresponding diff and change images to the multi-dimensional dictionary
        so they can be saved.

        Args:
          imgLoc: a dictionary representing the location of the screenshot within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          diffImg: a PIL image object of the diff image
          changeImg: a PIL image object of the change image

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """

        if imgLoc is None and diffImg is None and changeImg is None:
            return False

        if self.storeScreenshot(imgLoc):
            self.storeDiff(imgLoc, diffImg)
            self.storeChange(imgLoc, changeImg)
        else:
            return False

        return True

    def locateImgForDiff(self, loc, serviceName = config.service):
        """
        Locates the image to diff against.

        Args:
          loc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          serviceName: the name of the service to grab the image from (Defaults to the service in the config file)

        Returns:
          A dictionary representing the location of the original image to diff against in the
            multi-dimensional dictionary
        """
        if serviceName.upper() == "S3":
            imgReference = screenshooter.saves.s3Service.collectImg(self.imgs, loc)
        elif serviceName.upper() == "FILESYSTEM":
            imgReference = screenshooter.saves.fsService.collectImg(self.imgs, loc)
        return imgReference

    def getImg(self, loc, tmp = False):
        """
        Retrieves the PIL image object from the multi-dimensional dictionary.

        Args:
          loc: a dictionary representing the location of the image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          tmp: a boolean stating whether or not to grab from the tmp dictionary, True means grab from the tmp
            dictionary (Defaults to False)

        Returns:
          A PIL image object
        """
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
        """
        Checks to make sure all the information is acceptable before performing the diff.

        Args:
          originalLoc: a dictionary representing the location of the original image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          modifiedLoc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}

        Returns:
          The pixel difference between the two images.

        Raises:
          UnboundLocalError: The class level images are null and the parameters do not provide locations to open them.
        """
        if (originalLoc is None and modifiedLoc is None) and (self.originalImg is None or self.modifiedImg is None) and self.diff is None:
            raise UnboundLocalError("The class level images are null and the parameters" +
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
        elif self.diff is not None:
            return self.diff
        else:
            return None

    def getDiff(self, originalLoc = None, modifiedLoc = None):
        """
        Gets the difference between two images and applies a highlight over them if specified.

        Args:
          originalLoc: a dictionary representing the location of the original image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)
          modifiedLoc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)

        Returns:
          A PIL image object of the diff image.
        """

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
        """
        Subtract two pixels.

        Args:
          first: An RGBA pixel value
          second: An RGBA pixel value

        Returns:
          A tuple containing the result of the absolute value of the subtraction of the two pixels.
        """
        return tuple([abs(first[0] - second[0]), abs(first[1] - second[1]), abs(first[2] - second[2]), abs(first[3] - second[3])])

    def getChange(self, originalLoc = None, modifiedLoc = None):
        """
        Gets the changed difference between two images and applies a highlight over them if specified.

        Args:
          originalLoc: a dictionary representing the location of the original image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)
          modifiedLoc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)

        Returns:
          A PIL image object of the change image.
        """

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
        """
        A singular function to run through the multi-dimensional dictionary and diff all images in the
        tmp dictionary and then store the images that result in a diff/change for saving.
        """
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
