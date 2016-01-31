# add-ons repository for FreeCAD

This repository is a collection of useful additional workbenches and modules for FreeCAD made by community members, gathered here for your convenience.

Since these are not part of the official FreeCAD package and not supported by the FreeCAD team, you should read the information provided on each of the addons page above before installing any of them, to make sure you know what you are installing. Also, bug reports and feature requests should be made directly on each addon page.

### Installing

There are three ways to install any of the addons above:

#### 1. Using the installer macro

The installer macro can be launched from inside FreeCAD, and will download and install any of the addons above automatically. To install the installer macro:

1. Right-click on [addons_installer.FCMacro](https://github.com/FreeCAD/FreeCAD-addons/raw/master/addons_installer.FCMacro) and choose **Save as...**
2. Place the downloaded macro in your **FreeCAD Macros folder**. The FreeCAD Macros folder location is indicated in menu **Macros -> Macros -> User macros location**:
![the execute macro dialog](http://www.freecadweb.org/wiki/images/1/1e/Macro_installer_01.jpg)
3. Restart FreeCAD. The addons installer will now be listed in menu **Macro -> Macros** and can be launched by selecting it then clicking the **Execute** button:

![the addons installer](http://www.freecadweb.org/wiki/images/c/c6/Macro_installer_02.jpg)

#### 2. Using the "pluginloader" addon

The plugin loader is a much more elaborate way to install and manage additional content for freecad. Install it with the method above, or following the instructions on the [pluginloader page](https://github.com/microelly2/freecad-pluginloader).

#### 3. Manual install

Each of these addons can be downloaded by clicking the **Download ZIP** button found on top of each addon page, or using **Git**. Most of the addons must either be placed in your user's FreeCAD/Mod folder, or in the Macros folder. Refer to the instructions on each addon page for complete instructions.

### Adding your workbench to the collection

Have you made an interesting workbench or module that we are not aware of? Tell us on the [FreeCAD forum](http://forum.freecadweb.org) so we can add it here!
