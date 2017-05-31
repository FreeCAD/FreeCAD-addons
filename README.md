# add-ons repository for FreeCAD

This repository is a collection of useful additional workbenches and modules for FreeCAD made by community members, gathered here for your convenience.

Since these are not part of the official FreeCAD package and not supported by the FreeCAD team, you should read the information provided on each of the addons page above before installing any of them, to make sure you know what you are installing. Also, bug reports and feature requests should be made directly on each addon page.

### Current add-ons
Short description of each add-on that is available in this repository
 
#### CADExchanger
CAD Exchanger addon for FreeCAD

![example](https://forum.freecadweb.org/download/file.php?id=37230)

This addons allows FreeCAD to import and export to several additional file formats supported by the [CAD Exchanger](http://cadexchanger.com/) application. See the CAD Exchanger website for details on support of these formats.

#### Cfd
Computional Fluid Dynamics (CFD) for FreeCAD based on OpenFOAM solver 
(has been forked in to CFDFoam)
#### Curves
This is a python workbench, with a collection of tools for Nurbs curves and surfaces  
#### FCGear

#### GDT 
Labeling software module for Geometric Dimensioning and Tolerancing (GD&T) in 2D and 3D technical drawings.
-	Allows the GD&T information to be added to the design itself, thus linking design, manufacturing and quality specifications   
-	Implements the ISO16792 standard for both 2D and 3D parts.  
-	Incorporates a homogeneous graphical interface and integrated with the technical design tools and 3D.  
-	There is no precedent developed as free software.  
![screenshot](https://forum.freecadweb.org/download/file.php?id=36916)  
#### IconThemes
Icon themes for FreeCAD
#### Launcher
Launcher widget for FreeCAD
#### NavigationIndicator
Navigation indicator for FreeCAD
#### Part-o-magic
Experiment on FreeCAD-wide automation of Part container management 
Compatible with FreeCAD v0.17. (It won't work with FC v0.16.)

The goal is to experiment with UI and ways to bring assembly infrastructure into the whole FreeCAD. Sure you have seen that new PartDesign things called Part and Body. The aim of Part-o-magic is to bring similar things to every workbench in FreeCAD, and make working with them more convenient.

With Part-o-magic, organizing a multi-part project (i.e. an assembly) is much easier.

Beware. Part-o-magic is an epic hack. It will collide with similar functionality in FreeCAD as it is introduced. In case of doubt, you can always switch to Part-o-magic workbench, and disable Observer.
![figure](https://raw.githubusercontent.com/wiki/DeepSOIC/Part-o-magic/pictures/rotating-plate.png)
#### PieMenu
PieMenu widget for FreeCAD
#### ShortCuts
Shortcuts overlay for FreeCAD
#### TabBar
TabBar widget for FreeCAD
#### WebTools
WebTools workbench for FreeCAD

This workbench contains tools to interact with different web services:

* [Git](https://www.freecadweb.org/wiki/Arch_Git): Manages the current document with [Git](https://en.wikipedia.org/wiki/Git)
* [BimServer](https://www.freecadweb.org/wiki/Arch_BimServer): Connects and interacts with a [BIM server](http://www.bimserver.org) instance
* [Sketchfab](https://www.freecadweb.org/wiki/Web_Sketchfab): Connects and uploads a model to a [Sketchfab](http://www.sketchfab) account
#### animation
Animation Toolkit for FreeCAD  
This Workbench can be used to create sequences of pictures.
#### assembly2
Assembly workbench for FreeCAD v0.15, 0.16 and 0.17 with support for importing parts from external files. Although the original programmer of the workbench (hamish) is no longer active this workbench is still maintained as good as possible. Feel free to post issues and pull requests. Assembly2 requires numpy to be installed (bundled with FreeCAD since 0.15.4671). Thanks to Maurice (@easyw-fc) assembly2 will work with files from FreeCAD 0.17.
#### bolts
BOLTS is an Open Library for Technical Specifications.

This repository contains all the tools and data that are required to build the different distributions and the website. You only need to get the content of this repository if you want to contribute content to BOLTS or want to develop the tools that are used to manage it.
#### cadquery_module
Module that adds a tabbed CadQuery editor to FreeCAD. Please see the [cadquery freecad module github wiki](https://github.com/jmwright/cadquery-freecad-module/wiki) for more detailed information on getting started.

![Module User Interface](http://innovationsts.com/images/Version_1_0_0_1_and_Later_Interface.png)
#### cura_engine
CuraEngine Plugin for FreeCAD  
This is a Python macro workbench used to integrate CuraEngine into FreeCAD
#### drawing_dimensioning
Drawing dimensioning workbench for FreeCAD v0.15.4576 and newer.
#### dxf_library
This repository contains files needed to add DXF support (import-export) to FreeCAD.
Note: The files in this repository are not needed anymore when using the built-in DXF importer (default since FreeCAD 0.16). They are still needed if you wish to use the legacy python importer (settable in Edit-> Preferences -> Import/Export -> DXF) or if you wish to export directly from the 3D model (exporting a Drawing page to DXF also doesn't require these files)
#### exploded_animation
FreeCAD workbench to create exploded views and animations of assemblies.  
Features:
* Create nice explosions of assemblies graphically (no code at all!)
* Create sub-exploded groups
* Give rotation to screws and nuts for realistic disassembles
* Use the provided auxiliary assembly tools to place your parts together
![show](http://2.bp.blogspot.com/-Og8hzXXrAS0/VuaVxWhcKEI/AAAAAAAACv4/MCYpnIEPUrgeOrYIxr9ZoGqXdT9_bszjQ/s1600/Captura%2Bde%2Bpantalla%2Bde%2B2016-03-14%2B09%253A32%253A47.png)  
[Screencast](https://www.youtube.com/watch?v=lzYR7I2h7KQ)
#### fasteners
A workbench to add/attach various fasteners to parts
Details at http://theseger.com/projects/2015/06/fasteners-workbench-for-freecad/
#### flamingo
 "Flamingo tools" is a set of macros made to speed up some actions in FreeCAD
#### geodata
geodata support for freecad
This workbench uses geodata from openstreetmap.org
#### kerkythea
Kerkythea exporter for FreeCAD
#### lattice
[Deprecated!] Old version of FreeCAD workbench with advanced array tools
#### lattice2
FreeCAD workbench with advanced array tools.

The workbench purpose is working with placements and arrays of placements. It is a sort of assembly workbench, but with emphasis on arrays. There are no constraints and relations, there are just arrays of placements that can be generated, combined, transformed, superimposed and populated with shapes. 

Ever wondered how to create a protractor with FreeCAD? That's the aim of the workbench (including tick labeling). Also, exploded assemblies can be made with the workbench.

Additionally, the workbench features a few general-purpose tools, such as parametric downgrade, bounding boxes, shape info tool, and tools for working with collections of shapes (compounds).

One of the big design goals of the workbench is being as parametric as possible.

![Lattice2-FreeCAD-wormcutter](https://raw.githubusercontent.com/wiki/DeepSOIC/Lattice2/gallery/worm-cutter-done.png)

![Lattice2-FreeCAD-placement-interpolator](https://raw.githubusercontent.com/wiki/DeepSOIC/Lattice2/gallery/placement_interpolator_fixed.png)

Take a look at other examples in the [Gallery of screenshots](https://github.com/DeepSOIC/Lattice2/wiki/Gallery).
#### nurbs

#### parts_library
This addon contains a library of Parts to be used in FreeCAD. It is maintained by the community of users of FreeCAD and is not part of the FreeCAD project, although it is made with the aim to be used as a repository of parts by FreeCAD in the future.
#### pcb
Printed Circuit Board Workbench for FreeCAD PCB 
Flexible Printed Circuit Board Workbench for FreeCAD FPCB 

![screenshot](http://a.fsdn.com/con/app/proj/eaglepcb2freecad/screenshots/FreeCAD-PCB_assembly.png)

#### persistenttoolbars
Persistent toolbars support for FreeCAD 
Note: Starting with FreeCAD 0.17 persistent toolbars is part of the default FreeCAD experience.
#### pluginloader

#### pyrate
Optical Design with Python.
![screenshot](https://cloud.githubusercontent.com/assets/12564815/24820302/9b8cf4a0-1be8-11e7-8d8b-de0184587145.png)
#### reconstruction
reconstruction models from images for freecad
#### ret3d
Retr3d (ˈriːˌtred) is a framework dedicated to affordable 3D printing equipment for developing economies that can be locally sourced, locally maintained and locally improved.

We believe that 3D printing can be as transformative in developing countries as the mobile phone. As with the mobile phone, which has already changed the way people across the Africa communicate, introducing 3D printing at the community level offers the potential to localize manufacturing. Which is why we are making it possible to build Retr3d machines from the thousands of tonnes of e-waste which would otherwise end up as landfill.

Retr3d uses python and FreeCAD to 3D model printable parts for the construction of more 3D printers. Through globalVars.py dimensions of procured e-waste are turned into customized 3D models. Retr3d's software depends on FreeCAD's python scripting API.
![printer](https://github.com/masterperson40/retr3d/raw/master/docs/printer.png)
#### sheetmetal
FreeCAD SheetMetal Workbench
Details: http://theseger.com/projects/2015/06/sheet-metal-addon-for-freecad/
#### symbols-library
FreeCAD Symbols Library  
This repository contains a library of SVG symbols to be used in FreeCAD. Although they consist of simple SVG files, so they can also be imported inside the 3D document, they are primarily made for use on Drawing pages.
#### timber
A Timber module for FreeCAD
#### workfeature
Tool utility to create Points (mid points, center of circle, center of object(s)...), Axes (from 2 points, Normal of a plane...), Planes (from 3 points, from one axis and a point...) and many other useful features to facilitate the creation of your project. This utility is up next in the combo view with "Work Features" label.


### Installing

*Starting from FreeCAD v. 0.17.9940 the addons installer is included in FreeCAD, and can be accessed form the Tools menu, so there is no need to install anything anymore. The instructions below are only needed for older versions.*

There are three ways to install any of the addons above (also check this more in-depth [tutorial](http://www.freecadweb.org/wiki/index.php?title=How_to_install_additional_workbenches) on the FreeCAD wiki):

#### 1. Using the installer macro

The installer macro can be launched from inside FreeCAD, and will download and install any of the addons above automatically. To install the installer macro:

1. Download [addons_installer.FCMacro](https://rawgit.com/FreeCAD/FreeCAD-addons/master/addons_installer.FCMacro)
2. Place the downloaded macro in your **FreeCAD Macros folder**. The FreeCAD Macros folder location is indicated in menu **Macros -> Macros -> User macros location**:
![the execute macro dialog](http://www.freecadweb.org/wiki/images/1/1e/Macro_installer_01.jpg)
3. Restart FreeCAD. The addons installer will now be listed in menu **Macro -> Macros** and can be launched by selecting it then clicking the **Execute** button:

![the addons installer](http://www.freecadweb.org/wiki/images/c/c6/Macro_installer_02.jpg)

#### 2. Using the "pluginloader" addon

The plugin loader is a much more elaborate way to install and manage additional content for freecad. Install it with the method above, or following the instructions on the [pluginloader page](https://github.com/microelly2/freecad-pluginloader).

#### 3. Manual install

Each of these addons can be downloaded by clicking the **Download ZIP** button found on top of each addon page, or using **Git**. Most of the addons must either be placed in your user's FreeCAD/Mod folder, or in the Macros folder. Refer to the instructions on each addon page for complete instructions. 

**Note**: Your user's FreeCAD folder location is obtained by typing in FreeCAD's python console: `FreeCAD.ConfigGet("UserAppData")`while the Macros folder location is indicated in the dialog opened from menu *Macro -> Macros...*

### Adding your workbench to the collection

Have you made an interesting workbench or module that we are not aware of? Tell us on the [FreeCAD forum](http://forum.freecadweb.org) so we can add it here!
