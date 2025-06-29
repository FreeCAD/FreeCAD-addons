
# Allowed Python Packages

The `ALLOWED_PYTHON_PACKAGES` file lists Python  
packages that addons can request to be installed.

New packages can be added by opening an [Issue].

<br/>

## Format

The config doesn't follow any Python manifest formats,  
it's just a simple text file where each line that isn't empty  
and not a comment is interpreted as a Python package.

Packages cannot be declared with a version nor wildcards.


[Issue]: https://github.com/FreeCAD/FreeCAD-addons/issues/new/choose