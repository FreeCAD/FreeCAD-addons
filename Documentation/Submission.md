
# Submission

How to submit your addon to this collection.

<br/>


## Preparation

### Repository

-   Ensure your repository is hosted  
    on one of the following platforms:

    [GitHub] , [Gitlab] , [Framagit]  
    [salsa.debian.org] , [Codeberg]


-   Add the `freecad` & `addon` topics to  
    your repository to improve searchability.

-   Ensure your README is readable in the addon manager UI  
    as  some things don't renders the same as in the browser.

    Example : [SheetMetal Workbench]

### Addon

-   Your addon should have an SVG logo  
    that represents what the addon does.

    Format : `SVG`

    Filesize : `≤ 10Kb`

-   Ensure your addon has a valid [Package Manifest] with as  
    much information as possible to improve searchability.

<br/>


## Feedback

Announce your addon on the [FreeCAD Forum][Forum]

⮞ Make people aware 

⮞ Collect feedback  

⮞ Have people test it

<br/>


## Documentation

Create a page for your addon on the FreeCAD wiki.

*Don't forget to add `[[Category:Addons]]` to*  
*it and add it to the [External Workbenches] page.*

<br/>


## Registration

### Issue

Open an issue via our [Template][Issue Template] and link the  
Pull Request that will be created in the next step.

### Pull Request

Create a [Pull Request] in this repository  
that contains the following set of changes:

-   Add your addon to the [`.gitmodules`][Git Modules] file.

    The list is kept in alphabetical order, so  
    add your entry at the appropriate position.

    The git submodule command will not do  
    this, so you will need to this by hand.

    ( This is for FreeCAD ≤ 1.0 compatibility )

-   Add your addon to the [`AddonCatalog.json`][Addon Catalog] file.

    This format of this file supports multiple  
    repository branches & versions of FreeCAD.

    ( This is for FreeCAD 1.0+ compatibility )


### Commit Ids

Note that the commit number is not relevant to  
what will be installed by the addon manager.

The addon manager always installs the latest  
*Head* of the specified branch and falls back to  
`master` for the branch.


<!----------------------------------------------------------------------------->

[SheetMetal Workbench]: https://github.com/shaise/FreeCAD_SheetMetal/blob/master/README.md
[External Workbenches]: https://freecadweb.org/wiki/External_workbenches
[Package Manifest]: https://wiki.freecadweb.org/Package_Metadata
[Issue Template]: https://github.com/FreeCAD/FreeCAD-addons/issues/new?template=add-a-new-workbench-addon-to-this-repo.md
[Pull Request]: https://github.com/FreeCAD/FreeCAD-addons
[Forum]: https://forum.freecad.org/

[salsa.debian.org]: https://salsa.debian.org/public
[Framagit]: https://framagit.org/public/projects
[Codeberg]: https://codeberg.org/
[Gitlab]: https://about.gitlab.com/
[GitHub]: https://github.com/

[Addon Catalog]: https://github.com/FreeCAD/FreeCAD-addons/blob/master/AddonCatalog.json
[Git Modules]: https://github.com/FreeCAD/FreeCAD-addons/blob/master/.gitmodules