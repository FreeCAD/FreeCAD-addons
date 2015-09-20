This repository doesn't contain code itself, but uses git submodules system to 
gather interesting addons for FreeCAD made by the community into one convenient
place. By cloning this repository, you get all of them at once.

Once cloned, you can update all the submodules at once with:

    git submodule update
    
At the moment, the repository is made more for developers, because it still 
requires manual operations to add the different modules to your FreeCAD
installation. See instructions provided in each of the submodule. There are,
however, two easier ways to use all the addons at once:

1) Use the "pluginloader" module

2) Once git-cloned, add the path of this repo to your FreeCAD modules path
by starting it with the -M (additional modules path) switch:

    FreeCAD -M /path/to/this/folder
    
Note that some of the submodules of this repo are not made to be used as
FreeCAD modules, and therefore won't be enabled by method 2) above.
