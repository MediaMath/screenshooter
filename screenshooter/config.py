import os

#Global Parameters set here
pictureType = ".png"  # must contain period

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

#Saves

#Environment Directory
envDir = 'QA'

#Base Directory to diff images against
baseDir = 'Base'

#Save the screenshots taken on next run to the base directory
baseStore = True

#Amazon S3

#Amazon specific parameters
bucket = os.environ['S3BUCKET']  # "nameOfYourBucket"
profile = os.environ['S3USER']  # "yourUsername"

# Keys
accessKey = os.environ['S3ACCESSKEY']
secretKey = os.environ['S3SECRETKEY']

#FILESYSTEM

#User specific Parameters
username = os.environ['USER']   # "yourUsername"

# alter according to where you placed the files, must end in /
projectPath = "/Users/" + username + "/Documents/Projects/screenshot/"
imagePath = "/Users/" + username + "/Pictures/"
