import FreeCAD as App
import FreeCADGui as Gui
import os
wb_path = "/home/haaken/.local/share/FreeCAD/Mod/BulletDesigner"
print("Checking workbench...")
print("Path exists:", os.path.exists(wb_path))
print("InitGui exists:", os.path.exists(os.path.join(wb_path, "InitGui.py")))
wb_list = Gui.listWorkbenches()
print("Registered workbenches:", list(wb_list.keys())[:15])
if "BulletDesignerWorkbench" in str(wb_list):
    print("FOUND BulletDesignerWorkbench")
else:
    print("NOT FOUND in workbench list")
try:
    import sys
    sys.path.insert(0, wb_path)
    import InitGui
    print("InitGui imported OK")
except Exception as e:
    print("Import error:", e)
