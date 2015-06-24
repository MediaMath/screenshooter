import os
import fnmatch
import screenshooter.config as config
from PIL import Image
import datetime
import shutil


class fsService():

    def __init__(self):
        pass

    def collectFSImgs(self, baseDir):
        dictPics = dict()
        for dirView in fnmatch.filter(os.listdir(baseDir), "*View"):
            if os.path.isdir(os.path.join(baseDir, dirView)):
                screenshotsView = dict()
                for dirDate in fnmatch.filter(os.listdir(os.path.join(baseDir, dirView)), "*-*-*"):
                    if os.path.isdir(os.path.join(baseDir, dirView, dirDate)):
                        screenshotsDate = dict()
                        for filename in fnmatch.filter(os.listdir(os.path.join(baseDir,
                                                       dirView, dirDate)), "*" + config.pictureType):
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
                                                       "tmp", dirView, dirDate)), "*" + config.pictureType):
                            screenshotsDate[filename] = Image.open(os.path.join(baseDir,
                                                                   "tmp", dirView, dirDate, filename))
                screenshotsView[dirDate] = screenshotsDate
            screenshotsTemp[dirView] = screenshotsView
        dictPics['tmp'] = screenshotsTemp
        return dictPics

    def saveFS(self, imgs):
        if imgs is None:
            raise ("Can not save anything, the multi-dimensional dictionary is None")
        today = datetime.datetime.now().date().isoformat()
        try:
            for view in fnmatch.filter(imgs, "*View"):
                if not os.path.exists(os.path.join(config.baseImageDir, view)):
                    os.mkdir(os.path.join(config.baseImageDir, view))
                if not os.path.exists(os.path.join(config.baseImageDir, view, today)):
                    os.mkdir(os.path.join(config.baseImageDir, view, today))
                for function in imgs[view][today]:
                    imgs[view][today][function].save(os.path.join(config.baseImageDir, view,
                                                                  today, function))
            return True
        except (KeyError, IOError):
            return False

    def cleanupFS(self):
        try:
            path = config.baseImageDir + "tmp"
            shutil.rmtree(path)
        except IOError:
            return False
        return True
