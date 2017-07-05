#!/usr/bin/env bash
cd "$(dirname "$0")"
echo $PWD
pyinstaller --windowed wxgpgpsport.py --icon ./images/Map.ico -p ./modules/ -p ./plugins/ --workpath $TMPDIR
cp -R images dist/wxgpgpsport.app/Contents/MacOS/
cp -R docs dist/wxgpgpsport.app/Contents/MacOS/
cp -R scripts dist/wxgpgpsport.app/Contents/MacOS/
cp -R plugins dist/wxgpgpsport.app/Contents/MacOS/
cp wxgpgpsport.ini dist/wxgpgpsport.app/Contents/MacOS/
