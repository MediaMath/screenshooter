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
