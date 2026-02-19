"""
Trajectory Calculator command for Bullet Designer workbench.

This command opens a dialog for calculating bullet trajectory including
transonic zone analysis, drop, spin drift, and velocity decay.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide2 import QtWidgets, QtCore, QtGui
import os
import sys
import math
import bisect

# Add Utils to path
wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(wb_path, "Utils"))

from Utils.Calculations import (
    calculate_stability_factor_miller,
    calculate_ballistic_coefficient_g1,
    calculate_sectional_density
)
from Utils.MaterialDatabase import get_material_database

# G7 Reference Drag Table (CD vs Mach)
MACH_TABLE = [0.0, 0.5, 0.7, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925,
               0.95, 0.975, 1.0, 1.025, 1.05, 1.1, 1.2, 1.3, 1.5,
               1.8, 2.0, 2.5, 3.0]
CD_TABLE = [0.1198, 0.1197, 0.1196, 0.1312, 0.1352, 0.1404, 0.1479,
            0.1589, 0.1776, 0.2034, 0.2165, 0.2346, 0.2407, 0.2497,
            0.2596, 0.2677, 0.2680, 0.2656, 0.2458, 0.2344, 0.2049, 0.1776]


def interpolate_cd_g7(mach: float) -> float:
    """
    Interpolate G7 drag coefficient from mach number.
    
    Uses linear interpolation between table points.
    
    Args:
        mach: Mach number
        
    Returns:
        G7 drag coefficient (CD)
    """
    if mach <= 0:
        return CD_TABLE[0]
    if mach >= MACH_TABLE[-1]:
        return CD_TABLE[-1]
    
    # Find insertion point
    idx = bisect.bisect_left(MACH_TABLE, mach)
    
    if idx == 0:
        return CD_TABLE[0]
    if idx >= len(MACH_TABLE):
        return CD_TABLE[-1]
    
    # Linear interpolation
    mach_low = MACH_TABLE[idx - 1]
    mach_high = MACH_TABLE[idx]
    cd_low = CD_TABLE[idx - 1]
    cd_high = CD_TABLE[idx]
    
    if mach_high == mach_low:
        return cd_low
    
    t = (mach - mach_low) / (mach_high - mach_low)
    return cd_low + t * (cd_high - cd_low)


def calculate_g7_bc_from_g1(bc_g1: float, boat_tail_angle_deg: float) -> float:
    """
    Calculate G7 BC from G1 BC using boat tail angle conversion factor.
    
    BC_G7 = BC_G1 / conversion_factor
    
    Conversion factors based on boat tail angle:
    - 7-9° boat tail → 2.0
    - 5-7° boat tail → 2.1
    - 9-11° boat tail → 1.95
    - flat base → 2.3
    
    Args:
        bc_g1: G1 ballistic coefficient
        boat_tail_angle_deg: Boat tail angle in degrees (0 for flat base)
        
    Returns:
        G7 ballistic coefficient
    """
    if boat_tail_angle_deg <= 0:
        # Flat base
        conversion_factor = 2.3
    elif 5.0 <= boat_tail_angle_deg < 7.0:
        conversion_factor = 2.1
    elif 7.0 <= boat_tail_angle_deg <= 9.0:
        conversion_factor = 2.0
    elif 9.0 < boat_tail_angle_deg <= 11.0:
        conversion_factor = 1.95
    else:
        # Interpolate for angles outside standard ranges
        if boat_tail_angle_deg < 5.0:
            # Between flat and 5°
            t = boat_tail_angle_deg / 5.0
            conversion_factor = 2.3 - t * (2.3 - 2.1)
        else:  # > 11°
            # Extrapolate beyond 11°
            conversion_factor = 1.95 - (boat_tail_angle_deg - 11.0) * 0.01
    
    return bc_g1 / conversion_factor


def calculate_air_density(pressure_hpa: float, temperature_c: float) -> float:
    """
    Calculate air density using ideal gas law.
    
    rho = (P_pa * 0.0289644) / (8.31446 * T_kelvin)
    
    Where:
    - P_pa = pressure in Pascals (hPa * 100)
    - T_kelvin = temperature in Kelvin (Celsius + 273.15)
    - 0.0289644 = molar mass of dry air (kg/mol)
    - 8.31446 = universal gas constant (J/(mol·K))
    
    Args:
        pressure_hpa: Atmospheric pressure in hectopascals
        temperature_c: Temperature in Celsius
        
    Returns:
        Air density in kg/m³
    """
    pressure_pa = pressure_hpa * 100.0
    temperature_kelvin = temperature_c + 273.15
    
    if temperature_kelvin <= 0:
        return 0.0
    
    rho = (pressure_pa * 0.0289644) / (8.31446 * temperature_kelvin)
    return rho


def calculate_speed_of_sound(temperature_c: float) -> float:
    """
    Calculate speed of sound in air.
    
    c = 331.3 * sqrt(T_kelvin / 273.15)
    
    Args:
        temperature_c: Temperature in Celsius
        
    Returns:
        Speed of sound in m/s
    """
    temperature_kelvin = temperature_c + 273.15
    if temperature_kelvin <= 0:
        return 331.3
    
    c = 331.3 * math.sqrt(temperature_kelvin / 273.15)
    return c


def calculate_spin_drift(stability_factor: float, length_mm: float, diameter_mm: float, range_m: float) -> float:
    """
    Calculate spin drift using Litz empirical formula.
    
    drift_inches = 1.25 * (SG + 1.2) * (bullet_length_calibers ** 1.83)
    
    Converted to mm per 100m interval for display.
    
    Args:
        stability_factor: Miller stability factor (SG)
        length_mm: Bullet length in mm
        diameter_mm: Bullet diameter in mm
        range_m: Range in meters
        
    Returns:
        Spin drift in millimeters (cumulative at this range)
    """
    if diameter_mm <= 0 or length_mm <= 0:
        return 0.0
    
    # Convert to inches and calibers
    length_inches = length_mm / 25.4
    diameter_inches = diameter_mm / 25.4
    bullet_length_calibers = length_inches / diameter_inches
    
    # Litz formula (gives drift per 100 yards, converted to per 100m)
    # Formula gives drift in inches per 100 yards
    drift_per_100yd_inches = 1.25 * (stability_factor + 1.2) * (bullet_length_calibers ** 1.83)
    
    # Convert to mm per 100m
    # 100 yards = 91.44 meters
    drift_per_100m_mm = (drift_per_100yd_inches * 25.4) * (100.0 / 91.44)
    
    # Scale by range (drift accumulates with range)
    # Approximate: drift increases roughly quadratically with range
    drift_at_range = drift_per_100m_mm * (range_m / 100.0) ** 1.5
    
    return drift_at_range


def trajectory_derivatives(state, rho, A, m_kg, i7, c):
    """
    Calculate derivatives for RK4 trajectory integration.
    
    State vector: [x, y, vx, vy]
    Returns: [dx/dt, dy/dt, dvx/dt, dvy/dt]
    
    Args:
        state: State vector [x, y, vx, vy]
        rho: Air density (kg/m³)
        A: Bullet cross-sectional area (m²)
        m_kg: Bullet mass (kg)
        i7: G7 form factor (SD / BC_G7)
        c: Speed of sound (m/s)
        
    Returns:
        Derivative vector [vx, vy, ax, ay]
    """
    x, y, vx, vy = state
    
    # Velocity magnitude
    v = math.sqrt(vx * vx + vy * vy)
    
    if v <= 0:
        return [0.0, 0.0, 0.0, -9.80665]
    
    # Mach number
    mach = v / c if c > 0 else 0.0
    
    # G7 drag coefficient
    cd_g7 = interpolate_cd_g7(mach)
    
    # Bullet drag coefficient
    cd = i7 * cd_g7
    
    # Drag force
    F_drag = 0.5 * rho * v * v * cd * A
    
    # Acceleration components
    ax = -(F_drag / m_kg) * (vx / v)
    ay = -(F_drag / m_kg) * (vy / v) - 9.80665
    
    return [vx, vy, ax, ay]


def integrate_trajectory_rk4(
    v0_mps: float,
    elevation_deg: float,
    rho: float,
    A: float,
    m_kg: float,
    i7: float,
    c: float,
    max_range_m: float,
    stability_factor: float,
    length_mm: float,
    diameter_mm: float,
    min_velocity_mps: float = 50.0
):
    """
    Integrate bullet trajectory using RK4 method.
    
    Args:
        v0_mps: Initial velocity in m/s
        elevation_deg: Barrel elevation angle in degrees
        rho: Air density (kg/m³)
        A: Bullet cross-sectional area (m²)
        m_kg: Bullet mass (kg)
        i7: G7 form factor (SD / BC_G7)
        c: Speed of sound (m/s)
        max_range_m: Maximum range to calculate (m)
        stability_factor: Miller stability factor for spin drift calculation
        length_mm: Bullet length in mm
        diameter_mm: Bullet diameter in mm
        min_velocity_mps: Minimum velocity threshold (default 50 m/s)
        
    Returns:
        List of trajectory points: [(range_m, velocity_mps, mach, drop_cm, spin_drift_mm, time_s), ...]
    """
    # Initial state: [x, y, vx, vy]
    elevation_rad = math.radians(elevation_deg)
    state = [0.0, 0.0, v0_mps * math.cos(elevation_rad), v0_mps * math.sin(elevation_rad)]
    
    dt = 0.001  # Time step: 1 ms
    t = 0.0
    
    trajectory_points = []
    last_output_range = -100.0  # Track last output to output at 100m intervals
    
    while True:
        # Calculate derivatives
        k1 = trajectory_derivatives(state, rho, A, m_kg, i7, c)
        k2_state = [state[i] + dt/2 * k1[i] for i in range(4)]
        k2 = trajectory_derivatives(k2_state, rho, A, m_kg, i7, c)
        k3_state = [state[i] + dt/2 * k2[i] for i in range(4)]
        k3 = trajectory_derivatives(k3_state, rho, A, m_kg, i7, c)
        k4_state = [state[i] + dt * k3[i] for i in range(4)]
        k4 = trajectory_derivatives(k4_state, rho, A, m_kg, i7, c)
        
        # Update state using RK4
        for i in range(4):
            state[i] += dt / 6.0 * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i])
        
        t += dt
        
        # Current position and velocity
        x = state[0]
        y = state[1]
        vx = state[2]
        vy = state[3]
        v = math.sqrt(vx * vx + vy * vy)
        mach = v / c if c > 0 else 0.0
        
        # Check termination conditions
        if v < min_velocity_mps:
            break
        if x >= max_range_m:
            break
        if y < -1000.0:  # Bullet dropped too far
            break
        
        # Output at 100m intervals
        if x - last_output_range >= 100.0:
            drop_cm = -y * 100.0  # Convert m to cm
            spin_drift_mm = calculate_spin_drift(stability_factor, length_mm, diameter_mm, x)
            trajectory_points.append((x, v, mach, drop_cm, spin_drift_mm, t))
            last_output_range = x
    
    return trajectory_points


class TrajectoryCalculatorDialog(QtWidgets.QDialog):
    """
    Dialog for trajectory calculations including transonic analysis.
    """
    
    def __init__(self, bullet_obj=None, parent=None):
        """
        Initialize the trajectory calculator dialog.
        
        Args:
            bullet_obj: Optional bullet object to use
            parent: Parent widget
        """
        super().__init__(parent)
        self.bullet_obj = bullet_obj
        self.setWindowTitle("Trajectory & Transonic Calculator")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
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
        
        self.boat_tail_angle_spin = QtWidgets.QDoubleSpinBox()
        self.boat_tail_angle_spin.setRange(0.0, 15.0)
        self.boat_tail_angle_spin.setSuffix(" °")
        self.boat_tail_angle_spin.setDecimals(1)
        self.boat_tail_angle_spin.setValue(9.0)
        input_layout.addRow("Boat Tail Angle:", self.boat_tail_angle_spin)
        
        self.bc_g1_spin = QtWidgets.QDoubleSpinBox()
        self.bc_g1_spin.setRange(0.1, 2.0)
        self.bc_g1_spin.setDecimals(3)
        self.bc_g1_spin.setValue(0.5)
        input_layout.addRow("BC G1 (override):", self.bc_g1_spin)
        
        self.bc_auto_checkbox = QtWidgets.QCheckBox("Auto-calculate BC G1")
        self.bc_auto_checkbox.setChecked(True)
        self.bc_auto_checkbox.toggled.connect(self._on_bc_auto_toggled)
        input_layout.addRow("", self.bc_auto_checkbox)
        
        self.velocity_spin = QtWidgets.QDoubleSpinBox()
        self.velocity_spin.setRange(100.0, 1500.0)
        self.velocity_spin.setSuffix(" m/s")
        self.velocity_spin.setValue(853.0)
        self.velocity_spin.setDecimals(1)
        input_layout.addRow("Muzzle Velocity:", self.velocity_spin)
        
        self.elevation_spin = QtWidgets.QDoubleSpinBox()
        self.elevation_spin.setRange(-45.0, 45.0)
        self.elevation_spin.setSuffix(" °")
        self.elevation_spin.setValue(0.0)
        self.elevation_spin.setDecimals(1)
        input_layout.addRow("Barrel Elevation:", self.elevation_spin)
        
        self.temperature_spin = QtWidgets.QDoubleSpinBox()
        self.temperature_spin.setRange(-40.0, 50.0)
        self.temperature_spin.setSuffix(" °C")
        self.temperature_spin.setValue(15.0)
        self.temperature_spin.setDecimals(1)
        input_layout.addRow("Temperature:", self.temperature_spin)
        
        self.pressure_spin = QtWidgets.QDoubleSpinBox()
        self.pressure_spin.setRange(800.0, 1200.0)
        self.pressure_spin.setSuffix(" hPa")
        self.pressure_spin.setValue(1013.25)
        self.pressure_spin.setDecimals(2)
        input_layout.addRow("Pressure:", self.pressure_spin)
        
        self.max_range_spin = QtWidgets.QDoubleSpinBox()
        self.max_range_spin.setRange(100.0, 5000.0)
        self.max_range_spin.setSuffix(" m")
        self.max_range_spin.setValue(2000.0)
        self.max_range_spin.setDecimals(0)
        input_layout.addRow("Max Range:", self.max_range_spin)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Results section
        results_group = QtWidgets.QGroupBox("Results")
        results_layout = QtWidgets.QVBoxLayout()
        
        # Summary box
        self.summary_label = QtWidgets.QLabel("Click 'Calculate' to run trajectory analysis")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px;")
        results_layout.addWidget(self.summary_label)
        
        # Trajectory table
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Range (m)", "Velocity (m/s)", "Mach", "Drop (cm)", "Spin Drift (mm)", "Time (s)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        results_layout.addWidget(self.table)
        
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
    
    def _on_bc_auto_toggled(self, checked):
        """Enable/disable BC G1 override based on auto-calculate checkbox."""
        self.bc_g1_spin.setEnabled(not checked)
    
    def _load_bullet_data(self, bullet_obj=None):
        """Load data from bullet object."""
        obj = bullet_obj or self.bullet_obj
        
        if obj and hasattr(obj, "Diameter"):
            self.diameter_spin.setValue(obj.Diameter)
            self.length_spin.setValue(obj.Length)
            self.weight_spin.setValue(obj.ActualWeight if hasattr(obj, "ActualWeight") and obj.ActualWeight > 0 else obj.Weight)
            
            if hasattr(obj, "BoatTailAngle"):
                self.boat_tail_angle_spin.setValue(obj.BoatTailAngle)
            
            # Auto-calculate BC if enabled
            if self.bc_auto_checkbox.isChecked():
                ogive_type = obj.OgiveType if hasattr(obj, "OgiveType") else "Tangent"
                bc_g1 = calculate_ballistic_coefficient_g1(
                    obj.Diameter, obj.Weight, obj.Length, ogive_type
                )
                self.bc_g1_spin.setValue(bc_g1)
    
    def calculate(self):
        """Perform trajectory calculations."""
        try:
            # Get inputs
            diameter_mm = self.diameter_spin.value()
            length_mm = self.length_spin.value()
            weight_grains = self.weight_spin.value()
            boat_tail_angle_deg = self.boat_tail_angle_spin.value()
            bc_g1 = self.bc_g1_spin.value() if not self.bc_auto_checkbox.isChecked() else self.bc_g1_spin.value()
            velocity_mps = self.velocity_spin.value()
            elevation_deg = self.elevation_spin.value()
            temperature_c = self.temperature_spin.value()
            pressure_hpa = self.pressure_spin.value()
            max_range_m = self.max_range_spin.value()
            
            # Auto-calculate BC if enabled
            if self.bc_auto_checkbox.isChecked():
                bullet_obj = self.bullet_obj or (self.bullet_combo.itemData(self.bullet_combo.currentIndex()) if self.bullet_combo.currentIndex() >= 0 else None)
                if bullet_obj and hasattr(bullet_obj, "OgiveType"):
                    ogive_type = bullet_obj.OgiveType
                else:
                    ogive_type = "Tangent"
                bc_g1 = calculate_ballistic_coefficient_g1(
                    diameter_mm, weight_grains, length_mm, ogive_type
                )
                self.bc_g1_spin.setValue(bc_g1)
            
            # Calculate derived values
            # G7 BC
            bc_g7 = calculate_g7_bc_from_g1(bc_g1, boat_tail_angle_deg)
            
            # Sectional density
            sd = calculate_sectional_density(diameter_mm, weight_grains)
            
            # G7 form factor
            i7 = sd / bc_g7 if bc_g7 > 0 else 0.0
            
            # Air density
            rho = calculate_air_density(pressure_hpa, temperature_c)
            
            # Speed of sound
            c = calculate_speed_of_sound(temperature_c)
            
            # Transonic thresholds
            transonic_entry_mach = 1.1
            transonic_exit_mach = 0.9
            transonic_entry_velocity = transonic_entry_mach * c
            transonic_exit_velocity = transonic_exit_mach * c
            
            # Bullet properties
            diameter_m = diameter_mm / 1000.0
            A = math.pi * (diameter_m / 2.0) ** 2  # Cross-sectional area in m²
            weight_kg = weight_grains / 15432.3584  # Convert grains to kg
            m_kg = weight_kg
            
            # Calculate stability factor for spin drift
            # Use default twist rate of 10 inches/turn (reasonable for most rifle calibers)
            twist_rate_inches = 10.0
            
            bullet_obj = self.bullet_obj or (self.bullet_combo.itemData(self.bullet_combo.currentIndex()) if self.bullet_combo.currentIndex() >= 0 else None)
            material_density = 8.70  # Default copper
            if bullet_obj:
                if hasattr(bullet_obj, "Density"):
                    material_density = float(bullet_obj.Density)
            
            # Calculate stability factor
            stability_factor, _ = calculate_stability_factor_miller(
                diameter_mm, length_mm, weight_grains, twist_rate_inches, velocity_mps,
                temperature_c, pressure_hpa,
                effective_diameter_mm=None,
                material_density_g_per_cm3=material_density
            )
            
            # Integrate trajectory
            trajectory_points = integrate_trajectory_rk4(
                velocity_mps, elevation_deg, rho, A, m_kg, i7, c,
                max_range_m, stability_factor, length_mm, diameter_mm,
                min_velocity_mps=50.0
            )
            
            # Track transonic entry/exit
            transonic_entry_range = None
            transonic_exit_range = None
            stability_at_transonic = None
            
            for range_m, v, mach, drop_cm, spin_drift_mm, time_s in trajectory_points:
                # Track transonic entry/exit
                if transonic_entry_range is None and mach <= transonic_entry_mach:
                    transonic_entry_range = range_m
                    stability_at_transonic = stability_factor
                if transonic_exit_range is None and mach <= transonic_exit_mach:
                    transonic_exit_range = range_m
            
            # Update table
            self.table.setRowCount(len(trajectory_points))
            for row, (range_m, v, mach, drop_cm, spin_drift_mm, time_s) in enumerate(trajectory_points):
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{range_m:.0f}"))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{v:.1f}"))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{mach:.3f}"))
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{drop_cm:.1f}"))
                self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{spin_drift_mm:.1f}"))
                self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{time_s:.2f}"))
            
            # Update summary
            summary_text = "<b>Trajectory Summary:</b><br>"
            summary_text += f"BC G1: {bc_g1:.3f} | BC G7: {bc_g7:.3f}<br>"
            summary_text += f"Sectional Density: {sd:.3f} | G7 Form Factor: {i7:.3f}<br>"
            summary_text += f"Air Density: {rho:.4f} kg/m³ | Speed of Sound: {c:.1f} m/s<br><br>"
            
            if transonic_entry_range is not None:
                summary_text += f"<b style='color: orange;'>Transonic Entry:</b> {transonic_entry_range:.0f} m (Mach 1.1)<br>"
                if transonic_exit_range is not None:
                    summary_text += f"<b style='color: orange;'>Transonic Zone:</b> {transonic_entry_range:.0f} m to {transonic_exit_range:.0f} m<br>"
                    summary_text += f"<b style='color: green;'>Fully Subsonic:</b> {transonic_exit_range:.0f} m (Mach 0.9)<br>"
                else:
                    summary_text += f"<b style='color: orange;'>Transonic Zone:</b> {transonic_entry_range:.0f} m to end of trajectory<br>"
                
                if stability_at_transonic is not None:
                    stability_threshold = 1.8  # Monolithic copper/brass default
                    if stability_at_transonic < stability_threshold:
                        summary_text += f"<br><b style='color: red;'>WARNING:</b> Stability at transonic entry: {stability_at_transonic:.2f} (below threshold {stability_threshold:.1f})<br>"
                    else:
                        summary_text += f"<br>Stability at transonic entry: {stability_at_transonic:.2f} (stable)<br>"
            else:
                summary_text += "<b style='color: green;'>Bullet remains supersonic throughout trajectory</b><br>"
            
            summary_text += "<br><b>BC Truing Formula (reference):</b><br>"
            summary_text += "BC_true = BC_nominal × (V_measured / V_calculated)^(1/2)"
            
            self.summary_label.setText(summary_text)
            
        except Exception as e:
            App.Console.PrintError(f"Error calculating trajectory: {e}\n")
            import traceback
            traceback.print_exc()
            self.summary_label.setText(f"<b style='color: red;'>Error:</b> {str(e)}")


class TrajectoryCalculatorCommand:
    """
    Command to open trajectory calculator.
    """
    
    def __init__(self):
        """Initialize the command."""
        wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.resources = {
            "Pixmap": os.path.join(
                wb_path, "Resources", "icons", "Calculator.svg"
            ),
            "MenuText": "Trajectory & Transonic",
            "ToolTip": "Calculate bullet trajectory with transonic zone analysis",
            "Accel": "T"
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
        dialog = TrajectoryCalculatorDialog(bullet_obj)
        dialog.exec_()


# Register command (only if Gui is available)
try:
    Gui.addCommand("BulletDesigner_TrajectoryCalculator", TrajectoryCalculatorCommand())
except Exception as e:
    App.Console.PrintError(f"Failed to register TrajectoryCalculator command: {e}\n")
