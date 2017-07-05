[TOC]
 
1. GENERAL CONSIDERATIONS  
==========================

1.1 What does wxGPGPSport stands for?
-------------------------------------
wxGPGPSport stands for wx General Purpose GPS Sport.  

1.2 What programming language does it use? 
------------------------------------------
wxGPGPSport is written in python 2.7, but it should be compatible with any 2.x version.  
wxGPGPSport is not compatible with python 3.x  

1.3 What is your favorite color?
--------------------------------
Blue, no yellow! Arghhhh!

1.4 Why did you write it?
-------------------------
I bought a canmore GP102+ GPS (cheap) for windsurf and other outdoor activities. As I was not satisfied by the software provided (windows only, not flexible enough), nore by other software available on the net, I decided to see what I could code on my own.  
Originally, wxGPGPSport is an exercise to learn python+numpy+matplotlib. The project then slowly evolved towards a more integrated GPS app. Although it does not claim to be as powerful as X or Y, It is very flexible, and I had a lot of fun while developing this app.  

1.5 What licence is it released?
--------------------------------
wxGPGPSport is open source. I haven't decided a license yet. Let's say it's GPL.  

2. INSTALLATION
===============

2.1 How do I install it, The easy way.
--------------------------------------
Since version 20170630, the wxgpx is compatible with pyinstaller. You can therefore directly download a binary release (at least for windows) from the project home page (http://develandco.blog.free.fr) (github doesn't support files larger than 25MB).  
The binary version is named wxgpx-latest-xx.zip where xx is either win32 or osx
On windows, just download , unzip, and doubleclick on wxgpgpsport.exe 
On macOSX, just download, unzip and doubleclick wxgpgpsport.  
On linux, No binaries are available.

2.2 How do I install it, I already have a python 2.x environment (win and linux, and maybe MacOSX)?
----------------------------------------------------------------------------------------------------
If you already have a python environment installed, then you should install the following modules:
* python-dateutil
* numpy
* matplotlib
* lxml
* wxPython
* PyOpenGL WITH glut support (for font display). Although opengl is not mandatory, displaying traces is much faster with OpenGL

On windows platform, all required modules (see next paragraph) can be downloaded from the following url: http://www.lfd.uci.edu/~gohlke/pythonlibs/ Be sure to get the appropriate python version (cp27) and the correct architecture for your system.  
You can install them using:  
`pip install path/to/your/downloaded/package.whl`  
Alternatively, most of them can just be installed using:  
`pip install mypackage`  
However, on my python installation,  
`pip install lxml` will fail (pip install lxml==3.6.0 is ok)  
`pip install PyOpenGL PyOpenGL-accelerate` will not install GLUT properly.  

On linux platform, all required packages can be installed using you package manager (synaptic for debian, yumex or dnf for fedora)  

On OSX platform, it may be tricky to have all requirements to work... see corresponding section of this file.  
Once all required packages have been installed, extract wxGPGPSport archive.  
Note that the software should work even without OpenGL. However, all drawings on map will be slower.  

2.3 How do I Install it, I'm on windows and I do not have a working python 2.7 install?
---------------------------------------------------------------------------------------
- Download and install Python2.7 (64 bits or 32 bits depending on your system. I use 32 bits although my system is win64). Be sure to select the option “Add python.exe to Path” Python 3.x will not work!   
(64 bits) https://www.python.org/ftp/python/2.7.12/python-2.7.12.amd64.msi  
(32 bit) https://www.python.org/ftp/python/2.7.12/python-2.7.12.msi

- If you didn’t select “Add python.exe to Path” in installer, adjust system environment variables (right click on computer, advanced settings -> Environment Variables) and modify the system variable PATH (if you installed python in C:\Python27): PATH=C:\Python27\;C:\Python27\Scripts;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem

- Open a command window (Accessories->Command Prompt) and type:  
`python -m pip install --upgrade pip`

- Go to http://www.lfd.uci.edu/~gohlke/pythonlibs/ and download the following packages (Choose appropriate win32.whl or win_amd64.whl when available depending on your python version - Be carefull to download python 2.7 versions)  

    * setuptools-28.6.0-py2.py3-none-any.whl
    * pyparsing-2.1.10-py2.py3-none-any.whl
    * pytz-2016.7-py2.py3-none-any.whl
    * six-1.10.0-py2.py3-none-any.whl
    * setuptools-28.6.0-py2.py3-none-any.whl
    * cycler-0.10.0-py2.py3-none-any.whl
    * python_dateutil-2.6.0-py2.py3-none-any.whl
    * numpy-1.11.2+mkl-cp27-cp27m-win32.whl
    * matplotlib-1.5.3-cp27-cp27m-win32.whl
    * lxml-3.6.4-cp27-cp27m-win32.whl
    * PyOpenGL-3.1.1-cp27-cp27m-win32.whl
    * PyOpenGL_accelerate-3.1.1-cp27-cp27m-win32.whl
    * wxPython_common-3.0.2.0-py2-none-any.whl
    * wxPython-3.0.2.0-cp27-none-win32.whl

	(for 64 bits python version, replace win32.whl with win_amd64.whl)

- Install the downloaded packages (in that order) using the command window (Accessories->Command Prompt)  
`pip install path/to/your/downloaded/package.whl`

- You’re done. Your python environment should be about 250MB. Installation through conda/miniconda is also possible (see OSX section), but takes much more space on disk. Be careful that, if you use conda, you’ll still have to download PyOpenGL packages, as the one provided by pip do not include glut/freeglut.  

- If you downloaded the entire git repo, there will file named install_requirements.bat that will install all required packages. However, the script may fail to set the correct PATH, in which case you should refer to the beginning of this paragraph.

2.4 How do I install it, I'm on MacOSX (intel based) and I do not have a working python 2.7 install?
----------------------------------------------------------------------------------------------------
Yes, you have! OSX comes with preinstalled python. you should just take care that you installed the required modules. However, getting all dependencies to work with the OSX preinstalled python version might be tricky. Hence, I recommend using miniconda2 for OSX.

- Download and install miniconda2 :  
https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh

- Download and install wxPython for OSX :  
http://downloads.sourceforge.net/wxpython/wxPython3.0-osx-3.0.2.0-cocoa-py2.7.dmg

- Open a terminal and type:  
`conda install dateutil`  
`conda install numpy`  
`conda install matplotlib`  
`conda install lxml`  
`conda install pip`  
`conda clean --all`  
`pip install PyOpenGL PyOpenGL_accelerate`  

- If you do not want to install a new python environment, then the following should work (in a terminal - but I haven’t tested this method I would be happy to get some feedback)  
`sudo easy_install pip`  
`pip install dateutil numpy matplotlib lxml`  
`pip install PyOpenGL PyOpenGL_accelerate`  

- Once all required packages have been installed, extract wxGPGPSport archive.
NB: I'm not sure the program will work on PPC based macintosh. I would be happy to have some feedback

2.5 How do I install it, I'm on linux and I don't have a working python 2.7 install?
------------------------------------------------------------------------------------
Yes, you have (I'm not sure any recent distribution comes without python!)  
Please refer to you software manager (synaptic, yumex/dnf) to install appropriate python modules.  
Once all required packages have been installed, extract wxGPGPSport archive.

2.6 How do I run it?
--------------------
On windows: doubleclick launch_WIN.bat, or on wxgpgpsport.py if you python files are already associated with python executables (right click on *.py file, then select open with and browse to miniconda/python.exe or miniconda\pythonw.exe).  
On macOSX: doubleclick launch_OSX.command, or enter pythonw .gpgpsport.py in a terminal window.  
On linux  : open a command prompt and run python gpgpsport.py, or double click glaunch_linux.sh after chmod +x ./gpgpsport.sh), or associate *.py files with correct program python. Depends on your file manager.

3. BRIEF MANUAL
===================

3.1 Getting started:
-------------------
At startup, the software window is divided into 3 main panels:
* The top left panel (map panel) shows a view of the earth.
* The bottom panel (time panel) should be empty.
* The top right panel (plugin notebook) displays a notebook where a variety of plugins can display additional data computed from current file.
* The status bar will display information about the current point.
* In all program, the mouse wheel is emulated with Ctrl+left click and Ctrl+right click. I found it very convenient on a laptop without mouse wheel.

3.2 Opening a file: 
------------------
* Using the menu (File->Open), you’ll get a file selection dialog box where you can browse to the file you want to open.
* The program can read gpx files v1.0 (\*.gpx), compressed gpx files (\*.gpz, gpx.gz) and Garmin fit files (\*.fit). Be sure to select the right type of file in the file selector filter combo box.
* If no information is found concerning speed in the file, the speed is calculated according to GPS positions and time. Some other information (such as slope, course,…) are calculated by the software and everything is stored in a table (to learn more about this table, see plugins section, table and shell).

3.3 Using the map panel:
-----------------------
* The map panel displays the trace using false colors (red=very fast, blue=very slow). The background is dynamically fetched from various tile servers.
* A palette of tools is displayed in the upper left corner. The active tool determines which layer will handle mouse clicks and keyboard events. The default tool is the pan-zoom tool, which enables to translate and zoom the map.
* You can zoom in and out using the mouse wheel.
* You can translate using the mouse (left click+drag)
* You can right click on the map and choose an alternate map tile provider (some of them may not be working). The default provider is open street maps. It is possible to load tiles from google satellite, but you have to know that accessing these tiles outside the dedicated google api is illegal!
* You can use F10, F11 and F5 to zoom in, zoom out and refresh the current view (that is force the software to re-download map images)
* When you move the mouse, an indicator (green arrowhead by default) will indicate the current point (trace point closest to mouse pointer). The position of the cursor is updated in time panel (see below).
* You can customize the information displayed on map by double clicking on the map. A dialog will appear with several options:  
** key for color code: the value that will be used to calculate false colors for track representation. False colors vary from blue (for minimum) to red (for maximum). If you do not want false colors, then select none in the drop down combo box. At the present time, the palette cannot be modified without using custom scripts (see the script 'palette')  
** line width: the width of line used to display gps track and current indicator. Default is 2.  
** custom color: the color used to draw track if 'use custom color' is selected as the key for false colors.  
** indicator style: you can choose between dot, arrowhead, vector from and vector to current point. If you choose arrowhead or vector, you'll need to specify a key for the direction (arrowhead/vector) and a key for vector length (vector only).  
** custom color: the color to use to draw indicator.  
** key for angle and key for magnitude: the values used to determine arrowhead/vector orientation and vector magnitude.  
** zoom factor: used to adjust vector length on map.  
** draw label check box: whether to draw or not a label nearby to current point.  
** key fro label: the value to be used for label.  
** label position: an x,y couple indicating the relative position of the label.  

3.4 Using the time panel:
------------------------
* The time panel displays a graph where speed (by default) is plotted against time (by default).  
* The mouse wheel on X- and Y- axis enables you to zoom at some specific portion of the curve (it may be necessary to click on the panel in order to give focuss to this panel).  
* Left click+drag on X-axis and drag to displace the area represented.  
* Double click on graph to choose graph parameters. Most parameters should be pretty self-eplanatory. You can plot up to 3 overlapping graphs with same X-axis.  
* When you move the mouse, the vertical cursor (red) moves to follow the mouse. On map panel, the current position (green arrowhead by default) will follow the position of the cursor.  

3.5 Selecting datas in time panel:
----------------------------------
* You can select a small range of data by using left click+drag in time panel curve. The selected area will appear grey.  
* Using right click, you can enable/disable the selected points (or the non-selected points). Once a selection is disabled, all panels are updated (including plugins) and all calculations in plugins are restricted to selected datas.  
* Use left click (without drag) to empty selection.  
* To enable all points, simply enable all selected points (whatever the selection), then enable all non-selected points. Alternatively, select no point and use “enable non-selected points”.
* Delete points is reserved for future use and should not be used. As wxGPGPSport does not save fit or gpx files, your files will not de damaged if you use this option. (\*.npz files will lose the points that you deleted).

3.6 Saving files:
----------------
* wxGPGPSport saves the files as standard numpy arrays (*.npz). This files can then be opened in with the standard file->open menu. All columns in table are saved in the npz file.
* wxGPGPSport can save the files as GPX (*.gpx) files, with the possibility to additional datas as extensions.

3.7 Changing units:
------------------
* By selecting GPX->Units menus, a popup dialog will appear where you can change units for the current file.
* The program only works with International units (SI: meters, seconds, m/s,…). All calculations are made using these units, and converted to appropriate units using a conversion factor immediately before being displayed.  
For instance, if you ask for km/h as units, datas will be multiplied by 3.6 (1m/s=3.6 km/h)
* Unit consistency is not checked: you can use seconds (s) for the distance, and nautic miles (nq) for duration!
* For each data in table, a combo box allows you to choose the unit you whish.

3.8 Using replay:
----------------
* If a selection is made in time panel, then you can replay the selected part of the trace using GPX->replay menu. The Replay speed is an arbitrary number representing the interval between two time points, in ms.
* You can stop the replay by re-selecting the menu GPX->replay
* During replay, the current position is not updated according to mouse position.

4. PLUGINS AND SCRIPTS
======================

The program uses a simple plugin architecture. There is currently no option in the program to select which plugins are loaded If you want to disable some plugins, just add an underscore to the name of the appropriate *.py file in plugins directory.  
Plugin tabs can be moved to reorder them, but they can also be docked on the side of the window so that several plugins can be displayed at the same time.

4.1 Gauge and Meter plugin:
---------------------------
* The gauge and meter plugins displays a dynamic color gauge or speedmeter representing speed (or any other parameter)
* Double click to select parameters
* these two plugin provide a Screenshot(path) command (see 4.8 Shell plugin) that allows you to save their state as images (for later embedding in video software through universal subtitle file)

4.2 Statistics plugin:
----------------------
* The statistics plugin displays some information about the current file. It should be pretty self-explanatory
* No user interaction is possible with this plugin (beside copying text)

4.3 ScatterPlot plugin:
-----------------------
* The scatter plot plugin displays X-Y plots of any numeric value in table. The same controls as in time view are available:
* mouse wheel in X- and Y- axis to zoom
* left click+drag in axis to move the region of interest
* double click to select plot parameters

4.4 Polar plugin: 
-----------------
* The polar plot plugin displays theta-radius plots of any numeric value in table. Usually, course is used for theta, but you may feel free to use any other value.
* Mouse wheel in graph to zoom
* Double click to select plot parameters

4.5 Histogram plugin:
---------------------
* The histogram plugin displays an histogram of a given measurement (default is speed).
* Mouse wheel on graph to zoom
* Left click+drag to move the region of interest
* Double click to select histogram parameters, such as number of columns.

4.6 Measurement plugin:
-----------------------
* The measurement plugin can be used to measure the width and height of the entire map panel.
* When the Measure tool is selected on map (the pen and meter icon), you can use left click to add points to default path. The path is drawn on map and its length is automatically updated in the measure plugin panel. You can delete points from the path by right clicking on points (when measure tool is selected).

4.7 Table plugin:
-----------------
* The table plugin displays a table with all values that were imported from the current file and the values calculated (either automatically, or by user)
* The OK column will allow you to select/deselect individual points (unselected points are excluded from calculations. This is the same as enabling-disabling datas using the time view
* You can directly edit a value, and the corrected value will be updated in time panel, map panel and individual plugins
* You can select individual cells, multiple cells with shift+click, entire columns or entire lines by clicking in column/line headers.
* Clicking on selected column header will enable you to suppress columns, insert columns, and sort the entire table according to this column values (both ascending and descending sort can be made.
* Clicking on row header will enable you to enable/disable the selected (or the non selected) data points.

4.8 Waypoints plugin:
---------------------
* The waypoints plugin can be used to select only parts of the track based on specific waypoints, also called “doors” (like in a ski slalom). In order to use the waypoints plugin, you have to use the waypoints tool on the map (the flag icon).
* You can draw directly the doors (waypoints) on the map by left clicking then dragging the mouse to define two points. A waypoint is passed each time the track crosses the segment defined by the waypoint.
* You can remove waypoints by right clicking on the dots that materialize the waypoints.
* Each time you add a waypoint, the list of waypoint is updated in that waypoints panel. You can copy it to later save this list. Pasting a list of waypoints in this panel (followed by enter) will update the doors portion on the map.  
When you click on analyse button, the software will ask you the list of waypoints to be crossed. Just enter a coma separated list of waypoints number in the order you want to cross them. The software will then extract the suitable track portions and display some information on these portions. If requested (default behavior), the software will disable any point outside the suitable track portion.


4.9 Shell plugin:
-----------------
* The shell plugin is simply a python shell that gives you access to the internals of the program. Using the shell plugin, you can manipulate your gps track as you want.
* The table holding all datas is a numpy ndarray that can be accessed through the gpx variable.
All methods from the gpx objects are available, however, in most cases, you’ll only use the following ones:
```python
def append_column(self,key,typ):
def drop_column(self,key):
def move_column(self, oldkey, newkey):
def append_row(self, values):
def drop_row(self,rownum):
def get_last_row_idx(self):
def get_last_col_idx(self):
def get_headers(self):
def get_header_names(self):
def get_header_types(self):
def has_field(self,field):
def get_col_count(self):
def get_row_count(self):
def set_unit(self,key,value):
def get_unit(self,key):
def get_unit_sym(self,key):
def get_unit_desc(self,key):
def get_scale(self,key):
def set_scale(self, key, value):
def hv_distance(self):
def hv_course(self):
def hv_speed(self,skipnan=True):
def slope(self,conv=10,skipnan=False):
def hv_nearest(self, lat, lon):
def duration(self):
def hv_pace(self,dist,ahead=False):
def sort_asc(self,key):
def sort_desc(self,key):
def get_top_n(self,key,n):
def ok(self):
def discard(self):
def nanmean(self,a):
```

- you can easily access the individual table columns using the following syntax:

```python
gpx['key']      # or, for a given cell gpx['key'][rowidx]
gpx['lat'][0]   # gives the latitude of the first point in file
gpx['lat'][10]  # gives the latitude of the 10th point in file
gpx['lat']      # returns an array holding all latitudes
```

- The data are returned in SI units (remember that wxGPGPSPort only works in SI units, then converts to user defined units).  There is a workaround to access scaled values, which is to index you array with a tupple (key, scaled):
```python
gpx[('speed',1)] # returns speed in user defined units
gpx[('speed',0)] # returns speed in SI units
```

- You can also filter out disabled values using a 3 element tupple (key, scaled, enabled)
```python
# both formulations are equivalent
# return speed of all enabled points in user units
gpx[('speed',1,1)]
gpx['speed'][np.where(gpx['ok']==1)]*gpx.get_scale('speed')
```

_Sounds complicate!!_ So here are a few exemples:
- Calculate maximum seed in SI units:
```python
print "vmax: ", gpx['speed'].max(),"m/s"
```

- Calculate average speed in user units:
```python
print "average speed: ",                \
gpx['speed'].mean()*gpx.get_scale('speed'), \
gpx.get_unit_sym('speed')
```
or, using tupple indexing:
```python
print "average speed: ",gpx[('speed',1)].mean(),gpx.get_unit_sym('speed')
```

- Calculate the average speed for points above 3m/s:
```python
indices = np.where(gpx['speed']>3)
print "average above 3m/s: ", gpx['speed'][indices].mean()
```

or, skipping the intermediate array:
```python
print "avg above 3m/s: ", gpx['speed'][np.where(gpx['speed']>3)].mean()
```

- Calculate the average speed for points below 3kts using tuple indexing:
```python
gpx.set_unit('speed', 'kts')
print "avg below 3kts: ",gpx[('speed',1)][np.where(gpx[('speed',1)]<3)].mean()
```

- Selecting only points where speed is above 10km/h:
```python
gpx.set_unit('speed', 'km/h')
gpx['ok'][np.where(gpx[('speed',1)]<10)]=False
sh.upd()    # send update signal to all panels and plugins
```

* Creating and deleting new columns:
You can create an extra column in the table and manipulate its values by providing a name and the type of data (floating point numbers, in most cases), then rename or delete the column.
```python
gpx.append_column('accel', 'float')
gpx['accel']=np.ediff1d(gpx['speed'],0)/gpx['deltat']
gpx.move_column('accel', 'acceleration')
gpx.drop_column('acceleration')
```

* You can write all your instructions in a script then run the script using “run script…” button in shell plugin.

* Any file in the scripts folder named Startup.py will be executed immediately after program starts.

* the script module gives you access to the following objects/commands:
```python
gpx         # the array holding all values, with associated methods.
mapview     # the map object. All methods from WxMapWidget are available|
timeview    # the time object. All methods from WxTimeWidget are available
app         # the application itself. All methods from wx.Panel are available, but you’ll mainly use app.OpenFile(filename) and app.SaveFile(filename)
sh          # the shell by itself. Usefull commands may include sh.clear() to clear the shell, sh.run(filename) to run an external python file, sh.copy(text) to put text in the clipboard, and sh.upd() to force an update of map, time and plugin panels
WxQuery     # access to simple gui    (see the moule WxQuery in modules folder)
```
For instance, to clear the cache of downloaded tiles, you may enter:
```python
mapview.TruncCache(0,0)
```

4.10 Internals:
--------------
The internal columns used for calculation in table are listed below: do not modify these columns!! Columns starting with underscore are reserved for program and should not be used in your scripts (or read only). Columns starting with underscore are ignored when file is saved in npz format (and I advice not to export them in gpx files)
```python
ok          # is point marked as valid or not?
time        # time of recording. if absent from gpx file, will be automatically generated
lat         # latitude
lon         # longitude
distance    # cumulative distance since beginning of recording
idx         # the index of point in file. Usefull for scripting
deltat      # interval (s) between two consecutive points
deltaxy     # distance (m) between two consecutive points
duration    # cumulative time(s) since beginning of recordings
```

The following columns may be either read (when available) or calculated from gps:
```python
speed       # the instantaneous speed. Doppler (if available) or computed from gps data
course      # the course of the ship, in degrees
```

Other columns imported from gps/fit file may include:
```python
ele             # elevation data
magvar          # magnetic orientation of gps
hr/heartrate    # heart rate
cadence         # cadence
power           # power
temp            # temperature
distance        # distance may be overridden by internal distance calculation
```
if elevation (‘ele’) data is found, the soft will calculate ‘slope’ value (inaccurate)
Some other variables are created by some scripts, such as:
```python
wind_dir            # wind direction, in degrees (North=0)
wind_avg            # average wind speed
wind_mini           # minimal wind speed
wind_maxi           # maximal wind speed
app_wind_avg        # apparent wind speed
app_wind_dir        # apparent wind direction (buggy)
tack                # port and starboard tack (one is 1.0, the other -1.0)
```


4.11 Exemple scripts:
---------------------

I’ve tried to provide some scripts examples. Some are heavily commented, some other are not!

- Average_above_speed  
A very simple script showing how to use wxQuery to display a simple Graphical user interface and output some results to shell window.

- Windsurf_statistics  
A More complex example that display complete statistics about windsurf session. Informations are output to the shell window. A summary of main values is copied in the clipboard so you can paste it in an excel spreadsheet.

- Time_shift  
A very simple script showing how to use wxQuery to alter the time of gpx points in current file.

- Winds_up_import  
This script is able to import the wind speed and direction from a “saved” html file. To use it, you must first go to winds-up site, then reach the statistics page for the date and spot where your gps file was recorded (for instance http://www.winds-up.com/spot-hourtin-lac-windsurf-kitesurf-25-observations-releves-vent.html?date=2017-01-13 ).  
The script will automatically parse the file and generate four columns in current file:  
```python
wind_avg     # average wind speed  
wind_mini    # minimal wind speed  
wind_maxi    # maximal wind speed  
wind_dir     # wind direction, in degrees, that is the direction the wind is pointing to north=0. South winds points towards the North
```

- Wind
A very simple plugin to enter the values of speed when you can’t or don’t want to download from winds-up. 
The script will generate four columns in table, as  Winds-up_import.py
```python
wind_avg      # average wind speed  
wind_mini     # minimal wind speed  
wind_maxi     # maximal wind speed  
wind_dir      # wind direction, in degrees, that is the direction the wind is pointing to (north=0. South winds points towards the North)
```

- Palette
The palette script is a proof of concept. It shows you how to monkey patch (https://en.wikipedia.org/wiki/Monkey_patch) the software to use matplotlib palettes to display the gps track.

- Batch_process_template
As indicated, it is a template showing how to batch process files. You’ll have to modify it so that it fits your needs.

- Apparent_wind_VMG
Very buggy for now… The script calculates apprent wind (but not VMG for now). There is a bug which causes the apparent wind to be oriented 180° during the jibe.

- Jibe_analysis
Still unstable. performs some basic statistics about jibe. You need to geive wind direction in degrees and the number of points for smoothing (convolution).
two columns are created:
```python
tack          # the current tack, ranging from -1.0 to 1.0   
conv_speed    # the convolved (ie smoothed) speed
```  

- GPSBabel_open
Uses GPSBabel to directly open convert foreign files to xml and open them in wxgpgpsport.  
GPSBabel must be installed on your system.
You may need to edit the script to correct the location of gpsbabel program.  

- GPSBabel_export
Uses GPSBabel to directly export to foreign file format. Be aware thta not all formats are writable:  
GPSBabel must be installed on your system.
If you convert to kml, you have the option to open the file in google earth immediately.
You may need to edit the script to correct the location of gpsbabel (and google earth) programs.  

 5. ABOUT THIS DOCUMENT
=======================
This document is written in markdown and converted to html using stackedit (https://stackedit.io/editor#411)
 and escape html entities(http://www.htmlescape.net/htmlescape_tool.html).

 6. TODO LIST
=============

6.1 Main program
----------------
* CSV/TSV import with time format string.  
import heartrate and other info from other captors.  
timeshift should be possible to precisely adjust datas.
* TCX file import.  
* List of plugins that should not be loaded (through \*.ini file).  
* On demand plugin loading and unloading.  
* GPX1.1 import.  
* Panel or entire frame screenshot (accessible by script) (app->plugin("name")->Screenshot(path))
(already implemented in wxGauge.py and wxSpeedmeter.py)

6.2 Scripts
-----------
* Correction of elevation data using google elevation api.  
https://maps.googleapis.com/maps/api/elevation/json?locations=lat1,lon1|lat2,lon2|lat3|lon3  
* Automatic wind direction calculation - abandonned feature. An estimation can be done using
`np.mod(gpx[('course',1,1)],180).mean()+90`
* Jibe/tack analysis, with Vmax, Vmin, jibe duration (time before we recover a given speed), jibe curve diameter (still buggy)
* Apparent wind and VMG (still buggy)
* \*.srt (subtitle rip) export for use with sport camera. Synchronisation required
* \*.usf (universal subtitle format) export *with* pictures for use with sport camera.

6.3 Plugins
-----------
The code to load working can also work in the frozen version (provided you copy the plugins folder to frozen app root folder).
In order to get the plugins to work, the following extra modules are imported by pyinstaller.
```python
import wx.lib.agw.peakmeter as pm
import wx.lib.agw.speedmeter as sm
import wx.html2
from wx.py import shell
import  wx.grid as  wxgrid
```

If you want to develop plugins that need to import extra python modules, you'll have to install a full python environment (in any case, installing a full environnement is better to develop plugins and scriots.