import io
import os
import fnmatch
from PIL import Image
import datetime
import shutil
import re


def remove_new(val):
    """
    Removes the string 'new' from a string.

    Args:
      val: a string value containing 'new' string.

    Returns:
      The value passed in without the 'new' portion of the string.
    """
    return "".join(filter(None, re.split('new_?', val)))


class fs_service():
    """
    fs_service is a saving and retrieval service for the images used in screenshooter. This service
    uses the local filesystem.
    """

    def __init__(self, user_config):
        if user_config is None:
            raise UnboundLocalError("A configuration file has not been referenced, please provide one.")
        self.config = user_config

    def collect_images(self, base_dir, imgs = None):
        """
        Collects all images from a directory and places them into a multi-dimensional
        dictionary.

        Args:
          base_dir: the base directory where all the images are located.
          imgs: the multi-dimensional dictionary to place all the images (Defaults to None)

        Returns:
          The multi-dimensional dictionary with all the images in it.
        """
        dict_pics = imgs or dict()

        previous_path = os.path.join(base_dir, self.config.env_dir, self.config.base_dir)
        if not os.path.isdir(previous_path):
            return dict_pics
        for dir_view in fnmatch.filter(os.listdir(previous_path), "*[Vv]iew"):

            previous_path = os.path.join(previous_path, dir_view)
            if os.path.isdir(previous_path):
                if dir_view not in dict_pics:
                    dict_pics[dir_view] = dict()

                for filename in fnmatch.filter(os.listdir(previous_path), "*" + self.config.picture_type):
                    path = os.path.join(previous_path, filename)
                    mod_time = os.stat(path).st_mtime
                    date = datetime.datetime.fromtimestamp(mod_time).date().isoformat()

                    if date not in dict_pics[dir_view]:
                        dict_pics[dir_view][date] = dict()

                    dict_pics[dir_view][date][filename] = Image.open(os.path.join(path))

        return dict_pics

    def collect_img(self, imgs, tmp_loc):
        """
        Collects a single image from a directory path.

        Args:
          imgs: the multi-dimensional dictionary to place the image in.
          tmp_loc: a dictionary containing the location of the temp image
            in the multi-dimensional dictionary.

        Returns:
          A dictionary containing the location of the image that was placed
          in the multi-dimensional dictionary.
        """
        tmp_view = tmp_loc['View']
        tmp_date = tmp_loc['Date']
        tmp_function = tmp_loc['Function']

        if tmp_view in imgs:
            if tmp_date in imgs[tmp_view]:
                if tmp_function in imgs[tmp_view][tmp_date]:
                    tmp = imgs[tmp_view][tmp_date][tmp_function]
                    if tmp:
                        return tmp_loc
                    return None

        path = os.path.join(self.config.image_path, self.config.env_dir, self.config.base_dir, tmp_view, tmp_function)
        mod_time = os.stat(path).st_mtime
        date = datetime.datetime.fromtimestamp(mod_time).date().isoformat()
        if tmp_view not in imgs:
            imgs[tmp_view] = dict()
        if date not in imgs[tmp_view]:
            imgs[tmp_view][date] = dict()
        imgs[tmp_view][date][tmp_function] = Image.open(path)
        return {'View': tmp_view, 'Date': date, 'Function': tmp_function}

    def save(self, imgs):
        """
        Saves images to the storage drive.

        Args:
          imgs: the multi-dimensional dictionary that contains the images
            to be saved.

        Returns:
          A boolean stating whether or not it succeeded, True means success.
        """
        if imgs is None:
            raise ("Can not save anything, the multi-dimensional dictionary is None")
        today = datetime.datetime.now().date().isoformat()
        save_to_base = self.config.base_store
        base_path = os.path.join(self.config.image_path, self.config.env_dir)
        base_dir = self.config.base_dir
        try:
            if not os.path.exists(base_path):
                os.mkdir(base_path)
            if not os.path.exists(os.path.join(base_path, base_dir)):
                os.mkdir(os.path.join(base_path, base_dir))
            for view in fnmatch.filter(imgs, "*View"):
                if not os.path.exists(os.path.join(base_path, view)):
                    os.mkdir(os.path.join(base_path, view))
                if not os.path.exists(os.path.join(base_path, base_dir, view)):
                    os.mkdir(os.path.join(base_path, base_dir, view))
                for day in fnmatch.filter(imgs[view], today + "*"):
                    if not os.path.exists(os.path.join(base_path, view, day)):
                        os.mkdir(os.path.join(base_path, view, day))
                    for function in fnmatch.filter(imgs[view][day], "new*"):
                        imgs[view][day][function].save(os.path.join(base_path, view,
                                                                    day, remove_new(function)))
                        if ("Diff" not in function or "Change" not in function) and save_to_base:
                            imgs[view][day][function].save(os.path.join(base_path, base_dir, view, remove_new(function)))
            return True
        except (KeyError, IOError):
            return False

    #This is no longer useful, could refactor to eliminate files past a default archive date
    def cleanupfs(self):
        try:
            path = self.config.image_path + "tmp"
            shutil.rmtree(path)
        except IOError:
            return False
        return True


class s3_service():
    """
    s3_service is a saving and retrieval service for the images used in screenshooter. This service
    uses Amazon's s3.
    """

    def __init__(self, user_config):
        if user_config is None:
            raise UnboundLocalError("A configuration file has not been referenced, please provide one.")
        import boto3 as boto
        self.config = user_config
        self.boto = boto

    def parse_out_backslash(self, location):
        """
        Removes backslashes from a string

        Args:
          location: the string containing backslashes

        Returns:
          A dictionary containing the number of directories
          in the location and an array of each directory in the
          location string.
        """
        return location.split('/')

    def concat_in_backslash(self, *args):
        """
        Creates a string with a backslash in between each string argument.

        Args:
          args: an indescriminate number of string arguments.

        Returns:
          A string value containing each arg with a '/' inbetween them.
        """
        return "/".join(args)

    def collect_images(self, imgs = None):
        """
        Collects all images from an s3 bucket and places them into a multi-dimensional
        dictionary.

        Args:
          imgs: the multi-dimensional dictionary to place all the images (Defaults to None)

        Returns:
          The multi-dimensional dictionary with all the images in it.
        """
        dict_pics = imgs or dict()
        session = self.boto.session.Session(aws_access_key_id = self.config.access_key, aws_secret_access_key = self.config.secret_key)
        s3 = session.client('s3')
        try:
            contents = s3.list_objects(Bucket = self.config.bucket, Prefix = '/'.join(self.config.env_dir, self.config.base_dir))
        except ClientError:
            return dict_pics
        for content in contents['Contents']:
            if content['Size'] == 0:
                continue
            parsed_key = self.parse_out_backslash(content['Key'])
            if len(parsed_key) != 4:
                continue
            environment = parsed_key[0]
            if environment != self.config.env_dir:
                continue
            base_dir = parsed_key[1]
            if base_dir != self.config.base_dir:
                continue
            view = parsed_key[2]
            function = parsed_key[3]
            data = s3.get_object(Bucket = self.config.bucket, Key = content['Key'])
            data_bytes_io = io.BytesIO(data['Body'].read())
            if view not in dict_pics:
                dict_pics[view] = dict()
            if date not in dict_pics[view]:
                dict_pics[view][date] = dict()
            dict_pics[view][date][function] = Image.open(data_bytes_io)
        return dict_pics

    def collect_img(self, imgs, tmp_loc):
        """
        Collects a single image from a s3 bucket.

        Args:
          imgs: the multi-dimensional dictionary to place the image in.
          tmp_loc: a dictionary containing the location of the temp image
            in the multi-dimensional dictionary.

        Returns:
          A dictionary containing the location of the image that was placed
          in the multi-dimensional dictionary.
        """
        tmp_view = tmp_loc['View']
        tmp_function = tmp_loc['Function']

        session = self.boto.session.Session(aws_access_key_id = self.config.access_key, aws_secret_access_key = self.config.secret_key)
        s3 = session.client('s3')

        loc = self.concat_in_backslash(self.config.env_dir, self.config.base_dir, tmp_view, tmp_function)
        try:
            data = s3.get_object(Bucket = self.config.bucket, Key = loc)
        except ClientError:
            return None
        data_bytes_io = io.BytesIO(data['Body'].read())
        date = data['LastModified'].date().isoformat()
        if tmp_view not in imgs:
            imgs[tmp_view] = dict()
        if date not in imgs[tmp_view]:
            imgs[tmp_view][date] = dict()
        imgs[tmp_view][date][tmp_function] = Image.open(data_bytes_io)
        return {'View': tmp_view, 'Date': date, 'Function': tmp_function}

    def save(self, imgs):
        """
        Saves images to s3 based on their location in the multi-dimensional
        dictionary.

        Args:
          imgs: the multi-dimensional dictionary that contains the images
            to be saved.

        Returns:
          A boolean stating whether or not it succeeded, True means success.
        """
        environment_dir = self.config.env_dir
        base_dir = self.config.base_dir
        bucket = self.config.bucket
        save_to_base = self.config.base_store
        if imgs is None:
            raise ("Can not save anything, the multi-dimensional dictionary is None")
        responses = list()
        count = 0
        session = self.boto.session.Session(aws_access_key_id = self.config.access_key, aws_secret_access_key = self.config.secret_key)
        s3 = session.client('s3')
        today = datetime.datetime.now().date().isoformat()
        for view in imgs:
            if view == 'tmp':
                continue
            for day in fnmatch.filter(imgs[view], today + "*"):
                for function in fnmatch.filter(imgs[view][day], "new*"):
                    bytes_img_io = io.BytesIO()
                    imgs[view][day][function].save(bytes_img_io, "PNG")
                    bytes_img_io.seek(0)
                    bytes_to_save = bytes_img_io.read()
                    responses.append(s3.put_object(Body = bytes_to_save, Bucket = bucket,
                                                   Key = self.concat_in_backslash(environment_dir, view, day, remove_new(function)), ContentType = "image/png"))
                    #check to make sure not diff or change
                    if ("Diff" not in function and "Change" not in function) and save_to_base:
                        responses.append(s3.put_object(Body = bytes_to_save, Bucket = self.config.bucket,
                                                       Key = self.concat_in_backslash(environment_dir, base_dir, view, remove_new(function)),
                                                       ContentType = "image/png"))
                        count += 1
                    count += 1
        return {'count': count, 'responses': responses}
