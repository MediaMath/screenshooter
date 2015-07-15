#Screenshooter - v 0.1.0
Documentation - Elan Moyal - MediaMath Manhattan

###Table of Contents
- [Description](#description)
- [Setup](#setup)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Running Tests](#running-tests)
- [Usage](#usage)
- [FAQ](#faq)
- [Reference](#reference)
  - [General rules](#general-rules)
  - [Differ](#differ)
  - [Capsule](#capsule)
- [Limitations](#limitations)
- [History](#history)
- [License](#license)

##Description

Screenshooter allows one to obtain a difference between a current UI layout and a previous UI layout via screenshots.

Screenshooter contains a wrapper on Selenium Webdriver that will help automate the testing of various situations while taking a screenshot of various portions of the UI. Once screenshooter has obtained all the screenshots from the tests a method may be called to compare them against previous versions of that same UI. If there is a difference the updated image is saved along with the difference / change. The previous versions are stored via some other system i.e. on the local filesystem, or something like Amazon S3.

##Setup

######Virtual Environment
To simplify a few things a virtual environment was used while developing this package. This was done using virtualenv and virtualenvwrapper. To set up the virtual environment first install virtualenv and then virtualenvwrapper.

```python
pip install virtualenv
pip install virtualenvwrapper
```

Then to set up the virtual environment via virtualenvwrapper the following must be done:
```
$ export WORKON_HOME=~/Envs #tells virtualenvwrapper where to place your virtual environments
$ source /usr/local/bin/virtualenvwrapper.sh #lets terminal know you want to start using virtualenvwrapper commands

#to create a virtual environment
$ mkvirtualenv venvName

#to use virtual environment
$ workon envName

#Additional useful commands

#to stop using virtual environment
$ deactivate

#to remove virtual environment
$ rmvirtualenv envName
```

Once a virtual environment has been created only 2 commands need to be called to get up and Running
```
$ source /usr/local/bin/virtualenvwrapper.sh
$ workon envName
```

Then `$ cd` into the directory where your project is located and that's it!
For more info about [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/index.html)

######Environment Variables
Info acquired from this [blog](http://irisbeta.com/article/30408704/environment-variables-and-virtualenv/)

To set up environment variables that exist only in specific virtual environments the following can be done.

1. Activate the virtual envirionment you would like to use.

    ```
    $ workon envName
    ```
2. Edit the postactivate script

    ```
    $ nano $VIRTUAL_ENV/bin/postactivate
    ```
3. Set envirionment variables (there shouldn't be a space before or after the = sign)

    ```
    export USERNAME="OptimusPrime"
    ```
4. Exit via `CONTROL + x` and accept all

To test
```
$ deactivate
$ workon envName
$ echo $USERNAME
OptimusPrime
```

###Dependencies
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

**NOTE:** Alter the config.py file so that screenshooter can find the correct directory in your file system and allow the tests to run

###Installation

###Running Tests
Running the tests are simple:
```
py.test tests/

# or to run just one test case
py.test tests/TestName.py
```
or if your current working directory is the directory where the test(s) is/are held:
```
py.test

# to run just one test case
py.test TestName.py
```
pytest will pick up all the files beginning with Test and run them.

<!-- For an example of how Screenshooter works uncomment `diff.show()` in the test function `testGetDiffReturnsValueWithoutLocation` and `dif.change()` in the test function `testGetChangeReturnsValueWithoutLocation` of TestScreenshot.py

This will open up the diff image and the change image for you to see. -->

##Usage

Screenshooter is made of three seperate modules: capsule, differ, and saves. Capsule is the wrapper for selenium webdriver that takes screenshots and uses them to implement differ. Differ takes the images and creates the image differences of them. Saves grabs all the existing images from some external or local source and packages them into a single multi-dimensional dictionary that can be used by Differ.

All interaction with screenshooter can be done through capsule (if the defaults on differ are acceptable; future versions will allow altering of differ via the config file).

**Note:** All examples will be using pytest

Basic Example of usage:
```python
from selenium import webdriver
from screenshooter.capsule import Capsule

class SomeTestingFramework():
      @classmethod
      def setup_class(cls):
          cls.capsule = Capsule()

      def setup_method(self, method):
          self.driver = webdriver.Chrome()
          self.driver.set_window_size(1280, 720)

      def teardown_method(self, method):
          self.driver.quit()

      @classmethod
      def teardown_class(cls):
          cls.capsule.generateDiffs("s3")

      def testGetHomepage(self):
          self.capsule.getPage(self.driver, "HomePageView", "GetHomePage", "url")
          assert self.driver.current_url == "url"
```

Capsule should be instantiated at the top most scope of the testing framework, this guarantees that the screenshots being taken maintain existence until needed. The generateDiffs method should be called at the very end of all the tests, this is to minimize calls to external services; such as Amazon S3.

The generateDiffs method calls the Differ run function which implements only default options. Differ's main purpose is to either generate a diff image or a change image or both.

######Differ Example:
Given 2 images

screenshot1
![screenshot of original image](./tests/imgs/screenshot1.png?raw=true "Original Image")

and screenshot2
![screenshot of modified image](./tests/imgs/screenshot3.png?raw=true "Modified Image")

Notice the only difference between the two images is the blue bar on the top.

This is what happens when the diff method is called:
![Image of Diff outcome](./tests/imgs/Diff.png?raw=true "Diff Image")

And this is what happens when the change method is called:
![Image of Change outcome](./tests/imgs/Change.png?raw=true "Change Image")

The diff method will show the difference between both images, while the change method will only show what has been changed from the first image to the second image. Notice that the change method does not highlight the blue bar since it no longer exists in that image, but the shift upward of everything else is highlighted. Deletions in the change method are not highlighted but are in the diff method, please be aware of this when choosing accordingly.

**NOTE:** A change of an object's position counts as a deletion since those pixels are no longer in that spot, but instead in a different spot (addition)

##FAQ
Q: What do you mean by multi-dimensional dictionary?

A: See [general rules of thumb](general-rules) for an example. The purpose is so that the images may be accessed in O(1) time in a similar format to directories.

Q: What is the difference between Diff and Change?

A: See [example](#differ-example)
<!-- Explain difference using graphics step by step -->

##Reference

###General Rules:
- All images are stored in a multi-dimensional dictionary of the format:
```python
imgs[View][Date][Function]
```
where
```python
imgsFunction = image  # image is of type PIL.Image
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

###Differ

Differ is in charge of creating the diff images between the temporary images and the already stored images.

Contents:
- [Change](#change)
- [Diff](#diff)
- [Equality](#equality)
- [Locating Images](#locating-images-to-perform-diffs)

####Change
```python
getChange(color = (0, 150, 255), highlightDiff = True, originalLoc = None, modifiedLoc = None)
```
Args:
- color: determines the color of the highlighted portions of the change image
  - Default: RGB(0, 150, 255)
- highlightDiff: boolean that determines whether or not to apply a highlight to the change image
  - Default: True
  - **Note** if false the change image will show the change in more vibrant colors while the rest of the image is opaque
- originalLoc: the location of the original image
  - Default: None
  - **Note** if `equals` has been called before this method then it will default to the original location provided there
- modifiedLoc: the location of the modified image
  - Default: None
  - **Note** if `equals` has been called before this method then it will default to the modified location provided there

This method will only display the diff of the image that changed from the original thus it is crucial to make sure the original and modified images are correct or the correct result won't be returned and at best inverted.

If default parameters are fine but locations need to be adjusted implement the following call:
```python
original = {'View': someView, 'Date': someDate, 'Function': someFunction}
modified = {'View': someOtherView, 'Date': someOtherDate, 'Function': someOtherFunction}
getChange(originalLoc = original, modifiedLoc = modified)
```

####Diff
```python
getDiff(color = (0, 150, 255), highlightDiff = True, originalLoc = None, modifiedLoc = None)
```
Args:
- color: determines the color of the highlighted portions of the change image
  - Default: RGB(0, 150, 255)
- highlightDiff: boolean that determines whether or not to apply a highlight to the diff image
  - Default: True
  - **Note** if false the diff image will show the diff in more vibrant colors while the rest of the image is opaque
- originalLoc: the location of the original image
  - Default: None
    - **Note** if `equals` has been called before this method then it will default to the original location provided there
- modifiedLoc: the location of the modified image
  - Default: None
    - **Note** if `equals` has been called before this method then it will default to the modified location provided there

<!-- **NOTE:** If this is False the color doesn't matter it won't bother changing it even if a color is specified. To speed up operation set to False as changing the color is slow. -->

If the default parameters for color are fine but the last images used by the equals function are not, implement the following call:

```python
original = {'View': someView, 'Date': someDate, 'Function': someFunction}
modified = {'View': someOtherView, 'Date': someOtherDate, 'Function': someOtherFunction}
getDiff(originalLoc = original, modifiedLoc = modified)
```
The only thing that must be different between the two values is function, otherwise it's the same image.

**NOTE:** If the locations are not given as parameters and equals has not been called or images have not been assigned to the class an UnboundLocalError will be raised, this needs to be handled.

####Equality

Checks for an exact match of images. Currently is unable to compute if the image modes are different. Invalid equality will be captured if the image sizes are not exactly the same as well as having the same file type (ie. .png, .jpg, etc.).

####Locating Images to Perform Diffs

Returns the location of the already stored image. Requires the dictionary path to the temp image. Loops through the dictionary of images based on the temp image's view dictionary (this results in a dictionary of date dictionaries). The date dictionaries are sorted in descending order so that the oldest date (the one closest to now) is first. The first date is then used to attempt a retrieval of the image already stored, if it doesn't find one it moves on to the next date; if it does find one the dictionary location of that image is returned.

###Capsule
Contents:
- [Base Methods](#base-methods)
  - [clickElement](#clickelement)
  - [enterElement](#enterelement)
  - [getXPath](#getxpath)
  - [screenshot](#screenshot)
- [Methods](#methods)
  - [clickButton](#clickbutton)
  - [clickHyperlink](#clickhyperlink)
  - [clickInputButton](#clickinputButton)
  - [getPage](#getPage)
  - [inputEnter](#inputenter)
  - [scrollPage](#scrollpage)

###Base Methods
---
####clickElement
```python
clickElement(driver, view, function, xPath, iFrame = None)
```
Args:
- `driver`, `view`, `function`: passed into `screenshot(driver, view, function)`
- `xPath`: used to locate the correct element
- `iFrame`: used to switch focus to the frame given
  - Acceptable values: either a name field or id field i.e. `<element id='value'>` or `<element name='value'`
  - Default: `None`

A click action is performed on the xPath argument and a screenshot is taken.

---

####enterElement
```python
enterElement(driver, view, function, element)
```
Args:
- `driver`, `view`, `function`: passed into `screenshot(driver, view, function)`
- `element`: used to perform an enter key press on that element and then a screenshot is taken

The reason the whole element is taken instead of the xPath like the previous clickElement method is because often times data needs to be entered before the enter key is pressed, this allows for such data entry.

---

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

---

####screenshot
```python
screenshot(driver, view, function)
```
Args:
- driver: the selenium driver used
- view: what view are you currently in i.e. HomePage, AboutMe, etc. (can be more abstract if you wish)
- function: what function are you using to take a screenshot (make sure this has a descriptive name so it can be easily identifiable as to what role the screenshot has)

---

###Methods
---

####clickButton
```python
clickButton(driver, view, function, iFrame = None, **kwargs)
```
Args:
- `driver`, `view`, `function`, `iFrame`: passed into `clickElement(driver, view, function, iFrame)`
- `**kwargs`: passed into `getXPath(**kwargs)`
  - return value: passed into `clickElement(driver, view, function, iFrame, value)`

> This method makes use of the HTML5 tag `<button></button>`.

---

####clickHyperlink
```python
clickHyperlink(driver, view, function, iFrame = None, **kwargs)
```
Args:
- `driver`, `view`, `function`, `iFrame`: passed into `clickElement(driver, view, function, iFrame)`
- `**kwargs`: passed into `getXPath(**kwargs)`
  - return value: passed into `clickElement(driver, view, function, iFrame, value)`

> This method makes use of the HTML tag `<a href="url"></a>`.

---

####clickInputButton
```python
clickInputButton(driver, view, function, iFrame = None, **kwargs)
```
Args:
- `driver`, `view`, `function`, `iFrame`: passed into `clickElement(driver, view, function, iFrame)`
- `**kwargs`: passed into `getXPath(**kwargs)`
  - return value: passed into `clickElement(driver, view, function, iFrame, value)`

> This method makes use of the HTML tag `<input type="submit" ></input>`.

---

####getPage
```python
getPage(driver, view, function, page, splash = False, ignoreSplash = True)
```
Args:
- `driver`, `view`, `function`: passed into `screenshot(driver, view, function)`
- `page`: url of the page you would like to visit, this must be in the format `http://pagetovisit.com` or `http://www.pagetovisit.com` where `https` is also valid or any other TLD i.e. `.net`, `.org`, etc
- `splash`: boolean referencing if the page contains a splash page
  - Default: False (there is not a splash page)
- `ignoreSplash`: boolean referencing whether to take a picture of the splash page as well or to just ignore it
  - Default: True (ignore the splash page)

This method will route to a page and then take a screenshot.

---

####inputEnter
```python
inputEnter(driver, view, function, inputText, iFrame = None, **kwargs)
```
Args:
- `driver`, `view`, `function`: passed into `enterElement(driver, view, function)`
- `**kwargs`: passed into `getXPath(**kwargs)`
- `inputText`: used for the content that should be entered into the text box before enterElement has been called
- `iFrame`: used to switch focus to the frame given
  - Acceptable values: either a name or id field i.e. `<input name='value'>` or `<input id='value'>`
  - Default: None

> This method makes use of the HTML tag `<input type="text" >inputText</input>`.

---

####scrollPage
```python
scrollPage(driver, view, function)
```
Args:
- `driver`, `view`, `function`: passed into `enterElement(driver, view, function)`

This method will scroll the length of the viewable page (what you see on your screen) and then take a screenshot, doing this repeatedly until the entire page has been scrolled. Use this in conjunction with `getPage` to route to a specific page and screenshot every part of it.

---

##Limitations

##History

###TO-DO
- [x] Update Readme
- [x] Reorganize Readme
- [x] Update wording/structure of [Differ](#differ)
- [x] Rename Screenshot to Differ
- [x] Add and configure setup.py
- [ ] Add in missing info (Installation, setup.py url, etc.) once open source is greenlighted

####Things that should be added to Readme
- [x] How to setup virtual environment
- [x] How to set and unset environment variables for virtual environments
- [x] How Capsule and its various functions work / should be called

####For Next Version
- [ ] Allow modifications of Differ via config instead of parameters
- [ ] How to deal with Today changes in UI
- [ ] Speed Improvements

##License
<!-- Probably doing an MIT License -->
