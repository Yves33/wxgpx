

###(July 14,2017)
* Jibe analysis script now calculates the downwind distance lost
* Minor bugfix in gpxobj.py (recomputes 'idx' column each time points are deleted). This allows reopening npz files that were not properly saved.
* 'idx', is not exported anymore in npz files.
* Added an __init__.py file to script folder to be able to import from this folder (from scripts import whateveryouwant)
* __init__.py, *.pyc and lib*.py files are now ignored from script list
* Added a proof of concept script to create an overlay on map and draw stuff on it (Test_overlay.py and liboverlay.py)

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
* initial bianry releases for OSX and win32
* adapted code to be compliant with PyInstaller-3.2
* updates in documentation
* reorganisation of github repo structure