import screenshooter.config as config
import pytest
import datetime
from datetime import timedelta
from PIL import Image
from screenshooter.Differ import Differ
import time


class TestDiffer:

    nonExistentScreenLoc = "blah"

    @classmethod
    def setup_class(cls):
        cls.tmpImg1 = Image.open(config.baseProjectDir + "tests/imgs/screenshot1.png")
        cls.tmpImg2 = Image.open(config.baseProjectDir + "tests/imgs/screenshot2.png")
        cls.tmpImg3 = Image.open(config.baseProjectDir + "tests/imgs/screenshot3.png")

        cls.img1 = Image.open(config.baseProjectDir + "tests/imgs/screenshot1.png")
        cls.img2 = Image.open(config.baseProjectDir + "tests/imgs/screenshot1.png")
        cls.img3 = Image.open(config.baseProjectDir + "tests/imgs/screenshot1.png")

    def setup_method(self, method):
        yesterday = datetime.datetime.now() - timedelta(days = 1)
        self.screenshotProcess = Differ()
        self.firstScreenshot = {'View': 'SomeView', 'Date': yesterday.date().isoformat(), 'Function': 'screenshot1.png'}
        self.secondScreenshot = {'View': 'SomeView', 'Date': yesterday.date().isoformat(), 'Function': 'screenshot2.png'}
        self.thirdScreenshot = {'View': 'SomeView', 'Date': yesterday.date().isoformat(), 'Function': 'screenshot3.png'}

        self.first = self.tmpImg1
        self.second = self.tmpImg2
        self.third = self.tmpImg3

    #
    # @classmethod
    # def teardown_class(cls):
    #     return
    #

    # Stub out the multi-dimensional dictionary so it isn't reliant on where it obtains the information from
    @pytest.fixture(autouse = True)
    def assignImages(self, monkeypatch):
        view = self.firstScreenshot['View']
        date = self.firstScreenshot['Date']

        monkeypatch.setitem(self.screenshotProcess.imgs, 'tmp', dict())
        monkeypatch.setitem(self.screenshotProcess.imgs['tmp'], view, dict())
        monkeypatch.setitem(self.screenshotProcess.imgs, view, dict())
        monkeypatch.setitem(self.screenshotProcess.imgs['tmp'][view], date, dict())
        monkeypatch.setitem(self.screenshotProcess.imgs[view], date, dict())

        firstFunction = self.firstScreenshot['Function']
        monkeypatch.setitem(self.screenshotProcess.imgs['tmp'][view][date], firstFunction, self.tmpImg1)
        monkeypatch.setitem(self.screenshotProcess.imgs[view][date], firstFunction, self.img1)

        secondFunction = self.secondScreenshot['Function']
        monkeypatch.setitem(self.screenshotProcess.imgs['tmp'][view][date], secondFunction, self.tmpImg2)
        monkeypatch.setitem(self.screenshotProcess.imgs[view][date], secondFunction, self.img2)

        thirdFunction = self.thirdScreenshot['Function']
        monkeypatch.setitem(self.screenshotProcess.imgs['tmp'][view][date], thirdFunction, self.tmpImg3)
        monkeypatch.setitem(self.screenshotProcess.imgs[view][date], thirdFunction, self.img3)

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
        assert self.screenshotProcess.getDiff(originalLoc = self.nonExistentScreenLoc,
                                              modifiedLoc = self.firstScreenshot) is None

    def testGetDiffInvalidSecondLocation(self):
        assert self.screenshotProcess.getDiff(originalLoc = self.firstScreenshot,
                                              modifiedLoc = self.nonExistentScreenLoc) is None

    def testGetDiffReturnsValueWithLocation(self):
        assert self.screenshotProcess.getDiff(originalLoc = self.firstScreenshot,
                                              modifiedLoc = self.thirdScreenshot) is not None

    def testGetDiffWithSameScreenshots(self):
        self.screenshotProcess.img1 = self.first
        self.screenshotProcess.img2 = self.second
        assert self.screenshotProcess.getDiff() is None

    def testGetDiffReturnsValueWithoutLocation(self):
        self.screenshotProcess.img1 = self.first
        self.screenshotProcess.img2 = self.third
        diff = self.screenshotProcess.getDiff()
        # diff.show()
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
        # change.show()
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
        date = datetime.datetime.now().date().isoformat()
        diff = self.screenshotProcess.imgs[view][date]['newscreenshot3Diff.png']
        change = self.screenshotProcess.imgs[view][date]['newscreenshot3Change.png']
        assert diff is not None and change is not None
