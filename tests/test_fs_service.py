import pytest
import os
import shutil
import datetime
import screenshooter.config as config
from screenshooter.saves import fs_service
from PIL import Image
import time


def setup_module(module):
    imgs_dir = config.project_path + "tests/imgs/"
    screen1 = "screenshot1.png"
    screen2 = "screenshot2.png"
    screen3 = "screenshot3.png"

    saves_path = config.image_path
    environment_dir = config.env_dir
    base_dir = config.base_dir
    full_saves_path = os.path.join(saves_path, environment_dir, base_dir, "SomeView")

    if not os.path.exists(os.path.join(saves_path, environment_dir)):
        os.mkdir(os.path.join(saves_path, environment_dir))
    if not os.path.exists(os.path.join(saves_path, environment_dir, base_dir)):
        os.mkdir(os.path.join(saves_path, environment_dir, base_dir))

    if not os.path.exists(full_saves_path):
        os.mkdir(full_saves_path)
    if not os.path.exists(os.path.join(full_saves_path, screen1)):
        shutil.copy(imgs_dir + screen1, full_saves_path)
    if not os.path.exists(os.path.join(full_saves_path, screen3)):
        shutil.copy(imgs_dir + screen2, full_saves_path)
        os.rename(os.path.join(full_saves_path, screen2), os.path.join(full_saves_path, screen3))
    if not os.path.exists(os.path.join(full_saves_path, screen2)):
        shutil.copy(imgs_dir + screen2, full_saves_path)


def teardown_module(module):
    path = config.image_path + config.env_dir
    shutil.rmtree(path)


class TestFSService():

    non_existent_screen_loc = "blah"

    def setup_method(self, method):
        self.today = datetime.datetime.now().date().isoformat()
        self.imgs = dict()
        self.imgs["tmp"] = dict()
        self.imgs["tmp"]["SomeView"] = dict()
        self.imgs["tmp"]["SomeView"][self.today] = dict()
        self.imgs["tmp"]["SomeView"][self.today]["screenshot1.png"] = Image.open(config.project_path + "tests/imgs/screenshot1.png")
        self.imgs["tmp"]["SomeView"][self.today]["screenshot2.png"] = Image.open(config.project_path + "tests/imgs/screenshot2.png")
        self.imgs["tmp"]["SomeView"][self.today]["screenshot3.png"] = Image.open(config.project_path + "tests/imgs/screenshot3.png")

        self.fs = fs_service()

    def test_collect_filesystem_screenshots_returns_value(self):
        assert self.imgs["tmp"]["SomeView"][self.today]["screenshot1.png"] is not None
        assert self.fs.collect_images(config.image_path, self.imgs) is not None
        assert self.imgs["SomeView"][self.today]["screenshot1.png"] is not None

    def test_collect_filesystem_screenshots_fails(self):
        with pytest.raises(FileNotFoundError):
            self.fs.collect_images(self.non_existent_screen_loc)

    def test_save_fs(self):
        pics = self.fs.collect_images(config.image_path, self.imgs)
        pics["SomeView"][self.today]["newscreenshot1.png"] = pics["SomeView"][self.today]["screenshot1.png"]
        assert self.fs.save(pics) == True
        assert os.path.exists(os.path.join(config.image_path, config.env_dir, "SomeView", self.today, "screenshot1.png")) == True

    # keeping this in case refactor of cleanup happens
    # def test_cleanup_tmp_dir(self):
    #     self.fs.cleanupfs()
    #     assert os.path.exists(config.image_path + "tmp") == False

    def test_collect_image(self, monkeypatch):
        loc = {'View': "SomeView", "Date": self.today, "Function": "screenshot1.png"}
        assert self.fs.collect_img(self.imgs, loc) is not None
        assert self.imgs["SomeView"][self.today]["screenshot1.png"] is not None

        monkeypatch.delitem(self.imgs["SomeView"][self.today], "screenshot1.png", False)
        assert self.fs.collect_img(self.imgs, loc) is not None
        assert self.imgs["SomeView"][self.today]["screenshot1.png"] is not None
