# WBO Workbench-Organizer widget for FreeCAD
# Copyright (C) 2015, 2016, 2017, 2018 triplus @ FreeCAD who provided
# the wonderful TabBar widget on which this is based.
# Copyright (C) 2024 Oliver Rafelsberger
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""TabBar widget for FreeCAD."""
__pathToolbar__ = "User parameter:BaseApp/Workbench/Global/Toolbar"
__pathTabbar__  = "User parameter:BaseApp/Workbench/Global/Toolbar/Tabs"
__parameters__  = FreeCAD.ParamGet("User parameter:BaseApp/WB_Organizer")
print("WBO Start")

if __parameters__.GetBool("Enabled", 1):

    # Delete duplicate toolbars (can be added by customize dialog).
    pTB = FreeCAD.ParamGet(__pathToolbar__)
    n = 1
    while n < 30:
        group = "Custom_" + str(n)
        if pTB.HasGroup(group):
            if pTB.GetGroup(group).GetString("Name") == "Tabs":
                pTB.RemGroup(group)
        n += 1

    # Create toolbar.
    pTB = FreeCAD.ParamGet(__pathTabbar__)
    pTB.SetString("Name", "Tabs")
    pTB.SetBool("Active", 1)

    import WBO_Gui
