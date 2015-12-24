This repository doesn't contain code itself, but uses git submodules system to 
gather interesting addons for FreeCAD made by the community into one convenient
place. By cloning this repository, you get all of them at once:

    git clone https://github.com/FreeCAD/FreeCAD-addons.git

Once cloned, you can update all the submodules at once with:

    git submodule foreach git pull

There are different ways to use the contents of thisrepository:

1) Use the "pluginloader" module

2) Add this repository as additional modules foler to FreeCAD
by starting FreeCAD with the -M switch like this:

    FreeCAD -M /path/to/this/folder
    
3) Symlink or copy individual submodules of your choice to
your modules folder, which is normally /home/YOUR_USER/.FreeCAD/Mod
on Linux and Mac, and C:\Users\YOUR_USER\Application Data\Roaming\FreeCAD\Mod
on Wndows (the Mod subfolder should be created if needed).
    
Note that some of the submodules of this repo are not made to be used as
FreeCAD modules, and therefore won't be enabled by method 2) above.

4) EXPERIMENTAL - download the addons_installer macro, place it in your macros
folder, restart FreeCAD and run it form the macros menu.
