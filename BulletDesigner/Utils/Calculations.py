"""
Ballistic calculations and formulas for bullet design.

This module provides functions for calculating ballistic properties
including stability, ballistic coefficient, sectional density, and twist rates.
"""

import math
from typing import Optional, Tuple, Dict


def calculate_sectional_density(diameter_mm: float, weight_grains: float) -> float:
    """
    Calculate sectional density (SD) of a bullet.
    
    Sectional density = Weight (lbs) / Diameter^2 (inches)
    
    Args:
        diameter_mm: Bullet diameter in millimeters
        weight_grains: Bullet weight in grains
        
    Returns:
        Sectional density (dimensionless)
    """
    if diameter_mm <= 0 or weight_grains <= 0:
        return 0.0
    
    # Convert to inches and pounds
    diameter_inches = diameter_mm / 25.4
    weight_lbs = weight_grains / 7000.0
    
    sd = weight_lbs / (diameter_inches ** 2)
    return sd


def calculate_ballistic_coefficient_g1(
    diameter_mm: float,
    weight_grains: float,
    length_mm: float,
    ogive_type: str = "Tangent"
) -> float:
    """
    Estimate G1 ballistic coefficient using empirical formulas.
    
    This is a simplified estimation. Real BC depends on many factors
    including velocity, shape, and atmospheric conditions.
    
    Args:
        diameter_mm: Bullet diameter in millimeters
        weight_grains: Bullet weight in grains
        length_mm: Bullet length in millimeters
        ogive_type: Type of ogive ("Tangent", "Secant", "Elliptical")
        
    Returns:
        Estimated G1 ballistic coefficient
    """
    if diameter_mm <= 0 or weight_grains <= 0 or length_mm <= 0:
        return 0.0
    
    # Convert to inches
    diameter_inches = diameter_mm / 25.4
    length_inches = length_mm / 25.4
    
    # Calculate sectional density
    sd = calculate_sectional_density(diameter_mm, weight_grains)
    
    # Form factor estimation based on ogive type
    # Lower form factor = better BC
    form_factors = {
        "Tangent": 0.85,
        "Secant": 0.80,
        "Elliptical": 0.75
    }
    form_factor = form_factors.get(ogive_type, 0.85)
    
    # BC = SD / Form Factor
    bc = sd / form_factor
    
    # Apply length correction (longer bullets generally have better BC)
    length_ratio = length_inches / diameter_inches
    if length_ratio > 4.0:
        bc *= 1.05  # Slight boost for long bullets
    
    return round(bc, 3)


def calculate_recommended_twist_rate(
    diameter_mm: float,
    length_mm: float,
    weight_grains: float,
    velocity_mps: float = 853.0,
    effective_diameter_mm: Optional[float] = None,
    material_density_g_per_cm3: Optional[float] = None
) -> Tuple[float, str]:
    """
    Calculate recommended barrel twist rate using Greenhill formula or Miller-based formula.
    
    For monolithic copper/brass bullets, uses Miller-based required twist calculation:
    T_required = d × √[(30 × m) / (1.8 × d³ × l × (1 + l²))] × (2800/V)^(1/6)
    
    For lead-core bullets, uses Greenhill formula:
    T = 150 * D^2 / L (or with velocity correction for V > 2800 fps)
    
    Args:
        diameter_mm: Bullet diameter in millimeters (nominal/groove diameter)
        length_mm: Bullet length in millimeters
        weight_grains: Bullet weight in grains
        velocity_mps: Muzzle velocity in meters per second (default 853 m/s = ~2800 fps)
        effective_diameter_mm: Effective diameter at bearing bands (if None, uses diameter_mm)
        material_density_g_per_cm3: Material density in g/cm³ (used to determine bullet type)
        
    Returns:
        Tuple of (twist_rate_inches, formatted_string)
        Example: (8.0, "1:8\"")
    """
    if diameter_mm <= 0 or length_mm <= 0:
        return (0.0, "N/A")
    
    # Determine if monolithic copper/brass bullet
    is_monolithic_copper_brass = False
    if material_density_g_per_cm3 is not None:
        if 7.0 <= material_density_g_per_cm3 <= 9.5:
            is_monolithic_copper_brass = True
    
    # Use effective diameter (bearing band diameter) if provided
    d_effective_mm = effective_diameter_mm if effective_diameter_mm is not None else diameter_mm
    
    # Convert to inches (formula uses imperial units)
    diameter_inches = d_effective_mm / 25.4
    length_inches = length_mm / 25.4
    
    # Convert velocity to fps
    velocity_fps = velocity_mps * 3.28084
    
    if is_monolithic_copper_brass:
        # Miller-based required twist for monolithic copper/brass bullets
        # T_required = d × √[(30 × m) / (1.8 × d³ × l × (1 + l²))] × (2800/V)^(1/6)
        length_calibers = length_inches / diameter_inches
        
        # Calculate numerator: 30 × m
        numerator = 30.0 * weight_grains
        
        # Calculate denominator: 1.8 × d³ × l × (1 + l²)
        denominator = 1.8 * (diameter_inches ** 3) * length_calibers * (1.0 + length_calibers ** 2)
        
        # Calculate square root term
        sqrt_term = math.sqrt(numerator / denominator) if denominator > 0 else 0.0
        
        # Calculate velocity correction: (2800/V)^(1/6)
        if velocity_fps > 0:
            velocity_correction = math.pow(2800.0 / velocity_fps, 1.0 / 6.0)
        else:
            velocity_correction = 1.0
        
        # Final twist rate
        twist_rate = diameter_inches * sqrt_term * velocity_correction
    else:
        # Greenhill formula for lead-core bullets
        if velocity_fps <= 2800:
            twist_rate = 150.0 * (diameter_inches ** 2) / length_inches
        else:
            velocity_factor = math.sqrt(velocity_fps / 2800.0)
            twist_rate = 150.0 * (diameter_inches ** 2) / length_inches * velocity_factor
    
    # Round to nearest reasonable value (typically 7, 8, 9, 10, 12, 14)
    twist_rate = round(twist_rate)
    
    # Format as "1:X\""
    formatted = f"1:{int(twist_rate)}\""
    
    return (twist_rate, formatted)


def calculate_stability_factor_miller(
    diameter_mm: float,
    length_mm: float,
    weight_grains: float,
    twist_rate_inches: float,
    velocity_mps: float = 853.0,
    temperature_c: float = 15.0,
    pressure_hpa: float = 1013.25,
    effective_diameter_mm: Optional[float] = None,
    material_density_g_per_cm3: Optional[float] = None
) -> Tuple[float, float]:
    """
    Calculate stability factor using Miller's formula with modified threshold for monolithic bullets.
    
    FORMULA:
    Sg = (30 × m × (V/2800)^(1/3)) / ((T/d)² × d³ × l × (1 + l²))
    
    WHERE:
    - m = bullet mass (grains)
    - V = muzzle velocity (ft/sec)
    - T = twist rate (inches per turn)
    - d = effective bullet diameter (inches) - use bearing band diameter for land-riding bullets
    - l = bullet length in calibers = L/d
    - L = bullet length (inches)
    
    STABILITY THRESHOLD:
    - Monolithic copper/brass bullets: Sg ≥ 1.8
    - Lead-core bullets: Sg ≥ 1.5
    
    CRITICAL: Use EFFECTIVE diameter for land-riding/banded bullets, not nominal diameter.
    The effective diameter is the diameter at the bearing bands, not the full bullet diameter.
    
    Args:
        diameter_mm: Bullet diameter in millimeters (nominal/groove diameter)
        length_mm: Bullet length in millimeters
        weight_grains: Bullet weight in grains
        twist_rate_inches: Barrel twist rate (e.g., 8 for 1:8")
        velocity_mps: Muzzle velocity in meters per second (default ~853 m/s = ~2800 fps)
        temperature_c: Temperature in Celsius (default 15°C = ~59°F)
        pressure_hpa: Atmospheric pressure in hectopascals (default 1013.25 hPa = 29.92 inHg)
        effective_diameter_mm: Effective diameter at bearing bands (if None, uses diameter_mm)
        material_density_g_per_cm3: Material density in g/cm³ (used to determine if monolithic copper/brass)
        
    Returns:
        Tuple of (stability_factor, stability_threshold)
        - stability_factor: Calculated stability factor (dimensionless)
        - stability_threshold: Required threshold (1.8 for monolithic copper/brass, 1.5 for lead-core)
    """
    if diameter_mm <= 0 or length_mm <= 0 or weight_grains <= 0 or twist_rate_inches <= 0:
        return (0.0, 1.5)
    
    # Determine if monolithic copper/brass bullet
    # Monolithic copper/brass typically has density 7.85-8.96 g/cm³
    # Lead-core bullets typically have density > 10 g/cm³
    is_monolithic_copper_brass = False
    if material_density_g_per_cm3 is not None:
        # Monolithic copper/brass: density typically 7.85-9.0 g/cm³
        # Lead-core: density typically > 10 g/cm³
        if 7.0 <= material_density_g_per_cm3 <= 9.5:
            is_monolithic_copper_brass = True
    
    # Determine stability threshold
    stability_threshold = 1.8 if is_monolithic_copper_brass else 1.5
    
    # Use effective diameter (bearing band diameter) if provided, otherwise use nominal diameter
    # For land-riding bullets, effective diameter is the groove diameter (where bands engage)
    # For groove-riding bullets, effective diameter equals nominal diameter
    d_effective_mm = effective_diameter_mm if effective_diameter_mm is not None else diameter_mm
    
    # Convert to inches (formula uses imperial units)
    diameter_inches = d_effective_mm / 25.4
    length_inches = length_mm / 25.4
    
    # Mass in grains
    mass_grains = weight_grains
    
    # Convert velocity to fps
    velocity_fps = velocity_mps * 3.28084
    
    # Length in calibers (critical: Miller uses length/diameter, not absolute length)
    length_calibers = length_inches / diameter_inches
    
    # Twist rate in calibers per turn
    twist_calibers = twist_rate_inches / diameter_inches
    
    # Convert metric inputs to imperial for corrections
    # Temperature: Celsius to Fahrenheit
    temperature_f = (temperature_c * 9.0 / 5.0) + 32.0
    # Pressure: hPa to inHg (1 hPa = 0.0295299830714 inHg)
    pressure_inhg = pressure_hpa * 0.0295299830714
    
    # Temperature correction (formula uses Rankine: F + 459.67)
    # Standard reference: 59°F = 518.67°R
    temp_correction = math.sqrt((temperature_f + 459.67) / 518.67)
    
    # Pressure correction (standard is 29.92 inHg)
    pressure_correction = math.sqrt(pressure_inhg / 29.92)
    
    # Velocity correction factor: f_v = (v/2800)^(1/3)
    # Standard reference velocity is 2800 fps
    if velocity_fps > 0:
        velocity_correction = math.pow(velocity_fps / 2800.0, 1.0 / 3.0)
    else:
        velocity_correction = 1.0
    
    # Miller's formula with velocity correction: Sg = (30 × m × (V/2800)^(1/3)) / ((T/d)² × d³ × l × (1 + l²))
    # Note: The velocity correction is already applied above, so we multiply it in
    stability = (30.0 * mass_grains * velocity_correction) / (
        (twist_calibers ** 2) * 
        (diameter_inches ** 3) * 
        length_calibers * 
        (1.0 + length_calibers ** 2)
    )
    
    # Apply atmospheric corrections
    stability *= temp_correction * pressure_correction
    
    # Round to 2 decimal places for display
    return (round(stability, 2), stability_threshold)


def calculate_volume_from_weight(weight_grains: float, density_g_per_cm3: float) -> float:
    """
    Calculate bullet volume from weight and material density.
    
    Args:
        weight_grains: Bullet weight in grains
        density_g_per_cm3: Material density in g/cm³
        
    Returns:
        Volume in cubic millimeters
    """
    if weight_grains <= 0 or density_g_per_cm3 <= 0:
        return 0.0
    
    # Convert grains to grams
    weight_grams = weight_grains / 15.4323584
    
    # Calculate volume in cm³
    volume_cm3 = weight_grams / density_g_per_cm3
    
    # Convert to mm³
    volume_mm3 = volume_cm3 * 1000.0
    
    return volume_mm3


def calculate_weight_from_volume(volume_mm3: float, density_g_per_cm3: float) -> float:
    """
    Calculate bullet weight from volume and material density.
    
    Args:
        volume_mm3: Bullet volume in cubic millimeters
        density_g_per_cm3: Material density in g/cm³
        
    Returns:
        Weight in grains
    """
    if volume_mm3 <= 0 or density_g_per_cm3 <= 0:
        return 0.0
    
    # Convert mm³ to cm³
    volume_cm3 = volume_mm3 / 1000.0
    
    # Calculate weight in grams
    weight_grams = volume_cm3 * density_g_per_cm3
    
    # Convert to grains
    weight_grains = weight_grams * 15.4323584
    
    return weight_grains


def calculate_bearing_surface(
    diameter_mm: float,
    length_mm: float,
    num_bands: int,
    band_length_mm: float,
    band_spacing_mm: float
) -> float:
    """
    Calculate total bearing surface area of bullet.
    
    Bearing surface = area of all driving bands + body contact area
    
    Args:
        diameter_mm: Bullet diameter in millimeters
        length_mm: Total bullet length in millimeters
        num_bands: Number of driving bands
        band_length_mm: Length of each band in millimeters
        band_spacing_mm: Spacing between bands in millimeters
        
    Returns:
        Bearing surface area in square millimeters
    """
    if diameter_mm <= 0 or length_mm <= 0:
        return 0.0
    
    # Circumference
    circumference = math.pi * diameter_mm
    
    # Band area
    band_area = num_bands * band_length_mm * circumference
    
    # Body area (simplified - assumes bands are the main bearing surface)
    # For more accuracy, subtract band areas from total surface
    total_surface = circumference * length_mm
    
    # If we have bands, use band area; otherwise use total surface
    if num_bands > 0:
        bearing_surface = band_area
    else:
        # No bands - entire surface is bearing surface
        bearing_surface = total_surface
    
    return bearing_surface


def calculate_ogive_radius(
    caliber_ratio: float,
    diameter_mm: float,
    ogive_type: str = "Tangent"
) -> float:
    """
    Calculate ogive radius from caliber ratio.
    
    Args:
        caliber_ratio: Ogive length in calibers (diameter units)
        diameter_mm: Bullet diameter in millimeters
        ogive_type: Type of ogive ("Tangent", "Secant", "Elliptical")
        
    Returns:
        Ogive radius in millimeters
    """
    if caliber_ratio <= 0 or diameter_mm <= 0:
        return 0.0
    
    ogive_length = (caliber_ratio * diameter_mm) / 2.0
    
    # For tangent ogive: R = (L^2 + D^2/4) / (2*D)
    # Simplified approximation
    if ogive_type == "Tangent":
        radius = (ogive_length ** 2 + (diameter_mm / 2) ** 2) / diameter_mm
    elif ogive_type == "Secant":
        # Secant ogive typically has larger radius
        radius = (ogive_length ** 2 + (diameter_mm / 2) ** 2) / diameter_mm * 1.1
    else:  # Elliptical
        # Elliptical approximation
        radius = ogive_length * 1.2
    
    return radius


def calculate_bullet_dimensions_from_weight(
    target_weight_grains: float,
    groove_diameter_mm: float,
    land_diameter_mm: float,
    material_density_g_per_cm3: float,
    num_bands: int,
    band_length_mm: float,
    band_spacing_mm: float,
    ogive_caliber_ratio: float,
    ogive_type: str,
    boat_tail_angle_deg: float,
    meplat_diameter_mm: float,
    land_riding: bool = True,
    max_iterations: int = 10
) -> Dict[str, float]:
    """
    Calculate bullet dimensions from target weight and other parameters.
    
    This function performs reverse calculation: given a target weight,
    it calculates the required bullet length and other dimensions.
    
    Args:
        target_weight_grains: Target bullet weight in grains
        groove_diameter_mm: Groove diameter in mm
        land_diameter_mm: Land diameter in mm
        material_density_g_per_cm3: Material density in g/cm³
        num_bands: Number of driving bands
        band_length_mm: Length of each band in mm
        band_spacing_mm: Spacing between bands in mm
        ogive_caliber_ratio: Ogive caliber ratio
        ogive_type: Type of ogive ("Tangent", "Secant", "Elliptical")
        boat_tail_angle_deg: Boat tail angle in degrees
        meplat_diameter_mm: Meplat (tip) diameter in mm
        land_riding: True for land riding (body at land diameter), False for groove riding
        max_iterations: Maximum iterations for boat tail adjustment
        
    Returns:
        Dictionary with calculated dimensions and ballistic properties:
        - total_length_mm: Total bullet length
        - boat_tail_length_mm: Boat tail length (may be adjusted)
        - bearing_surface_length_mm: Length of bearing surface section
        - ogive_length_mm: Ogive length
        - gap_length_needed_mm: Required gap length between bands
        - gap_coverage_mm: Actual gap coverage from spacing
        - calculated_weight_grains: Calculated weight (should match target)
        - ballistic_coefficient_g1: Calculated G1 ballistic coefficient
        - sectional_density: Sectional density
        - length_diameter_ratio: Length to diameter ratio
        - meplat_ratio: Meplat to groove diameter ratio
        - form_factor: Final form factor used in BC calculation
        - is_valid: Whether dimensions are valid
        - validation_message: Message explaining validation result
    """
    # Constants
    GRAINS_TO_GRAMS = 0.06479891
    CM3_TO_MM3 = 1000.0
    
    # 1. REQUIRED VOLUME
    weight_g = target_weight_grains * GRAINS_TO_GRAMS
    volume_total_mm3 = (weight_g / material_density_g_per_cm3) * CM3_TO_MM3
    
    # 2. RADII
    r_groove = groove_diameter_mm / 2.0
    r_land = land_diameter_mm / 2.0
    r_meplat = meplat_diameter_mm / 2.0
    
    # 3. OGIVE LENGTH
    ogive_length_mm = (ogive_caliber_ratio * groove_diameter_mm) / 2.0
    
    # 4. OGIVE VOLUME (paraboloid approximation)
    # Using simplified paraboloid volume: V = (π × r² × h) / 2
    # Average radius approximation for ogive
    V_ogive_mm3 = (math.pi * r_land * r_land * ogive_length_mm) / 2.0
    
    # 5. BOAT TAIL (iterative calculation)
    boat_tail_length_mm = groove_diameter_mm * 0.7  # Start estimate
    boat_tail_angle_rad = math.radians(boat_tail_angle_deg)
    
    for iteration in range(max_iterations):
        # Calculate boat tail base radius
        bt_reduction = boat_tail_length_mm * math.tan(boat_tail_angle_rad)
        r_base = r_land - bt_reduction
        r_base = max(r_base, r_groove * 0.3)  # Minimum 30% of groove radius
        
        # Boat tail volume (frustum of cone)
        # V = (π × h / 3) × (r1² + r1×r2 + r2²)
        V_boattail_mm3 = (math.pi * boat_tail_length_mm / 3.0) * (
            r_base * r_base + r_base * r_land + r_land * r_land
        )
        
        # 6. BEARING SURFACE VOLUME NEEDED
        V_bearing_mm3 = volume_total_mm3 - V_ogive_mm3 - V_boattail_mm3
        
        if V_bearing_mm3 <= 0:
            # Boat tail too long, reduce it
            boat_tail_length_mm *= 0.8
            continue
        
        # 7. BEARING SURFACE BREAKDOWN
        band_coverage_mm = num_bands * band_length_mm
        gap_coverage_mm = (num_bands - 1) * band_spacing_mm if num_bands > 1 else 0.0
        
        if land_riding:
            # LAND RIDING: Body is at land diameter, bands are annular expansions
            # Body volume = π × r_land² × length
            # Band volume = num_bands × π × (r_groove² - r_land²) × band_length
            
            # Volume of bands (annular cylinders from land to groove)
            V_bands_mm3 = num_bands * math.pi * (r_groove * r_groove - r_land * r_land) * band_length_mm
            
            # Volume needed for gaps (land diameter cylinder)
            V_gaps_needed_mm3 = V_bearing_mm3 - V_bands_mm3
            
            if V_gaps_needed_mm3 < 0:
                # Bands alone exceed volume - reduce boat tail further
                boat_tail_length_mm *= 0.9
                continue
            
            # Gap length needed (at land diameter)
            gap_length_needed_mm = V_gaps_needed_mm3 / (math.pi * r_land * r_land)
        else:
            # GROOVE RIDING: Body is at groove diameter
            # Volume of bands (annular cylinders)
            V_bands_mm3 = num_bands * math.pi * (r_groove * r_groove - r_land * r_land) * band_length_mm
            
            # Volume needed for gaps (groove diameter cylinder)
            V_gaps_needed_mm3 = V_bearing_mm3 - V_bands_mm3
            
            if V_gaps_needed_mm3 < 0:
                # Bands alone exceed volume - reduce boat tail further
                boat_tail_length_mm *= 0.9
                continue
            
            # Gap length needed (at groove diameter)
            gap_length_needed_mm = V_gaps_needed_mm3 / (math.pi * r_groove * r_groove)
        
        # Total bearing surface length
        total_bearing_length_mm = band_coverage_mm + gap_length_needed_mm
        
        # VALIDATION: gap_length_needed should ≥ gap_coverage
        if gap_length_needed_mm >= gap_coverage_mm:
            # Valid! Calculate total length
            total_length_mm = boat_tail_length_mm + total_bearing_length_mm + ogive_length_mm
            
            # Verify calculated weight
            # Recalculate volumes for verification
            V_ogive_check = (math.pi * r_land * r_land * ogive_length_mm) / 2.0
            V_boattail_check = (math.pi * boat_tail_length_mm / 3.0) * (
                r_base * r_base + r_base * r_land + r_land * r_land
            )
            V_bands_check = num_bands * math.pi * (r_groove * r_groove - r_land * r_land) * band_length_mm
            if land_riding:
                V_gaps_check = gap_length_needed_mm * math.pi * r_land * r_land
            else:
                V_gaps_check = gap_length_needed_mm * math.pi * r_groove * r_groove
            V_total_check = V_ogive_check + V_boattail_check + V_bands_check + V_gaps_check
            
            calculated_weight_g = (V_total_check / CM3_TO_MM3) * material_density_g_per_cm3
            calculated_weight_grains = calculated_weight_g / GRAINS_TO_GRAMS
            
            # 9. BALLISTIC COEFFICIENT (G1) CALCULATION
            # a. Convert to inches
            diameter_in = groove_diameter_mm / 25.4
            length_in = total_length_mm / 25.4
            
            # b. Sectional Density
            weight_lbs = target_weight_grains / 7000.0
            SD = weight_lbs / (diameter_in * diameter_in)
            
            # c. Form Factor (base based on ogive type)
            form_factors_base = {
                "Tangent": 0.85,
                "Secant": 0.80,
                "Elliptical": 0.75
            }
            i = form_factors_base.get(ogive_type, 0.85)
            
            # d. Length correction
            length_ratio = length_in / diameter_in
            if length_ratio > 4.0:
                i = i * 0.95  # Longer = better BC
            elif length_ratio < 3.0:
                i = i * 1.05  # Shorter = worse BC
            
            # e. Meplat correction
            meplat_ratio = meplat_diameter_mm / groove_diameter_mm
            if meplat_ratio > 0.3:
                i = i * 1.10  # Blunt tip = worse BC
            elif meplat_ratio < 0.1:
                i = i * 0.98  # Sharp tip = better BC
            
            # f. Boat tail correction
            if boat_tail_angle_deg > 0:
                i = i * 0.95  # Boat tail = better BC
            
            # g. Final BC
            BC_G1 = SD / i
            
            is_valid = True
            validation_message = f"Valid: gap_length_needed ({gap_length_needed_mm:.2f}mm) >= gap_coverage ({gap_coverage_mm:.2f}mm)"
            
            return {
                "total_length_mm": total_length_mm,
                "boat_tail_length_mm": boat_tail_length_mm,
                "bearing_surface_length_mm": total_bearing_length_mm,
                "ogive_length_mm": ogive_length_mm,
                "gap_length_needed_mm": gap_length_needed_mm,
                "gap_coverage_mm": gap_coverage_mm,
                "calculated_weight_grains": calculated_weight_grains,
                "target_weight_grains": target_weight_grains,
                "weight_error_percent": abs(calculated_weight_grains - target_weight_grains) / target_weight_grains * 100.0,
                "ballistic_coefficient_g1": BC_G1,
                "sectional_density": SD,
                "length_diameter_ratio": length_ratio,
                "meplat_ratio": meplat_ratio,
                "form_factor": i,
                "is_valid": is_valid,
                "validation_message": validation_message
            }
        else:
            # Gap doesn't fit - reduce boat tail and try again
            boat_tail_length_mm *= 0.9
    
    # Failed to find valid solution
    gap_length_needed_final = gap_length_needed_mm if 'gap_length_needed_mm' in locals() else 0.0
    gap_coverage_final = gap_coverage_mm if 'gap_coverage_mm' in locals() else 0.0
    
    return {
        "total_length_mm": 0.0,
        "boat_tail_length_mm": boat_tail_length_mm,
        "bearing_surface_length_mm": 0.0,
        "ogive_length_mm": ogive_length_mm,
        "gap_length_needed_mm": gap_length_needed_final,
        "gap_coverage_mm": gap_coverage_final,
        "calculated_weight_grains": 0.0,
        "target_weight_grains": target_weight_grains,
        "weight_error_percent": 100.0,
        "ballistic_coefficient_g1": 0.0,
        "sectional_density": 0.0,
        "length_diameter_ratio": 0.0,
        "meplat_ratio": meplat_diameter_mm / groove_diameter_mm if groove_diameter_mm > 0 else 0.0,
        "form_factor": 0.0,
        "is_valid": False,
        "validation_message": f"Failed to find valid dimensions after {max_iterations} iterations. Gap needed ({gap_length_needed_final:.2f}mm) < gap coverage ({gap_coverage_final:.2f}mm). Try reducing band spacing or increasing target weight."
    }
