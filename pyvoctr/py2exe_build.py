# setup.py
from distutils.core import setup
import py2exe
#setup(window=["pyvoctr.py"])

setup(
	windows = [
		{
			"script" : "pyvoctr.py",
			"icon_resources" : [(0, "pyvoc.ico")]
		}
	], 
	options = 
		{
			"py2exe" : {"includes" : ["sip", "PyQt4"]}
		}
)
