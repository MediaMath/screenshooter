from screenshooter.differ import Differ
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

    def __init__(self, user_config = None):
        if user_config is None:
            import screenshooter.config as config
            self.config = config
        else:
            self.config = user_config
        self.differ = Differ(self.config)
        self.imgs = self.differ.imgs

    def get_x_path(self, **kwargs):
        """
        Calculates the xpath for the first element specified on the current page from the key
        word arguments given.

        Args:
          kwargs: Key word arguments representing attributes of an element.

        Returns:
          The xpath for the first element.
        """
        tag = kwargs.get("tag", None)
        class_tag = kwargs.get("class_tag", None)
        id_tag = kwargs.get("id_tag", None)
        value = kwargs.get("value", None)
        text = kwargs.get("text", None)
        name = kwargs.get("name", None)

        x_path = "//" + tag

        if class_tag:
            x_path += "[@class='" + class_tag + "']"
        if id_tag:
            x_path += "[@id='" + id_tag + "']"
        if value:
            x_path += "[@value='" + value + "']"
        if text:
            x_path += "[@text()='" + text + "']"
        if name:
            x_path += "[@name='" + name + "']"

        x_path += "[1]"
        return x_path

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

    def get_page(self, driver, view, function, page, splash = False, ignore_splash = True):
        """
        Route to a page then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          page: the url of the page to route to.
          splash: a boolean representing whether or not there is a splash screen,
            True means there is a splash screen (Defaults to False)
          ignore_splash: a boolean representing whether or not to ignore the splash screen,
            True means ignore the splash screen (Defaults to True)
        """
        driver.get(page)
        if not splash:
            self.screenshot(driver, view, function)
            return
        elif not ignore_splash:
            self.screenshot(driver, view, function)

        time.sleep(5)
        self.screenshot(driver, view, function)

    def scroll_page(self, driver, view, function):
        """
        Scroll the entire page, scrolling by viewable screen for each scroll. Take a screenshot after each scroll.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
        """
        height = driver.execute_script("return window.document.body.scrollHeight;")
        visible_height = driver.execute_script("return window.innerHeight;")
        move_height = visible_height
        i = 1
        while move_height < height:
            driver.execute_script("window.scrollTo(0, " + str(move_height) + ");")
            self.screenshot(driver, view, function + "[" + str(i) + "]")
            move_height += visible_height
            i += 1

    def click_button(self, driver, view, function, i_frame = None, **kwargs):
        """
        Click a button then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          i_frame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        x_path = self.get_x_path(tag ='button', **kwargs)
        self.click_element(driver, view, function, x_path, i_frame)

    def click_input_button(self, driver, view, function, i_frame = None, **kwargs):
        """
        Click a submission button on an input form then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          i_frame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        x_path = self.get_x_path(tag = "input[@type='submit']", **kwargs)
        self.click_element(driver, view, function, x_path, i_frame)

    def click_hyperlink(self, driver, view, function, i_frame = None, **kwargs):
        """
        Click a hyperlink then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          i_frame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        x_path = self.get_x_path(tag = "a", **kwargs)
        self.click_element(driver, view, function, x_path, i_frame)

    def input_enter(self, driver, view, function, input_text, i_frame = None, **kwargs):
        """
        Apply text to a text box on a submission form then press enter. Take a screenshot after
        pressing enter.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          input_text: the text that will be placed into the text box.
          i_frame: the name/id of the iframe that the element can be found in.
          kwargs: the key word arguments that can be used to locate the xpath.
        """
        x_path = self.get_x_path(tag = "input[@type='text']", **kwargs)

        if i_frame:
            driver.switch_to.frame(i_frame)
        element = driver.find_element_by_xpath(x_path)
        element.clear()
        element.send_keys(input_text)
        self.enter_element(driver, view, function, element)

    def click_element(self, driver, view, function, x_path, i_frame = None):
        """
        Click an element based on its xpath then take a screenshot.

        Args:
          driver: the driver used by selenium.
          view: the view that is being seen e.g. HomePageView.
          function: the name of the function that is calling the screenshot.
          x_path: the xpath of the first location of that element.
          i_frame: the name/id of the iframe that the element can be found in.
        """
        if i_frame:
            driver.switch_to.frame(i_frame)
        element = driver.find_element_by_xpath(x_path)
        element.click()
        self.screenshot(driver, view, function)

    def enter_element(self, driver, view, function, element):
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

    def generate_diffs(self, service_name = self.config.service):
        """
        Generate the diffs of the images that have been placed in the multi-dimensional dictionary.

        Args:
          service_name: the name of the service where images are stored.

        Returns:
          True if successful
        """
        if service_name.upper() == "S3":
            from screenshooter.saves import s3_service
            service = s3_service(self.config)
        elif service_name.upper() == "FILESYSTEM":
            from screenshooter.saves import fs_service
            service = fs_service(self.config)

        if self.config.collect_all_images:
            service.collect_images(self.config.image_path, self.differ.imgs)
        self.differ.run()
        service.save(self.differ.imgs)

        return True
