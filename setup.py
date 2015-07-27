from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name = 'screenshooter',
    packages = ['screenshooter'],
    version = '0.1',
    description = 'Screenshooter allows one to obtain a difference between a current UI layout and a previous UI layout via screenshots.',
    long_description = 'Screenshooter contains a wrapper on Selenium Webdriver that will help automate the testing of various situations while taking a screenshot of various portions of the UI. Once screenshooter has obtained all the screenshots from the tests a method may be called to compare them against previous versions of that same UI. If there is a difference the updated image is saved along with the difference / change.',
    author = 'Elan Moyal',
    author_email = 'emoyal@mediamath.com',
    url = '',
    download_url = '',
    license = 'MIT',
    classifiers = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Programming Language :: Python :: 3.4', 'Topic :: Multimedia :: Graphics', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing', 'Topic :: Software Development :: User Interfaces'],
    install_requires = required
)
