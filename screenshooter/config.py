import os

#Global Parameters set here
picture_type = ".png"  # must contain period

#Differ

#The color that the diff image will contain / set to None for no highlight
highlight_color = (0, 150, 255, 255)

#Run get_diff method by default
run_diff = True

#Run get_change method by default
run_change = True

#Capsule

#Which size to set the browser to
browser_width = 1280
browser_height = 720

#Default service to use
service = 'S3'

#Saves

#Environment Directory
env_dir = 'QA'

#Base Directory to diff images against
base_dir = 'Base'

#Save the screenshots taken on next run to the base directory
base_store = True

#Amazon S3

#Amazon specific parameters
bucket = os.environ['S3BUCKET']  # "name_of_your_bucket"
profile = os.environ['S3USER']  # "your_username"

# Keys
access_key = os.environ['S3ACCESSKEY']
secret_key = os.environ['S3SECRETKEY']

#FILESYSTEM

#User specific Parameters
username = os.environ['USER']   # "your_username"

# alter according to where you placed the files, must end in /
project_path = "/Users/" + username + "/Documents/Projects/screenshot/"
image_path = "/Users/" + username + "/Pictures/"
