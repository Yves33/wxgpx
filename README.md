# WxGPGPSport #

## Brief introduction. ##
wxGPGPSport (Wxpython General Purpose GPS for Sport) Is a general purpose software to read and analyse GPStracks generated by sport GPS. It was originally intended to visualize my windsurf sessions recorded by a canmore GP-102+ GPS (a cheap one). Although some other solutions are available on the net (GPSAr, GPSSpeedResults), wxGPGPSport is supposed to be much more flexible.

Below is a typical screenshot of the program displaying one of my windsurf session.

![Screenshot](https://github.com/Yves33/wxgpx/blob/master/wxgpgpsport.jpg)





- Windows XP (32 bits)
- Windows 7 (32 and 64 bits)
- OSX 
- Linux (32 and 64 bits)

## Features. ##
wxGPGPSport is written in python 2.x (not compatible with python 3.x) using the wonderfull wxPython, numpy and matplotlib toolkits. It is fully cross platform and has been successfully tested on windows XP, windows 7 (32 and 64 bits), mac OSX mavericks (10.9) and fedora linux (and should work without any problem on any other linux distrib). The software features:

  - Reading *.gpx 1.0 and garmin *.fit files
  - Saving *.gpx 1.0 and numpy arrays (*.npz)
  - Automatic display of GPS track on maps using false colors
  - Download maps from a variety of user defined tile servers
  - Nice graphical display of GPS track parameters
  - An easy system of plugins intended to extend its capabilities
  - A powefull python scripting system to manipulate and automate your GPS tracks analysis, import and export tracks through GPSBabel, ...


## How do I install It? ##
### Installing from source ###
Please refer to the file Readme.md inside the docs folder of the archive. Basically, you'll need a working python environment, with the following packages:
  - wxPython
  - PyOpenGL
  - lxml
  - matplotlib
  - numpy
  - python-dateutils
### Setup a python environment ###
If you need to setup a python environment, under the "releases tag", you should find an archive named PythonDependencies.zip, which contains all the files required to install a python-2.7 environment (windows machine), as well as an installation script ('install_requirements.bat').  
Once python and dependancies are installed, just download, extract, and double_click launch_xxx
  
  ### Installing binaries ###
  wxgpgpsport is now compatible with pyinstaller. Windows and macOSX binaries are available. Just download the files under the release tag, unzip and double click wxgpgpsport.exe (or wxgpgpsport on OSX).  
https://github.com/Yves33/wxgpx/releases/download/2017-07-14/wxgpgpsport-latest-osx.zip  
https://github.com/Yves33/wxgpx/releases/download/2017-07-14/wxgpgpsport-latest-win32.zip  
  

