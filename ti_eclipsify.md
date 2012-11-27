# ti_eclipsify.py Documentation

## Overview

ti_eclipsify.py takes an existing Titanium application project and prepares it for importing into Eclipse as an Android project. The advantage of this is that you can then use the imported project to debug the Titanium SDK libraries themselves (set breakpoints in Titanium SDK code, etc.)

## Prereqs

The idea here is that your Titanium project becomes an Android project in Eclipse.  The Android project type is available in Eclipse only if you have installed the [Android ADT Plugin for Eclipse](http://developer.android.com/tools/sdk/eclipse-adt.html).  So that's a prereq.

You will need to have the Titanium Mobile SDK sources and be capable of building them (meaning, building and packaging the SDK itself).  We don't cover that here.

Finally, you'll need to have all the titanium projects installed into your Eclipse workspace.  That's not covered here.

## Usage

1. Build your Titanium project at least once (using Titanium Studio, Titanum CLI, whatever.)

2. Run `ti_eclipsify.py` (I like to alias it to `ec`) from the project root folder.

3. Import the project into Eclipse. When importing, please note that the "root" of the project from Eclipse's perspective is the build/android folder below the Titanium project's root.

4. You should now be able to run the project from Eclipse as an Android app, including running it in debug mode and setting and hitting breakpoints in the Titanium projects.

## Caveats

* Projects built with Titanium Studio or CLI use a different keystore and key than projects imported to (and then run from) Eclipse.  So to run an imported project from Eclipse, you'll first need to remove the app from your test device/emulator if it's already there, otherwise there will be a key conflict and Android won't let the app install from Eclipse.

* Are some of the Titanium projects showing errors in Eclipse?  Don't forget to refresh all projects after building Titanium SDK from the command line.
