import screenshooter.config as config
import pytest
import datetime
from datetime import timedelta
from PIL import Image
from PIL import ImageChops
from screenshooter.differ import Differ
import time


class TestDiffer:

    skip = pytest.mark.skipif(False, reason = "I said skip")

    non_existent_screen_loc = "blah"

    @classmethod
    def setup_class(cls):
        cls.tmp_img_1 = Image.open(config.project_path + "tests/imgs/screenshot1.png")
        cls.tmp_img_2 = Image.open(config.project_path + "tests/imgs/screenshot2.png")
        cls.tmp_img_3 = Image.open(config.project_path + "tests/imgs/screenshot3.png")

        cls.img1 = cls.tmp_img_1
        cls.img2 = cls.tmp_img_1
        cls.img3 = cls.tmp_img_1

    def setup_method(self, method):
        yesterday = datetime.datetime.now() - timedelta(days = 1)
        self.screenshot_process = Differ()
        self.first_screenshot = {'View': 'SomeView', 'Date': yesterday.date().isoformat(), 'Function': 'screenshot1.png'}
        self.second_screenshot = {'View': 'SomeView', 'Date': yesterday.date().isoformat(), 'Function': 'screenshot2.png'}
        self.third_screenshot = {'View': 'SomeView', 'Date': yesterday.date().isoformat(), 'Function': 'screenshot3.png'}

        self.first = self.tmp_img_1
        self.second = self.tmp_img_2
        self.third = self.tmp_img_3

    #
    # @classmethod
    # def teardown_class(cls):
    #     return
    #

    # Stub out the multi-dimensional dictionary so it isn't reliant on where it obtains the information from
    @pytest.fixture(autouse = True)
    def assign_images(self, monkeypatch):
        view = self.first_screenshot['View']
        date = self.first_screenshot['Date']

        monkeypatch.setitem(self.screenshot_process.imgs, 'tmp', dict())
        monkeypatch.setitem(self.screenshot_process.imgs['tmp'], view, dict())
        monkeypatch.setitem(self.screenshot_process.imgs, view, dict())
        monkeypatch.setitem(self.screenshot_process.imgs['tmp'][view], date, dict())
        monkeypatch.setitem(self.screenshot_process.imgs[view], date, dict())

        first_function = self.first_screenshot['Function']
        monkeypatch.setitem(self.screenshot_process.imgs['tmp'][view][date], first_function, self.tmp_img_1)
        monkeypatch.setitem(self.screenshot_process.imgs[view][date], first_function, self.img1)

        second_function = self.second_screenshot['Function']
        monkeypatch.setitem(self.screenshot_process.imgs['tmp'][view][date], second_function, self.tmp_img_2)
        monkeypatch.setitem(self.screenshot_process.imgs[view][date], second_function, self.img2)

        third_function = self.third_screenshot['Function']
        monkeypatch.setitem(self.screenshot_process.imgs['tmp'][view][date], third_function, self.tmp_img_3)
        monkeypatch.setitem(self.screenshot_process.imgs[view][date], third_function, self.img3)

    @skip
    def test_screenshot_comparison_equals(self):
        assert self.screenshot_process.equals(self.first, self.second) == True

    @skip
    def test_screenshot_comparison_not_equal(self):
        assert self.screenshot_process.equals(self.first, self.third) == False

    @skip
    def test_screenshot_store(self):
        assert self.screenshot_process.store(self.first_screenshot) == True

    @skip
    def test_screenshot_void_parameters_store(self):
        assert self.screenshot_process.store() == False

    @skip
    def test_screenshot_invalid_parameters_store(self):
        with pytest.raises(TypeError):
            self.screenshot_process.store(self.non_existent_screen_loc)

    @skip
    def test_get_diff_void_parameters(self):
        self.screenshot_process.original_img = None
        self.screenshot_process.modified_img = None
        with pytest.raises(UnboundLocalError):
            self.screenshot_process.get_diff()

    @skip
    def test_get_diff_invalid_first_location(self):
        assert self.screenshot_process.get_diff(original_loc = self.non_existent_screen_loc,
                                              modified_loc = self.first_screenshot) is None

    @skip
    def test_get_diff_invalid_second_location(self):
        assert self.screenshot_process.get_diff(original_loc = self.first_screenshot,
                                              modified_loc = self.non_existent_screen_loc) is None

    @skip
    def test_get_diff_returns_value_with_location(self):
        assert self.screenshot_process.get_diff(original_loc = self.first_screenshot,
                                              modified_loc = self.third_screenshot) is not None

    @skip
    def test_get_diff_with_same_screenshots(self):
        self.screenshot_process.original_img = self.first
        self.screenshot_process.modified_img = self.second
        assert self.screenshot_process.get_diff() is None

    @skip
    def test_get_diff_returns_value_without_location(self):
        self.screenshot_process.diff = ImageChops.difference(self.first, self.third)
        self.screenshot_process.original_img = self.first
        self.screenshot_process.modified_img = self.third
        diff = self.screenshot_process.get_diff()
        # diff.show()
        assert diff is not None

    @skip
    def test_get_change_void_parameters(self):
        self.screenshot_process.original_img = None
        self.screenshot_process.modified_img = None
        with pytest.raises(UnboundLocalError):
            self.screenshot_process.get_change()

    @skip
    def test_get_change_invalid_first_location(self):
        assert self.screenshot_process.get_change(original_loc = self.non_existent_screen_loc,
                                                modified_loc = self.first_screenshot) is None

    @skip
    def test_get_change_invalid_second_location(self):
        assert self.screenshot_process.get_change(original_loc = self.first_screenshot,
                                                modified_loc = self.non_existent_screen_loc) is None

    @skip
    def test_get_change_returns_value_with_location(self):
        assert self.screenshot_process.get_change(original_loc = self.first_screenshot,
                                                modified_loc = self.third_screenshot) is not None

    @skip
    def test_get_change_returns_value_without_location(self):
        self.screenshot_process.diff = ImageChops.difference(self.first, self.third)
        self.screenshot_process.original_img = self.first
        self.screenshot_process.modified_img = self.third
        change = self.screenshot_process.get_change()
        # change.show()
        assert change is not None

    @skip
    def test_get_change_with_same_screenshots(self):
        self.screenshot_process.original_img = self.first
        self.screenshot_process.modified_img = self.second
        assert self.screenshot_process.get_change() is None

    # @skip
    # def test_run(self):
    #     self.screenshot_process.run()
    #     view = self.third_screenshot['View']
    #     date = (datetime.datetime.now() - timedelta(days = 1)).date().isoformat()
    #     diff = self.screenshot_process.imgs[view][date]['newscreenshot3_diff.png']
    #     change = self.screenshot_process.imgs[view][date]['newscreenshot3_change.png']
    #     assert diff is not None and change is not None
