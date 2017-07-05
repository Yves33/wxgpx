@echo off
SET TARGET=wxgpgpsport
pyinstaller.exe -p .\modules\ -p .\plugins\  %TARGET%.py 
xcopy /e /Y /i images dist\%TARGET%\images
xcopy /e /Y /i docs dist\%TARGET%\docs
xcopy /e /Y /i scripts dist\%TARGET%\scripts
xcopy /e /Y /i plugins dist\%TARGET%\plugins
xcopy /Y wxgpgpsport.ini dist\wxgpgpsport\
pause