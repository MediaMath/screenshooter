from screenshooter.Differ import Differ
from selenium.webdriver.common.keys import Keys
from PIL import Image
from datetime import datetime
import io
import time


class Capsule():
    def __init__(self):
        self.differ = Differ()
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
            driver.execute_script("window.scrollTo(0, " + str(moveHeight) + ");")
            self.screenshot(driver, view, function + "[" + str(i) + "]")
            moveHeight += visibleHeight
            i += 1

    def clickButton(self, driver, view, function, iFrame = None, **kwargs):
        xPath = self.getXPath(tag ='button', **kwargs)
        self.clickElement(driver, view, function, xPath, iFrame)

    def clickInputButton(self, driver, view, function, iFrame = None, **kwargs):
        xPath = self.getXPath(tag = "input[@type='submit']", **kwargs)
        self.clickElement(driver, view, function, xPath, iFrame)

    def clickHyperlink(self, driver, view, function, iFrame = None, **kwargs):
        xPath = self.getXPath(tag = "a", **kwargs)
        self.clickElement(driver, view, function, xPath, iFrame)

    def inputEnter(self, driver, view, function, inputText, iFrame = None, **kwargs):
        xPath = self.getXPath(tag = "input[@type='text']", **kwargs)

        if iFrame:
            driver.switch_to.frame(iFrame)
        element = driver.find_element_by_xpath(xPath)
        element.clear()
        element.send_keys(inputText)
        self.enterElement(driver, view, function, element)

    def clickElement(self, driver, view, function, xPath, iFrame = None):
        if iFrame:
            driver.switch_to.frame(iFrame)
        element = driver.find_element_by_xpath(xPath)
        element.click()
        self.screenshot(driver, view, function)

    def enterElement(self, driver, view, function, element):
        element.send_keys(Keys.ENTER)
        self.screenshot(driver, view, function)

    def generateDiffs(self, serviceName):
        if serviceName.upper() == "S3":
            from screenshooter.saves import s3Service
            service = s3Service()
        elif serviceName.upper() == "FILESYSTEM":
            from screenshooter.saves import fsService
            service = fsService()

        service.collectImages(self.differ.imgs)
        self.differ.run()
        service.save(self.differ.imgs)

        return True
