### About Python Dictionary Trainer ###

The entire purpose of the application is to display words from a dictionary in a post-it-like window.

Features:
  * Pin on top of other windows (`Always on Top` in context menu)
  * Hide window decorations (`Hide window frame`)
  * Show translated phrase after a configurable delay  (`Set think time`)
  * Change background color (`Set background color`)
  * Click to advance to next word
  * HTML support in definitions
  * Very simple dictionary format
Example dictionary file:
```
el perro = dog
la bombilla = bulb
```
To use your own dictionary, save the file with a `.txt` extension and open it via right-click > Open dictionary.

### Adding pictures ###
You can add HTML tags to the text of entries:
Example:
```
el perro = <img src='dog.jpg'>dog
la bombilla = <img src='bulb.jpg'><br>bulb
```

Example:

![http://pyvoctr.googlecode.com/svn/trunk/pyvoctr/pyvcontr_card.png](http://pyvoctr.googlecode.com/svn/trunk/pyvoctr/pyvcontr_card.png)

### Installation on Windows ###
Download and run the [installer](http://pyvoctr.googlecode.com/files/pyvoctr_setup.exe). A launcher icon will be created in your Start Menu under `Python Vocabulary Trainer`.

### Installation on Linux ###
Checkout the project from Subversion
```
    svn co http://pyvoctr.googlecode.com/svn/trunk/pyvoctr/
```
and then start the app by running:
```
    python pyvoctr.py
```


### Similar Projects ###

If you are looking for a vocabulary trainer with more features, have a look at the following projects:

  * [anki](http://ichi2.net/anki)
  * [mnemosyne](http://mnemosyne-proj.sourceforge.net)