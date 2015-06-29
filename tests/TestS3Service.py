import io
import pytest
import datetime
from PIL import Image
import screenshooter.config as config
from screenshooter.saves import s3Service


class TestS3Service():

    def setup_method(self, method):
        self.s3 = s3Service()

    @pytest.fixture()
    def assignImages(self, monkeypatch):
        self.tmpImg1 = Image.open(config.baseProjectDir + "imgs/screenshot1.png")
        self.tmpImg2 = Image.open(config.baseProjectDir + "imgs/screenshot2.png")
        self.tmpImg3 = Image.open(config.baseProjectDir + "imgs/screenshot3.png")

        self.img1 = Image.open(config.baseProjectDir + "imgs/screenshot1.png")
        self.img2 = Image.open(config.baseProjectDir + "imgs/screenshot1.png")
        self.img3 = Image.open(config.baseProjectDir + "imgs/screenshot1.png")

        self.imgs = dict()
        view = 'SomeView'
        date = datetime.datetime.now().date().isoformat()

        monkeypatch.setitem(self.imgs, 'tmp', dict())
        monkeypatch.setitem(self.imgs['tmp'], view, dict())
        monkeypatch.setitem(self.imgs, view, dict())
        monkeypatch.setitem(self.imgs['tmp'][view], date, dict())
        monkeypatch.setitem(self.imgs[view], date, dict())

        firstFunction = 'newscreenshot1.png'
        monkeypatch.setitem(self.imgs['tmp'][view][date], firstFunction, self.tmpImg1)
        monkeypatch.setitem(self.imgs[view][date], firstFunction, self.img1)

        secondFunction = 'newscreenshot2.png'
        monkeypatch.setitem(self.imgs['tmp'][view][date], secondFunction, self.tmpImg2)
        monkeypatch.setitem(self.imgs[view][date], secondFunction, self.img2)

        thirdFunction = 'newscreenshot3.png'
        monkeypatch.setitem(self.imgs['tmp'][view][date], thirdFunction, self.tmpImg3)
        monkeypatch.setitem(self.imgs[view][date], thirdFunction, self.img3)

    def testParseOutBackslash(self):
        assert any("/" in val for val in self.s3.parseOutBackslash("something/with/slashes")['array']) == False

    def testParseInBackslash(self):
        values = "values"
        dictionary = "dictionary"
        some = "some"
        assert ("/" in self.s3.concatInBackslash(some, dictionary, values)) == True

    def testRemoveNew(self):
        val = "newPhrase"
        assert self.s3.removeNew(val) == "Phrase"

    def testCollectImagesFromS3(self, monkeypatch):
        monkeypatch.setattr(self.s3, 'boto', boto())
        assert self.s3.collectS3Images() is not None

    def testSaveImagesToS3(self, monkeypatch, assignImages):
        monkeypatch.setattr(self.s3, 'boto', boto())
        result = self.s3.saveS3(self.imgs)
        assert result['count'] == len(result['responses'])


# Mock / Stub of Boto -> S3 in order to run methods for testing
class boto():

    def __init__(self):
        pass

    def client(self, arg):
        return s3()


class s3():

    def __init__(self):
        pass

    def list_objects(self, **kwargs):
        return{'Contents': [{'Key': "SomeView/today/screenshot1.png"}]}

    def get_object(self, **kwargs):
        bytesImgIO = io.BytesIO()
        byteImg = Image.open(config.baseProjectDir + "imgs/screenshot1.png")
        byteImg.save(bytesImgIO, "PNG")
        bytesImgIO.seek(0)
        return {'Body': bytesImgIO.read()}

    def put_object(self, **kwargs):
        return {"Doesn't": "matter"}
