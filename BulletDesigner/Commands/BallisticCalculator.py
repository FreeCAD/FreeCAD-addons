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
        
        self._create_ui()
        self._load_bullet_data()
    
    def _create_ui(self):
        """Create the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Input section
        input_group = QtWidgets.QGroupBox("Input Parameters")
        input_layout = QtWidgets.QFormLayout()
        
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
        self.velocity_spin.setRange(100.0, 5000.0)
        self.velocity_spin.setSuffix(" fps")
        self.velocity_spin.setValue(2800.0)
        input_layout.addRow("Velocity:", self.velocity_spin)
        
        # Atmospheric conditions
        self.temp_spin = QtWidgets.QDoubleSpinBox()
        self.temp_spin.setRange(-40.0, 120.0)
        self.temp_spin.setSuffix(" °F")
        self.temp_spin.setValue(59.0)
        input_layout.addRow("Temperature:", self.temp_spin)
        
        self.pressure_spin = QtWidgets.QDoubleSpinBox()
        self.pressure_spin.setRange(20.0, 35.0)
        self.pressure_spin.setSuffix(" inHg")
        self.pressure_spin.setValue(29.92)
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
    
    def calculate(self):
        """Perform ballistic calculations."""
        try:
            diameter = self.diameter_spin.value()
            length = self.length_spin.value()
            weight = self.weight_spin.value()
            ogive_type = self.ogive_type_combo.currentText()
            twist_rate = self.twist_spin.value()
            velocity = self.velocity_spin.value()
            temperature = self.temp_spin.value()
            pressure = self.pressure_spin.value()
            
            # Calculate stability
            stability = calculate_stability_factor_miller(
                diameter, length, weight, twist_rate,
                velocity, temperature, pressure
            )
            self.stability_label.setText(f"{stability:.2f}")
            
            # Stability status
            if stability >= 1.5:
                status = "Stable (Good)"
                color = "green"
            elif stability >= 1.0:
                status = "Marginally Stable"
                color = "orange"
            else:
                status = "Unstable"
                color = "red"
            
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
                diameter, length, weight, velocity
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
