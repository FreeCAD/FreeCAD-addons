# add-ons repository for FreeCAD

This repository is a collection of useful additional workbenches and modules for FreeCAD made by community members, gathered here for your convenience.

Since these are not part of the official FreeCAD package and not supported by the FreeCAD team, although this list is curated and maintained by the FreeCAD team, you should read the information provided on each of the addons page above before installing any of them, to make sure you know what you are installing. Also, bug reports and feature requests should be made directly on each addon page.

**Note**: The commit number indicated in the github tree above is not considered by the Addons Manager. What is installed or updated is always the latest *master* branch of every addon

### Current add-ons
For a description of each Addon please open FreeCAD use the dropdown menu `Tools > Addon manager` to scroll between all available Addons. 
You can also click on each individually linked Addons in this repository to read their README files.    

### Installing

#### Important Note
***Starting from FreeCAD v0.17.9940 the Addon Manager was finally implemented in to FreeCAD. It can be accessed from the dropdown Tools -> 'Addon Manager' menu. For earlier versions (≤v0.16), please see the [Deprecated Installation Methods](#deprecated-installation-methods) section***.

#### 1. Builtin Addon Manager

With version 0.17 FreeCAD now has a built-in Addon Manager that will install 3rd party workbenches and macros. To access it via ***Tools -> Addon Manager*** as per the screenshot:

![freecad-0.17-addon_manager-screenshot](https://user-images.githubusercontent.com/4140247/37867768-2eb7db20-2f73-11e8-83fb-8868995ba49d.png)


#### 2. Manual install

Each of these addons can be downloaded by clicking the **Download ZIP** button found on top of each addon page, or using **Git**. Most of the addons must either be placed in your user's FreeCAD/Mod folder, or in the Macros folder. Refer to the instructions on each addon page for complete instructions. 

**Note**: Your user's FreeCAD folder location is obtained by typing in FreeCAD's python console: `FreeCAD.ConfigGet("UserAppData")`while the Macros folder location is indicated in the dialog opened from menu *Macro -> Macros...*

### Adding your workbench to the collection

Have you made an interesting workbench or module that we are not aware of? Tell us on the [FreeCAD forum](http://forum.freecadweb.org) so we can add it here!

To submit your workbench to the repository you must also need the following tasks to be completed:
1. Announce your Workbench on the FreeCAD Forums
2. Create a PR and add your Workbench to the [FreeCAD-Addon_Details](https://github.com/FreeCAD/FreeCAD-addons/blob/master/FreeCAD-Addon-Details.md) page.
3. Create a dedicated page for your workbench on the FreeCAD wiki (don't forget to add `[[Category:Addons]]` to it) + add it to https://freecadweb.org/wiki/External_workbenches
4. Create an entry on https://www.freecadweb.org/wiki/Template:DevWorkbenches
5. Tag (AKA 'label) your Github repo with the following: `freecad`, `addons`, and `workbench`  

### Translating External Workbenches

For wider usage of external workbenches, we recommend that workbench developers integrate the ability to [translate their workbench(s)](https://www.freecadweb.org/wiki/Translating_an_external_workbench). FreeCAD uses a 3rd-party crowdsource translation service called [Crowdin](https://crowdin.com/project/freecad). There are some [automated scripts](https://www.freecadweb.org/wiki/Crowdin_Scripts) that we use to push and pull translations from Crowdin via their API. Developers are invited to help improve these scripts so as to include their own workbenches in the process. Further discussion on [this forum thread](https://forum.freecadweb.org/viewtopic.php?f=10&t=36413). 

### Deprecated Installation Methods
<details>
  <summary>Before FreeCAD v. 0.17.9940 the methods below were utilized to automate the installation of workbenches and macros. This sections is being kept for historical purposes.
</summary>
  
#### 1. Using the installer macro

The installer macro can be launched from inside FreeCAD, and will download and install any of the addons above automatically. To install the installer macro:

1. Download [addons_installer.FCMacro](https://raw.githubusercontent.com/FreeCAD/FreeCAD-addons/da3cb72c54f94430e9afd8200b48f4f2f6ac7c8c/addons_installer.FCMacro)
2. Place the downloaded macro in your **FreeCAD Macros folder**. The FreeCAD Macros folder location is indicated in menu **Macros -> Macros -> User macros location**:
![the execute macro dialog](http://www.freecadweb.org/wiki/images/1/1e/Macro_installer_01.jpg)
3. Restart FreeCAD. The addons installer will now be listed in menu **Macro -> Macros** and can be launched by selecting it then clicking the **Execute** button:

![the addons installer](http://www.freecadweb.org/wiki/images/c/c6/Macro_installer_02.jpg)

#### 2. Using the "pluginloader" addon

The plugin loader is a much more elaborate way to install and manage additional content for freecad. Install it with the method above, or following the instructions on the [pluginloader page](https://github.com/microelly2/freecad-pluginloader).
</details>
