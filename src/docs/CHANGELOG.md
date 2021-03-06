###(September 07,2017)
* Fixed bug in wxmappanel.DrawLocalTile function (incorrect tile frame when tile image is not available)
* Added SaveBuffer(buff,filename,imgtype) to wxGLArtist and wxDCArtist (untested)
* Added CacheAll(maxzoom) to download all zoom levels for a given area (well... only generates a list of tiles.)
* Changed name of Startup script to onStartup.py and moved implementation to app (so the plugin is now executed after all plugin have loaded)
* Created onOpenFile.py and onSaveFile.py which are executed immediately after opening aand before saving a file.
(Not tested in frozen verion. An onOpenFile.py script could for exemple convert from GMT to local time, set appropriate units...)
* Fixed documentation, now generated through python markdown module

###(July 28,2017)
* Set window title to reflect current file path
* Fixed units for course in wxMeasure plugin (not configurable)
* Modified proof of concept script to create an overlay on map and draw stuff on it (test_overlay.py and liboverlay.py)
* Added a proof of concept script to create patches on time view (test_patches.py)
* Added a demo script to create an interactive frame with controls and buttons (test_interactive_frame.py)

###(July 14,2017)
* Jibe analysis script now calculates the downwind distance lost
* Minor bugfix in gpxobj.py (recomputes 'idx' column each time points are deleted). This allows reopening npz files that were not properly saved.
* 'idx', is not exported anymore in npz files.
* Added an __init__.py file to script folder to be able to import from this folder (from scripts import whateveryouwant)
* __init__.py, *.pyc and lib*.py files are now ignored from script list
* Added a proof of concept script to create an overlay on map and draw stuff on it (test_overlay.py and liboverlay.py)

###(July 06,2017)
* wxmappanel.Haversine (lat1, lon1, lat2, lon2) now returns tupple (distance, course).
* In measure plugin,
    - dump cumulative distance, "as the crow flies" distance and course.
    - dump individual segment length and course.

###(July 04,2017)
* GPSBabel import script
* GPSBabel export script (with google earth visualisation option if kml is chosen)
* Add previously executed scripts to script list in shell plugin (still minor bugs in remembering last executed script)
* Fixed wxMapBase.TruncCache(size,count)
* Fixed wxquery 'wxfile' (Filter for non existing files is now '' instead of None)
* Fixed bug that prevented loading gpx when Time info displayed 1/10th of seconds
* Renamed (CAPITALIZE)and updated documentation
* Created this CHANGELOG file.

###(July 02,2017)
* Initial binary releases for OSX and win32
* Adapted code to be compliant with PyInstaller-3.2
* Updates in documentation
* Reorganisation of github repo structure
