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
#Options are (S3, FILESYSTEM)
service = 'S3'

#Saves

#Collect all images by default
collect_all_images = False

#Environment Directory
env_dir = 'QA'

#Base Directory to diff images against
base_dir = 'Base'

#Save the screenshots taken on next run to the base directory
base_store = True

#Amazon S3

#Amazon specific parameters
bucket = os.getenv('S3_BUCKET')  # "name_of_your_bucket"
profile = os.getenv('S3_USER')  # "your_username"

# Keys
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

#FILESYSTEM

# alter according to where you placed the files, must end in /
project_path = os.path.expanduser("~/Documents/Projects/screenshot/")
image_path = os.path.expanduser("~/Pictures/")
