import os
#User specific Parameters
user = os.environ['USER']   # "yourUsername"

#Global Parameters set here

baseImageDir = "/Users/" + user + "/Pictures/"
pictureType = ".png"  # must contain period

# alter according to where you placed the files, must end in /
baseProjectDir = "/Users/" + user + "/Documents/Projects/screenshot/"

#Amazon specific parameters
bucket = os.environ['S3BUCKET']  # "nameOfYourBucket"
profile = os.environ['S3USER']  # "yourUsername"

# Keys
accessKey = os.environ['S3ACCESSKEY']
secretKey = os.environ['S3SECRETKEY']


#Differ

#The color that the diff image will contain / set to None for no highlight
highlightColor = (0, 150, 255, 255)

#Run getDiff method by default
runDiff = True

#Run getChange method by default
runChange = True

#Capsule

#Which size to set the browser to
browserWidth = 1280
browserHeight = 720

#Default service to use
service = 'S3'
