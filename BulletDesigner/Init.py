"""
FreeCAD Bullet Designer Workbench - Initialization

This file is executed when FreeCAD starts (both console and GUI mode).
Use for non-GUI initialization only.
"""

import FreeCAD as App
import os

# Version information
__version__ = "1.0.0"
__author__ = "Bullet Designer Team"
__date__ = "2025-02-16"

# Workbench directory - handle case where __file__ might not be defined
try:
    wb_path = os.path.dirname(__file__)
except NameError:
    # Fallback: use FreeCAD's Mod path
    wb_path = os.path.join(App.getUserAppDataDir(), "Mod", "BulletDesigner")


def Initialize():
    """
    Initialize the workbench when FreeCAD starts.
    
    This function is called by FreeCAD when the workbench is loaded.
    Use for non-GUI initialization only.
    """
    App.Console.PrintLog("Loading Bullet Designer module...\n")
    
    # Register file formats (if needed in future)
    # App.addImportType("Bullet files (*.bullet)", "BulletDesigner")
    # App.addExportType("Bullet files (*.bullet)", "BulletDesigner")


def Uninitialize():
    """
    Uninitialize the workbench when FreeCAD closes or workbench is switched.
    
    This function is called by FreeCAD when the workbench is unloaded.
    Use for cleanup of resources, observers, etc.
    """
    App.Console.PrintLog("Unloading Bullet Designer module...\n")


def GetResources():
    """
    Return workbench resources (icon, menu, etc.)
    This is used by InitGui.py but can be called from here too.
    """
    return {
        "MenuText": "Bullet Designer",
        "ToolTip": "Design parametric bullets and projectiles",
        "Icon": os.path.join(wb_path, "Resources", "icons", "BulletDesigner.svg")
    }
