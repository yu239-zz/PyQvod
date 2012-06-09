
INTRODUCTION:

PyQvod_v0.5 is a python wrapper for Qvod (in windows) + wine, inspired by a java version here:

http://www.ubuntusoft.com/qvod-download-for-linux.html

You can easily download a video with a valid Qvod URL from the Internet.
 
INSTALLATION:

This software package comes with both the source code and a standalone executable free from installation. However, no matter which one you choose, in order to run the Qvod downloader in linux, you have to install wine first.

Wine allows you to run many Windows programs on Linux. Its homepage can be found at WineHQ.org. To install wine in Ubuntu Desktop, you can simply open the software center and search for 'wine'. Alternatively, you can type in the terminal:

sudo apt-get install wine

After installation, no other configuration requires.

Also you need a browser plugin to capture the Qvod URL inside a webpage after you pressing some key. Checkout the 'plugins' directory. You can find plugins for both firefox and chromium.

a> For firefox users, simply drag the .xpi file onto the browser to install.

b> For chromium users, click on the 'customize' icon on the upper-right, then choose 'tools->extensions->Load unpacked extension', select the whole directory 'qvodurlfinder_chromium'. Done.

These two plubins are downloaded and modified from this link:

http://code.google.com/p/debbuilder-cn/downloads/list


1> Run standalone executable

You can place the directory 'executable' anywhere, as long as that you don't change the structure inside the directory. You need first to modify the configure file 'config', then cd into 'standalone' and run 'PyQvod' or simply double-click on the 'PyQvod'. Here is a trick: you could set an alias for the executable. Open the '~/.bashrc' file and add a line as follows: 

alias qvod='cd your-path-to-PyQvod/executable/standalone ; ./PyQvod'

Save the file and you can type command 'qvod' in a new terminal to launch the downloader.

NOTE: This method may have errors if your system glib version is incompatible with the executable. I provide two versions and hopefully they can satisfy most 'not-so-old' linux systems. If there is still any graphical problem, you may want to run the code.

2> Run through code

This wrapper is written in Python with wxPython library, which means that you don't have to compile the code but just interpret the code. Most linux systems come with Python installed, and it's best that you can make sure your Python version is 2.6 or 2.7. 

If you don't have Python or wxPython, in Ubuntu type the command:

sudo apt-get install python

sudo apt-get install python-wxgtk2.8

For other linux system or further information, see 

http://www.python.org/getit/

http://www.wxpython.org/download.php

Now you are ready to run the code. Again first modify the 'config' file. The main file is 'PyQvod.py'. Also, open the '~/.bashrc' file and add a line as follows:

alias qvod='cd your-path-to-PyQvod/project/src ; python ./PyQvod.py'

This will give you the 'qvod' command.

HOW TO USE:

After launching the software, you can press 'ctrl+e' in firefox or 'ctrl+q' in chromium. If capture succeeds, a Qvod URL will be added into the downloader.

LINCENSE:

This software is under MIT license,
or generally a DWYW (do whatever you want) license.
If something goes wrong, don't try to find me :).

Any bug, read the code and fix by yourself first. Or send the email to yu239 _AT_ purdue _DOT_ edu

Date: 06/08/2012
