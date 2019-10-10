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
- [ ] Is this backward compatible with any previous version of FC? If so, please mention in the README.md
- [ ] Does this use 3rd party dependencies?  
  - [ ] numpy
  - [ ] scipy
  - Please specify if there are any other dependencies below and in the README.md

### README.md
- [ ] Is [Markdown][Markdown-link] friendly
- [ ] Has a **Prerequisite** or **Dependencies** section
- [ ] Links to a ``LICENCE`` file (Note: FreeCAD uses LGPL3, most people choose that or GPL3)
- [ ] Has a Screenshot and/or a section for screenshots
- [ ] Links to a [FreeCAD Forum discussion thread][FreeCAD-Thread  

### Misc.
- [ ] Do you keep a [changelog][Changelog]?  
  If so, where?  
- [ ] Your Addon has an SVG based Logo?
- [ ] Once your Addon/Workbench is accepted, you'll open a PR for FreeCAD master in order to add said Logo in to the FreeCAD Addon Manager dialog? ([Example][Add-Icons-to-Master]), see directions below:   
  1. Copy the SVG to `FreeCAD/src/Mod/AddonManager/Resources/Icons` (Note the formatting of the file name is important).
  2. Edit the `FreeCAD/src/Mod/AddonManager/Resources/AddonManager.qrc` and alphabetically place the path (in the previous step) to the icon of your workbench in the list.  
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
[Add-Icons-to-Master]: https://github.com/FreeCAD/FreeCAD/commit/bd985feef323468380a2e5dd88fb3b7046849826
[FC-ExternalWB-Wiki]: https://www.freecadweb.org/wiki/External_workbenches
[Coding-conventions]: https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Fem/coding_conventions.md#python-and-c
[Codespell]: https://github.com/codespell-project/codespell
[Github-Topics]: https://help.github.com/en/articles/classifying-your-repository-with-topics
[Github-Tags]: https://help.github.com/en/articles/creating-releases
