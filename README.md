tidevtools from Bill Dawson
============================

Includes a script to make a Titanium mobile project, and a script to "eclipsify" a project.

Suggested Steps To Use It
--------------------------

- Clone this repository.
- Copy tidevtools_settings.py.sample -> tidevtools_settings.py.
- Open tidevtools_settings.py and change the values -- I think they're self-explanatory.
- chmod +x *.py
- Make life easy on yourself and make some aliases.  I do this...

     alias mp="/Users/bill/projects/tidevtools/ti_makeproj.py"

     alias ec="/Users/bill/projects/tidevtools/ti_eclipsify.py"

     alias an="/Users/bill/projects/tidevtools/ti_android_device.py"

Usage Instructions
-------------------

### ti_makeproj.py
Makes a Titanium mobile project, including making its entry in the Titanium Developer Sqlite DB (so you see it next time you open Developer).

set ANDROID_SDK environment variable!

Usage:

`ti_makeproj.py [Project name]`

Example:

`ti_makeproj.py MyProject`

That will create a MyProject folder in the folder you specify in the PROJECT_FOLDER variable in your tidevtools_settings.py.

### ti_eclipsify.py

Does what you expect.  Run it while you are sitting in the root of a project (where the tiapp.xml is.)

### ti_android_device.py

If you're sitting in a Titanium project folder (a folder with tiapp.xml) and run this with no options, it checks to see if the project you're sitting in is installed on any connected Android devices.  If it is, it gives you options to uninstall from those devices.  Also, if it sees that build/android/bin/app.apk is there (i.e., you've built the project at leat once), it gives you options to install the APK on any of the connected devices.

Alternatively, you can run this script from anywhere with the "-u [package_filter]" option, such as:

`ti_android_device.py -u com.billdawson`

It will then check all your connected Android devices to see if they have any packages whose names begin with the filter you've provided.  If it finds any, it gives you the option to uninstall those matching packages from the device(s).  You can select one-by-one the ones you want to uninstall (and from which device.)
