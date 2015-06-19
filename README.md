#Screenshot

Some general rules of thumb:
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
- All mentions of location refer to location within the multi-dimensional dictionary

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

The third and fourth parameters are locations to the images that the diff is going to be of.

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
The getChange method operates the same way as the getDiff function with a greater reliance on original and modified images. This method will only display the diff of the image that changed from the original thus it is crucial to make sure the original and modified images are correct or the correct result won't be returned and at best inverted.

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
- [ ] Test everything
- [ ] Error Security
