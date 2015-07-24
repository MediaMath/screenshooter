import io
import os
import fnmatch
import screenshooter.config as config
from PIL import Image
import datetime
import shutil
import boto3 as boto


def removeNew(val):
    output = ""
    parsedVals = val.split("new")
    for parsedval in parsedVals:
        output += parsedval
    return output


class fsService():

    def __init__(self):
        pass

    def collectImages(self, baseDir, imgs = None):
        dictPics = imgs or dict()
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

        #this portion only grabs the images in the tmp directory - I don't think I need this (revisit)
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

    def save(self, imgs):
        if imgs is None:
            raise ("Can not save anything, the multi-dimensional dictionary is None")
        today = datetime.datetime.now().date().isoformat()
        try:
            for view in fnmatch.filter(imgs, "*View"):
                if not os.path.exists(os.path.join(config.baseImageDir, view)):
                    os.mkdir(os.path.join(config.baseImageDir, view))
                for day in fnmatch.filter(imgs[view], today + "*"):
                    if not os.path.exists(os.path.join(config.baseImageDir, view, day)):
                        os.mkdir(os.path.join(config.baseImageDir, view, day))
                    for function in fnmatch.filter(imgs[view][day], "new*"):
                        imgs[view][day][function].save(os.path.join(config.baseImageDir, view,
                                                                    day, removeNew(function)))
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


class s3Service():

    def __init__(self):
        self.boto = boto

    def parseOutBackslash(self, location):
        parsedString = location.split('/')
        return {'count': len(parsedString), 'array': parsedString}

    def concatInBackslash(self, *args):
        val = ""
        for arg in args:
            if "." not in arg:
                val += arg + "/"
            else:
                val += arg
        return val

    def collectImages(self, imgs = None):
        dictPics = imgs or dict()
        session = self.boto.session.Session(aws_access_key_id = config.accessKey, aws_secret_access_key = config.secretKey)
        s3 = session.client('s3')
        contents = s3.list_objects(Bucket = config.bucket)
        for content in contents['Contents']:
            if content['Size'] == 0:
                continue
            parsedKey = self.parseOutBackslash(content['Key'])['array']
            if len(parsedKey) != 3:
                continue
            view = parsedKey[0]
            date = parsedKey[1]
            function = parsedKey[2]
            data = s3.get_object(Bucket = config.bucket, Key = content['Key'])
            dataBytesIO = io.BytesIO(data['Body'].read())
            if view not in dictPics:
                dictPics[view] = dict()
            if date not in dictPics[view]:
                dictPics[view][date] = dict()
            dictPics[view][date][function] = Image.open(dataBytesIO)
        return dictPics

    def collectImg(self, imgs, tmpLoc):
        tmpView = tmpLoc['View']
        tmpFunction = tmpLoc['Function']

        session = self.boto.session.Session(aws_access_key_id = config.accessKey, aws_secret_access_key = config.secretKey)
        s3 = session.client('s3')

        loc = "{}/{}/{}/{}".format(config.envDir, config.baseDir, tmpView, tmpFunction)
        try:
            data = s3.get_object(Bucket = config.bucket, Key = loc)
        except ClientError:
            return None
        dataBytesIO = io.BytesIO(data['Body'].read())
        date = data['LastModified'].date().isoformat()
        if tmpView not in imgs:
            imgs[tmpView] = dict()
        if date not in imgs[tmpView]:
            imgs[tmpView][date] = dict()
        imgs[tmpView][date][tmpFunction] = Image.open(dataBytesIO)
        return {'View': tmpView, 'Date': date, 'Function': tmpFunction}

    def save(self, imgs):
        environmentDir = config.envDir
        baseDir = config.baseDir
        bucket = config.bucket
        saveToBase = config.baseStore
        if imgs is None:
            raise ("Can not save anything, the multi-dimensional dictionary is None")
        responses = list()
        count = 0
        session = self.boto.session.Session(aws_access_key_id = config.accessKey, aws_secret_access_key = config.secretKey)
        s3 = session.client('s3')
        today = datetime.datetime.now().date().isoformat()
        for view in imgs:
            if view == 'tmp':
                continue
            for day in fnmatch.filter(imgs[view], today + "*"):
                for function in fnmatch.filter(imgs[view][day], "new*"):
                    bytesImgIO = io.BytesIO()
                    imgs[view][day][function].save(bytesImgIO, "PNG")
                    bytesImgIO.seek(0)
                    bytesToSave = bytesImgIO.read()
                    responses.append(s3.put_object(Body = bytesToSave, Bucket = bucket,
                                                   Key = self.concatInBackslash(environmentDir, view, day, removeNew(function)), ContentType = "image/png"))
                    #check to make sure not diff or change
                    if "Diff" not in function and "Change" not in function and saveToBase:
                        responses.append(s3.put_object(Body = bytesToSave, Bucket = config.bucket,
                                                       Key = self.concatInBackslash(environmentDir, baseDir, view, removeNew(function)),
                                                       ContentType = "image/png"))
                    count += 1
        return {'count': count, 'responses': responses}
