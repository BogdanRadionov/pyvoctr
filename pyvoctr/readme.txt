About Python Vocabulary Trainer
===============================

Python Vocabulary Trainer was inspired by the Parley vocabulary trainer widget in KDE 4.3. My original goal was to make a similar application which would work on any platform. 

The entire purpose of the application is to display words from a dictionary in a flashcard-like window. The matching translation is displayed after a configurable delay. 

Features: 
	* Can stay on top of other windows (`Always on Top` in context menu) 
	* Hide windows decorations (`Hide window title`) 
	* Show translated phrase after a configurable delay (`Set think time`)
	* Change background color (`Set background color`)
	* Click to advance to next word 
	* Simple dictionary format (e.g. la harina = flour) Py


Dependencies
============

Python Vocabulary Trainer uses the PyQT4 library. The Windows installer contains all the required libraries.

To run the app on Linux you will need to have PyQT4 bindings and the QT4 libraries which might already be installed on your system. To install dependencies in Ubuntu or other Debian-based system, use the following command:

    sudo apt-get install python-qt4

To run the app use this command:

    python pyvoctr.py


Similar Projects
================

If you need a more serious vocabulary trainer with more features, have a look at the following apps:

   * anki - http://ichi2.net/anki/
   * mnemosyne - http://mnemosyne-proj.sourceforge.net


Feedback
========
Suggestions and bug reports are welcome at dogpizza at gmail dot com

