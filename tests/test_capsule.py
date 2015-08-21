from screenshooter.capsule import Capsule
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import pytest
import time


class TestCapsule():

    skip = pytest.mark.skipif(False, reason = "I said skip")

    def setup_method(self, method):
        self.capsule = Capsule()
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1280, 720)
        self.today = datetime.now().date().isoformat()

    def teardown_method(self, method):
        self.driver.quit()

    @skip
    def test_screenshot(self):
        self.driver.get("http://google.com")
        self.capsule.screenshot(self.driver, "SomeView", "SomeFunction")
        assert self.capsule.imgs['tmp']["SomeView"][self.today]["SomeFunction.png"] is not None

    @skip
    def test_get_page(self):
        self.capsule.get_page(self.driver, "HomePageView", "get_home_page", "http://google.com")
        assert self.capsule.imgs['tmp']["HomePageView"][self.today]["get_home_page.png"] is not None

    @skip
    def test_scroll_page(self):
        self.driver.get("http://pytest.org")
        self.capsule.scroll_page(self.driver, "HomePageView", "get_home_page")
        i = 1
        while(True):
            try:
                self.capsule.imgs['tmp']["HomePageView"][self.today]["get_home_page[" + str(i) + "].png"]
            except KeyError:
                break
            i += 1
        assert (i - 1) > 0

    @skip
    def test_click_button(self):
        self.driver.get("https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button")
        self.capsule.click_button(self.driver, "ButtonTestView", "button_test", class_tag = "only-icon", id_tag = "advanced-menu")
        #self.capsule.imgs['tmp']["ButtonTestView"][self.today]["button_test.png"].show()
        assert self.capsule.imgs['tmp']["ButtonTestView"][self.today]["button_test.png"] is not None

    @skip
    def test_click_input_button_with_i_frame_name(self):
        self.driver.get("http://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit")
        self.capsule.click_input_button(self.driver, "ButtonTestView", "input_button_test", "view", value = "Submit")
        assert self.capsule.imgs['tmp']["ButtonTestView"][self.today]["input_button_test.png"] is not None

    @skip
    def test_click_input_button_with_i_frame_id(self):
        self.driver.get("http://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit")
        self.capsule.click_input_button(self.driver, "ButtonTestView", "input_button_test", "iframeResult", value = "Submit")
        assert self.capsule.imgs['tmp']["ButtonTestView"][self.today]["input_button_test.png"] is not None

    @skip
    def test_click_hyperlink(self):
        self.driver.get("http://pytest.org")
        self.capsule.click_hyperlink(self.driver, "HyperlinkTestView", "hyperlink_test", class_tag = "reference internal")
        assert self.capsule.imgs['tmp']["HyperlinkTestView"][self.today]["hyperlink_test.png"] is not None and \
            self.driver.current_url == "http://pytest.org/latest/contents.html#toc"

    @skip
    def test_input_with_enter_key_pressed(self):
        self.driver.get("http://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit")
        self.capsule.input_enter(self.driver, "input_test_view", "input_submission_test", "Bobby", "view", name = "FirstName")
        # self.capsule.imgs['tmp']["input_test_view"][self.today]["input_submission_test.png"].show()
        assert self.capsule.imgs['tmp']["input_test_view"][self.today]["input_submission_test.png"] is not None

    # @skip  #comment this function out since it will make a call to s3 (not a real unit test, more of a functional test)
    # def test_generate_diffs(self):
    #     self.driver.get("http://google.com")
    #     self.capsule.screenshot(self.driver, "HompageView", "GenerateDiffsTest")
    #     assert self.capsule.generate_diffs("S3") == True
