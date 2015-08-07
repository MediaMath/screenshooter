from screenshooter.Differ import Differ
import screenshooter.config as config
from selenium.webdriver.common.keys import Keys
from PIL import Image
from datetime import datetime
import io
import time


class Capsule():
    """
    Capsule is a wrapper on selenium webdriver that allows certain actions to be taken
    and then take a screenshot following that action. These screenshots can later be used
    to create a diff image.
    """

    def __init__(self):
        self.differ = Differ()
        self.imgs = self.differ.imgs

    def getXPath(self, **kwargs):
        """
        Calculates the xpath for the first element specified on the current page from the key
        word arguments given.

        Args:
          kwargs: Key word arguments representing attributes of an element.

        Returns:
          The xpath for the first element.
        """
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
        """
        Take a screenshot of the current screen and stores it in the tmp dictionary of the
        multi-dimensional dictionary.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
        """
        today = datetime.now().date().isoformat()

        if 'tmp' not in self.imgs:
            self.imgs['tmp'] = dict()
        if view not in self.imgs['tmp']:
            self.imgs['tmp'][view] = dict()
        if today not in self.imgs['tmp'][view]:
            self.imgs['tmp'][view][today] = dict()

        self.imgs['tmp'][view][today][function + ".png"] = Image.open(io.BytesIO(driver.get_screenshot_as_png()))

    def getPage(self, driver, view, function, page, splash = False, ignoreSplash = True):
        """
        Route to a page then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          page: the url of the page to route to.
          splash: a boolean representing whether or not there is a splash screen,
            True means there is a splash screen (Defaults to False)
          ignoreSplash: a boolean representing whether or not to ignore the splash screen,
            True means ignore the splash screen (Defaults to True)
        """
        driver.get(page)
        if not splash:
            self.screenshot(driver, view, function)
            return
        elif not ignoreSplash:
            self.screenshot(driver, view, function)

        time.sleep(5)
        self.screenshot(driver, view, function)

    def scrollPage(self, driver, view, function):
        """
        Scroll the entire page, scrolling by viewable screen for each scroll. Take a screenshot after each scroll.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
        """
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
        """
        Click a button then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          iFrame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        xPath = self.getXPath(tag ='button', **kwargs)
        self.clickElement(driver, view, function, xPath, iFrame)

    def clickInputButton(self, driver, view, function, iFrame = None, **kwargs):
        """
        Click a submission button on an input form then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          iFrame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        xPath = self.getXPath(tag = "input[@type='submit']", **kwargs)
        self.clickElement(driver, view, function, xPath, iFrame)

    def clickHyperlink(self, driver, view, function, iFrame = None, **kwargs):
        """
        Click a hyperlink then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          iFrame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        xPath = self.getXPath(tag = "a", **kwargs)
        self.clickElement(driver, view, function, xPath, iFrame)

    def inputEnter(self, driver, view, function, inputText, iFrame = None, **kwargs):
        """
        Apply text to a text box on a submission form then press enter. Take a screenshot after
        pressing enter.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          inputText: the text that will be placed into the text box.
          iFrame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        xPath = self.getXPath(tag = "input[@type='text']", **kwargs)

        if iFrame:
            driver.switch_to.frame(iFrame)
        element = driver.find_element_by_xpath(xPath)
        element.clear()
        element.send_keys(inputText)
        self.enterElement(driver, view, function, element)

    def clickElement(self, driver, view, function, xPath, iFrame = None):
        """
        Click an element based on its xpath then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          xPath: the xpath of the first location of that element.
          iFrame: the name/id of the iframe that the element can be found in.
        """
        if iFrame:
            driver.switch_to.frame(iFrame)
        element = driver.find_element_by_xpath(xPath)
        element.click()
        self.screenshot(driver, view, function)

    def enterElement(self, driver, view, function, element):
        """
        Press the enter key on the element then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          element: the element to press enter on.
        """
        element.send_keys(Keys.ENTER)
        self.screenshot(driver, view, function)

    def generateDiffs(self, serviceName = config.service):
        """
        Generate the diffs of the images that have been placed in the multi-dimensional dictionary.

        Args:
          serviceName: the name of the service where images are stored.

        Returns:
          True if successful
        """
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
