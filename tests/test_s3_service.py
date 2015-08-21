import io
import pytest
import datetime
from PIL import Image
import screenshooter.config as config
import screenshooter.saves as saves


class TestS3Service():

    def setup_method(self, method):
        self.s3 = saves.s3_service()

    @pytest.fixture()
    def assign_images(self, monkeypatch):
        self.tmp_img_1 = Image.open(config.project_path + "tests/imgs/screenshot1.png")
        self.tmp_img_2 = Image.open(config.project_path + "tests/imgs/screenshot2.png")
        self.tmp_img_3 = Image.open(config.project_path + "tests/imgs/screenshot3.png")

        self.img1 = self.tmp_img_1
        self.img2 = self.tmp_img_1
        self.img3 = self.tmp_img_1

        self.imgs = dict()
        view = 'SomeView'
        self.date = datetime.datetime.now().date().isoformat()

        monkeypatch.setitem(self.imgs, 'tmp', dict())
        monkeypatch.setitem(self.imgs['tmp'], view, dict())
        monkeypatch.setitem(self.imgs, view, dict())
        monkeypatch.setitem(self.imgs['tmp'][view], self.date, dict())
        monkeypatch.setitem(self.imgs[view], self.date, dict())

        first_function = 'newscreenshot1.png'
        monkeypatch.setitem(self.imgs['tmp'][view][self.date], first_function, self.tmp_img_1)
        monkeypatch.setitem(self.imgs[view][self.date], first_function, self.img1)

        second_function = 'newscreenshot2.png'
        monkeypatch.setitem(self.imgs['tmp'][view][self.date], second_function, self.tmp_img_2)
        monkeypatch.setitem(self.imgs[view][self.date], second_function, self.img2)

        third_function = 'newscreenshot3.png'
        monkeypatch.setitem(self.imgs['tmp'][view][self.date], third_function, self.tmp_img_3)
        monkeypatch.setitem(self.imgs[view][self.date], third_function, self.img3)

    def test_parse_out_backslash(self):
        assert any("/" in val for val in self.s3.parse_out_backslash("something/with/slashes")['array']) == False

    def test_parse_in_backslash(self):
        values = "values"
        dictionary = "dictionary"
        some = "some"
        assert ("/" in self.s3.concat_in_backslash(some, dictionary, values)) == True

    def test_remove_new(self):
        val = "new_phrase"
        assert saves.remove_new(val) == "phrase"

    def test_collect_images_from_s3(self, monkeypatch):
        monkeypatch.setattr(self.s3, 'boto', boto())
        assert self.s3.collect_images() is not None

    def test_save_images_to_s3(self, monkeypatch, assign_images):
        monkeypatch.setattr(self.s3, 'boto', boto())
        result = self.s3.save(self.imgs)
        assert result['count'] == len(result['responses'])

    #Add test for collect_img
    def test_collect_image(self, monkeypatch, assign_images):
        monkeypatch.setattr(self.s3, 'boto', boto())
        loc = {'View': "SomeView", "Date": self.date, "Function": 'screenshot1.png'}
        assert self.s3.collect_img(self.imgs, loc) == loc


# Mock / Stub of Boto -> S3 in order to run methods for testing
class boto():

    def __init__(self):
        pass

    def client(self, arg):
        return s3()

    class session():
        class Session():
            def __init__(self, **kwargs):
                pass

            def client(self, *args):
                return s3()


class s3():

    def __init__(self):
        pass

    def list_objects(self, **kwargs):
        return{'Contents': [{'Key': "SomeView/today/screenshot1.png", 'Size': 1}]}

    def get_object(self, **kwargs):
        bytes_img_io = io.BytesIO()
        byte_img = Image.open(config.project_path + "tests/imgs/screenshot1.png")
        byte_img.save(bytes_img_io, "PNG")
        bytes_img_io.seek(0)
        return {'Body': bytes_img_io, 'LastModified': datetime.datetime.now()}

    def put_object(self, **kwargs):
        return {"Doesn't": "matter"}
