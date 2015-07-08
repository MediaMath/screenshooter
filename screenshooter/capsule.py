from screenshooter.Screenshot import Screenshot
from selenium.webdriver.common.keys import Keys
from PIL import Image
from datetime import datetime
import io
import time


class Capsule():
    def __init__(self):
        self.differ = Screenshot()
        self.imgs = self.differ.imgs

    def getXPath(self, **kwargs):
        tag = kwargs.get("tag", None)
        classTag = kwargs.get("classTag", None)
        idTag = kwargs.get("idTag", None)
        value = kwargs.get("value", None)
        text = kwargs.get("text", None)
        name = kwargs.get("name", None)

        xPath = "//" + tag

        if classTag:
            xPath += "[@class='" + classTag + "']"
        if idTag:
            xPath += "[@id='" + idTag + "']"
        if value:
            xPath += "[@value='" + value + "']"
        if text:
            xPath += "[@text()='" + text + "']"
        if name:
            xPath += "[@name='" + name + "']"

        xPath += "[1]"
        return xPath

    def screenshot(self, driver, view, function):
        today = datetime.now().date().isoformat()

        if 'tmp' not in self.imgs:
            self.imgs['tmp'] = dict()
        if view not in self.imgs['tmp']:
            self.imgs['tmp'][view] = dict()
        if today not in self.imgs['tmp'][view]:
            self.imgs['tmp'][view][today] = dict()

        self.imgs['tmp'][view][today][function + ".png"] = Image.open(io.BytesIO(driver.get_screenshot_as_png()))

    def getPage(self, driver, view, function, page, splash = False, ignoreSplash = True):
        driver.get(page)
        if not splash:
            self.screenshot(driver, view, function)
            return
        elif not ignoreSplash:
            self.screenshot(driver, view, function)

        time.sleep(5)
        self.screenshot(driver, view, function)

    def scrollPage(self, driver, view, function):
        height = driver.execute_script("return window.document.body.scrollHeight;")
        visibleHeight = driver.execute_script("return window.innerHeight;")
        moveHeight = visibleHeight
        i = 1
        while moveHeight < height:
            driver.execute_script("window.scrollTo(0, " + moveHeight + ");")
            self.screenshot(driver, view, function + "[" + i + "]")
            moveHeight += visibleHeight
            i += 1

    def clickButton(self, driver, view, function, classTag = None, idTag = None):
        xPath = self.getXPath(tag ='button', classTag = classTag, idTag = idTag)
        self.clickElement(driver, view, function, xPath)

    def clickInputButton(self, driver, view, function, classTag = None, idTag = None, value = None):
        xPath = self.getXPath(tag = "input[@type = 'submit']", classTag = classTag, idTag = idTag, value = value)
        self.clickElement(driver, view, function, xPath)

    def clickHyperlink(self, driver, view, function, **kwargs):
        xPath = self.getXPath(tag = "a", **kwargs)
        self.clickElement(driver, view, function, xPath)

    def inputEnter(self, driver, view, function, inputText, **kwargs):
        xPath = self.getXPath(tag = "input[@type='text']", **kwargs)

        element = driver.find_element_by_xpath(xPath)
        element.send_keys(inputText)
        self.enterElement(driver, view, function, element)

    def clickElement(self, driver, view, function, xPath):
        element = driver.find_element_by_xpath(xPath)
        element.click()
        self.screenshot(driver, view, function)

    def enterElement(self, driver, view, function, element):
        element.key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
        self.screenshot(driver, view, function)
