import pytest
import os
import shutil
import datetime
import screenshooter.config as config
from screenshooter.saves import fsService
from screenshooter.Differ import Differ


def setup_module(module):
    path = config.baseImageDir + "tmp"
    today = datetime.datetime.now().date().isoformat()
    imgsDir = config.baseProjectDir + "tests/imgs/"
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


class TestFSService():

    nonExistentScreenLoc = "blah"
    directoryLocationOfScreenshots = config.baseImageDir

    def setup_method(self, method):
        self.screenshotProcess = Differ()
        self.fs = fsService()

    def testCollectFilesystemScreenshotsReturnsValue(self):
        assert self.fs.collectImages(self.directoryLocationOfScreenshots) is not None

    def testCollectFilesystemScreenshotsFails(self):
        with pytest.raises(FileNotFoundError):
            self.fs.collectImages(self.nonExistentScreenLoc)

    def testSaveFS(self):
        imgs = self.fs.collectImages(self.directoryLocationOfScreenshots)
        assert self.fs.save(imgs) == True

    def testCleanupTmpDir(self):
        self.fs.cleanupFS()
        assert os.path.exists(self.directoryLocationOfScreenshots + "tmp") == False
