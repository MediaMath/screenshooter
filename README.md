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

Screenshooter contains a wrapper on Selenium Webdriver that will help automate the testing of various situations while taking a screenshot of various portions of the UI. Once screenshooter has obtained all the screenshots from the tests a method may be called to compare them against previous versions of that same UI. If there is a difference the updated image is saved along with the difference / change. The previous versions are stored via some other system e.g. on the local filesystem, or something like Amazon S3.

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

A: See [general rules of thumb](#general-rules) for an example. The purpose is so that the images may be accessed in O(1) time in a similar format to directories.

Q: What is the difference between Diff and Change?

A: See [example](#differ-example)

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
- View refers to some string value ending in View e.g. `'SomeView'`
- Date refers to some string value with the format YYYY-MM-DD e.g. `'2015-06-19'`
- Function is meant to be the name of the function that called for a screenshot, this allows ease of use when identifying what took the screenshot and what it is of. Hence, it is referred to as function.
  - **NOTE**: The name of the function will be the string value that represents the name of the image e.g. `'blah.png'`
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
- originalLoc: the location of the original image
  - Default: None
  - **Note** if `equals` has been called before this method then it will default to the original location provided there
- modifiedLoc: the location of the modified image
  - Default: None
  - **Note** if `equals` has been called before this method then it will default to the modified location provided there

Config Args:
  - color: determines the color of the highlighted portions of the change image
    - Default: RGB(0, 150, 255)
    - **Note**: if color is set to None the image will not contain highlighted portions, instead the diff will be brighter than the rest of the image

This method will only display the diff of the image that changed from the original thus it is crucial to make sure the original and modified images are exactly that or the correct result won't be returned and at best inverted.

####Diff
```python
getDiff(color = (0, 150, 255), highlightDiff = True, originalLoc = None, modifiedLoc = None)
```
Args:
- originalLoc: the location of the original image
  - Default: None
    - **Note** if `equals` has been called before this method then it will default to the original location provided there
- modifiedLoc: the location of the modified image
  - Default: None
    - **Note** if `equals` has been called before this method then it will default to the modified location provided there

Config Args:
- color: determines the color of the highlighted portions of the change image
  - Default: RGB(0, 150, 255)
  - **Note**: if color is set to None the image will not contain highlighted portions, instead the diff will be brighter than the rest of the image

**NOTE:** If the locations are not given as parameters and equals has not been called or images have not been assigned to the class an UnboundLocalError will be raised, this needs to be handled.

####Equality

Checks for an exact match of images. Currently is unable to compute if the image modes are different. Invalid equality will be captured if the image sizes are not exactly the same as well as not having the same file type (ie. .png, .jpg, etc.).

####Locating Images to Perform Diffs

There are two methods to locate images:

1. The image is grabbed when it is needed.
  - This will make an api call if an api service is being used.
  - The image will be added to the multi-dimensional dictionary once it is located
2. All images are retrieved at once
  - All api calls are made before locating the image
  - Checks to see if image exists in dictionary

This is can be done using any service, by default it's the one chosen in the config file.

Requires: location of temp image to diff against

Returns: location to where the stored image is located in the multi-dimensional dictionary

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

This method will press the enter key on the given element. The reason the whole element is taken instead of the xPath is because often times data needs to be entered before the enter key is pressed, this allows for such data entry.

---

####getXPath
```python
getXPath(**kwargs)
```
Acceptable Key Word Arguments:
- `tag = 'someHTMLTag'` e.g. `<button></button>`, `<a></a>`, `<input>` etc.
- `classTag = 'cssClass'` i.e. `<button class="someClass"></button>`
- `idTag = 'cssID'` i.e. `<button id="someID"></button>`
- `value = 'inputValue'` i.e. `<input value="Hello">`
- `text = 'textContent'` i.e. `<input type="text" value="textContent">`
- `name = 'elementName'` i.e. `<button name="someName"></button>`

This method returns the XPath of the first element found based on the arguments given.

---

####screenshot
```python
screenshot(driver, view, function)
```
Args:
- driver: the selenium driver used
- view: what view are you currently in e.g. HomePage, AboutMe, etc. (can be more abstract if you wish)
- function: what function are you using to take a screenshot (make sure this has a descriptive name so it can be easily identifiable as to what role the screenshot has)

This method takes a screenshot of the current screen. The size of the screenshot is based on the size of the browser, it is recommended to create a default size that the browser gets formed to.

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

This method will click a button then take a screenshot.

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

This method will click a hyperlink then take a screenshot.

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

This method will click an input of type submit and then take a screenshot.

---

####getPage
```python
getPage(driver, view, function, page, splash = False, ignoreSplash = True)
```
Args:
- `driver`, `view`, `function`: passed into `screenshot(driver, view, function)`
- `page`: url of the page you would like to visit, this must be in the format `http://pagetovisit.com` or `http://www.pagetovisit.com` where `https` is also valid or any other TLD e.g. `.net`, `.org`, etc
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

This method will apply the text given to an input textbox, press the enter key and then take a screenshot.

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
#####Equality
Checking for equality has a few limitations, all related to only being able to check for exact equality:

1. Images must be of the same [mode type](#http://pillow.readthedocs.org/en/latest/reference/Image.html#PIL.Image.mode)
2. Images must be of the same size (e.g. 1280 X 720p)
3. Images must be of the same file type (e.g. .png)

> Q: What do you mean by exact equality?

Equality is checked by subtracting pixels. Thus, if two pixels are exactly equal they will have the same pixel and the result will be a tuple of 0's.

> Q: Why should I care that only exact equality is implemented?

I'll give an example:
Say you have two images, which to the human eye appear identical. Let's say that image1 contains all pixels of value RGB(128, 128, 128) and image2 contains all pixels of value RGB(129, 128, 128). These should appear identical however when run through this system the two images would not be equivalent. Maybe this level of exactness is needed, maybe not, but please be aware that it exists.

#####Methods
Majority of the selenium wrapper methods rely on the idea that after clicking, or key pressing enter, it will cause a route change. Once the route has been changed, or a pop up is shown, a screenshot will be taken. If clicking on a certain element, or hitting enter, does not change the route please do not use one of the wrapper methods. If you do use a wrapper method on a non route changing element a screenshot will still be taken and duplicate images will exist in storage with different names. These would have to be manually deleted if they are unwanted.

#####Testing
Just to note, all tests have been done using OSX and have not be tested on any other Unix-like system or Windows. The saves module (specificly fsService) may also need some reworking in order to be functional on another Unix-like system or Windows.

##History

###Change Log

This project adheres to [Semantic Versioning](http://semver.org/).

####0.2.0 - unreleased
#####Added
- `collectImg` method to each service in the `saves` module in order to collect only a single image when needed
- `subtractPixels` method in `Differ` in order to subtract individual pixels; used by `getChange` method


#####Changed
- `collectImages` method in `fsService` now only grabs images from the `"environment/base"` directory specified in the config file
- `save` method in both services of the `save` module now saves to two locations: the first being the standard archive location in the environment directory (`"environment/view/date/function"`), the second being the base directory if specified to do so by the config file (`"environment/base/view/function"`)
- `equals` method in `Differ` now stores the difference between images to a class level scope
- `storeScreenshot` method in `Differ` will now archive images if they carry the same date; giving the old image an archived timestamp on it's location
- `locateImgForDiff` method in `Differ` now queries the `saves` module for the location of the image
- `sanitizeForDiff` method in `Differ` now returns a single value; the difference between the two images it retrieves or the value already stored
- `getDiff` method in `Differ` now does direct pixel access on the image for a ~5X boost in speed
- `getChange` method in `Differ` now does direct pixel access as well as combining highlighting into the subtraction of the original image for a ~4.6X boost in speed
- `run` method in `Differ` now defaults to what is specified in the config file for evaluating the diff and change image

#####Removed
- `getDiff` method in `Differ` has had 2 parameters removed `color` and `highlightDiff`; the `color` parameter has been moved to the config file and will only operate on defaulting to that, the `highlightDiff` parameter was too obscure and instead no color given results in not wanting a highlight as opposed to the extra boolean variable that specifies it
- `getChange` method in `Differ` has had the same 2 parameters removed as `getDiff` for the same reason

###TO-DO
- [ ] Add in missing info (Installation, setup.py url, etc.) once open source is greenlighted
- [x] Allow modifications of Differ via config instead of parameters
- [x] How to deal with Today changes in UI
- [x] Speed Improvements
- [x] Create environment and base directory to store images
- [x] Update Tests
- [x] Add Contributing.md
- [ ] Add Notes
- [ ] Add code comments
- [ ] Reformat to fit snake_case style
- [x] Update Readme

####Things that should be added to Readme
- [x] Add Changelog
- [x] Update how retrieval of images works
- [x] Add config args to applicable functions

####For Next Version


##License
Copyright (c) MediaMath, Inc. 2015

This is licensed under the [MIT License](http://opensource.org/licenses/MIT)
