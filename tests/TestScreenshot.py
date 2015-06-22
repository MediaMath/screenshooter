import screenshooter.config as config
import pytest
import datetime
import shutil
import os
from PIL import Image
from screenshooter.Screenshot import Screenshot
import time


def setup_module(module):
    path = config.baseImageDir + "tmp"
    today = datetime.datetime.now().date().isoformat()
    #baseCopyPath = "/Users/emoyal/Documents/Projects/screenshot/"
    imgsDir = "../imgs/"
    screen1 = "screenshot1.png"
    screen2 = "screenshot2.png"
    screen3 = "screenshot3.png"
    fullPath = os.path.join(path, "SomeView", today)
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.exists(os.path.join(path, "SomeView")):
        os.mkdir(os.path.join(path, "SomeView"))
    if not os.path.exists(os.path.join(path, "SomeView", today)):
        os.mkdir(fullPath)
    if not os.path.exists(os.path.join(fullPath, screen1)):
        shutil.copy2(imgsDir + screen1, fullPath)
    if not os.path.exists(os.path.join(fullPath, screen2)):
        shutil.copy2(imgsDir + screen2, fullPath)
    if not os.path.exists(os.path.join(fullPath, screen3)):
        shutil.copy2(imgsDir + screen3, fullPath)

    savesPath = config.baseImageDir
    fullSavesPath = os.path.join(savesPath, "SomeView", today)
    if not os.path.exists(os.path.join(savesPath, "SomeView")):
        os.mkdir(os.path.join(savesPath, "SomeView"))
    if not os.path.exists(fullSavesPath):
        os.mkdir(fullSavesPath)
    if not os.path.exists(os.path.join(fullSavesPath, screen1)):
        shutil.copy2(imgsDir + screen1, fullSavesPath)
    if not os.path.exists(os.path.join(fullSavesPath, screen3)):
        shutil.copy2(imgsDir + screen2, fullSavesPath)
        os.rename(os.path.join(fullSavesPath, screen2), os.path.join(fullSavesPath, screen3))
    if not os.path.exists(os.path.join(fullSavesPath, screen2)):
        shutil.copy2(imgsDir + screen2, fullSavesPath)

def teardown_module(module):
    path = config.baseImageDir + "SomeView/"
    shutil.rmtree(path)


class TestScreenshot:

    nonExistentScreenLoc = config.baseImageDir + "nonexistent.png"
    directoryLocationOfScreenshots = config.baseImageDir

    def setup_method(self, method):
        self.screenshotProcess = Screenshot()
        self.firstScreenshot = {'View': 'SomeView', 'Date': datetime.datetime.now().date().isoformat(), 'Function': 'screenshot1.png'}
        self.secondScreenshot = {'View': 'SomeView', 'Date': datetime.datetime.now().date().isoformat(), 'Function': 'screenshot2.png'}
        self.thirdScreenshot = {'View': 'SomeView', 'Date': datetime.datetime.now().date().isoformat(), 'Function': 'screenshot3.png'}

        firstView = self.firstScreenshot['View']
        firstDate = self.firstScreenshot['Date']
        firstFunction = self.firstScreenshot['Function']
        self.first = self.screenshotProcess.imgs['tmp'][firstView][firstDate][firstFunction]

        secondView = self.secondScreenshot['View']
        secondDate = self.secondScreenshot['Date']
        secondFunction = self.secondScreenshot['Function']
        self.second = self.screenshotProcess.imgs['tmp'][secondView][secondDate][secondFunction]

        thirdView = self.thirdScreenshot['View']
        thirdDate = self.thirdScreenshot['Date']
        thirdFunction = self.thirdScreenshot['Function']
        self.third = self.screenshotProcess.imgs['tmp'][thirdView][thirdDate][thirdFunction]

    #
    # @classmethod
    # def teardown_class(cls):
    #     return
    #

    def testCollectFilesystemScreenshotsReturnsValue(self):
        assert self.screenshotProcess.collectFSImgs(self.directoryLocationOfScreenshots) is not None

    def testCollectFilesystemScreenshotsFails(self):
        with pytest.raises(FileNotFoundError):
            self.screenshotProcess.collectFSImgs(self.nonExistentScreenLoc)

    def testScreenshotComparisonEquals(self):
        assert self.screenshotProcess.equals(self.first, self.second) == True

    def testScreenshotComparisonNotEqual(self):
        assert self.screenshotProcess.equals(self.first, self.third) == False

    def testScreenshotStore(self):
        assert self.screenshotProcess.store(self.firstScreenshot) == True

    def testScreenshotVoidParametersStore(self):
        assert self.screenshotProcess.store() == False

    def testScreenshotInvalidParametersStore(self):
        with pytest.raises(TypeError):
            self.screenshotProcess.store(self.nonExistentScreenLoc)

    def testGetDiffVoidParameters(self):
        self.screenshotProcess.img1 = None
        self.screenshotProcess.img2 = None
        with pytest.raises(UnboundLocalError):
            self.screenshotProcess.getDiff()

    def testGetDiffInvalidFirstLocation(self):
        assert self.screenshotProcess.getDiff(firstLoc = self.nonExistentScreenLoc,
                                              secondLoc = self.firstScreenshot) is None

    def testGetDiffInvalidSecondLocation(self):
        assert self.screenshotProcess.getDiff(firstLoc = self.firstScreenshot,
                                              secondLoc = self.nonExistentScreenLoc) is None

    def testGetDiffReturnsValueWithLocation(self):
        assert self.screenshotProcess.getDiff(firstLoc = self.firstScreenshot,
                                              secondLoc = self.thirdScreenshot) is not None

    def testGetDiffWithSameScreenshots(self):
        self.screenshotProcess.img1 = self.first
        self.screenshotProcess.img2 = self.second
        assert self.screenshotProcess.getDiff() is None

    def testGetDiffReturnsValueWithoutLocation(self):
        self.screenshotProcess.img1 = self.first
        self.screenshotProcess.img2 = self.third
        diff = self.screenshotProcess.getDiff()
        #diff.show()
        assert diff is not None

    def testGetChangeVoidParameters(self):
        self.screenshotProcess.img1 = None
        self.screenshotProcess.img2 = None
        with pytest.raises(UnboundLocalError):
            self.screenshotProcess.getChange()

    def testGetChangeInvalidFirstLocation(self):
        assert self.screenshotProcess.getChange(originalLoc = self.nonExistentScreenLoc,
                                                modifiedLoc = self.firstScreenshot) is None

    def testGetChangeInvalidSecondLocation(self):
        assert self.screenshotProcess.getChange(originalLoc = self.firstScreenshot,
                                                modifiedLoc = self.nonExistentScreenLoc) is None

    def testGetChangeReturnsValueWithLocation(self):
        assert self.screenshotProcess.getChange(originalLoc = self.firstScreenshot,
                                                modifiedLoc = self.thirdScreenshot) is not None

    def testGetChangeReturnsValueWithoutLocation(self):
        self.screenshotProcess.img1 = self.first
        self.screenshotProcess.img2 = self.third
        change = self.screenshotProcess.getChange()
        #change.show()
        assert change is not None

    def testGetChangeWithSameScreenshots(self):
        self.screenshotProcess.img1 = self.first
        self.screenshotProcess.img2 = self.second
        assert self.screenshotProcess.getChange() is None

    def testLocateImageForDiff(self):
        assert self.screenshotProcess.locateImgForDiff(self.thirdScreenshot) is not None

    def testLocateImageForDiffInvalidLocation(self):
        loc = {'View': 'SomeView', 'Date': datetime.datetime.now().date().isoformat(), 'Function': 'screenshot4.png'}
        assert self.screenshotProcess.locateImgForDiff(loc) is None

    def testRun(self):
        self.screenshotProcess.run()
        view = self.thirdScreenshot['View']
        date = self.thirdScreenshot['Date']
        diff = self.screenshotProcess.imgs[view][date]['screenshot3Diff.png']
        change = self.screenshotProcess.imgs[view][date]['screenshot3Change.png']
        assert diff is not None and change is not None

    def testSaveFS(self):
        assert self.screenshotProcess.saveFS() == True

    def testCleanupTmpDir(self):
        self.screenshotProcess.cleanupFS()
        assert os.path.exists(self.directoryLocationOfScreenshots + "tmp") == False
