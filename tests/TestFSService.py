import pytest
import os
import shutil
import datetime
import screenshooter.config as config
from screenshooter.saves import fsService
from PIL import Image
import time


def setup_module(module):
    imgsDir = config.projectPath + "tests/imgs/"
    screen1 = "screenshot1.png"
    screen2 = "screenshot2.png"
    screen3 = "screenshot3.png"

    savesPath = config.imagePath
    environmentDir = config.envDir
    baseDir = config.baseDir
    fullSavesPath = os.path.join(savesPath, environmentDir, baseDir, "SomeView")

    if not os.path.exists(os.path.join(savesPath, environmentDir)):
        os.mkdir(os.path.join(savesPath, environmentDir))
    if not os.path.exists(os.path.join(savesPath, environmentDir, baseDir)):
        os.mkdir(os.path.join(savesPath, environmentDir, baseDir))

    if not os.path.exists(fullSavesPath):
        os.mkdir(fullSavesPath)
    if not os.path.exists(os.path.join(fullSavesPath, screen1)):
        shutil.copy(imgsDir + screen1, fullSavesPath)
    if not os.path.exists(os.path.join(fullSavesPath, screen3)):
        shutil.copy(imgsDir + screen2, fullSavesPath)
        os.rename(os.path.join(fullSavesPath, screen2), os.path.join(fullSavesPath, screen3))
    if not os.path.exists(os.path.join(fullSavesPath, screen2)):
        shutil.copy(imgsDir + screen2, fullSavesPath)


def teardown_module(module):
    path = config.imagePath + config.envDir
    shutil.rmtree(path)


class TestFSService():

    nonExistentScreenLoc = "blah"

    def setup_method(self, method):
        self.today = datetime.datetime.now().date().isoformat()
        self.imgs = dict()
        self.imgs["tmp"] = dict()
        self.imgs["tmp"]["SomeView"] = dict()
        self.imgs["tmp"]["SomeView"][self.today] = dict()
        self.imgs["tmp"]["SomeView"][self.today]["screenshot1.png"] = Image.open(config.projectPath + "tests/imgs/screenshot1.png")
        self.imgs["tmp"]["SomeView"][self.today]["screenshot2.png"] = Image.open(config.projectPath + "tests/imgs/screenshot2.png")
        self.imgs["tmp"]["SomeView"][self.today]["screenshot3.png"] = Image.open(config.projectPath + "tests/imgs/screenshot3.png")

        self.fs = fsService()

    def testCollectFilesystemScreenshotsReturnsValue(self):
        assert self.imgs["tmp"]["SomeView"][self.today]["screenshot1.png"] is not None
        assert self.fs.collectImages(config.imagePath, self.imgs) is not None
        assert self.imgs["SomeView"][self.today]["screenshot1.png"] is not None

    def testCollectFilesystemScreenshotsFails(self):
        with pytest.raises(FileNotFoundError):
            self.fs.collectImages(self.nonExistentScreenLoc)

    def testSaveFS(self):
        pics = self.fs.collectImages(config.imagePath, self.imgs)
        pics["SomeView"][self.today]["newscreenshot1.png"] = pics["SomeView"][self.today]["screenshot1.png"]
        assert self.fs.save(pics) == True
        assert os.path.exists(os.path.join(config.imagePath, config.envDir, "SomeView", self.today, "screenshot1.png")) == True

    # keeping this in case refactor of cleanup happens
    # def testCleanupTmpDir(self):
    #     self.fs.cleanupFS()
    #     assert os.path.exists(config.imagePath + "tmp") == False

    def testCollectImage(self, monkeypatch):
        loc = {'View': "SomeView", "Date": self.today, "Function": "screenshot1.png"}
        assert self.fs.collectImg(self.imgs, loc) is not None
        assert self.imgs["SomeView"][self.today]["screenshot1.png"] is not None

        monkeypatch.delitem(self.imgs["SomeView"][self.today], "screenshot1.png", False)
        assert self.fs.collectImg(self.imgs, loc) is not None
        assert self.imgs["SomeView"][self.today]["screenshot1.png"] is not None
