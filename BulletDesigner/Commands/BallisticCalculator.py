"""
Ballistic Calculator command for Bullet Designer workbench.

This command opens a dialog for calculating ballistic properties
including stability, BC, and twist rate recommendations.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtWidgets, QtCore
import os
import sys

# Add Utils to path
wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(wb_path, "Utils"))

from Utils.Calculations import (
    calculate_stability_factor_miller,
    calculate_ballistic_coefficient_g1,
    calculate_sectional_density,
    calculate_recommended_twist_rate
)

# Units: 0 = Metric (m/s, Celsius, hPa), 1 = Imperial (fps, Fahrenheit, inHg)
PREF_GROUP = "User parameter:BaseApp/Preferences/Mod/BulletDesigner"
FPS_TO_MPS = 0.3048
INHG_TO_HPA = 33.8639


def _get_ballistic_units():
    """Get ballistic calculator units from FreeCAD preferences (0=Metric, 1=Imperial)."""
    param = App.ParamGet(PREF_GROUP)
    return param.GetInt("Units", 0)


def _set_ballistic_units(metric):
    """Save ballistic calculator units to FreeCAD preferences."""
    param = App.ParamGet(PREF_GROUP)
    param.SetInt("Units", 0 if metric else 1)


class BallisticCalculatorDialog(QtWidgets.QDialog):
    """
    Dialog for ballistic calculations.
    """
    
    def __init__(self, bullet_obj=None, parent=None):
        """
        Initialize the calculator dialog.
        
        Args:
            bullet_obj: Optional bullet object to use
            parent: Parent widget
        """
        super().__init__(parent)
        self.bullet_obj = bullet_obj
        self.setWindowTitle("Ballistic Calculator")
        self.setMinimumWidth(500)
        self._metric = (_get_ballistic_units() == 0)
        
        self._create_ui()
        self._load_bullet_data()
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Input section
        input_group = QtWidgets.QGroupBox("Input Parameters")
        input_layout = QtWidgets.QFormLayout()
        
        # Units toggle (follows FreeCAD/BulletDesigner preference)
        self.units_combo = QtWidgets.QComboBox()
        self.units_combo.addItems(["Metric (m/s, °C, hPa)", "Imperial (fps, °F, inHg)"])
        self.units_combo.setCurrentIndex(0 if self._metric else 1)
        self.units_combo.currentIndexChanged.connect(self._on_units_changed)
        input_layout.addRow("Units:", self.units_combo)
        
        # Bullet selection
        self.bullet_combo = QtWidgets.QComboBox()
        self._populate_bullet_combo()
        input_layout.addRow("Bullet:", self.bullet_combo)
        
        # Manual entry fields
        self.diameter_spin = QtWidgets.QDoubleSpinBox()
        self.diameter_spin.setRange(0.1, 50.0)
        self.diameter_spin.setSuffix(" mm")
        self.diameter_spin.setDecimals(2)
        input_layout.addRow("Diameter:", self.diameter_spin)
        
        self.length_spin = QtWidgets.QDoubleSpinBox()
        self.length_spin.setRange(1.0, 200.0)
        self.length_spin.setSuffix(" mm")
        self.length_spin.setDecimals(2)
        input_layout.addRow("Length:", self.length_spin)
        
        self.weight_spin = QtWidgets.QDoubleSpinBox()
        self.weight_spin.setRange(1.0, 2000.0)
        self.weight_spin.setSuffix(" grains")
        self.weight_spin.setDecimals(1)
        input_layout.addRow("Weight:", self.weight_spin)
        
        self.ogive_type_combo = QtWidgets.QComboBox()
        self.ogive_type_combo.addItems(["Tangent", "Secant", "Elliptical"])
        input_layout.addRow("Ogive Type:", self.ogive_type_combo)
        
        # Barrel parameters
        self.twist_spin = QtWidgets.QDoubleSpinBox()
        self.twist_spin.setRange(1.0, 50.0)
        self.twist_spin.setSuffix(" inches")
        self.twist_spin.setValue(10.0)
        input_layout.addRow("Barrel Twist:", self.twist_spin)
        
        self.velocity_spin = QtWidgets.QDoubleSpinBox()
        self._apply_velocity_units(set_default=True)
        input_layout.addRow("Velocity:", self.velocity_spin)
        
        # Atmospheric conditions
        self.temp_spin = QtWidgets.QDoubleSpinBox()
        self._apply_temp_units(set_default=True)
        input_layout.addRow("Temperature:", self.temp_spin)
        
        self.pressure_spin = QtWidgets.QDoubleSpinBox()
        self._apply_pressure_units(set_default=True)
        input_layout.addRow("Pressure:", self.pressure_spin)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Results section
        results_group = QtWidgets.QGroupBox("Results")
        results_layout = QtWidgets.QFormLayout()
        
        self.stability_label = QtWidgets.QLabel("N/A")
        results_layout.addRow("Stability Factor:", self.stability_label)
        
        self.stability_status_label = QtWidgets.QLabel("")
        results_layout.addRow("Status:", self.stability_status_label)
        
        self.bc_label = QtWidgets.QLabel("0.0")
        results_layout.addRow("BC (G1):", self.bc_label)
        
        self.sd_label = QtWidgets.QLabel("0.0")
        results_layout.addRow("Sectional Density:", self.sd_label)
        
        self.recommended_twist_label = QtWidgets.QLabel("N/A")
        results_layout.addRow("Recommended Twist:", self.recommended_twist_label)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.calculate_button = QtWidgets.QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        button_layout.addWidget(self.calculate_button)
        
        button_layout.addStretch()
        
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Connect bullet selection change
        self.bullet_combo.currentIndexChanged.connect(self._on_bullet_selected)
    
    def _apply_velocity_units(self, set_default=False):
        """Set velocity spinbox range and suffix; optionally set default value."""
        if self._metric:
            self.velocity_spin.setRange(100.0, 1500.0)
            self.velocity_spin.setSuffix(" m/s")
            if set_default:
                self.velocity_spin.setValue(853.0)
        else:
            self.velocity_spin.setRange(300.0, 5000.0)
            self.velocity_spin.setSuffix(" fps")
            if set_default:
                self.velocity_spin.setValue(2800.0)
        self.velocity_spin.setDecimals(1)
    
    def _apply_temp_units(self, set_default=False):
        """Set temperature spinbox range and suffix; optionally set default value."""
        if self._metric:
            self.temp_spin.setRange(-40.0, 50.0)
            self.temp_spin.setSuffix(" °C")
            if set_default:
                self.temp_spin.setValue(15.0)
        else:
            self.temp_spin.setRange(-40.0, 120.0)
            self.temp_spin.setSuffix(" °F")
            if set_default:
                self.temp_spin.setValue(59.0)
        self.temp_spin.setDecimals(1)
    
    def _apply_pressure_units(self, set_default=False):
        """Set pressure spinbox range and suffix; optionally set default value."""
        if self._metric:
            self.pressure_spin.setRange(800.0, 1200.0)
            self.pressure_spin.setSuffix(" hPa")
            if set_default:
                self.pressure_spin.setValue(1013.25)
        else:
            self.pressure_spin.setRange(23.0, 35.0)
            self.pressure_spin.setSuffix(" inHg")
            if set_default:
                self.pressure_spin.setValue(29.92)
        self.pressure_spin.setDecimals(2)
    
    def _on_units_changed(self, index):
        """Convert current values and switch velocity/temp/pressure to new units."""
        new_metric = (index == 0)
        if new_metric == self._metric:
            return
        
        # Read current values in old units
        vel = self.velocity_spin.value()
        temp = self.temp_spin.value()
        press = self.pressure_spin.value()
        
        self._metric = new_metric
        _set_ballistic_units(self._metric)
        
        # Convert values
        if new_metric:
            vel = vel * FPS_TO_MPS
            temp = (temp - 32.0) * 5.0 / 9.0
            press = press * INHG_TO_HPA
        else:
            vel = vel / FPS_TO_MPS
            temp = temp * 9.0 / 5.0 + 32.0
            press = press / INHG_TO_HPA
        
        # Update range/suffix then set converted values
        self._apply_velocity_units(set_default=False)
        self._apply_temp_units(set_default=False)
        self._apply_pressure_units(set_default=False)
        self.velocity_spin.setValue(vel)
        self.temp_spin.setValue(temp)
        self.pressure_spin.setValue(press)
    
    def _populate_bullet_combo(self):
        """Populate bullet combo box with document objects."""
        self.bullet_combo.addItem("Manual Entry", None)
        
        if App.ActiveDocument:
            for obj in App.ActiveDocument.Objects:
                if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type"):
                    if obj.Proxy.Type == "BulletFeature":
                        self.bullet_combo.addItem(obj.Label, obj)
    
    def _on_bullet_selected(self, index):
        """Called when bullet selection changes."""
        bullet_obj = self.bullet_combo.itemData(index)
        if bullet_obj:
            self._load_bullet_data(bullet_obj)
    
    def _load_bullet_data(self, bullet_obj=None):
        """Load data from bullet object."""
        obj = bullet_obj or self.bullet_obj
        
        if obj and hasattr(obj, "Diameter"):
            self.diameter_spin.setValue(obj.Diameter)
            self.length_spin.setValue(obj.Length)
            self.weight_spin.setValue(obj.ActualWeight if obj.ActualWeight > 0 else obj.Weight)
            
            index = self.ogive_type_combo.findText(obj.OgiveType)
            if index >= 0:
                self.ogive_type_combo.setCurrentIndex(index)
            
            # Select this bullet in combo
            for i in range(self.bullet_combo.count()):
                if self.bullet_combo.itemData(i) == obj:
                    self.bullet_combo.setCurrentIndex(i)
                    break
        
        # Calculate initial results
        self.calculate()
    
    def _get_velocity_mps(self):
        """Return velocity in m/s for calculations."""
        v = self.velocity_spin.value()
        return v if self._metric else (v * FPS_TO_MPS)
    
    def _get_temperature_c(self):
        """Return temperature in Celsius for calculations."""
        t = self.temp_spin.value()
        return t if self._metric else ((t - 32.0) * 5.0 / 9.0)
    
    def _get_pressure_hpa(self):
        """Return pressure in hPa for calculations."""
        p = self.pressure_spin.value()
        return p if self._metric else (p * INHG_TO_HPA)
    
    def calculate(self):
        """Perform ballistic calculations."""
        try:
            diameter = self.diameter_spin.value()
            length = self.length_spin.value()
            weight = self.weight_spin.value()
            ogive_type = self.ogive_type_combo.currentText()
            twist_rate = self.twist_spin.value()
            velocity = self._get_velocity_mps()
            temperature = self._get_temperature_c()
            pressure = self._get_pressure_hpa()
            
            # Get effective diameter and material density from bullet object if available
            effective_diameter = None
            material_density = None
            bullet_obj = self.bullet_obj or (self.bullet_combo.itemData(self.bullet_combo.currentIndex()) if self.bullet_combo.currentIndex() >= 0 else None)
            
            if bullet_obj:
                # For land-riding bullets, effective diameter is groove diameter (where bands engage)
                # For groove-riding bullets, effective diameter equals nominal diameter
                if hasattr(bullet_obj, "LandRiding") and bullet_obj.LandRiding:
                    # Land-riding: effective diameter is groove diameter (diameter property)
                    effective_diameter = diameter
                else:
                    # Groove-riding: effective diameter equals nominal diameter
                    effective_diameter = diameter
                
                # Get material density
                if hasattr(bullet_obj, "Density"):
                    material_density = float(bullet_obj.Density)
            
            # Calculate stability
            App.Console.PrintMessage(f"Ballistic Calculator inputs:\n")
            App.Console.PrintMessage(f"  Diameter: {diameter:.2f} mm\n")
            if effective_diameter and abs(effective_diameter - diameter) > 0.01:
                App.Console.PrintMessage(f"  Effective Diameter: {effective_diameter:.2f} mm (bearing bands)\n")
            App.Console.PrintMessage(f"  Length: {length:.2f} mm\n")
            App.Console.PrintMessage(f"  Weight: {weight:.2f} grains\n")
            if material_density:
                App.Console.PrintMessage(f"  Material Density: {material_density:.2f} g/cm³\n")
            App.Console.PrintMessage(f"  Twist: {twist_rate:.2f} inches\n")
            App.Console.PrintMessage(f"  Velocity: {velocity:.2f} m/s\n")
            App.Console.PrintMessage(f"  Temperature: {temperature:.2f} °C\n")
            App.Console.PrintMessage(f"  Pressure: {pressure:.2f} hPa\n")
            
            stability, threshold = calculate_stability_factor_miller(
                diameter, length, weight, twist_rate,
                velocity, temperature, pressure,
                effective_diameter, material_density
            )
            
            App.Console.PrintMessage(f"  Calculated stability: {stability:.4f}\n")
            App.Console.PrintMessage(f"  Stability threshold: {threshold:.2f} ({'Monolithic copper/brass' if threshold >= 1.8 else 'Lead-core'})\n")
            self.stability_label.setText(f"{stability:.2f}")
            
            # Stability status using correct threshold
            if stability >= threshold:
                status = "Stable (Good)"
                color = "green"
            elif stability >= threshold * 0.67:  # ~1.0 for lead-core, ~1.2 for monolithic
                status = "Marginally Stable"
                color = "orange"
            else:
                status = "Unstable"
                color = "red"
            
            App.Console.PrintMessage(f"  Status: {status} (threshold check: {stability:.4f} >= {threshold:.2f} = {stability >= threshold})\n")
            
            self.stability_status_label.setText(status)
            self.stability_status_label.setStyleSheet(f"color: {color}")
            
            # Calculate BC
            bc = calculate_ballistic_coefficient_g1(
                diameter, weight, length, ogive_type
            )
            self.bc_label.setText(f"{bc:.3f}")
            
            # Calculate SD
            sd = calculate_sectional_density(diameter, weight)
            self.sd_label.setText(f"{sd:.3f}")
            
            # Calculate recommended twist
            twist_rate, twist_str = calculate_recommended_twist_rate(
                diameter, length, weight, velocity,
                effective_diameter, material_density
            )
            self.recommended_twist_label.setText(twist_str)
            
        except Exception as e:
            App.Console.PrintError(f"Error calculating ballistics: {e}\n")


class BallisticCalculatorCommand:
    """
    Command to open ballistic calculator.
    """
    
    def __init__(self):
        """Initialize the command."""
        wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.resources = {
            "Pixmap": os.path.join(
                wb_path, "Resources", "icons", "Calculator.svg"
            ),
            "MenuText": "Ballistic Calculator",
            "ToolTip": "Calculate ballistic properties and stability",
            "Accel": "C"
        }
    
    def GetResources(self):
        """Return command resources."""
        return self.resources
    
    def IsActive(self):
        """Check if command is active."""
        return True
    
    def Activated(self):
        """Execute the command."""
        # Try to get selected bullet
        bullet_obj = None
        if App.ActiveDocument and Gui.Selection.getSelection():
            sel = Gui.Selection.getSelection()[0]
            if hasattr(sel, "Proxy") and hasattr(sel.Proxy, "Type"):
                if sel.Proxy.Type == "BulletFeature":
                    bullet_obj = sel
        
        # Open dialog
        dialog = BallisticCalculatorDialog(bullet_obj)
        dialog.exec_()


# Register command (only if Gui is available)
try:
    Gui.addCommand("BulletDesigner_BallisticCalculator", BallisticCalculatorCommand())
except Exception as e:
    App.Console.PrintError(f"Failed to register BallisticCalculator command: {e}\n")
