set zip="D:\Program Files\7-Zip\7z.exe"
del pyvoctr.zip
%zip% a -tzip -mx9 pyvoctr.zip pyvoctr.py pyvoctr.pyw license.txt  pyvoc.ico en-es-mine.txt en-es-mnemosyne.txt make_installer.bat readme.txt
