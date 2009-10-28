rem python setup.py py2exe --includes sip
python py2exe_build.py py2exe
"d:\Program Files\NSIS\makensis.exe" make_nsis.nsi
pause