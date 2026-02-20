"""
Task panel for bullet parameter editing.

This module provides a GUI panel for editing bullet parameters
with real-time preview updates.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtWidgets, QtCore, QtGui
import os
import sys
import json

# Add Utils to path
wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(wb_path, "Utils"))

from Utils.MaterialDatabase import get_material_database
from Utils.Calculations import calculate_bullet_dimensions_from_weight


class BulletTaskPanel:
    """
    Task panel for editing bullet parameters.
    """
    
    def __init__(self, bullet_obj):
        """
        Initialize the task panel.
        
        Args:
            bullet_obj: The bullet object to edit
        """
        self.bullet_obj = bullet_obj
        self.form = QtWidgets.QWidget()
        self.form.setWindowTitle("Bullet Parameters")
        
        # Create UI
        self._create_ui()
        
        # Don't apply on initial load - only when user changes values
        self._initial_load = True
        
        # Connect signals
        self._connect_signals()
        
        # Load current values (without applying - just display)
        self._load_values()
        
        # Set initial visibility state for land diameter after loading values
        if hasattr(self, 'land_diameter_label') and hasattr(self, 'land_riding_checkbox'):
            land_riding_val = self.land_riding_checkbox.isChecked()
            self.land_diameter_label.setVisible(land_riding_val)
            self.land_diameter_spin.setVisible(land_riding_val)
            self.land_diameter_spin.setEnabled(land_riding_val)
        
        # Mark initial load complete - allow updates now
        # Use Qt timer to mark complete after UI has settled
        QtCore.QTimer.singleShot(100, self._mark_initial_load_complete)
    
    def _mark_initial_load_complete(self):
        """Mark that initial load is complete and updates can proceed."""
        App.Console.PrintMessage("=== TaskPanel: Initial load complete - updates enabled ===\n")
        self._initial_load = False
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QtWidgets.QVBoxLayout(self.form)
        
        # Create tab widget
        tabs = QtWidgets.QTabWidget()
        
        # Basic tab
        basic_tab = self._create_basic_tab()
        tabs.addTab(basic_tab, "Basic")
        
        # Ogive tab
        ogive_tab = self._create_ogive_tab()
        tabs.addTab(ogive_tab, "Ogive")
        
        # Bands tab
        bands_tab = self._create_bands_tab()
        tabs.addTab(bands_tab, "Bands")
        
        # Base tab
        base_tab = self._create_base_tab()
        tabs.addTab(base_tab, "Base")
        
        # Material tab
        material_tab = self._create_material_tab()
        tabs.addTab(material_tab, "Material")
        
        layout.addWidget(tabs)
        
        # Calculated values display
        calc_group = QtWidgets.QGroupBox("Calculated Values")
        calc_layout = QtWidgets.QFormLayout()
        
        self.actual_weight_label = QtWidgets.QLabel("0.0 grains")
        calc_layout.addRow("Actual Weight:", self.actual_weight_label)
        
        self.volume_label = QtWidgets.QLabel("0.0 mm³")
        calc_layout.addRow("Volume:", self.volume_label)
        
        self.bc_label = QtWidgets.QLabel("0.0")
        calc_layout.addRow("BC (G1):", self.bc_label)
        
        self.sd_label = QtWidgets.QLabel("0.0")
        calc_layout.addRow("Sectional Density:", self.sd_label)
        
        self.twist_label = QtWidgets.QLabel("N/A")
        calc_layout.addRow("Recommended Twist:", self.twist_label)
        
        calc_group.setLayout(calc_layout)
        layout.addWidget(calc_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.preview_checkbox = QtWidgets.QCheckBox("Live Preview")
        self.preview_checkbox.setChecked(True)
        button_layout.addWidget(self.preview_checkbox)
        
        button_layout.addStretch()
        
        self.apply_button = QtWidgets.QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_basic_tab(self):
        """Create the basic parameters tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        
        # Design Type selection
        self.design_type_combo = QtWidgets.QComboBox()
        self.design_type_combo.addItems(["Traditional", "VLD"])
        self.design_type_combo.currentTextChanged.connect(self._on_design_type_changed)
        layout.addRow("Design Type:", self.design_type_combo)
        
        # Land Riding checkbox
        self.land_riding_checkbox = QtWidgets.QCheckBox("Land Riding Bullet")
        self.land_riding_checkbox.setToolTip("Body rides on land diameter (6.5mm), bands expand to groove diameter (6.7mm)")
        self.land_riding_checkbox.setChecked(True)
        self.land_riding_checkbox.stateChanged.connect(self._on_land_riding_changed)
        layout.addRow("", self.land_riding_checkbox)
        
        self.diameter_spin = QtWidgets.QDoubleSpinBox()
        self.diameter_spin.setRange(0.1, 50.0)
        self.diameter_spin.setSuffix(" mm")
        self.diameter_spin.setDecimals(2)
        layout.addRow("Diameter:", self.diameter_spin)
        
        self.land_diameter_label = QtWidgets.QLabel("Land Diameter:")
        self.land_diameter_spin = QtWidgets.QDoubleSpinBox()
        self.land_diameter_spin.setRange(0.1, 50.0)
        self.land_diameter_spin.setSuffix(" mm")
        self.land_diameter_spin.setDecimals(2)
        layout.addRow(self.land_diameter_label, self.land_diameter_spin)
        
        self.length_spin = QtWidgets.QDoubleSpinBox()
        self.length_spin.setRange(1.0, 200.0)
        self.length_spin.setSuffix(" mm")
        self.length_spin.setDecimals(2)
        layout.addRow("Length:", self.length_spin)
        
        self.weight_spin = QtWidgets.QDoubleSpinBox()
        self.weight_spin.setRange(1.0, 2000.0)
        self.weight_spin.setSuffix(" grains")
        self.weight_spin.setDecimals(1)
        layout.addRow("Target Weight:", self.weight_spin)
        
        widget.setLayout(layout)
        return widget
    
    def _create_ogive_tab(self):
        """Create the ogive parameters tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        
        self.ogive_type_combo = QtWidgets.QComboBox()
        self.ogive_type_combo.addItems(["Tangent", "Secant", "Elliptical"])
        layout.addRow("Ogive Type:", self.ogive_type_combo)
        
        self.ogive_ratio_spin = QtWidgets.QDoubleSpinBox()
        self.ogive_ratio_spin.setRange(2.0, 15.0)
        self.ogive_ratio_spin.setSuffix(" calibers")
        self.ogive_ratio_spin.setDecimals(1)
        layout.addRow("Ogive Length:", self.ogive_ratio_spin)
        
        self.meplat_spin = QtWidgets.QDoubleSpinBox()
        self.meplat_spin.setRange(0.0, 10.0)
        self.meplat_spin.setSuffix(" mm")
        self.meplat_spin.setDecimals(2)
        layout.addRow("Meplat Diameter:", self.meplat_spin)
        
        widget.setLayout(layout)
        return widget
    
    def _create_bands_tab(self):
        """Create the driving bands tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        
        self.num_bands_spin = QtWidgets.QSpinBox()
        self.num_bands_spin.setRange(0, 6)
        layout.addRow("Number of Bands:", self.num_bands_spin)
        
        self.band_length_spin = QtWidgets.QDoubleSpinBox()
        self.band_length_spin.setRange(0.1, 10.0)
        self.band_length_spin.setSuffix(" mm")
        self.band_length_spin.setDecimals(2)
        layout.addRow("Band Length:", self.band_length_spin)
        
        self.band_spacing_spin = QtWidgets.QDoubleSpinBox()
        self.band_spacing_spin.setRange(0.0, 20.0)
        self.band_spacing_spin.setSuffix(" mm")
        self.band_spacing_spin.setDecimals(2)
        layout.addRow("Band Spacing:", self.band_spacing_spin)
        
        widget.setLayout(layout)
        return widget
    
    def _create_base_tab(self):
        """Create the base parameters tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        
        self.base_type_combo = QtWidgets.QComboBox()
        self.base_type_combo.addItems(["Flat", "BoatTail"])
        layout.addRow("Base Type:", self.base_type_combo)
        
        self.boat_tail_length_spin = QtWidgets.QDoubleSpinBox()
        self.boat_tail_length_spin.setRange(0.0, 20.0)
        self.boat_tail_length_spin.setSuffix(" mm")
        self.boat_tail_length_spin.setDecimals(2)
        layout.addRow("Boat Tail Length:", self.boat_tail_length_spin)
        
        self.boat_tail_angle_spin = QtWidgets.QDoubleSpinBox()
        self.boat_tail_angle_spin.setRange(0.0, 20.0)
        self.boat_tail_angle_spin.setSuffix(" °")
        self.boat_tail_angle_spin.setDecimals(1)
        layout.addRow("Boat Tail Angle:", self.boat_tail_angle_spin)
        
        widget.setLayout(layout)
        return widget
    
    def _create_material_tab(self):
        """Create the material selection tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        
        material_db = get_material_database()
        material_names = material_db.get_material_names()
        
        self.material_combo = QtWidgets.QComboBox()
        self.material_combo.addItems(material_names)
        layout.addRow("Material:", self.material_combo)
        
        self.density_spin = QtWidgets.QDoubleSpinBox()
        self.density_spin.setRange(1.0, 20.0)
        self.density_spin.setSuffix(" g/cm³")
        self.density_spin.setDecimals(2)
        layout.addRow("Density:", self.density_spin)
        
        widget.setLayout(layout)
        return widget
    
    def _connect_signals(self):
        """Connect UI signals to update functions."""
        # Basic - use both valueChanged and editingFinished for spinboxes
        # valueChanged fires while typing, editingFinished fires when done editing
        self.diameter_spin.valueChanged.connect(self._on_parameter_changed)
        self.diameter_spin.editingFinished.connect(self._on_parameter_changed)
        
        self.land_diameter_spin.valueChanged.connect(self._on_parameter_changed)
        self.land_diameter_spin.editingFinished.connect(self._on_parameter_changed)
        
        self.length_spin.valueChanged.connect(self._on_parameter_changed)
        self.length_spin.editingFinished.connect(self._on_parameter_changed)
        
        # Weight needs special handling - recalculate dimensions when changed
        self.weight_spin.valueChanged.connect(self._on_weight_changed)
        self.weight_spin.editingFinished.connect(self._on_weight_changed)
        
        # Ogive
        self.ogive_type_combo.currentTextChanged.connect(self._on_parameter_changed)
        self.ogive_ratio_spin.valueChanged.connect(self._on_parameter_changed)
        self.ogive_ratio_spin.editingFinished.connect(self._on_parameter_changed)
        self.meplat_spin.valueChanged.connect(self._on_parameter_changed)
        self.meplat_spin.editingFinished.connect(self._on_parameter_changed)
        
        # Bands
        self.num_bands_spin.valueChanged.connect(self._on_parameter_changed)
        self.band_length_spin.valueChanged.connect(self._on_parameter_changed)
        self.band_length_spin.editingFinished.connect(self._on_parameter_changed)
        self.band_spacing_spin.valueChanged.connect(self._on_parameter_changed)
        self.band_spacing_spin.editingFinished.connect(self._on_parameter_changed)
        
        # Base
        self.base_type_combo.currentTextChanged.connect(self._on_parameter_changed)
        self.boat_tail_length_spin.valueChanged.connect(self._on_parameter_changed)
        self.boat_tail_length_spin.editingFinished.connect(self._on_parameter_changed)
        self.boat_tail_angle_spin.valueChanged.connect(self._on_parameter_changed)
        self.boat_tail_angle_spin.editingFinished.connect(self._on_parameter_changed)
        
        # Material
        self.material_combo.currentTextChanged.connect(self._on_material_changed)
        self.density_spin.valueChanged.connect(self._on_parameter_changed)
        self.density_spin.editingFinished.connect(self._on_parameter_changed)
    
    def _load_values(self):
        """Load current values from object."""
        if not self.bullet_obj:
            return
        
        # Helper to convert Quantity to float
        def to_float(prop_value):
            """Convert property to float, handling Quantity objects."""
            if hasattr(prop_value, 'getValueAs'):
                try:
                    return prop_value.getValueAs('mm').Value
                except:
                    return float(prop_value.Value)
            elif hasattr(prop_value, 'Value'):
                return float(prop_value.Value)
            return float(prop_value)
        
        def to_angle_deg(prop_value):
            """Convert angle property to degrees."""
            if hasattr(prop_value, 'getValueAs'):
                try:
                    return prop_value.getValueAs('deg').Value
                except:
                    return float(prop_value.Value)
            elif hasattr(prop_value, 'Value'):
                return float(prop_value.Value)
            return float(prop_value)
        
        try:
            # Basic
            if hasattr(self.bullet_obj, "DesignType"):
                # Block signals to prevent triggering _on_design_type_changed during load
                obj_design_type = self.bullet_obj.DesignType
                App.Console.PrintMessage(f"=== _load_values() - Loading DesignType ===\n")
                App.Console.PrintMessage(f"  bullet_obj.DesignType = {obj_design_type}\n")
                App.Console.PrintMessage(f"  Combo box currentText before load: {self.design_type_combo.currentText()}\n")
                self.design_type_combo.blockSignals(True)
                index = self.design_type_combo.findText(obj_design_type)
                if index >= 0:
                    self.design_type_combo.setCurrentIndex(index)
                    App.Console.PrintMessage(f"  Set combo box to index {index} ({obj_design_type})\n")
                else:
                    App.Console.PrintWarning(f"  WARNING: DesignType '{obj_design_type}' not found in combo box!\n")
                self.design_type_combo.blockSignals(False)
                App.Console.PrintMessage(f"  Combo box currentText after load: {self.design_type_combo.currentText()}\n")
            if hasattr(self.bullet_obj, "LandRiding"):
                land_riding_val = bool(self.bullet_obj.LandRiding)
                App.Console.PrintMessage(f"=== _load_values() - Loading LandRiding ===\n")
                App.Console.PrintMessage(f"  bullet_obj.LandRiding = {land_riding_val}\n")
                App.Console.PrintMessage(f"  Checkbox isChecked() before load: {self.land_riding_checkbox.isChecked()}\n")
                # Block signals to prevent triggering _on_land_riding_changed during load
                self.land_riding_checkbox.blockSignals(True)
                self.land_riding_checkbox.setChecked(land_riding_val)
                self.land_riding_checkbox.blockSignals(False)
                App.Console.PrintMessage(f"  Set checkbox to {land_riding_val}\n")
                App.Console.PrintMessage(f"  Checkbox isChecked() after load: {self.land_riding_checkbox.isChecked()}\n")
                # Update land diameter visibility based on land riding state
                self.land_diameter_label.setVisible(land_riding_val)
                self.land_diameter_spin.setVisible(land_riding_val)
                self.land_diameter_spin.setEnabled(land_riding_val)
                App.Console.PrintMessage(f"  Updated UI visibility: land_diameter_label/spin visible={land_riding_val}, enabled={land_riding_val}\n")
            if hasattr(self.bullet_obj, "Diameter"):
                self.diameter_spin.setValue(to_float(self.bullet_obj.Diameter))
            if hasattr(self.bullet_obj, "LandDiameter"):
                land_dia_val = to_float(self.bullet_obj.LandDiameter)
                # Fix if LandDiameter is wrong (should be around 6.5, not 0.1)
                # But don't write back during initial load - just display correct value in UI
                if land_dia_val < 1.0 or land_dia_val > 10.0:
                    App.Console.PrintWarning(f"TaskPanel: LandDiameter is wrong ({land_dia_val}), displaying 6.50 in UI\n")
                    land_dia_val = 6.50
                    # Only fix if not during initial load
                    if not (hasattr(self, '_initial_load') and self._initial_load):
                        self.bullet_obj.LandDiameter = 6.50
                self.land_diameter_spin.setValue(land_dia_val)
            if hasattr(self.bullet_obj, "Length"):
                length_val = to_float(self.bullet_obj.Length)
                # Fix if Length is wrong (should be around 32.0, not 1.0 or very small)
                # But don't write back during initial load - just display correct value in UI
                if length_val < 10.0 or length_val > 100.0:
                    App.Console.PrintWarning(f"TaskPanel: Length is wrong ({length_val}), displaying calculated value in UI\n")
                    # Don't reset to 32.0 - keep the calculated value if it exists
                    # Just display what's in the object
                    pass
                self.length_spin.setValue(length_val)
            if hasattr(self.bullet_obj, "Weight"):
                weight_val = float(self.bullet_obj.Weight)
                # Fix if Weight is wrong (should be around 140, not 1)
                # But don't write back during initial load - just display correct value in UI
                if weight_val < 10.0 or weight_val > 1000.0:
                    App.Console.PrintWarning(f"TaskPanel: Weight is wrong ({weight_val}), displaying 140.0 in UI\n")
                    weight_val = 140.0
                    # Always fix the object property if it's wrong
                    self.bullet_obj.Weight = 140.0
                # Block signals temporarily to prevent triggering _on_weight_changed during load
                self.weight_spin.blockSignals(True)
                self.weight_spin.setValue(weight_val)
                self.weight_spin.blockSignals(False)
            
            # Ogive
            if hasattr(self.bullet_obj, "OgiveType"):
                index = self.ogive_type_combo.findText(self.bullet_obj.OgiveType)
                if index >= 0:
                    self.ogive_type_combo.setCurrentIndex(index)
            if hasattr(self.bullet_obj, "OgiveCaliberRatio"):
                self.ogive_ratio_spin.setValue(float(self.bullet_obj.OgiveCaliberRatio))
            if hasattr(self.bullet_obj, "MeplatDiameter"):
                self.meplat_spin.setValue(to_float(self.bullet_obj.MeplatDiameter))
            
            # Bands
            if hasattr(self.bullet_obj, "NumBands"):
                self.num_bands_spin.setValue(int(self.bullet_obj.NumBands))
            if hasattr(self.bullet_obj, "BandLength"):
                self.band_length_spin.setValue(to_float(self.bullet_obj.BandLength))
            if hasattr(self.bullet_obj, "BandSpacing"):
                self.band_spacing_spin.setValue(to_float(self.bullet_obj.BandSpacing))
            
            # Base
            if hasattr(self.bullet_obj, "BaseType"):
                index = self.base_type_combo.findText(self.bullet_obj.BaseType)
                if index >= 0:
                    self.base_type_combo.setCurrentIndex(index)
            if hasattr(self.bullet_obj, "BoatTailLength"):
                self.boat_tail_length_spin.setValue(to_float(self.bullet_obj.BoatTailLength))
            if hasattr(self.bullet_obj, "BoatTailAngle"):
                self.boat_tail_angle_spin.setValue(to_angle_deg(self.bullet_obj.BoatTailAngle))
            
            # Material
            if hasattr(self.bullet_obj, "Material"):
                index = self.material_combo.findText(self.bullet_obj.Material)
                if index >= 0:
                    self.material_combo.setCurrentIndex(index)
            if hasattr(self.bullet_obj, "Density"):
                self.density_spin.setValue(float(self.bullet_obj.Density))
            
            # Update calculated values
            self._update_calculated_values()
        except Exception as e:
            App.Console.PrintError(f"Error loading values: {e}\n")
            import traceback
            traceback.print_exc()
    
    def _on_weight_changed(self):
        """Called when weight changes - recalculate dimensions."""
        # Don't apply during initial load
        if hasattr(self, '_initial_load') and self._initial_load:
            return
        
        App.Console.PrintMessage(f"=== _on_weight_changed() - Weight changed to {self.weight_spin.value()} grains ===\n")
        
        # Always apply if preview is enabled (live preview)
        if self.preview_checkbox.isChecked():
            self.apply()
        else:
            App.Console.PrintMessage("  Live Preview disabled - changes will apply on OK\n")
    
    def _on_parameter_changed(self):
        """Called when any parameter changes."""
        # Don't apply during initial load - wait for user interaction
        if hasattr(self, '_initial_load') and self._initial_load:
            # Mark that user has interacted, so future changes should apply
            # But don't apply on this first change (it's just UI initialization)
            return
        
        App.Console.PrintMessage("=== _on_parameter_changed() - Parameter changed ===\n")
        
        # Always apply if preview is enabled (live preview)
        if self.preview_checkbox.isChecked():
            self.apply()
        else:
            App.Console.PrintMessage("  Live Preview disabled - changes will apply on OK\n")
    
    def _on_material_changed(self, material_name):
        """Called when material selection changes."""
        material_db = get_material_database()
        density = material_db.get_density(material_name)
        self.density_spin.setValue(density)
    
    def _on_land_riding_changed(self, state):
        """Handle land riding checkbox change."""
        if not self.bullet_obj:
            App.Console.PrintMessage(f"=== _on_land_riding_changed() - No bullet_obj, returning ===\n")
            return
        
        # Skip during initial load
        if hasattr(self, '_initial_load') and self._initial_load:
            App.Console.PrintMessage("=== _on_land_riding_changed() - Skipped (initial load) ===\n")
            return
        
        is_checked = (state == 2)  # Qt.Checked = 2
        
        # Get current value before change
        old_land_riding = self.bullet_obj.LandRiding if hasattr(self.bullet_obj, "LandRiding") else "None"
        App.Console.PrintMessage(f"=== _on_land_riding_changed() ===\n")
        App.Console.PrintMessage(f"  Checkbox state: {state} (Qt.Checked=2)\n")
        App.Console.PrintMessage(f"  Old LandRiding: {old_land_riding}\n")
        App.Console.PrintMessage(f"  New LandRiding: {is_checked}\n")
        App.Console.PrintMessage(f"  Checkbox isChecked(): {self.land_riding_checkbox.isChecked()}\n")
        
        # Show/hide land diameter based on checkbox state
        self.land_diameter_label.setVisible(is_checked)
        self.land_diameter_spin.setVisible(is_checked)
        self.land_diameter_spin.setEnabled(is_checked)
        App.Console.PrintMessage(f"  Updated UI visibility: land_diameter_label/spin visible={is_checked}, enabled={is_checked}\n")
        
        # Update object property
        if hasattr(self.bullet_obj, "LandRiding"):
            self.bullet_obj.LandRiding = is_checked
            App.Console.PrintMessage(f"  Set bullet_obj.LandRiding = {is_checked}\n")
            App.Console.PrintMessage(f"  Verified bullet_obj.LandRiding = {self.bullet_obj.LandRiding}\n")
        
        # Force recompute to update geometry immediately
        try:
            App.Console.PrintMessage("  Calling bullet_obj.recompute()\n")
            self.bullet_obj.recompute()
            # Update view
            if App.GuiUp:
                App.Console.PrintMessage("  Calling App.ActiveDocument.recompute()\n")
                App.ActiveDocument.recompute()
                Gui.updateGui()
                if hasattr(Gui, 'ActiveDocument') and Gui.ActiveDocument:
                    Gui.ActiveDocument.update()
        except Exception as e:
            App.Console.PrintError(f"Error updating geometry: {e}\n")
            import traceback
            traceback.print_exc()
    
    def _on_design_type_changed(self, design_type):
        """Called when design type changes."""
        if not self.bullet_obj:
            App.Console.PrintMessage(f"=== _on_design_type_changed() - No bullet_obj, returning ===\n")
            return
        
        # Skip during initial load
        if hasattr(self, '_initial_load') and self._initial_load:
            App.Console.PrintMessage(f"=== _on_design_type_changed() - Skipped (initial load) ===\n")
            return
        
        # Get current value before change
        old_design_type = self.bullet_obj.DesignType if hasattr(self.bullet_obj, "DesignType") else "None"
        App.Console.PrintMessage(f"=== _on_design_type_changed() ===\n")
        App.Console.PrintMessage(f"  Old DesignType: {old_design_type}\n")
        App.Console.PrintMessage(f"  New DesignType: {design_type}\n")
        App.Console.PrintMessage(f"  Combo box currentText: {self.design_type_combo.currentText()}\n")
        
        # CRITICAL: Set the DesignType property first, otherwise _load_values() will reset it
        if hasattr(self.bullet_obj, "DesignType"):
            self.bullet_obj.DesignType = design_type
            App.Console.PrintMessage(f"  Set bullet_obj.DesignType = {design_type}\n")
            App.Console.PrintMessage(f"  Verified bullet_obj.DesignType = {self.bullet_obj.DesignType}\n")
        
        # Update defaults based on design type (DO NOT change LandRiding)
        if design_type == "VLD":
            # VLD defaults - optimized for high BC
            if hasattr(self.bullet_obj, "OgiveType"):
                self.bullet_obj.OgiveType = "Secant"
            if hasattr(self.bullet_obj, "OgiveCaliberRatio"):
                self.bullet_obj.OgiveCaliberRatio = 9.0
            if hasattr(self.bullet_obj, "MeplatDiameter"):
                self.bullet_obj.MeplatDiameter = 0.5
            if hasattr(self.bullet_obj, "BoatTailLength"):
                self.bullet_obj.BoatTailLength = 8.0
            if hasattr(self.bullet_obj, "BoatTailAngle"):
                self.bullet_obj.BoatTailAngle = 8.0
        else:
            # Traditional defaults
            if hasattr(self.bullet_obj, "OgiveType"):
                self.bullet_obj.OgiveType = "Tangent"
            if hasattr(self.bullet_obj, "OgiveCaliberRatio"):
                self.bullet_obj.OgiveCaliberRatio = 7.0
            if hasattr(self.bullet_obj, "MeplatDiameter"):
                self.bullet_obj.MeplatDiameter = 1.5
            if hasattr(self.bullet_obj, "BoatTailLength"):
                self.bullet_obj.BoatTailLength = 5.0
            if hasattr(self.bullet_obj, "BoatTailAngle"):
                self.bullet_obj.BoatTailAngle = 9.0
        
        # Reload values to update UI
        self._load_values()
        
        # Force recompute to update geometry immediately
        try:
            App.Console.PrintMessage("  Calling bullet_obj.recompute()\n")
            self.bullet_obj.recompute()
            # Update view
            if App.GuiUp:
                App.Console.PrintMessage("  Calling App.ActiveDocument.recompute()\n")
                App.ActiveDocument.recompute()
                Gui.updateGui()
                if hasattr(Gui, 'ActiveDocument') and Gui.ActiveDocument:
                    Gui.ActiveDocument.update()
        except Exception as e:
            App.Console.PrintError(f"Error updating geometry: {e}\n")
            import traceback
            traceback.print_exc()
    
    def _update_calculated_values(self):
        """Update the calculated values display."""
        if not self.bullet_obj:
            return
        
        try:
            # Helper to safely get float value from Quantity
            def get_float_value(prop_value):
                """Get float value from property, handling Quantity objects."""
                if hasattr(prop_value, 'Value'):
                    return float(prop_value.Value)
                return float(prop_value)
            
            # Update labels with safe value extraction
            weight_val = get_float_value(self.bullet_obj.ActualWeight) if hasattr(self.bullet_obj, "ActualWeight") else 0.0
            self.actual_weight_label.setText(f"{weight_val:.1f} grains")
            
            volume_val = get_float_value(self.bullet_obj.Volume) if hasattr(self.bullet_obj, "Volume") else 0.0
            self.volume_label.setText(f"{volume_val:.2f} mm³")
            
            bc_val = get_float_value(self.bullet_obj.BC_G1) if hasattr(self.bullet_obj, "BC_G1") else 0.0
            self.bc_label.setText(f"{bc_val:.3f}")
            
            sd_val = get_float_value(self.bullet_obj.SectionalDensity) if hasattr(self.bullet_obj, "SectionalDensity") else 0.0
            self.sd_label.setText(f"{sd_val:.3f}")
            
            twist_val = str(self.bullet_obj.RecommendedTwist) if hasattr(self.bullet_obj, "RecommendedTwist") else "N/A"
            self.twist_label.setText(twist_val)
        except Exception as e:
            App.Console.PrintError(f"Error updating calculated values: {e}\n")
            import traceback
            traceback.print_exc()
    
    def apply(self):
        """Apply current parameter values to object."""
        if not self.bullet_obj:
            return
        
        # Don't apply during initial load
        if hasattr(self, '_initial_load') and self._initial_load:
            App.Console.PrintLog("TaskPanel: Skipping apply() during initial load\n")
            return
        
        App.Console.PrintMessage("=== TaskPanel.apply() - Applying parameter changes ===\n")
        
        try:
            # Basic
            self.bullet_obj.DesignType = self.design_type_combo.currentText()
            self.bullet_obj.LandRiding = self.land_riding_checkbox.isChecked()
            self.bullet_obj.Diameter = self.diameter_spin.value()
            self.bullet_obj.LandDiameter = self.land_diameter_spin.value()
            
            # Check if weight changed - if so, recalculate dimensions
            new_weight = self.weight_spin.value()
            old_weight = float(self.bullet_obj.Weight) if hasattr(self.bullet_obj, "Weight") else new_weight
            
            # Always recalculate if weight changed (even slightly)
            if abs(new_weight - old_weight) > 0.01:  # Weight changed (use smaller threshold)
                # Recalculate dimensions from weight
                self._recalculate_dimensions_from_weight(new_weight)
            else:
                # Just set length from UI
                self.bullet_obj.Length = self.length_spin.value()
            
            # Always update weight property
            self.bullet_obj.Weight = new_weight
            
            # Ogive
            self.bullet_obj.OgiveType = self.ogive_type_combo.currentText()
            self.bullet_obj.OgiveCaliberRatio = self.ogive_ratio_spin.value()
            self.bullet_obj.MeplatDiameter = self.meplat_spin.value()
            
            # Bands
            self.bullet_obj.NumBands = self.num_bands_spin.value()
            self.bullet_obj.BandLength = self.band_length_spin.value()
            self.bullet_obj.BandSpacing = self.band_spacing_spin.value()
            
            # Base
            self.bullet_obj.BaseType = self.base_type_combo.currentText()
            self.bullet_obj.BoatTailLength = self.boat_tail_length_spin.value()
            self.bullet_obj.BoatTailAngle = self.boat_tail_angle_spin.value()
            
            # Material
            self.bullet_obj.Material = self.material_combo.currentText()
            self.bullet_obj.Density = self.density_spin.value()
            
            # Recompute the object
            App.Console.PrintMessage("  Calling bullet_obj.recompute()\n")
            self.bullet_obj.recompute()
            
            # Force document recompute and view update
            if App.GuiUp:
                App.Console.PrintMessage("  Calling App.ActiveDocument.recompute()\n")
                App.ActiveDocument.recompute()
                # Update the view to show changes
                Gui.updateGui()
                # Refresh the 3D view
                if hasattr(Gui, 'ActiveDocument') and Gui.ActiveDocument:
                    Gui.ActiveDocument.update()
            
            App.Console.PrintMessage("=== TaskPanel.apply() complete ===\n")
            
            # Update calculated values
            self._update_calculated_values()
            
        except Exception as e:
            App.Console.PrintError(f"Error applying parameters: {e}\n")
            import traceback
            traceback.print_exc()
    
    def _recalculate_dimensions_from_weight(self, target_weight):
        """Recalculate bullet dimensions from target weight."""
        if not self.bullet_obj:
            return
        
        try:
            # Get current parameters
            diameter_mm = float(self.bullet_obj.Diameter.getValueAs('mm').Value) if hasattr(self.bullet_obj.Diameter, 'getValueAs') else float(self.bullet_obj.Diameter)
            land_diameter_mm = float(self.bullet_obj.LandDiameter.getValueAs('mm').Value) if hasattr(self.bullet_obj.LandDiameter, 'getValueAs') else float(self.bullet_obj.LandDiameter)
            density = float(self.bullet_obj.Density) if hasattr(self.bullet_obj, "Density") else 8.70
            num_bands = int(self.bullet_obj.NumBands) if hasattr(self.bullet_obj, "NumBands") else 4
            band_length_mm = float(self.bullet_obj.BandLength.getValueAs('mm').Value) if hasattr(self.bullet_obj.BandLength, 'getValueAs') else float(self.bullet_obj.BandLength)
            band_spacing_mm = float(self.bullet_obj.BandSpacing.getValueAs('mm').Value) if hasattr(self.bullet_obj.BandSpacing, 'getValueAs') else float(self.bullet_obj.BandSpacing)
            ogive_caliber_ratio = float(self.bullet_obj.OgiveCaliberRatio) if hasattr(self.bullet_obj, "OgiveCaliberRatio") else 7.0
            ogive_type = self.bullet_obj.OgiveType if hasattr(self.bullet_obj, "OgiveType") else "Tangent"
            boat_tail_angle_deg = float(self.bullet_obj.BoatTailAngle.getValueAs('deg').Value) if hasattr(self.bullet_obj.BoatTailAngle, 'getValueAs') else float(self.bullet_obj.BoatTailAngle)
            meplat_diameter_mm = float(self.bullet_obj.MeplatDiameter.getValueAs('mm').Value) if hasattr(self.bullet_obj.MeplatDiameter, 'getValueAs') else float(self.bullet_obj.MeplatDiameter)
            land_riding = bool(self.bullet_obj.LandRiding) if hasattr(self.bullet_obj, "LandRiding") else True
            
            # Calculate optimal dimensions
            result = calculate_bullet_dimensions_from_weight(
                target_weight_grains=target_weight,
                groove_diameter_mm=diameter_mm,
                land_diameter_mm=land_diameter_mm,
                density_g_per_cm3=density,
                num_bands=num_bands,
                band_length_mm=band_length_mm,
                band_spacing_mm=band_spacing_mm,
                ogive_caliber_ratio=ogive_caliber_ratio,
                ogive_type=ogive_type,
                boat_tail_angle_deg=boat_tail_angle_deg,
                meplat_diameter_mm=meplat_diameter_mm,
                land_riding=land_riding
            )
            
            if result and result.get('valid', False):
                # Update dimensions
                total_length_mm = result.get('total_length_mm', 32.0)
                boat_tail_length_mm = result.get('boat_tail_length_mm', 5.0)
                
                self.bullet_obj.Length = App.Units.Quantity(f"{total_length_mm:.2f} mm")
                self.bullet_obj.BoatTailLength = App.Units.Quantity(f"{boat_tail_length_mm:.2f} mm")
                
                # Update UI to reflect new values
                self.length_spin.setValue(total_length_mm)
                self.boat_tail_length_spin.setValue(boat_tail_length_mm)
                
                App.Console.PrintMessage(f"Recalculated dimensions: Length={total_length_mm:.2f}mm, BoatTail={boat_tail_length_mm:.2f}mm\n")
        except Exception as e:
            App.Console.PrintError(f"Error recalculating dimensions from weight: {e}\n")
            import traceback
            traceback.print_exc()
    
    def accept(self):
        """Accept and close the panel."""
        # Mark that initial load is complete before applying
        if hasattr(self, '_initial_load'):
            self._initial_load = False
        self.apply()
        Gui.Control.closeDialog()
    
    def reject(self):
        """Cancel and close the panel."""
        Gui.Control.closeDialog()
    
    def getStandardButtons(self):
        """Return standard dialog buttons."""
        return int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
