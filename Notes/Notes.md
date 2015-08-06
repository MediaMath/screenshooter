#Notes

##Attempted Speed Improvements

###Use `Image.getpixel()`
> This method will be used as the baseline for comparison of speed improvements.

Using the `PIL` library from `Pillow` the methods `Image.getpixel()` and `Image.putpixel()` were used to highlight the diff and change images.

####Diff
The following was the idea:

1. subtract the images (`Image.difference()`)
- invert the image (`Image.invert()`)
- loop through the pixels by (x, y) coordinates and check the pixel via `Image.getpixel()`
- if pixel should be modified use `Image.putpixel()`

```python
diff = ImageChops.invert(diff)
for x in range(diff.size[0]):
	for y in range(diff.size[1]):
		if diff.getpixel((x, y)) == (255, 255, 255, 255):
			continue
		diff.putpixel((x, y), (0, 150, 255))
Image.blend(diff, img1, 0.2)
```

####Change
The following was the idea:

1. subtract the images (`Image.difference()`)
- loop through the pixels by (x, y) coordinates and check the pixel via `Image.getpixel()`
- if pixel should be modified use `Image.putpixel()`
- then subtract the original image from this merged image and invert the result
- then loop through and apply the highlight per pixel if required

```python
invertOg = ImageChops.invert(originalCopy)  # invert the original image
mergingImg = invertOg.copy()								# copy the inverted original image


#This nested loop will run through the inverted original image copy
#and place on it the pixel from the diff image so long as the
#diff image pixel is not black (black means no difference)
for x in range(mergingImg.size[0]):
	for y in range(mergingImg.size[1]):
		pixel = diff.getpixel((x, y))
		if pixel == (0, 0, 0, 0):
			continue
		mergingImg.putpixel((x, y), pixel)

#Once all the pixels from the diff image have been applied, subtract the pixels
#from the inverted original image with the newly merged diff inverted original image
#then invert that result
finalDiff = ImageChops.invert(ImageChops.difference(mergingImg, invertOg))

#This nested loop will run through that final diff image and apply the highlight
#to any color other than white (after being inverted white means no difference)
for x in range(finalDiff.size[0]):
	for y in range(finalDiff.size[1]):
		if finalDiff.getpixel((x, y)) == (255, 255, 255, 255):
			continue
		finalDiff.putpixel((x, y), (0, 150, 255))

Image.blend(finalDiff, img1, 0.2)
```

---

###Use `Image.point()`

Using the `PIL` library from `Pillow` an attempt was made to to use the `Image.point()` function to speed up the highlighting of the diff image since it's an O(n^2) operation.

The following was the idea:

1. subtract the images (`Image.difference()`)
- invert the image (`Image.invert()`)
- using a function or lookup table: if the color was not `RGBA(255, 255, 255, 255)` then change the color to default

Quick reference on how `Image.point` works:

- if using a function (usually a lambda) it computes that value for a single band intensity value and then applies that across all bands e.g. `lambda x: x * 3` would run through each band from 0 - 255 and multiply that intensity value by 3; as far as I know you can't specify which band to apply the function to, it just applies it to all bands.
- if using a lookup table it resets the values at that spot in the band - the lookup table is as follows `[0, 1, 2, 3, ... , 255, 0, 1, 2, ..., 255, 0, 1, 2, ..., 255]` following the specification of RGB or RGBA i.e. the first 0 - 255 is R, the second is G etc. So if the value 2 in the R band was wanted to be set to 155 the lookup table would then have to be rewritten as [0, 1, 155, 3, ..., 255, 0, 1, ..., 255, 0, 1, ..., 255].
- The above information was obtained from use as well as (stackoverflow)[http://stackoverflow.com/questions/2181292/using-the-image-point-method-in-pil-to-manipulate-pixel-data]

The resulting code in testing came out to the following:
```python

#These band functions returned a lookup table to work with the Image.point function
#each band was set with an array value of that bands default color e.g. for an RGB(0, 150, 255)
#the setRedBand() function applies 0 to every value in the band except the last one - the reason for this
#is because we want the color RGB(255, 255, 255) to still be that color, we only want to highlight the portions that have
#been altered
def setRedBand():
	band = [0] * 255
	band.append(255)
	return band

def setGreenBand():
	band = [150] * 255
	band.append(255)
	return band

def setBlueBand():
	band = [255] * 255
	band.append(255)
	return band

img = diff

#The image is split into bands here to make it easier to understand how it works,
#they could just as easily be combined into a single Image.point() function on the whole
#image, just make sure to account for the alpha(A) band if required

diff = diff.split()
# diff[0].show()
# diff[1].show()
# diff[2].show()
# diff[3].show()
out = diff[0].point(setRedBand())
# out.show()
diff[0].paste(out)
out = diff[1].point(setGreenBand())
# out.show()
diff[1].paste(out)
out = diff[2].point(setBlueBand())
# out.show()
diff[2].paste(out)
diff = Image.merge(img.mode, diff)
# diff.show()
Image.blend(diff, img1, 0.2).show()
```

Output:
![Image.point() output](./image_point_screenshot.png)

As you can see the O in Google for some reason is pink even though I told everything to be RGB(0, 150, 255). This is due to the way that bands work. Since each band holds a range of intensity values from 0 to 255 when specifying what color to make the pixels only one band is being referenced. So when I want RGB(1, 6, 24) to be RGB(0, 150, 255) and I tell the R band at 1 to be 0 it means that every pixel that contains an R band of 1 will be 0: e.g. RGB(1, 2, 3) converts to RGB(0, 2, 3) as well even though thats not what was wanted to happen.

Therefore what is happening in this case is that all the bands are told to maintain 255, so any pixel with a 255 band in it will maintain that band e.g. (255, 124, 246) will result in (255, 150, 255) when what was really wanted was the result of (0, 150, 255).

The only way to alleviate this problem is if each band knew about the other bands so that when all the bands merge together only the pixel (255, 255, 255) would not be the default color. The problem with accomplishing that is the `Image.merge` function would have to be overwritten, but that's assuming that how it works is understood to the point where it can be modified; and even that assumes that each band can know about the others.



###Use `Image.getdata()`

Using the `PIL` library from `Pillow` an attempt was made to to use the `Image.getdata()` function to speed up the highlighting of the diff image since it's an O(n^2) operation.

The following was the idea:

1. subtract the images (`Image.difference()`)
- invert the image (`Image.invert()`)
- grab all the pixel values of the image using `Image.getdata()`
- convert this sequence into a list that can be manipulated
- put the manipulated sequence back into the image via `Image.putdata()`

Quick reference on how `Image.getdata()` works:

- It returns an object of type `ImagingCore` which refers to some `PIL` object that is used internally
- This object must then but constructed into a list i.e. `list(ImagingCoreObject)` since for whatever reason, and although it may work via access like a list, it will not allow an alteration on the data but once converted into a list will
- once the data has been altered accordingly its sequence of pixels will be changed to the sequence of pixels given to the method `Image.putdata()`

```python
diff = ImageChops.invert(diff)
sequence = list(diff.getdata())

for pixel in range(len(sequence)):
	if sequence[pixel] == (255, 255, 255, 255):
		continue
	sequence[pixel] = (0, 150, 255, 255)
# print(sequence)
diff.putdata(sequence)
# Image.blend(diff, img1, 0.2).show()
```

**THIS METHODOLOGY WORKS**, the reason for it not being implemented is because it is slightly slower than the current implementation. This method is ~4 times faster than the `Image.getpixel()` method.

Since the information from `Image.getdata()` must be converted to a list this costs more time than a direct access on each pixel. Pair the extra time of converting to a list with the fact that an O(n^2) operation (`Image[x, y]`) that must loop through some constant x number of pixels is equivalent to some O(n) operation that loops through the same x number of pixels means that the O(n^2) operation may end up being faster. In this instance it is.


##Current Implementation

###Diff Image

Using the `PIL` library from `Pillow` an attempt was made to to use direct access `Image[x, y]` to speed up the highlighting of the diff image since it's an O(n^2) operation.

The following was the idea:

1. subtract the images (`Image.difference()`)
- invert the image (`Image.invert()`)
- loop through the image via x coordinates and again via y coordinates and get the pixel at that [x, y]
- manipulate the pixel accordingly

Quick reference on how direct access works:

- It would be best to store the width and height of the image before enabling direct pixel access and so that the values don't have to be retrieved each time: this is done via `width = Image.size[0]` and `height = Image.size[1]`
- In order to enable direct access of pixels the Image must first be loaded via `Image.load()` this returns a PixelAccess object
- The modification of the PixelAccess object that is assigned via `Image.load()` will directly effect `Image`
- Once each pixel has been modified accordingly just reference `Image` again and it'll have all the modifications

```python
width = diff.size[0]
height = diff.size[1]
diff = ImageChops.invert(diff)
pix = diff.load()
for x in range(width):
	for y in range(height):
		if pix[x, y] == (255, 255, 255, 255):
			continue
		pix[x, y] = (0, 150, 255)
# diff.show()
# Image.blend(diff, img1, 0.2).show()
```

**THIS METHODOLOGY WORKS**, it is ~5 times faster than the `Image.getpixel()` method

###Change Image

Using the `PIL` library from `Pillow` an attempt was made to to use direct access `Image[x, y]` to speed up the highlighting of the change image since it's an O(n^2) operation.

The following was the idea:

1. subtract the images (`Image.difference()`)
- invert the image (`Image.invert()`)
- loop through the image via x coordinates and again via y coordinates and get the pixel at that [x, y]
- manipulate the pixel accordingly, combining color change and subtraction of original Image into a single nested loop

Quick reference on how direct access works:

- It would be best to store the width and height of the image before enabling direct pixel access and so that the values don't have to be retrieved each time: this is done via `width = Image.size[0]` and `height = Image.size[1]`
- In order to enable direct access of pixels the Image must first be loaded via `Image.load()` this returns a PixelAccess object
- The modification of the PixelAccess object that is assigned via `Image.load()` will directly effect `Image`
- Once each pixel has been modified accordingly just reference `Image` again and it'll have all the modifications

```python
mergingImg = ImageChops.invert(self.originalImg)

		width = mergingImg.size[0]
		height = mergingImg.size[1]

		diffPixels = diff.load()
		mergePixel = mergingImg.load()

		for x in range(width):
				for y in range(height):
						diffPixel = diffPixels[x, y]
						if diffPixel != (0, 0, 0, 0):
								if self.subtractPixels(diffPixel, mergePixel[x, y]) == (0, 0, 0, 0):
										mergePixel[x, y] = (255, 255, 255, 255)
								else:
										if color is None:
												continue
										mergePixel[x, y] = color
						else:
								mergePixel[x, y] = (255, 255, 255, 255)

		Image.blend(mergingImg, self.originalImg, 0.2)
```

The above code needs some explanation since it differs greatly from diff in reasoning.

The idea of the change image is to subtract out the original image from the diff image so that only the things that have changed will appear. `diffPixels` is the PixelAccess object from the diff image, while `mergePixel` is the PixelAccess object from the original image inverted, this will be the image that everything is applied to. The reason the original image is inverted is due to the way that the subtraction of pixels worked on the diff image, so that when a new subtraction of pixels between the diff image and the original image happens it'll work correctly.

**Note**: This assignment `diffPixel = diffPixels[x, y]` only works for accessing information, if the information is going to be altered i.e. `diffPixel = (255, 255, 255, 255)` it will not work

The first check is to see if the diff pixel is not black (black means that there is no difference between the two images) i.e. this is checking if there is a difference between the two images. The first nested check attempts to see if the two pixels are identical and if they are applies a white pixel (normally this would be a black pixel and then the image would have to be inverted, so instead the inversion is being applied per pixel). If the pixels are not identical it applies the color pixel if it has been set. If the diff pixel is black then a subtraction between the mergePixel and the original image pixel happens, however, since the mergePixel at this position has not been altered yet the two pixels are guaranteed to be identical, thus instead of performing the costly subtraction the pixel is marked as black (for no difference) and then inverted to white (to save time it is just set to white).

**THIS METHODOLOGY WORKS**, it is ~4.6 times faster than the `Image.getpixel()` method
