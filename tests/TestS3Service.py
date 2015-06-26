import pytest
from PIL import Image
import screenshooter.config as config
from screenshooter.saves import s3Service


class TestS3Service():

    def setup_method(self, method):
        self.s3 = s3Service()

    # @pytest.fixture()
    # def botoSetup(self):
    #     self.client = boto.client('s3')
    #
    # @pytest.fixture()
    # def noRequests(self, monkeypatch):
    #     monkeypatch.delattr("boto.client._make_api_call")

    def testParseOutBackslash(self):
        assert any("/" in val for val in self.s3.parseOutBackslash("something/with/slashes")['array']) == False

    def testParseInBackslash(self):
        values = "values"
        dictionary = "dictionary"
        some = "some"
        assert ("/" in self.s3.concatInBackslash(some, dictionary, values)) == True

    # @pytest.mark.usefixtures('botoSetup')
    def testCollectImagesFromS3(self, monkeypatch):
        # monkeypatch.setattr("boto3.s3.Client.list_objects", S3Stubs.stubObject)
        # monkeypatch.setattr(self.client, "get_object", S3Stubs.stubObjectData)
        # s3 = boto.client('s3')
        # s3.create_bucket(Bucket = config.bucket)
        # byteImg = Image.open(config.baseProjectDir + "imgs/screenshot1.png").tobytes
        # s3.put_object(Body = byteImg, Bucket = config.bucket, Key = "SomeView/today/screenshot1.png")
        monkeypatch.setattr(self.s3, 'boto', boto())
        assert self.s3.collectS3Images() is not None

    # @pytest.mark.usefixtures('botoSetup')
    # def testSaveImagesToS3(self, monkeypatch):
    #     result = self.s3.saveS3()
    #     assert result['count'] == len(result['responses'])  # <- this may not work if errors are reported in responses


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
        byteImg = Image.open(config.baseProjectDir + "imgs/screenshot1.png").tobytes()
        return {'Body': byteImg}
