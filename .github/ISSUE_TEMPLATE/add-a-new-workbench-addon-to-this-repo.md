---
name: Add a new Workbench/Addon to this Repo
about: I want to contribute a new Workbench/Addon
title: "[New Addon/Workbench]"
labels: 'New WB/Addon :package:'
assignees: ''

---

### Dependencies
- This Addon/workbench runs on:  
  - [ ] Most up to date stable release
  - [ ] Most up to date development release
  - [ ] Python 3 compatible
  - [ ] Qt5 compatible
  - [ ] Qt5 and Qt6 compatible (uses "import PySide" rather than "import PySide2")
- [ ] Is this backward compatible with any previous version of FC? If so, please mention in the README.md
- [ ] Does this use 3rd party dependencies?  
  - [ ] numpy
  - [ ] scipy
  - Please specify if there are any other dependencies below and in the README.md and package.xml files

### README.md
- [ ] Is [Markdown][Markdown-link] friendly
- [ ] Has a **Prerequisite** or **Dependencies** section
- [ ] Links to a ``LICENCE`` file (Note: FreeCAD uses LGPL2.1, most people choose that or GPL3)
- [ ] Has a Screenshot and/or a section for screenshots
- [ ] Links to a [FreeCAD Forum discussion thread][FreeCAD-Thread]

### Misc.
- [ ] Do you keep a [changelog][Changelog]?  
  If so, where?  
- [ ] Your Addon has an SVG based Logo?
- [ ] Your Addon has a [package.xml file][Package_Metadata]?
- [ ] Edit the FreeCAD [External Workbenches][FC-ExternalWB-Wiki] wiki page

### Housekeeping
- [ ] Fixed typos in the code using [`codespell`][Codespell]. We recommend running: `codespell -q 3`
- [ ] We recommend linting python code with PEP8. See [coding conventions][Code-conventions] 

### Github Related
- [ ] Does your repository use [Release tags][Github-Tags] ?
- [ ] Repository has [topics][Github-Topics] which include `FreeCAD` `Workbench` `Addon`  

**Note:** if your addon/workbench code doesn't reside on Github, please state the address where it is mentioned

 
[Markdown-link]: https://guides.github.com/features/mastering-markdown/
[FreeCAD-Thread]: https://forum.freecadweb.org/viewforum.php?f=8
[Changelog]: https://keepachangelog.com/en/1.0.0/
[Package_Metadata]: https://wiki.freecad.org/Package_Metadata
[FC-ExternalWB-Wiki]: https://www.freecadweb.org/wiki/External_workbenches
[Coding-conventions]: https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Fem/coding_conventions.md#python-and-c
[Codespell]: https://github.com/codespell-project/codespell
[Github-Topics]: https://help.github.com/en/articles/classifying-your-repository-with-topics
[Github-Tags]: https://help.github.com/en/articles/creating-releases
