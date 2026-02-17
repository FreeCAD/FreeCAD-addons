"""
Create Bullet command for Bullet Designer workbench.

This command creates a new parametric bullet object and opens
the task panel for parameter editing.
"""

import FreeCAD as App
import FreeCADGui as Gui
import os
import sys

# Get workbench directory
# Commands/CreateBullet.py -> Commands/ -> BulletDesigner/ (workbench root)
try:
    wb_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    # Fallback if __file__ not available
    import FreeCAD as App
    wb_path = os.path.join(App.getUserAppDataDir(), "Mod", "BulletDesigner")

# Add paths for imports
sys.path.insert(0, os.path.join(wb_path, "Gui"))
sys.path.insert(0, os.path.join(wb_path, "Objects"))

from Objects.BulletFeature import makeBulletFeature
from Gui.BulletTaskPanel import BulletTaskPanel


class CreateBulletCommand:
    """
    Command to create a new bullet object.
    """
    
    def __init__(self):
        """Initialize the command."""
        # Get icon path
        icon_path = os.path.join(wb_path, "Resources", "icons", "CreateBullet.svg")
        # Fallback if icon doesn't exist
        if not os.path.exists(icon_path):
            icon_path = ""
        
        self.resources = {
            "Pixmap": icon_path,
            "MenuText": "Create Bullet",
            "ToolTip": "Create a new parametric bullet",
            "Accel": "B"
        }
    
    def GetResources(self):
        """
        Return command metadata.
        
        Returns:
            dict: Command resources including icon, menu text, tooltip, etc.
        """
        return self.resources
    
    def IsActive(self):
        """
        Determine if command should be enabled.
        
        Returns:
            bool: True if command should be active, False otherwise
        """
        return App.ActiveDocument is not None
    
    def Activated(self):
        """
        Execute the command.
        
        Creates a new parametric bullet object and opens the task panel
        for parameter editing.
        """
        doc = App.ActiveDocument
        if not doc:
            App.Console.PrintError("No active document\n")
            return
        
        # Use transaction for undo/redo support
        doc.openTransaction("Create Bullet")
        
        try:
            # Create new bullet object
            bullet = makeBulletFeature("Bullet")
            
            if bullet:
                # Note: For sketch attachment, manually create a PartDesign Body:
                #   1. Switch to PartDesign workbench
                #   2. Create a new Body (PartDesign menu -> Create Body)
                #   3. Select the bullet object
                #   4. In the Body's properties, set "Base Feature" to the bullet object
                #   5. Set the Body as active (double-click or right-click -> Toggle active body)
                # Then you can attach sketches to bullet faces without "make independent copy" dialog
                App.Console.PrintMessage("Bullet created successfully\n")
                App.Console.PrintMessage("  To attach sketches: Create a PartDesign Body and set bullet as BaseFeature\n")
                        
                        # CRITICAL: Set the Body as active for PartDesign operations
                        # This is required for sketch creation and other PartDesign features
                        if App.GuiUp:
                            try:
                                # Set the Body as active in the GUI
                                Gui.Selection.clearSelection()
                                Gui.Selection.addSelection(body)
                                
                                # Activate the Body (make it the active Body for PartDesign)
                                if hasattr(Gui, 'activateWorkbench'):
                                    # Ensure PartDesign workbench is active
                                    try:
                                        Gui.activateWorkbench("PartDesignWorkbench")
                                    except:
                                        pass
                                
                                # Set active Body (if supported by FreeCAD version)
                                if hasattr(Gui.ActiveDocument, 'setActiveBody'):
                                    try:
                                        Gui.ActiveDocument.setActiveBody(body)
                                    except:
                                        pass
                                
                                App.Console.PrintMessage(f"Body '{body.Label}' set as active for PartDesign operations\n")
                            except Exception as e_gui:
                                App.Console.PrintWarning(f"Could not set Body as active in GUI: {e_gui}\n")
                        
                        body_created = True
                        App.Console.PrintMessage("Bullet created in PartDesign Body as base feature\n")
                        App.Console.PrintMessage("  Body Tip set to bullet object\n")
                        App.Console.PrintMessage("  Body is set as active - sketches can now attach to bullet faces\n")
                        App.Console.PrintMessage("  Note: Make sure PartDesign workbench is active for sketch creation\n")
                    else:
                        raise Exception("PartDesign not available")
                except Exception as e:
                    # If Body creation fails, try Part container as fallback
                    App.Console.PrintWarning(f"Could not create PartDesign Body: {e}\n")
                    import traceback
                    traceback.print_exc()
                    try:
                        # Fallback: Create a Part container
                        part_container = doc.addObject("App::Part", "BulletPart")
                        part_container.addObject(bullet)
                        part_container.Label = "Bullet Assembly"
                        App.Console.PrintMessage("Bullet created in Part container (sketch attachment may be limited)\n")
                        
                        if App.GuiUp:
                            Gui.Selection.clearSelection()
                            Gui.Selection.addSelection(part_container)
                    except Exception as e2:
                        # If both fail, continue without container
                        App.Console.PrintWarning(f"Could not create Part container: {e2}\n")
                        App.Console.PrintMessage("Bullet created as standalone object\n")
                
                # Values are now set in makeBulletFeature(), so we can safely open the task panel
                # The task panel will load the correct values
                panel = BulletTaskPanel(bullet)
                Gui.Control.showDialog(panel)
                
                # Recompute after panel is shown to generate geometry
                # execute() will skip if values aren't set (Length check)
                bullet.recompute()
                
                # Commit transaction
                doc.commitTransaction()
                
                # Fit view
                if App.GuiUp:
                    Gui.SendMsgToActiveView("ViewFit")
                
                App.Console.PrintMessage("Bullet created successfully\n")
            else:
                doc.abortTransaction()
                App.Console.PrintError("Failed to create bullet object\n")
                
        except Exception as e:
            # Rollback on error
            doc.abortTransaction()
            App.Console.PrintError(f"Error creating bullet: {str(e)}\n")
            import traceback
            traceback.print_exc()


# Register command (only if Gui is available)
try:
    Gui.addCommand("BulletDesigner_CreateBullet", CreateBulletCommand())
except Exception as e:
    App.Console.PrintError(f"Failed to register CreateBullet command: {e}\n")
