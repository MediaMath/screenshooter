#Screenshooter
Documentation - Elan Moyal - MediaMath Manhattan

###Table of Contents
- Dependencies
- General rules
- Running Tests
- Equality
- Locating Images to Perform Diffs
- Diff
- Change
- TO-DO

##Dependencies
Screenshooter is written in python v 3.4.

Screenshooter requires the [Pillow][1] fork of [PIL][2] to work. To install use pip.
[1]:http://pillow.readthedocs.org/en/latest/index.html
[2]:http://www.pythonware.com/products/pil/
```
pip install Pillow
```

Tests are implemented using pytest. To install use pip.
```
pip install pytest
```

**NOTE:** Alter the config.py file so that Screenshooter can find the correct directory in your file system and allow the tests to run

####Some general rules of thumb:
- All images are stored in a multi-dimensional dictionary of the format:
```python
imgs[View][Date][Function]
```
where
```python
imgsFunction = dict()
imgsDate = dict(imgsFunction)
imgsView = dict(imgsDate)
imgs = dict(imgsView)
```
- View refers to some string value ending in View i.e. `'SomeView'`
- Date refers to some string value with the format YYYY-MM-DD i.e. `'2015-06-19'`
- Function refers to some string value representing the name of the image i.e. `'blah.png'`
- The value stored at the end of the dictionary is an image of type PIL.Image
- All mentions of location refer to location within the multi-dimensional dictionary
- When passing around any location from function to function it is done in the following format
```python
dict = {'View': someView, 'Date': someDate, 'Function': someFunction}
```
where the values in this dictionary are the keys of the multi-dimensional dictionary stated above
- Tests are run using three screenshots of the google homepage with 1 & 2 being the same while 3 is different
- Those screenshots are stored with Screenshooter and copied to a local directory for testing (DO NOT REMOVE the screenshots stored with Screenshooter or the tests will not work)

##Running Tests
Running the tests are simple:
```
py.test testName.py
```
or if your current working directory is the directory where the test(s) is/are held:
```
py.test
```
pytest will pick up all the files beginning with Test and run them.

For an example of how Screenshooter works uncomment `diff.show()` in the test function `testGetDiffReturnsValueWithoutLocation` and `dif.change()` in the test function `testGetChangeReturnsValueWithoutLocation` of TestScreenshot.py

This will open up the diff image and the change image for you to see.


##Equality

Checks for an exact match of images. Currently is unable to compute if the image modes are different. Invalid equality will be captured if the image sizes are not exactly the same as well as having the same file type (ie. .png, .jpg, etc.).

##Locating Images to Perform Diffs

Returns the location of the already stored image. Requires the dictionary path to the temp image. Loops through the dictionary of images based on the temp image's view dictionary (this results in a dictionary of date dictionaries). The date dictionaries are sorted in descending order so that the oldest date (the one closest to now) is first. The first date is then used to attempt a retrieval of the image already stored, if it doesn't find one it moves on to the next date; if it does find one the dictionary location of that image is returned.


##Diff
The getDiff function accepts 4 optional parameters depending on use. The first parameter is the color in RGB format, and the second parameter is a boolean stating whether or not to use a color for the diff.

**NOTE:** If this is False the color doesn't matter it won't bother changing it even if a color is specified. To speed up operation set to False as changing the color is slow.

```python
getDiff(highlightDiff = False)
```

The diff image obtained is taken from the diff of the images retrieved from the locations provided by the third and fourth parameters.

**NOTE:** The third parameter must exclusively be the original image location and the fourth parameter the modified image location.

By default the color is RGB(0, 150, 255) and will be implemented. The image locations are set to None so that the images used are the last images used when equality was checked.

If the default parameters for color are fine but the last images used by the equals function are not, implement the following call:

```python
original = {'View': someView, 'Date': someDate, 'Function': someFunction}
modified = {'View': someOtherView, 'Date': someOtherDate, 'Function': someOtherFunction}
getDiff(firstLoc = original, secondLoc = modified)
```
The only thing that must be different between the two values is function, otherwise it's the same image.

**NOTE:** If the locations are not given as parameters and equals has not been called or images have not been assigned to the class an UnboundLocalError will be raised, this needs to be handled.

##Change
The getChange method operates the same way as the getDiff function. This method will only display the diff of the image that changed from the original thus it is crucial to make sure the original and modified images are correct or the correct result won't be returned and at best inverted.

If default parameters are fine but locations need to be adjusted implement the following call:
```python
original = {'View': someView, 'Date': someDate, 'Function': someFunction}
modified = {'View': someOtherView, 'Date': someOtherDate, 'Function': someOtherFunction}
getChange(originalLoc = original, modifiedLoc = modified)
```

##TO-DO

- [x] Determine whether or not two images are identical
- [x] Search through a directory recursively to identify equality
- [x] Compare two images and get the combined difference between them
- [x] Compare two images and get the modified difference from the original
- [x] Add image / diffs to specific directory based on whether or not the image already exists in storage
- [x] Iterate through a base directory to create the diffs
- [ ] Clean up directory structure / rename things
- [ ] Add Amazon S3 support
