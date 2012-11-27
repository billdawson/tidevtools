# ti_eclipsify.py Documentation

## Overview

ti_eclipsify.py takes an existing Titanium application project and prepares it for importing into Eclipse as an Android project. The advantage of this is that you can then use the imported project to debug the Titanium SDK libraries themselves (set breakpoints in Titanium SDK code, etc.)

## Prereqs

The idea here is that your Titanium project becomes an Android project in Eclipse.  The Android project type is available in Eclipse only if you have installed the [Android ADT Plugin for Eclipse](http://developer.android.com/tools/sdk/eclipse-adt.html).  So that's a prereq.

You will need to have the Titanium Mobile SDK sources and be capable of building them (meaning, building and packaging the SDK itself).  We don't cover that here.

Finally, you'll need to have all the titanium projects installed into your Eclipse workspace.  That's not covered here.

## First Time Setup

We need to set up a dummy project and import the Titanium projects into it in Eclipse. Doing this provides us with the .classpath, project.properties, etc., files that our later "eclipsified" projects will need.

1. Use Titanium Studio or the command-line to build and run a Titanium Android project.

2. In Eclipse, choose File -> Import -> Android -> Existing Android Code Into Workspace.

3. Click "Browse" to go find the root directory.

4. Navigate to the build/android folder below your Titanium project folder, and click "Open", then "Finish".  The project will appear as an Android project in your Eclipse workspace. It will have errors -- that's okay.

5. View the project's properties, such as by selecting "Properties" from the context menu or Project -> Properties from the menu.

6. In the Properties navigator, click on Android.

7. On the Android screen for Properties, notice the "Library" section near the bottom.  You'll want to add the "titanium" project, all "titanium-*" and all "kroll-*" projects as Android library projects.  So click "Add" and do that.

8. Create a folder somewhere on your file system (doesn't need to be anywhere related to a titanium project -- can be anywhere.)

9. Copy the .classpath, project.properties and .project files from the build/android folder of the Titanium project you were using above to the new folder.

10. Open your tidevtools_settings.py file and change (or add) the ECLIPSE_PROJ_BOOTSTRAP_PATH variable, setting it to the folder to which you just now copied the .classpath, .project and project.properties files.

11. Open the copy of .project that you put in the new folder, and tokenize the value of the `name` element by making it look like this:

        <name>[PROJECT_NAME]</name>

12. You're ready to go.

## Normal Use

Now that you've set it up, you can use it to eclipsify any Titanium project.  To do so:

1. Build the project at least once (using Ti Studio, CLI, whatever.)

2. Run `ti_eclipsify.py` (I like to alias it to `ec`) from the project root folder.

3. In Eclipse, import the project just as you did in steps 2, 3 and 4 in "First Time Setup" above.

4. You should now be able to run the project from Eclipse, including running it in debug mode and setting and hitting breakpoints in the Titanium projects.

## Caveats

* Projects built with Titanium Studio or CLI use a different keystore and key than projects imported to (and then run from) Eclipse.  So to run an imported project from Eclipse, you'll first need to remove the app from your test device/emulator if it's already there, otherwise there will be a key conflict and Android won't let the app install from Eclipse.

* Are some of the Titanium projects showing errors in Eclipse?  Don't forget to refresh all projects after building Titanium SDK from the command line.
