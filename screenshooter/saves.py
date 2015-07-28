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

        previousPath = os.path.join(baseDir, config.envDir, config.baseDir)
        for dirView in fnmatch.filter(os.listdir(previousPath), "*View"):

            previousPath = os.path.join(previousPath, dirView)
            if os.path.isdir(previousPath):
                if dirView not in dictPics:
                    dictPics[dirView] = dict()

                for filename in fnmatch.filter(os.listdir(previousPath), "*" + config.pictureType):
                    path = os.path.join(previousPath, filename)
                    modTime = os.stat(path).st_mtime
                    date = datetime.datetime.fromtimestamp(modTime).date().isoformat()

                    if date not in dictPics[dirView]:
                        dictPics[dirView][date] = dict()

                    dictPics[dirView][date][filename] = Image.open(os.path.join(path))

        return dictPics

    def collectImg(self, imgs, tmpLoc):
        tmpView = tmpLoc['View']
        tmpDate = tmpLoc['Date']
        tmpFunction = tmpLoc['Function']

        if tmpView in imgs:
            if tmpDate in imgs[tmpView]:
                if tmpFunction in imgs[tmpView][tmpDate]:
                    tmp = imgs[tmpView][tmpDate][tmpFunction]
                    if tmp:
                        return tmpLoc
                    return None

        path = os.path.join(config.imagePath, config.envDir, config.baseDir, tmpView, tmpFunction)
        modTime = os.stat(path).st_mtime
        date = datetime.datetime.fromtimestamp(modTime).date().isoformat()
        if tmpView not in imgs:
            imgs[tmpView] = dict()
        if date not in imgs[tmpView]:
            imgs[tmpView][date] = dict()
        imgs[tmpView][date][tmpFunction] = Image.open(path)
        return {'View': tmpView, 'Date': date, 'Function': tmpFunction}

    def save(self, imgs):
        if imgs is None:
            raise ("Can not save anything, the multi-dimensional dictionary is None")
        today = datetime.datetime.now().date().isoformat()
        saveToBase = config.baseStore
        basePath = os.path.join(config.imagePath, config.envDir)
        baseDir = config.baseDir
        try:
            if not os.path.exists(basePath):
                os.mkdir(basePath)
            if not os.path.exists(os.path.join(basePath, baseDir)):
                os.mkdir(os.path.join(basePath, baseDir))
            for view in fnmatch.filter(imgs, "*View"):
                if not os.path.exists(os.path.join(basePath, view)):
                    os.mkdir(os.path.join(basePath, view))
                if not os.path.exists(os.path.join(basePath, baseDir, view)):
                    os.mkdir(os.path.join(basePath, baseDir, view))
                for day in fnmatch.filter(imgs[view], today + "*"):
                    if not os.path.exists(os.path.join(basePath, view, day)):
                        os.mkdir(os.path.join(basePath, view, day))
                    for function in fnmatch.filter(imgs[view][day], "new*"):
                        imgs[view][day][function].save(os.path.join(basePath, view,
                                                                    day, removeNew(function)))
                        if ("Diff" not in function or "Change" not in function) and saveToBase:
                            imgs[view][day][function].save(os.path.join(basePath, baseDir, view, removeNew(function)))
            return True
        except (KeyError, IOError):
            return False

    #This is no longer useful, could refactor to eliminate files past a default archive date
    def cleanupFS(self):
        try:
            path = config.imagePath + "tmp"
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
                    if ("Diff" not in function and "Change" not in function) and saveToBase:
                        responses.append(s3.put_object(Body = bytesToSave, Bucket = config.bucket,
                                                       Key = self.concatInBackslash(environmentDir, baseDir, view, removeNew(function)),
                                                       ContentType = "image/png"))
                        count += 1
                    count += 1
        return {'count': count, 'responses': responses}
