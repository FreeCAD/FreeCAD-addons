"""
View providers for Bullet Designer objects.

This module provides 3D visualization for bullet objects.
"""

import FreeCAD as App
import FreeCADGui as Gui
import os
import sys

# Add Utils to path
wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(wb_path, "Utils"))

from Utils.MaterialDatabase import get_material_database


class ViewProviderBullet:
    """
    View provider for bullet objects.
    
    Handles 3D display, colors, and visual properties.
    """
    
    def __init__(self, vobj):
        """
        Initialize the view provider.
        
        Args:
            vobj: FreeCAD view object
        """
        vobj.Proxy = self
        # Don't store Object reference directly - it will be accessed via vobj.Object
        # Storing it causes serialization issues
        self.Type = "ViewProviderBullet"
    
    def getIcon(self):
        """Return icon path for this object."""
        return ""
    
    def attach(self, vobj):
        """Called when view object is attached."""
        # Don't store Object reference - access via vobj.Object when needed
        pass
    
    def updateData(self, obj, prop):
        """Called when object data changes."""
        # Update color when material changes
        # obj is the document object, not the view object
        if prop == "Material" and App.GuiUp:
            self._update_color(obj)
    
    def onChanged(self, vobj, prop):
        """Called when view property changes."""
        pass
    
    def _update_color(self, obj):
        """
        Update object color based on material.
        
        Args:
            obj: The document object
        """
        try:
            if not App.GuiUp:
                return
            
            material_db = get_material_database()
            color = material_db.get_color(obj.Material)
            
            if obj.ViewObject:
                obj.ViewObject.ShapeColor = tuple(color)
                obj.ViewObject.Transparency = 0
        except Exception as e:
            App.Console.PrintWarning(f"Error updating color: {e}\n")
    
    def setEdit(self, vobj, mode=0):
        """Called when object is edited."""
        return False
    
    def unsetEdit(self, vobj, mode=0):
        """Called when edit mode is exited."""
        pass
    
    def __getstate__(self):
        """Called when object is saved."""
        # Return serializable state
        return {"Type": "ViewProviderBullet"}
    
    def __setstate__(self, state):
        """Called when object is restored."""
        # Restore state
        if state:
            self.Type = state.get("Type", "ViewProviderBullet")
        else:
            self.Type = "ViewProviderBullet"
        return None


class ViewProviderCartridge:
    """
    View provider for cartridge objects (placeholder for future implementation).
    """
    
    def __init__(self, vobj):
        """Initialize the view provider."""
        vobj.Proxy = self
        # Don't store Object reference directly - it will be accessed via vobj.Object
        self.Type = "ViewProviderCartridge"
    
    def getIcon(self):
        """Return icon path."""
        return ""
    
    def attach(self, vobj):
        """Called when view object is attached."""
        # Don't store Object reference - access via vobj.Object when needed
        pass
    
    def updateData(self, obj, prop):
        """Called when object data changes."""
        pass
    
    def onChanged(self, vobj, prop):
        """Called when view property changes."""
        pass
    
    def setEdit(self, vobj, mode=0):
        """Called when object is edited."""
        return False
    
    def unsetEdit(self, vobj, mode=0):
        """Called when edit mode is exited."""
        pass
    
    def __getstate__(self):
        """Called when object is saved."""
        # Return serializable state
        return {"Type": "ViewProviderBullet"}
    
    def __setstate__(self, state):
        """Called when object is restored."""
        # Restore state
        if state:
            self.Type = state.get("Type", "ViewProviderBullet")
        else:
            self.Type = "ViewProviderBullet"
        return None
