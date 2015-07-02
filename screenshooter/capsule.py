from screenshooter.Screenshot import Screenshot
from PIL import Image
from datetime import datetime
import io
import time


class Capsule():
    def __init__(self):
        self.differ = Screenshot()
        self.imgs = self.differ.imgs

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

    def scrollPage(self):
        pass

    def clickButton(self):
        pass

    def clickHyperlink(self):
        pass

    def clickTab(self):
        pass

    def inputSubmit(self):
        pass
