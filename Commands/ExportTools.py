"""
Export tools for bullet objects.
"""

import FreeCAD as App
import FreeCADGui as Gui
import os


class ExportSTLCommand:
    """
    Command to export bullet to STL.
    """
    
    def __init__(self):
        """Initialize the command."""
        wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.resources = {
            "Pixmap": os.path.join(
                wb_path, "Resources", "icons", "Export.svg"
            ),
            "MenuText": "Export to STL",
            "ToolTip": "Export selected bullet to STL file",
            "Accel": ""
        }
    
    def GetResources(self):
        """Return command resources."""
        return self.resources
    
    def IsActive(self):
        """Check if command is active."""
        return App.ActiveDocument is not None and Gui.Selection.getSelection()
    
    def Activated(self):
        """Execute the command."""
        selection = Gui.Selection.getSelection()
        if not selection:
            App.Console.PrintWarning("Please select a bullet object.\n")
            return
        
        obj = selection[0]
        if not hasattr(obj, "Shape"):
            App.Console.PrintWarning("Selected object has no shape.\n")
            return
        
        # Use FreeCAD's export dialog
        from PySide2 import QtWidgets
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Export STL",
            "",
            "STL files (*.stl)"
        )
        
        if filename:
            try:
                import Mesh
                mesh = Mesh.Mesh(obj.Shape.tessellate(0.1))
                mesh.write(filename)
                App.Console.PrintMessage(f"Exported to {filename}\n")
            except Exception as e:
                App.Console.PrintError(f"Error exporting STL: {e}\n")


class ExportSTEPCommand:
    """
    Command to export bullet to STEP.
    """
    
    def __init__(self):
        """Initialize the command."""
        wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.resources = {
            "Pixmap": os.path.join(
                wb_path, "Resources", "icons", "Export.svg"
            ),
            "MenuText": "Export to STEP",
            "ToolTip": "Export selected bullet to STEP file",
            "Accel": ""
        }
    
    def GetResources(self):
        """Return command resources."""
        return self.resources
    
    def IsActive(self):
        """Check if command is active."""
        return App.ActiveDocument is not None and Gui.Selection.getSelection()
    
    def Activated(self):
        """Execute the command."""
        selection = Gui.Selection.getSelection()
        if not selection:
            App.Console.PrintWarning("Please select a bullet object.\n")
            return
        
        obj = selection[0]
        if not hasattr(obj, "Shape"):
            App.Console.PrintWarning("Selected object has no shape.\n")
            return
        
        # Use FreeCAD's export dialog
        from PySide2 import QtWidgets
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Export STEP",
            "",
            "STEP files (*.step *.stp)"
        )
        
        if filename:
            try:
                import Part
                Part.export([obj], filename)
                App.Console.PrintMessage(f"Exported to {filename}\n")
            except Exception as e:
                App.Console.PrintError(f"Error exporting STEP: {e}\n")


# Register commands (only if Gui is available)
try:
    Gui.addCommand("BulletDesigner_ExportSTL", ExportSTLCommand())
    Gui.addCommand("BulletDesigner_ExportSTEP", ExportSTEPCommand())
except Exception as e:
    App.Console.PrintError(f"Failed to register Export commands: {e}\n")
