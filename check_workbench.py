"""
Diagnostic script to check if BulletDesigner workbench is properly configured.
Run this in FreeCAD's Python console.
"""

import FreeCAD as App
import FreeCADGui as Gui
import os

print("=" * 60)
print("BulletDesigner Workbench Diagnostic")
print("=" * 60)

# Check if workbench directory exists
wb_path = "/home/haaken/.local/share/FreeCAD/Mod/BulletDesigner"
print(f"\n1. Workbench path: {wb_path}")
print(f"   Exists: {os.path.exists(wb_path)}")

# Check required files
required_files = ["Init.py", "InitGui.py", "package.xml"]
print("\n2. Required files:")
for f in required_files:
    path = os.path.join(wb_path, f)
    exists = os.path.exists(path)
    print(f"   {f}: {'✓' if exists else '✗ MISSING'}")

# Check if workbench is registered
print("\n3. Workbench registration:")
try:
    # Try to get the workbench
    wb_list = Gui.listWorkbenches()
    if "BulletDesignerWorkbench" in wb_list:
        print("   ✓ Found in workbench list")
    else:
        print("   ✗ NOT found in workbench list")
        print(f"   Available workbenches: {list(wb_list.keys())[:10]}...")
except Exception as e:
    print(f"   Error checking workbenches: {e}")

# Check if workbench is disabled
print("\n4. Disabled workbenches check:")
try:
    param = App.ParamGet("User parameter:BaseApp/Preferences/Workbenches")
    disabled = param.GetString("Disabled", "")
    if "BulletDesigner" in disabled or "Bullet Designer" in disabled:
        print("   ✗ Workbench is DISABLED in preferences")
        print(f"   Disabled list: {disabled}")
    else:
        print("   ✓ Workbench is not disabled")
except Exception as e:
    print(f"   Error checking preferences: {e}")

# Try to import InitGui
print("\n5. Import test:")
try:
    import sys
    sys.path.insert(0, wb_path)
    import InitGui
    print("   ✓ InitGui.py imports successfully")
    print(f"   Workbench class: {InitGui.BulletDesignerWorkbench}")
except Exception as e:
    print(f"   ✗ Failed to import InitGui: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic complete")
print("=" * 60)
