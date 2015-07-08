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
- Capsule
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

#Capsule

####getXPath
```python
getXPath(**kwargs)
```
This method returns only the first element found based on the arguments given.

Acceptable Key Word Arguments:
- `tag = 'someHTMLTag'` i.e. `<button></button>`, `<a></a>`, `<input>` etc.
- `classTag = 'cssClass'` i.e. `<button class="someClass"></button>`
- `idTag = 'cssID'` i.e. `<button id="someID"></button>`
- `value = 'inputValue'` i.e. `<input value="Hello">`
- `text = 'textContent'` i.e. `<input type="text" value="textContent">`
- `name = 'elementName'` i.e. `<button name="someName"></button>`

####screenshot
```python
screenshot(driver, view, function)
```
- driver: the selenium driver used
- view: what view are you currently in i.e. HomePage, AboutMe, etc. (can be more abstract if you wish)
- function: what function are you using to take a screenshot (make sure this has a descriptive name so it can be easily identifiable as to what role the screenshot has)

####clickElement
```python
clickElement(driver, view, function, xPath, iFrame = None)
```
The `driver`, `view`, and `function` arguments are passed along to the screenshot call. The `iFrame` argument is used to switch focus to the frame given; works with either a name field or id field i.e. `<element id='value'>` or `<element name='value'`; defaults to None. The `xPath` argument is used to locate the correct element, then a click action is performed on that argument and a screenshot is taken.

####enterElement
```python
enterElement(driver, view, function, element)
```
The `driver`, `view`, and `function` arguments are passed along to the screenshot call. The `element` argument is used to perform an enter key press on that element and then a screenshot is taken. The reason the whole element is taken instead of the xPath like the previous clickElement method is because often times data needs to be entered before the enter key is pressed, this allows for such data entry.

####inputEnter
```python
inputEnter(driver, view, function, inputText, iFrame = None, **kwargs)
```
This method makes calls to enterElement and getXPath, and `driver`, `view`, `function` and `kwargs` get passed in respectively. The `inputText` argument is used for the content that should be entered into the text box before enterElement has been called. The `iFrame` argument is used to switch focus to the frame given; works with either a name or id field i.e. `<input name='value'>` or `<input id='value'>`; defaults to None.
> This method makes use of the HTML tag `<input type="text" >inputText</input>`.

####clickButton
```python
clickButton(driver, view, function, iFrame = None, **kwargs)
```
This method makes calls to clickElement and getXPath, arguments are passed along respectively.
> This method makes use of the HTML5 tag `<button></button>`.

####clickInputButton
```python
clickInputButton(driver, view, function, iFrame = None, **kwargs)
```
This method makes calls to clickElement and getXPath, arguments are passed along respectively.
> This method makes use of the HTML tag `<input type="submit" ></input>`.

####clickHyperlink
```python
clickHyperlink(driver, view, function, iFrame = None, **kwargs)
```
This method makes calls to clickElement and getXPath, arguments are passed along respectively.
> This method makes use of the HTML tag `<a href="url"></a>`.

####getPage
```python
getPage(driver, view, function, page, splash = False, ignoreSplash = True)
```
This method makes a call to screenshot and the arguments `driver`, `view`, and `function` are passed to it. The argument `page` is the url of the page you would like to visit, this must be in the format `http://pagetovisit.com` or `http://www.pagetovisit.com` where `https` is also valid or any other TLD i.e. `.net`, `.org`, etc. The argument `splash` is a boolean referencing if the page contains a splash page. The argument `ignoreSplash` is a boolean referencing whether to take a picture of the splash page as well or to just ignore it. By default there is no splash page and the splash page will be ignored. This method will route to a page and then take a screenshot.

####scrollPage
```python
scrollPage(driver, view, function)
```
This method makes a call to screenshot and the arguments `driver`, `view`, and `function` are passed to it. This method will scroll the length of the viewable page (what you see on your screen) and then take a screenshot, doing this repeatedly until the entire page has been scrolled. Use this in conjunction with `getPage` to route to a specific page and screenshot every part of it.

##TO-DO
- [ ] Update Readme
- [ ] Reorganize Readme

###Things that should be added to Readme
- [ ] How to set and unset environment variables for virtual environments
- [ ] How Capsule and its various functions work / should be called
