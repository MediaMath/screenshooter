from PIL import Image
from PIL import ImageChops
import datetime
import screenshooter.saves


class Differ:
    """
    Differ is a service that allows the diffing of images.
    """

    def __init__(self, user_config):
        if user_config is None:
            raise UnboundLocalError("A configuration file has not been referenced, please provide one.")
        self.config = user_config
        self.imgs = dict()
        self.diff = None
        self.original_img = None
        self.modified_img = None
        self.archive_time = None
        self.img_type = config.picture_type

    def equals(self, first_img, second_img):
        """
        Identifies if first_img and second_img are identical to each other.

        Args:
          first_img: a PIL image object of the original image
          second_img: a PIL image object of the modified image

        Returns:
          A boolean stating whether or not the two images are identical, True means they are
          identical.
        """
        if first_img is None or second_img is None:
            return False
        self.original_img = first_img
        self.modified_img = second_img
        self.diff = ImageChops.difference(first_img, second_img)
        if self.diff.getbbox() != None:
            return False
        else:
            self.diff = None
            return True

    def archive_imgs(self, img_loc):
        """
        Archive the image given by img_loc and it's corresponding diff and change images.

        Args:
          img_loc: a dictionary representing the location of the image within the multi-dimensional
            dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
        """
        view = img_loc['View']
        date = img_loc['Date']
        function = img_loc['Function']

        if self.archive_time is None:
            self.archive_time = datetime.datetime.now().isoformat()
        if self.archive_time not in self.imgs[view]:
            self.imgs[view][self.archive_time] = dict()
        self.imgs[view][self.archive_time]["new" + function] = self.imgs[view][date][function]
        img_name = function.partition('.')
        if img_name[0] + "Diff" + self.img_type in self.imgs[view][date]:
            self.imgs[view][self.archive_time]["new" + img_name[0] + "Diff.png"] = self.imgs[view][date][img_name[0] + "Diff" + self.img_type]
        if img_name[0] + "Change" + self.img_type in self.imgs[view][date]:
            self.imgs[view][self.archive_time]["new" + img_name[0] + "Change.png"] = self.imgs[view][date][img_name[0] + "Change" + self.img_type]

    def store_screenshot(self, img_loc):
        """
        Moves the screenshot from it's temporary location in the multi-dimensional dictionary to a portion
        where it will actually be saved.

        Args:
          img_loc: a dictionary representing the location of the image within the multi-dimensional
            dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """
        if img_loc is None:
            return False

        view = img_loc['View']
        date = img_loc['Date']
        function = img_loc['Function']

        try:
            if view not in self.imgs:
                self.imgs[view] = dict()
            if date not in self.imgs[view]:
                self.imgs[view][date] = dict()
            if function in self.imgs[view][date]:
                self.archive_imgs(img_loc)
            self.imgs[view][date]["new" + function] = self.imgs['tmp'][view][date][function]
        except KeyError:
            del self.imgs[view][date]["new" + function]
            return False
        return True

    def store_diff(self, img_loc, diff_img):
        """
        Adds the diff image to the multi-dimensional dictionary so it can be saved.

        Args:
          img_loc: a dictionary representing the location of the image that was used to create the diff image within
            the multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          diff_img: a PIL image object of the diff image

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """
        if diff_img is None:
            return False

        view = img_loc['View']
        date = img_loc['Date']
        img_name = img_loc['Function'].partition('.')

        diff_name = "new" + img_name[0] + "Diff" + self.img_type
        self.imgs[view][date][diff_name] = diff_img
        return True

    def store_change(self, img_loc, change_img):
        """
        Adds the change image to the multi-dimensional dictionary so it can be saved.

        Args:
          img_loc: a dictionary representing the location of the image that was used to create the change image within
            the multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          change_img: a PIL image object of the diff image

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """
        if change_img is None:
            return False

        view = img_loc['View']
        date = img_loc['Date']
        img_name = img_loc['Function'].partition('.')

        change_name = "new" + img_name[0] + "Change" + self.img_type
        self.imgs[view][date][change_name] = change_img

        return True

    def store(self, img_loc = None, diff_img = None, change_img = None):
        """
        Adds the screenshot and it's corresponding diff and change images to the multi-dimensional dictionary
        so they can be saved.

        Args:
          img_loc: a dictionary representing the location of the screenshot within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          diff_img: a PIL image object of the diff image
          change_img: a PIL image object of the change image

        Returns:
          A boolean stating whether or not it was successful, True means successful.
        """

        if img_loc is None and diff_img is None and change_img is None:
            return False

        if self.store_screenshot(img_loc):
            self.store_diff(img_loc, diff_img)
            self.store_change(img_loc, change_img)
        else:
            return False

        return True

    def locate_img_for_diff(self, loc, service_name = config.service):
        """
        Locates the image to diff against.

        Args:
          loc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          service_name: the name of the service to grab the image from (Defaults to the service in the config file)

        Returns:
          A dictionary representing the location of the original image to diff against in the
            multi-dimensional dictionary
        """
        if service_name.upper() == "S3":
            img_reference = screenshooter.saves.s3_service.collect_img(self.imgs, loc)
        elif service_name.upper() == "FILESYSTEM":
            img_reference = screenshooter.saves.fs_service.collect_img(self.imgs, loc)
        return img_reference

    def get_img(self, loc, tmp = False):
        """
        Retrieves the PIL image object from the multi-dimensional dictionary.

        Args:
          loc: a dictionary representing the location of the image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          tmp: a boolean stating whether or not to grab from the tmp dictionary, True means grab from the tmp
            dictionary (Defaults to False)

        Returns:
          A PIL image object
        """
        view = loc['View']
        date = loc['Date']
        function = loc['Function']
        try:
            if tmp:
                return self.imgs['tmp'][view][date][function]
            return self.imgs[view][date][function]
        except KeyError:
            return None

    def sanitize_for_diff(self, original_loc, modified_loc):
        """
        Checks to make sure all the information is acceptable before performing the diff.

        Args:
          original_loc: a dictionary representing the location of the original image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
          modified_loc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}

        Returns:
          The pixel difference between the two images.

        Raises:
          UnboundLocalError: The class level images are null and the parameters do not provide locations to open them.
        """
        if (original_loc is None and modified_loc is None) and (self.original_img is None or self.modified_img is None) and self.diff is None:
            raise UnboundLocalError("The class level images are null and the parameters" +
                                    " do not provide locations to open them")
        if original_loc is not None and modified_loc is not None:
            try:
                self.original_img = self.get_img(original_loc)
                self.modified_img = self.get_img(modified_loc, True)
                self.diff = ImageChops.difference(self.original_img, self.modified_img)
                if self.diff.getbbox() is None:
                    return None
                return self.diff
            except (IOError, KeyError, TypeError):
                return None
        elif self.diff is not None:
            return self.diff
        else:
            return None

    def get_diff(self, original_loc = None, modified_loc = None):
        """
        Gets the difference between two images and applies a highlight over them if specified.

        Args:
          original_loc: a dictionary representing the location of the original image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)
          modified_loc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)

        Returns:
          A PIL image object of the diff image.
        """

        dif = self.sanitize_for_diff(original_loc, modified_loc)

        if dif is None:
            return None

        color = config.highlight_color

        dif = ImageChops.invert(dif)

        if not color:
            return Image.blend(dif, self.original_img, 0.2)

        width = dif.size[0]
        height = dif.size[1]
        pixel = dif.load()
        for x in range(width):
            for y in range(height):
                if pixel[x, y] == (255, 255, 255, 255):
                    continue
                pixel[x, y] = color

        return Image.blend(dif, self.original_img, 0.2)

    def subtract_pixels(self, first, second):
        """
        Subtract two pixels.

        Args:
          first: An RGBA pixel value
          second: An RGBA pixel value

        Returns:
          A tuple containing the result of the absolute value of the subtraction of the two pixels.
        """
        return tuple([abs(first[0] - second[0]), abs(first[1] - second[1]), abs(first[2] - second[2]), abs(first[3] - second[3])])

    def get_change(self, original_loc = None, modified_loc = None):
        """
        Gets the changed difference between two images and applies a highlight over them if specified.

        Args:
          original_loc: a dictionary representing the location of the original image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)
          modified_loc: a dictionary representing the location of the modified image within the
            multi-dimensional dictionary i.e. {'View': 'SomeView', 'Date': 'SomeDate', 'Function': 'SomeFunction'}
            (Defaults to None)

        Returns:
          A PIL image object of the change image.
        """

        diff = self.sanitize_for_diff(original_loc, modified_loc)

        if diff is None:
            return None

        color = config.highlight_color

        merging_img = ImageChops.invert(self.original_img)

        width = merging_img.size[0]
        height = merging_img.size[1]

        diff_pixels = diff.load()
        merge_pixel = merging_img.load()

        for x in range(width):
            for y in range(height):
                diff_pixel = diff_pixels[x, y]
                if diff_pixel != (0, 0, 0, 0):
                    if self.subtract_pixels(diff_pixel, merge_pixel[x, y]) == (0, 0, 0, 0):
                        merge_pixel[x, y] = (255, 255, 255, 255)
                    else:
                        if color is None:
                            continue
                        merge_pixel[x, y] = color
                else:
                    merge_pixel[x, y] = (255, 255, 255, 255)

        return Image.blend(merging_img, self.original_img, 0.2)

    def run(self):
        """
        A singular function to run through the multi-dimensional dictionary and diff all images in the
        tmp dictionary and then store the images that result in a diff/change for saving.
        """
        diff_flag = config.run_diff
        change_flag = config.run_change
        for view in self.imgs['tmp']:
            for date in self.imgs['tmp'][view]:
                for function in self.imgs['tmp'][view][date]:
                    modified_loc = {'View': view, 'Date': date, 'Function': function}
                    original_loc = self.locate_img_for_diff(modified_loc)
                    diff = None
                    change = None
                    if original_loc:
                        modified_img = self.get_img(modified_loc, True)
                        original_img = self.get_img(original_loc)
                        if self.equals(original_img, modified_img):
                            continue
                        if diff_flag:
                            diff = self.get_diff()
                        if change_flag:
                            change = self.get_change()
                    self.store(modified_loc, diff, change)
        return True
