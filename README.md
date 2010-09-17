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

Usage Instructions
-------------------

### ti_makeproj.py
Makes a Titanium mobile project, including making its entry in the Titanium Developer Sqlite DB (so you see it next time you open Developer).

Usage:

`ti_makeproj.py [Project name]`

Example:

`ti_makeproj.py MyProject`

That will create a MyProject folder in the folder you specify in the PROJECT_FOLDER variable in your tidevtools_settings.py.

### ti_eclipsify.py

Does what you expect.  Run it while you are sitting in the root of a project (where the tiapp.xml is.)
