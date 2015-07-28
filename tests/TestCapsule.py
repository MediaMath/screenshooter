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
    def testScreenshot(self):
        self.driver.get("http://google.com")
        self.capsule.screenshot(self.driver, "SomeView", "SomeFunction")
        assert self.capsule.imgs['tmp']["SomeView"][self.today]["SomeFunction.png"] is not None

    @skip
    def testGetPage(self):
        self.capsule.getPage(self.driver, "HomePageView", "getHomePage", "http://google.com")
        assert self.capsule.imgs['tmp']["HomePageView"][self.today]["getHomePage.png"] is not None

    @skip
    def testScrollPage(self):
        self.driver.get("http://pytest.org")
        self.capsule.scrollPage(self.driver, "HomePageView", "getHomePage")
        i = 1
        while(True):
            try:
                self.capsule.imgs['tmp']["HomePageView"][self.today]["getHomePage[" + str(i) + "].png"]
            except KeyError:
                break
            i += 1
        assert (i - 1) > 0

    @skip
    def testClickButton(self):
        self.driver.get("https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button")
        self.capsule.clickButton(self.driver, "ButtonTestView", "buttonTest", classTag = "only-icon", idTag = "advanced-menu")
        #self.capsule.imgs['tmp']["ButtonTestView"][self.today]["buttonTest.png"].show()
        assert self.capsule.imgs['tmp']["ButtonTestView"][self.today]["buttonTest.png"] is not None

    @skip
    def testClickInputButtonWithIFrameName(self):
        self.driver.get("http://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit")
        self.capsule.clickInputButton(self.driver, "ButtonTestView", "inputButtonTest", "view", value = "Submit")
        assert self.capsule.imgs['tmp']["ButtonTestView"][self.today]["inputButtonTest.png"] is not None

    @skip
    def testClickInputButtonWithIFrameID(self):
        self.driver.get("http://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit")
        self.capsule.clickInputButton(self.driver, "ButtonTestView", "inputButtonTest", "iframeResult", value = "Submit")
        assert self.capsule.imgs['tmp']["ButtonTestView"][self.today]["inputButtonTest.png"] is not None

    @skip
    def testClickHyperlink(self):
        self.driver.get("http://pytest.org")
        self.capsule.clickHyperlink(self.driver, "HyperlinkTestView", "hyperlinkTest", classTag = "reference internal")
        assert self.capsule.imgs['tmp']["HyperlinkTestView"][self.today]["hyperlinkTest.png"] is not None and \
            self.driver.current_url == "http://pytest.org/latest/contents.html#toc"

    @skip
    def testInputWithEnterKeyPressed(self):
        self.driver.get("http://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit")
        self.capsule.inputEnter(self.driver, "inputTestView", "inputSubmissionTest", "Bobby", "view", name = "FirstName")
        # self.capsule.imgs['tmp']["inputTestView"][self.today]["inputSubmissionTest.png"].show()
        assert self.capsule.imgs['tmp']["inputTestView"][self.today]["inputSubmissionTest.png"] is not None

    # @skip
    # def testGenerateDiffs(self):
    #     self.driver.get("http://google.com")
    #     self.capsule.screenshot(self.driver, "HompageView", "GenerateDiffsTest")
    #     assert self.capsule.generateDiffs("S3") == True
