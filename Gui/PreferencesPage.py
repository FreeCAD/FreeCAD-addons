"""
Preferences page for Bullet Designer workbench.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtWidgets, QtCore
import os
import sys

# Add Utils to path
wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(wb_path, "Utils"))

from Utils.MaterialDatabase import get_material_database


class BulletDesignerPreferencesPage:
    """
    Preferences page for Bullet Designer.
    """
    
    def __init__(self):
        """Initialize the preferences page."""
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Bullet Designer Preferences")
        
        layout = QtWidgets.QVBoxLayout(self.form)
        
        # Default material
        material_group = QtWidgets.QGroupBox("Default Material")
        material_layout = QtWidgets.QFormLayout()
        
        material_db = get_material_database()
        material_names = material_db.get_material_names()
        
        self.default_material_combo = QtWidgets.QComboBox()
        self.default_material_combo.addItems(material_names)
        material_layout.addRow("Default Material:", self.default_material_combo)
        
        material_group.setLayout(material_layout)
        layout.addWidget(material_group)
        
        # Default bullet parameters
        defaults_group = QtWidgets.QGroupBox("Default Bullet Parameters")
        defaults_layout = QtWidgets.QFormLayout()
        
        self.default_num_bands_spin = QtWidgets.QSpinBox()
        self.default_num_bands_spin.setRange(0, 6)
        self.default_num_bands_spin.setValue(0)
        defaults_layout.addRow("Default Number of Bands:", self.default_num_bands_spin)
        
        self.default_ogive_type_combo = QtWidgets.QComboBox()
        self.default_ogive_type_combo.addItems(["Tangent", "Secant", "Elliptical"])
        defaults_layout.addRow("Default Ogive Type:", self.default_ogive_type_combo)
        
        self.default_boat_tail_angle_spin = QtWidgets.QDoubleSpinBox()
        self.default_boat_tail_angle_spin.setRange(0.0, 20.0)
        self.default_boat_tail_angle_spin.setSuffix(" °")
        self.default_boat_tail_angle_spin.setValue(9.0)
        defaults_layout.addRow("Default Boat Tail Angle:", self.default_boat_tail_angle_spin)
        
        defaults_group.setLayout(defaults_layout)
        layout.addWidget(defaults_group)
        
        # Units
        units_group = QtWidgets.QGroupBox("Units")
        units_layout = QtWidgets.QFormLayout()
        
        self.units_combo = QtWidgets.QComboBox()
        self.units_combo.addItems(["Metric (mm)", "Imperial (inches)"])
        units_layout.addRow("Display Units:", self.units_combo)
        
        units_group.setLayout(units_layout)
        layout.addWidget(units_group)
        
        layout.addStretch()
    
    def saveSettings(self):
        """Save preferences."""
        # Save to FreeCAD preferences
        param_group = App.ParamGet("User parameter:BaseApp/Preferences/Mod/BulletDesigner")
        
        material_db = get_material_database()
        material_names = material_db.get_material_names()
        default_material = material_names[self.default_material_combo.currentIndex()]
        param_group.SetString("DefaultMaterial", default_material)
        
        param_group.SetInt("DefaultNumBands", self.default_num_bands_spin.value())
        
        ogive_type = self.default_ogive_type_combo.currentText()
        param_group.SetString("DefaultOgiveType", ogive_type)
        
        param_group.SetFloat("DefaultBoatTailAngle", self.default_boat_tail_angle_spin.value())
        
        units_index = self.units_combo.currentIndex()
        param_group.SetInt("Units", units_index)
    
    def loadSettings(self):
        """Load preferences."""
        param_group = App.ParamGet("User parameter:BaseApp/Preferences/Mod/BulletDesigner")
        
        default_material = param_group.GetString("DefaultMaterial", "Gilding Metal (95/5)")
        material_db = get_material_database()
        material_names = material_db.get_material_names()
        index = material_names.index(default_material) if default_material in material_names else 0
        self.default_material_combo.setCurrentIndex(index)
        
        default_num_bands = param_group.GetInt("DefaultNumBands", 0)
        self.default_num_bands_spin.setValue(default_num_bands)
        
        default_ogive_type = param_group.GetString("DefaultOgiveType", "Tangent")
        index = self.default_ogive_type_combo.findText(default_ogive_type)
        if index >= 0:
            self.default_ogive_type_combo.setCurrentIndex(index)
        
        default_angle = param_group.GetFloat("DefaultBoatTailAngle", 9.0)
        self.default_boat_tail_angle_spin.setValue(default_angle)
        
        units = param_group.GetInt("Units", 0)
        self.units_combo.setCurrentIndex(units)


# Register preferences page
Gui.addPreferencePage(BulletDesignerPreferencesPage, "Bullet Designer")
