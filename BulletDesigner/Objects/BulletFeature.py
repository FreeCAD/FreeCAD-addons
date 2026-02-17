"""
Parametric Bullet Feature object for FreeCAD.

This module implements the FeaturePython object that represents a bullet
with all its parametric properties.
"""

import FreeCAD as App
import Part
import os
import sys

# Add Utils to path
wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(wb_path, "Utils"))
sys.path.insert(0, os.path.join(wb_path, "Objects"))

from Utils.GeometryHelpers import (
    generate_bullet_profile_points,
    create_bullet_solid,
    validate_bullet_parameters
)
from Utils.Calculations import (
    calculate_weight_from_volume,
    calculate_sectional_density,
    calculate_ballistic_coefficient_g1,
    calculate_recommended_twist_rate,
    calculate_bearing_surface,
    calculate_bullet_dimensions_from_weight
)
from Utils.MaterialDatabase import get_material_database


class BulletFeature:
    """
    Parametric bullet feature object.
    
    This class implements a FeaturePython object that can be used
    in FreeCAD to create parametric bullets.
    """
    
    def __init__(self, obj):
        """
        Initialize the bullet feature.
        
        Args:
            obj: FreeCAD document object
        """
        self.Type = "BulletFeature"
        self._initializing = True  # Flag to prevent execute during init
        obj.Proxy = self
        
        # Basic Dimensions
        # Properties are added here, default values set in makeBulletFeature()
        obj.addProperty(
            "App::PropertyLength",
            "Diameter",
            "Basic",
            "Overall bullet diameter (groove diameter) in mm"
        )
        
        obj.addProperty(
            "App::PropertyLength",
            "LandDiameter",
            "Basic",
            "Land riding diameter in mm"
        )
        
        obj.addProperty(
            "App::PropertyLength",
            "Length",
            "Basic",
            "Total bullet length in mm"
        )
        
        obj.addProperty(
            "App::PropertyFloat",
            "Weight",
            "Basic",
            "Target weight in grains"
        )
        # Weight will be set in makeBulletFeature() - don't set default here
        
        # Design Type
        design_types = ["Traditional", "VLD"]
        obj.addProperty(
            "App::PropertyEnumeration",
            "DesignType",
            "Basic",
            "Bullet design type: Traditional or VLD (Very Low Drag)"
        )
        obj.DesignType = design_types
        obj.DesignType = "Traditional"  # Default
        
        # Land Riding option
        obj.addProperty(
            "App::PropertyBool",
            "LandRiding",
            "Basic",
            "Land riding bullet: body at land diameter with annular band expansions"
        )
        obj.LandRiding = True  # Default to land riding
        
        # Ogive Settings
        ogive_types = ["Tangent", "Secant", "Elliptical"]
        obj.addProperty(
            "App::PropertyEnumeration",
            "OgiveType",
            "Ogive",
            "Type of ogive profile"
        ).OgiveType = ogive_types
        obj.OgiveType = "Tangent"
        
        obj.addProperty(
            "App::PropertyFloat",
            "OgiveCaliberRatio",
            "Ogive",
            "Ogive length in calibers (diameter units)"
        )
        obj.OgiveCaliberRatio = 2.5  # Optimized for 32mm bullet with 4 bands
        
        obj.addProperty(
            "App::PropertyLength",
            "MeplatDiameter",
            "Ogive",
            "Tip (meplat) diameter in mm"
        )
        
        # Driving Bands
        obj.addProperty(
            "App::PropertyInteger",
            "NumBands",
            "Bands",
            "Number of driving bands (0-6)"
        )
        obj.NumBands = 4
        
        obj.addProperty(
            "App::PropertyLength",
            "BandLength",
            "Bands",
            "Length of each band in mm"
        )
        
        obj.addProperty(
            "App::PropertyLength",
            "BandSpacing",
            "Bands",
            "Space between bands in mm"
        )
        
        obj.addProperty(
            "App::PropertyLength",
            "BandDiameter",
            "Bands",
            "Band diameter in mm (usually = groove diameter)"
        )
        
        # Base/Boat Tail
        base_types = ["Flat", "BoatTail"]
        obj.addProperty(
            "App::PropertyEnumeration",
            "BaseType",
            "Base",
            "Base type"
        ).BaseType = base_types
        obj.BaseType = "BoatTail"
        
        obj.addProperty(
            "App::PropertyLength",
            "BoatTailLength",
            "Base",
            "Boat tail length in mm"
        )
        
        obj.addProperty(
            "App::PropertyAngle",
            "BoatTailAngle",
            "Base",
            "Boat tail angle in degrees"
        )
        
        # Material
        material_db = get_material_database()
        material_names = material_db.get_material_names()
        obj.addProperty(
            "App::PropertyEnumeration",
            "Material",
            "Material",
            "Bullet material"
        )
        obj.Material = material_names
        # Default to copper alloy (closest to solid copper alloy)
        if material_names:
            # Try to find copper alloy, otherwise use first available
            copper_alloy = None
            for mat in material_names:
                if "Copper" in mat or "copper" in mat.lower():
                    copper_alloy = mat
                    break
            obj.Material = copper_alloy if copper_alloy else material_names[0]
        
        obj.addProperty(
            "App::PropertyFloat",
            "Density",
            "Material",
            "Material density in g/cm³"
        )
        # Density will be set from material after Material is set
        
        # Calculated Properties (Read-only)
        obj.addProperty(
            "App::PropertyFloat",
            "ActualWeight",
            "Calculated",
            "Calculated weight in grains",
            1  # Read-only
        )
        obj.ActualWeight = 0.0
        
        obj.addProperty(
            "App::PropertyVolume",
            "Volume",
            "Calculated",
            "Bullet volume in mm³",
            1  # Read-only
        )
        obj.Volume = 0.0
        
        obj.addProperty(
            "App::PropertyArea",
            "BearingSurface",
            "Calculated",
            "Bearing surface area in mm²",
            1  # Read-only
        )
        obj.BearingSurface = 0.0
        
        obj.addProperty(
            "App::PropertyFloat",
            "BC_G1",
            "Calculated",
            "Estimated G1 ballistic coefficient",
            1  # Read-only
        )
        obj.BC_G1 = 0.0
        
        obj.addProperty(
            "App::PropertyFloat",
            "SectionalDensity",
            "Calculated",
            "Sectional density",
            1  # Read-only
        )
        obj.SectionalDensity = 0.0
        
        obj.addProperty(
            "App::PropertyString",
            "RecommendedTwist",
            "Calculated",
            "Recommended barrel twist rate",
            1  # Read-only
        )
        obj.RecommendedTwist = "1:8\""
        
        # Default values will be set in makeBulletFeature() after object creation
        # This prevents issues with property initialization order
        # NOTE: _initializing will be set to False AFTER values are set in makeBulletFeature()
    
    def execute(self, obj):
        """
        Execute (recompute) the bullet geometry.
        
        This is called whenever the object needs to be recomputed.
        """
        App.Console.PrintMessage("=== execute() called - Recalculating bullet geometry ===\n")
        
        # Skip if still initializing
        if hasattr(self, '_initializing') and self._initializing:
            App.Console.PrintMessage("  Skipping - still initializing\n")
            return
        
        # Early return if essential properties don't exist yet
        if not hasattr(obj, "Length") or not hasattr(obj, "Diameter"):
            App.Console.PrintMessage("  Skipping - essential properties not set yet\n")
            return
        
        # Convert Quantity properties to float values (in mm)
        # PropertyLength returns Quantity objects that need conversion
        def to_mm(prop_value):
            """Convert property to mm as float."""
            if prop_value is None:
                return 0.0
            try:
                # Try to get Value attribute first
                if hasattr(prop_value, 'getValueAs'):
                    # It's a Quantity object
                    return float(prop_value.getValueAs('mm').Value)
                elif hasattr(prop_value, 'Value'):
                    # Might be a Quantity with Value attribute
                    val = prop_value.Value
                    if hasattr(val, 'getValueAs'):
                        return float(val.getValueAs('mm').Value)
                    return float(val)
                else:
                    # Already a number
                    return float(prop_value)
            except (AttributeError, TypeError, ValueError):
                # Fallback: try direct conversion
                try:
                    return float(prop_value)
                except (TypeError, ValueError):
                    return 0.0
        
        # Skip if essential properties have invalid values (likely being reset)
        try:
            length_val = to_mm(obj.Length)
            if length_val < 5.0:  # Unrealistically short
                App.Console.PrintLog(f"Skipping execute() - Length too small ({length_val}mm), likely being reset\n")
                return
        except:
            pass
        
        # Allow 0 bands - it's a valid design choice (smooth bullet)
        # Only skip if we're clearly in an invalid state during initialization
        # (This guard was too aggressive - removed the NumBands=0 check)
        
        # Check if Length is actually set (not zero) - skip if values aren't ready
        try:
            length_mm = to_mm(obj.Length)
            if length_mm <= 0:
                # Values not set yet, skip execution
                App.Console.PrintLog(f"Skipping execute() - Length not set yet (value: {length_mm})\n")
                return
        except Exception as e:
            App.Console.PrintLog(f"Skipping execute() - error checking Length: {e}\n")
            return
        
        try:
            
            # Get property values and convert to float - use hasattr checks
            diameter_mm = to_mm(obj.Diameter) if hasattr(obj, "Diameter") else 6.7
            land_diameter_mm = to_mm(obj.LandDiameter) if hasattr(obj, "LandDiameter") else 6.50
            length_mm = to_mm(obj.Length) if hasattr(obj, "Length") else 32.0
            num_bands = int(obj.NumBands) if hasattr(obj, "NumBands") else 4
            band_length_mm = to_mm(obj.BandLength) if hasattr(obj, "BandLength") else 2.25
            band_spacing_mm = to_mm(obj.BandSpacing) if hasattr(obj, "BandSpacing") else 3.0
            ogive_caliber_ratio = float(obj.OgiveCaliberRatio) if hasattr(obj, "OgiveCaliberRatio") else 7.0
            meplat_diameter_mm = to_mm(obj.MeplatDiameter) if hasattr(obj, "MeplatDiameter") else 1.5
            boat_tail_length_mm = to_mm(obj.BoatTailLength) if hasattr(obj, "BoatTailLength") else 5.0
            
            # Handle BoatTailAngle carefully
            if hasattr(obj, "BoatTailAngle"):
                try:
                    if hasattr(obj.BoatTailAngle, 'getValueAs'):
                        boat_tail_angle_deg = float(obj.BoatTailAngle.getValueAs('deg').Value)
                    elif hasattr(obj.BoatTailAngle, 'Value'):
                        boat_tail_angle_deg = float(obj.BoatTailAngle.Value)
                    else:
                        boat_tail_angle_deg = float(obj.BoatTailAngle)
                except (AttributeError, TypeError, ValueError):
                    boat_tail_angle_deg = 9.0
            else:
                boat_tail_angle_deg = 9.0
            
            base_type = obj.BaseType if hasattr(obj, "BaseType") else "BoatTail"
            ogive_type = obj.OgiveType if hasattr(obj, "OgiveType") else "Tangent"
            
            # Track what we auto-correct to avoid duplicate error messages
            auto_corrected = []
            
            # Auto-correct invalid parameters BEFORE validation
            # Fix meplat if too large
            if meplat_diameter_mm >= land_diameter_mm:
                meplat_diameter_mm = max(0.1, land_diameter_mm * 0.5)  # Ensure minimum 0.1mm
                if hasattr(obj, "MeplatDiameter"):
                    obj.MeplatDiameter = App.Units.Quantity(f"{meplat_diameter_mm:.2f} mm")
                auto_corrected.append("meplat")
            
            # Fix boat tail if too long
            max_boat_tail = length_mm * 0.3
            if boat_tail_length_mm > max_boat_tail:
                boat_tail_length_mm = max_boat_tail
                if hasattr(obj, "BoatTailLength"):
                    obj.BoatTailLength = App.Units.Quantity(f"{boat_tail_length_mm:.2f} mm")
                auto_corrected.append("boat_tail")
            
            # Debug: Log values being passed to validation
            App.Console.PrintMessage(f"=== execute() validation inputs ===\n")
            App.Console.PrintMessage(f"  length_mm={length_mm}, diameter_mm={diameter_mm}\n")
            App.Console.PrintMessage(f"  num_bands={num_bands}, band_length_mm={band_length_mm}, band_spacing_mm={band_spacing_mm}\n")
            App.Console.PrintMessage(f"  ogive_caliber_ratio={ogive_caliber_ratio}, boat_tail_length_mm={boat_tail_length_mm}\n")
            
            # Calculate what validation will check
            if num_bands > 0:
                total_band_space = num_bands * band_length_mm
                if num_bands > 1:
                    total_band_space += (num_bands - 1) * band_spacing_mm
                ogive_length = (ogive_caliber_ratio * diameter_mm) / 2.0
                available_length = length_mm - ogive_length - boat_tail_length_mm
                App.Console.PrintMessage(f"  Validation calc: band_space={total_band_space}mm, available={available_length}mm\n")
                App.Console.PrintMessage(f"    ogive_length={ogive_length}mm (ratio={ogive_caliber_ratio} * diameter={diameter_mm} / 2)\n")
            
            # Validate parameters (after auto-correction)
            # Only validate if we haven't already fixed the issues
            is_valid, error_msg = validate_bullet_parameters(
                diameter_mm,
                land_diameter_mm,
                length_mm,
                num_bands,
                band_length_mm,
                band_spacing_mm,
                ogive_caliber_ratio,
                meplat_diameter_mm,
                boat_tail_length_mm
            )
            
            # Only log validation errors for issues we didn't auto-correct
            if not is_valid and error_msg:
                # Skip errors we've already fixed
                skip_error = False
                if "Meplat diameter" in error_msg and "meplat" in auto_corrected:
                    skip_error = True
                if "Boat tail length" in error_msg and "boat_tail" in auto_corrected:
                    skip_error = True
                
                if not skip_error:
                    App.Console.PrintWarning(f"Bullet parameter warning: {error_msg}\n")
                    App.Console.PrintMessage(f"  (Values: length={length_mm}, bands={num_bands}, band_len={band_length_mm}, spacing={band_spacing_mm})\n")
            
            # Always continue - geometry generation will use corrected values
            
            # Get land_riding property
            land_riding = True
            if hasattr(obj, "LandRiding"):
                land_riding = bool(obj.LandRiding)
            
            App.Console.PrintMessage("  Generating bullet profile points...\n")
            
            # Generate profile points
            profile_points = generate_bullet_profile_points(
                diameter_mm=diameter_mm,
                land_diameter_mm=land_diameter_mm,
                length_mm=length_mm,
                ogive_type=ogive_type,
                ogive_caliber_ratio=ogive_caliber_ratio,
                meplat_diameter_mm=meplat_diameter_mm,
                num_bands=num_bands,
                band_length_mm=band_length_mm,
                band_spacing_mm=band_spacing_mm,
                base_type=base_type,
                boat_tail_length_mm=boat_tail_length_mm,
                boat_tail_angle_deg=boat_tail_angle_deg,
                land_riding=land_riding
            )
            
            # Create solid
            App.Console.PrintMessage("  Creating bullet solid from profile...\n")
            bullet_solid = create_bullet_solid(profile_points)
            
            # Validate solid before assigning
            if not isinstance(bullet_solid, Part.Solid):
                App.Console.PrintError(f"  ERROR: Created shape is not a Part.Solid: {type(bullet_solid)}\n")
                raise ValueError("Bullet solid is not a valid Part.Solid")
            
            # Validate bounding box
            bbox = bullet_solid.BoundBox
            if not bbox.isValid():
                App.Console.PrintError(f"  ERROR: Solid has invalid bounding box\n")
                raise ValueError("Bullet solid has invalid bounding box")
            
            App.Console.PrintMessage(f"  Solid created: Volume={bullet_solid.Volume:.2f} mm³, "
                                   f"BBox=({bbox.XLength:.2f}, {bbox.YLength:.2f}, {bbox.ZLength:.2f}) mm\n")
            
            # Ensure solid is clean and valid for section views
            try:
                # Remove any internal edges/splits that might confuse section view
                bullet_solid = bullet_solid.removeSplitter()
                # Re-validate after cleaning
                if bullet_solid.Volume < 0.001:
                    raise ValueError("Solid volume became invalid after removeSplitter")
            except Exception as e:
                App.Console.PrintWarning(f"  Warning: Could not clean solid: {e}\n")
            
            # CRITICAL: Ensure shape has proper placement for section views
            # FreeCAD's section view tool requires shapes with identity placement
            bullet_solid.Placement = App.Placement()
            
            # Set the shape - this is critical for section views
            obj.Shape = bullet_solid
            
            # CRITICAL: Verify shape before assignment
            if bullet_solid.isNull():
                raise ValueError("Bullet solid is null")
            
            # Set the shape
            obj.Shape = bullet_solid
            
            # CRITICAL: Force FreeCAD to recognize the shape change
            # This ensures the bounding box is properly calculated and available for section views
            obj.enforceRecompute()
            
            # Verify shape was set correctly
            if not hasattr(obj, 'Shape') or obj.Shape.isNull():
                raise ValueError("Shape is null after assignment")
            
            # Force bounding box calculation by accessing it
            # This ensures FreeCAD computes and caches it for section views
            try:
                bbox_final = obj.Shape.BoundBox
                # Force validation by accessing properties
                _ = bbox_final.XLength
                _ = bbox_final.YLength  
                _ = bbox_final.ZLength
                
                if not bbox_final.isValid():
                    App.Console.PrintError(f"  ERROR: Shape bounding box invalid after assignment\n")
                    raise ValueError("Shape bounding box is invalid after assignment")
                
                App.Console.PrintMessage(f"  Shape BBox: X=[{bbox_final.XMin:.2f}, {bbox_final.XMax:.2f}], "
                                         f"Y=[{bbox_final.YMin:.2f}, {bbox_final.YMax:.2f}], "
                                         f"Z=[{bbox_final.ZMin:.2f}, {bbox_final.ZMax:.2f}] mm\n")
            except Exception as e:
                App.Console.PrintError(f"  ERROR accessing shape bounding box: {e}\n")
                raise ValueError(f"Failed to validate shape bounding box: {e}")
            
            # Ensure object placement is identity - section views work better with objects at origin
            obj.Placement = App.Placement()
            
            # Touch the object to ensure FreeCAD knows it changed
            obj.touch()
            
            App.Console.PrintMessage("  Bullet shape updated successfully\n")
            
            # Calculate properties
            App.Console.PrintMessage("  Updating calculated properties...\n")
            self._update_calculated_properties(obj)
            
            App.Console.PrintMessage("=== execute() complete - Geometry recalculated ===\n")
            
        except Exception as e:
            App.Console.PrintError(f"Error executing bullet feature: {e}\n")
            import traceback
            App.Console.PrintError(traceback.format_exc())
    
    def onChanged(self, obj, prop):
        """
        Called when a property changes.
        
        Args:
            obj: The document object
            prop: Name of the property that changed
        """
        # Skip entirely during initialization
        if hasattr(self, '_initializing') and self._initializing:
            return
        
        # Skip if essential properties don't exist yet
        if not hasattr(obj, "Material") or not hasattr(obj, "Diameter"):
            return
        
        # Helper function for value conversion (needed in onChanged)
        def to_mm(prop_value):
            """Convert property to mm as float."""
            if prop_value is None:
                return 0.0
            try:
                if hasattr(prop_value, 'getValueAs'):
                    return float(prop_value.getValueAs('mm').Value)
                elif hasattr(prop_value, 'Value'):
                    val = prop_value.Value
                    if hasattr(val, 'getValueAs'):
                        return float(val.getValueAs('mm').Value)
                    return float(val)
                else:
                    return float(prop_value)
            except (AttributeError, TypeError, ValueError):
                try:
                    return float(prop_value)
                except (TypeError, ValueError):
                    return 0.0
        
        # Update density when material changes
        if prop == "Material":
            try:
                if hasattr(obj, "Density") and hasattr(obj, "Material"):
                    material_db = get_material_database()
                    density = material_db.get_density(obj.Material)
                    obj.Density = density
            except Exception:
                pass  # Property might not exist yet
        
        # Update band diameter when groove diameter changes
        if prop == "Diameter":
            try:
                if hasattr(obj, "BandDiameter") and hasattr(obj, "Diameter"):
                    obj.BandDiameter = obj.Diameter
            except Exception:
                pass  # Property might not exist yet
        
        # Recompute if geometry-affecting properties change
        geometry_props = [
            "Diameter", "LandDiameter", "Length", "OgiveType",
            "OgiveCaliberRatio", "MeplatDiameter", "NumBands",
            "BandLength", "BandSpacing", "BandDiameter",
            "BaseType", "BoatTailLength", "BoatTailAngle"
        ]
        
        if prop in geometry_props:
            App.Console.PrintMessage(f"=== onChanged() - Property '{prop}' changed, triggering recompute ===\n")
            
            # Only trigger recompute if values are reasonable
            # Skip if values are clearly wrong (being reset)
            try:
                if prop == "Length":
                    length_val = to_mm(obj.Length) if 'to_mm' in locals() else (obj.Length.getValueAs('mm').Value if hasattr(obj.Length, 'getValueAs') else float(obj.Length))
                    if length_val < 5.0:
                        App.Console.PrintLog(f"Skipping recompute in onChanged - Length too small ({length_val}mm)\n")
                        return
                # NumBands can be 0 - it's a valid design choice (smooth bullet)
                # Don't skip recompute for NumBands=0
            except:
                pass
            
            # Trigger recompute
            if hasattr(obj, "recompute"):
                App.Console.PrintMessage(f"  Calling obj.recompute() for property '{prop}'\n")
                obj.recompute()
            else:
                App.Console.PrintWarning(f"  Object has no recompute() method!\n")
    
    def __getstate__(self):
        """Called when object is saved."""
        # Return serializable state
        return {"Type": self.Type if hasattr(self, "Type") else "BulletFeature"}
    
    def __setstate__(self, state):
        """Called when object is restored."""
        # Restore state
        if isinstance(state, dict):
            self.Type = state.get("Type", "BulletFeature")
        elif state:
            self.Type = state
        else:
            self.Type = "BulletFeature"
    
    def _update_calculated_properties(self, obj):
        """
        Update calculated properties based on geometry.
        
        Args:
            obj: The document object
        """
        try:
            # Helper to convert Quantity to float
            def to_mm(prop_value):
                """Convert property to mm as float."""
                if hasattr(prop_value, 'Value'):
                    return prop_value.getValueAs('mm').Value
                return float(prop_value)
            
            # Calculate volume from shape
            volume_mm3 = 0.0
            if obj.Shape:
                try:
                    if hasattr(obj.Shape, "Volume"):
                        volume_mm3 = obj.Shape.Volume
                    elif hasattr(obj.Shape, "getVolume"):
                        volume_mm3 = obj.Shape.getVolume()
                except:
                    # Shape might not be valid yet
                    pass
            
            obj.Volume = volume_mm3
            
            # Calculate actual weight from volume
            if volume_mm3 > 0:
                density = float(obj.Density) if hasattr(obj, "Density") else 8.86
                weight_grains = calculate_weight_from_volume(
                    volume_mm3,
                    density
                )
                obj.ActualWeight = weight_grains
            else:
                # Fallback: use target weight if volume not available
                if hasattr(obj, "Weight"):
                    try:
                        obj.ActualWeight = float(obj.Weight)
                    except:
                        obj.ActualWeight = 0.0
                else:
                    obj.ActualWeight = 0.0
            
            # Get property values as floats
            diameter_mm = to_mm(obj.Diameter) if hasattr(obj, "Diameter") else 6.7
            length_mm = to_mm(obj.Length) if hasattr(obj, "Length") else 32.0
            num_bands = int(obj.NumBands) if hasattr(obj, "NumBands") else 4
            band_length_mm = to_mm(obj.BandLength) if hasattr(obj, "BandLength") else 2.25
            band_spacing_mm = to_mm(obj.BandSpacing) if hasattr(obj, "BandSpacing") else 0.75
            weight_grains = float(obj.ActualWeight) if hasattr(obj, "ActualWeight") else 140.0
            ogive_type = obj.OgiveType if hasattr(obj, "OgiveType") else "Tangent"
            
            # Calculate bearing surface
            bearing_surface = calculate_bearing_surface(
                diameter_mm,
                length_mm,
                num_bands,
                band_length_mm,
                band_spacing_mm
            )
            obj.BearingSurface = bearing_surface
            
            # Calculate sectional density
            sd = calculate_sectional_density(
                diameter_mm,
                weight_grains
            )
            obj.SectionalDensity = sd
            
            # Calculate ballistic coefficient
            bc = calculate_ballistic_coefficient_g1(
                diameter_mm,
                weight_grains,
                length_mm,
                ogive_type
            )
            obj.BC_G1 = bc
            
            # Calculate recommended twist
            twist_rate, twist_str = calculate_recommended_twist_rate(
                diameter_mm,
                length_mm,
                weight_grains
            )
            obj.RecommendedTwist = twist_str
            
        except Exception as e:
            App.Console.PrintWarning(
                f"Error updating calculated properties: {e}\n"
            )


def makeBulletFeature(name="Bullet"):
    """
    Create a new bullet feature object.
    
    Args:
        name: Name for the object
        
    Returns:
        FreeCAD document object
    """
    doc = App.ActiveDocument
    if doc is None:
        App.Console.PrintError("No active document\n")
        return None
    
    obj = doc.addObject("Part::FeaturePython", name)
    
    # Create the feature (this adds all properties)
    BulletFeature(obj)
    
    # Set default values AFTER object creation
    # IMPORTANT: Use the document's unit system - PropertyLength expects values in document units
    # For FreeCAD, we can set PropertyLength as float (mm) or as Quantity
    App.Console.PrintMessage("=== makeBulletFeature: Calculating optimal dimensions from weight ===\n")
    try:
        # Set design type first (default to Traditional if not set)
        if not hasattr(obj, "DesignType") or not obj.DesignType:
            obj.DesignType = "Traditional"
        
        design_type = obj.DesignType
        
        # Set parameters based on design type
        App.Console.PrintMessage(f"Setting parameters for {design_type} design...\n")
        obj.Diameter = 6.7
        obj.LandDiameter = 6.50
        obj.Weight = 140.0
        obj.NumBands = 4
        obj.BandLength = 2.25
        obj.BandSpacing = 3.0
        obj.BandDiameter = 6.7
        obj.BaseType = "BoatTail"
        
        if design_type == "VLD":
            # VLD (Very Low Drag) design - optimized for high BC
            App.Console.PrintMessage("Using VLD defaults: longer ogive, smaller meplat, longer boat tail\n")
            obj.OgiveType = "Secant"  # Secant ogive for better BC
            obj.OgiveCaliberRatio = 9.0  # Longer ogive (9 calibers)
            obj.MeplatDiameter = 0.5  # Smaller meplat for better BC
            obj.BoatTailLength = 8.0  # Longer boat tail (will be calculated, but start higher)
            obj.BoatTailAngle = 8.0  # Slightly steeper angle
        else:
            # Traditional design - balanced performance
            App.Console.PrintMessage("Using Traditional defaults\n")
            obj.OgiveType = "Tangent"
            obj.OgiveCaliberRatio = 7.0
            obj.MeplatDiameter = 1.5
            obj.BoatTailLength = 5.0  # Will be calculated
            obj.BoatTailAngle = 9.0
        
        # Get material density
        material_db = get_material_database()
        material_names = material_db.get_material_names()
        if material_names:
            copper_alloy = next((mat for mat in material_names if "Copper" in mat or "copper" in mat.lower()), None)
            obj.Material = copper_alloy if copper_alloy else material_names[0]
            density = material_db.get_density(obj.Material)
            obj.Density = density
        else:
            density = 8.96  # Default copper density
        
        # Calculate optimal dimensions from target weight
        App.Console.PrintMessage("\n=== CALCULATING OPTIMAL DIMENSIONS ===\n")
        # Helper to safely get float value for display
        def get_display_value(prop_value):
            """Get float value for display, handling Quantity objects."""
            if hasattr(prop_value, 'getValueAs'):
                try:
                    return float(prop_value.getValueAs('mm').Value)
                except:
                    try:
                        return float(prop_value.Value)
                    except:
                        return float(prop_value)
            elif hasattr(prop_value, 'Value'):
                return float(prop_value.Value)
            return float(prop_value)
        
        def get_angle_display_value(prop_value):
            """Get angle value for display."""
            if hasattr(prop_value, 'getValueAs'):
                try:
                    return float(prop_value.getValueAs('deg').Value)
                except:
                    try:
                        return float(prop_value.Value)
                    except:
                        return float(prop_value)
            elif hasattr(prop_value, 'Value'):
                return float(prop_value.Value)
            return float(prop_value)
        
        App.Console.PrintMessage(f"Input Parameters:\n")
        design_type_str = str(obj.DesignType) if hasattr(obj, "DesignType") else "Traditional"
        land_riding_str = "Yes" if (hasattr(obj, "LandRiding") and obj.LandRiding) else "No"
        App.Console.PrintMessage(f"  Design Type: {design_type_str}\n")
        App.Console.PrintMessage(f"  Land Riding: {land_riding_str}\n")
        App.Console.PrintMessage(f"  Target Weight: {float(obj.Weight):.2f} grains\n")
        App.Console.PrintMessage(f"  Groove Diameter: {get_display_value(obj.Diameter):.2f} mm\n")
        App.Console.PrintMessage(f"  Land Diameter: {get_display_value(obj.LandDiameter):.2f} mm\n")
        App.Console.PrintMessage(f"  Material Density: {density:.2f} g/cm³\n")
        App.Console.PrintMessage(f"  Number of Bands: {int(obj.NumBands)}\n")
        App.Console.PrintMessage(f"  Band Length: {get_display_value(obj.BandLength):.2f} mm\n")
        App.Console.PrintMessage(f"  Band Spacing: {get_display_value(obj.BandSpacing):.2f} mm\n")
        App.Console.PrintMessage(f"  Ogive Caliber Ratio: {float(obj.OgiveCaliberRatio):.2f}\n")
        App.Console.PrintMessage(f"  Ogive Type: {str(obj.OgiveType)}\n")
        App.Console.PrintMessage(f"  Boat Tail Angle: {get_angle_display_value(obj.BoatTailAngle):.2f} deg\n")
        App.Console.PrintMessage(f"  Meplat Diameter: {get_display_value(obj.MeplatDiameter):.2f} mm\n")
        
        # Helper function to convert Quantity to float
        def to_float_value(prop_value):
            """Convert property to float, handling Quantity objects."""
            if hasattr(prop_value, 'getValueAs'):
                try:
                    return float(prop_value.getValueAs('mm').Value)
                except:
                    try:
                        return float(prop_value.Value)
                    except:
                        return float(prop_value)
            elif hasattr(prop_value, 'Value'):
                return float(prop_value.Value)
            return float(prop_value)
        
        def to_angle_deg_value(prop_value):
            """Convert angle property to degrees."""
            if hasattr(prop_value, 'getValueAs'):
                try:
                    return float(prop_value.getValueAs('deg').Value)
                except:
                    try:
                        return float(prop_value.Value)
                    except:
                        return float(prop_value)
            elif hasattr(prop_value, 'Value'):
                return float(prop_value.Value)
            return float(prop_value)
        
        # Convert all values to floats before passing to calculation
        weight_val = float(obj.Weight)
        diameter_val = to_float_value(obj.Diameter)
        land_diameter_val = to_float_value(obj.LandDiameter)
        band_length_val = to_float_value(obj.BandLength)
        band_spacing_val = to_float_value(obj.BandSpacing)
        meplat_val = to_float_value(obj.MeplatDiameter)
        boat_tail_angle_val = to_angle_deg_value(obj.BoatTailAngle)
        
        # Get land riding setting
        land_riding = bool(obj.LandRiding) if hasattr(obj, "LandRiding") else True
        
        calc_result = calculate_bullet_dimensions_from_weight(
            target_weight_grains=weight_val,
            groove_diameter_mm=diameter_val,
            land_diameter_mm=land_diameter_val,
            material_density_g_per_cm3=density,
            num_bands=int(obj.NumBands),
            band_length_mm=band_length_val,
            band_spacing_mm=band_spacing_val,
            ogive_caliber_ratio=float(obj.OgiveCaliberRatio),
            ogive_type=str(obj.OgiveType),
            boat_tail_angle_deg=boat_tail_angle_val,
            meplat_diameter_mm=meplat_val,
            land_riding=land_riding
        )
        
        # Display calculated results
        App.Console.PrintMessage("\n=== CALCULATED RESULTS ===\n")
        App.Console.PrintMessage(f"Total Length: {calc_result['total_length_mm']:.2f} mm\n")
        App.Console.PrintMessage(f"Boat Tail Length: {calc_result['boat_tail_length_mm']:.2f} mm\n")
        App.Console.PrintMessage(f"Bearing Surface Length: {calc_result['bearing_surface_length_mm']:.2f} mm\n")
        App.Console.PrintMessage(f"Ogive Length: {calc_result['ogive_length_mm']:.2f} mm\n")
        App.Console.PrintMessage(f"Gap Length Needed: {calc_result['gap_length_needed_mm']:.2f} mm\n")
        App.Console.PrintMessage(f"Gap Coverage: {calc_result['gap_coverage_mm']:.2f} mm\n")
        App.Console.PrintMessage(f"\nBallistic Properties:\n")
        App.Console.PrintMessage(f"  Ballistic Coefficient (G1): {calc_result['ballistic_coefficient_g1']:.3f}\n")
        App.Console.PrintMessage(f"  Sectional Density: {calc_result['sectional_density']:.3f}\n")
        App.Console.PrintMessage(f"  Length/Diameter Ratio: {calc_result['length_diameter_ratio']:.2f}\n")
        App.Console.PrintMessage(f"  Meplat Ratio: {calc_result['meplat_ratio']:.3f}\n")
        App.Console.PrintMessage(f"  Form Factor: {calc_result['form_factor']:.3f}\n")
        App.Console.PrintMessage(f"\nWeight Verification:\n")
        App.Console.PrintMessage(f"  Target Weight: {calc_result['target_weight_grains']:.2f} grains\n")
        App.Console.PrintMessage(f"  Calculated Weight: {calc_result['calculated_weight_grains']:.2f} grains\n")
        App.Console.PrintMessage(f"  Weight Error: {calc_result['weight_error_percent']:.2f}%\n")
        App.Console.PrintMessage(f"\nValidation: {calc_result['validation_message']}\n")
        App.Console.PrintMessage(f"Valid: {calc_result['is_valid']}\n")
        
        # Set calculated values
        if calc_result['is_valid']:
            # Set as plain floats - FreeCAD PropertyLength will handle units
            obj.Length = calc_result['total_length_mm']
            obj.BoatTailLength = calc_result['boat_tail_length_mm']
            App.Console.PrintMessage(f"\n=== APPLYING CALCULATED DIMENSIONS ===\n")
            App.Console.PrintMessage(f"Set Length = {calc_result['total_length_mm']:.2f} mm\n")
            App.Console.PrintMessage(f"Set BoatTailLength = {calc_result['boat_tail_length_mm']:.2f} mm\n")
        else:
            App.Console.PrintWarning(f"\nWARNING: Calculation failed!\n")
            App.Console.PrintWarning(f"Reason: {calc_result['validation_message']}\n")
            App.Console.PrintWarning(f"Attempting to use calculated values anyway...\n")
            # Try to use calculated values even if validation failed
            if calc_result['total_length_mm'] > 0:
                obj.Length = calc_result['total_length_mm']
                obj.BoatTailLength = calc_result['boat_tail_length_mm']
                App.Console.PrintMessage(f"Using calculated Length = {calc_result['total_length_mm']:.2f} mm\n")
                App.Console.PrintMessage(f"Using calculated BoatTailLength = {calc_result['boat_tail_length_mm']:.2f} mm\n")
            else:
                # Fallback to defaults only if calculation completely failed
                App.Console.PrintWarning(f"Calculation returned zero length, using safe defaults\n")
                obj.Length = 50.0  # Increased default to allow room
                obj.BoatTailLength = 5.0
        
        # Density was already set above during calculation
        
        # Verify values were set correctly by reading them back
        try:
            # Helper to safely get value in mm
            def get_mm_value(prop):
                try:
                    if hasattr(prop, 'getValueAs'):
                        return float(prop.getValueAs('mm').Value)
                    elif hasattr(prop, 'Value'):
                        return float(prop.Value)
                    else:
                        return float(prop)
                except:
                    return 0.0
            
            length_val = get_mm_value(obj.Length)
            land_diameter_val = get_mm_value(obj.LandDiameter)
            band_length_val = get_mm_value(obj.BandLength)
            band_spacing_val = get_mm_value(obj.BandSpacing)
            diameter_val = get_mm_value(obj.Diameter)
            ogive_ratio_val = float(obj.OgiveCaliberRatio)
            boat_tail_length_val = get_mm_value(obj.BoatTailLength)
            num_bands_val = int(obj.NumBands)
            
            App.Console.PrintMessage(f"=== VERIFICATION: Length={length_val}mm, Diameter={diameter_val}mm, LandDiameter={land_diameter_val}mm, NumBands={num_bands_val} ===\n")
            App.Console.PrintMessage(f"  BandLength={band_length_val}mm, BandSpacing={band_spacing_val}mm, OgiveRatio={ogive_ratio_val}\n")
            App.Console.PrintMessage(f"  BoatTailLength={boat_tail_length_val}mm\n")
            
            # Check if Length is wrong and fix it
            if length_val < 10.0 or length_val > 100.0:
                App.Console.PrintWarning(f"Length is incorrect ({length_val}mm), fixing to 32.0mm\n")
                obj.Length = 32.0
                length_val = get_mm_value(obj.Length)
                App.Console.PrintMessage(f"  After fix: Length={length_val}mm\n")
            
            # Check if LandDiameter is wrong and fix it
            if land_diameter_val < 1.0 or land_diameter_val > 10.0:
                App.Console.PrintWarning(f"LandDiameter is incorrect ({land_diameter_val}mm), fixing to 6.50mm\n")
                obj.LandDiameter = 6.50
                land_diameter_val = get_mm_value(obj.LandDiameter)
                App.Console.PrintMessage(f"  After fix: LandDiameter={land_diameter_val}mm\n")
            
            # Check if OgiveCaliberRatio is wrong and fix it
            if ogive_ratio_val < 2.0 or ogive_ratio_val > 15.0:
                App.Console.PrintWarning(f"OgiveCaliberRatio is incorrect ({ogive_ratio_val}), fixing to 7.0\n")
                obj.OgiveCaliberRatio = 7.0
                ogive_ratio_val = 7.0
                App.Console.PrintMessage(f"  After fix: OgiveCaliberRatio={ogive_ratio_val}\n")
            
            # Check if MeplatDiameter is wrong and fix it
            meplat_val = get_mm_value(obj.MeplatDiameter)
            if meplat_val < 0.5 or meplat_val > 5.0:
                App.Console.PrintWarning(f"MeplatDiameter is incorrect ({meplat_val}mm), fixing to 1.5mm\n")
                obj.MeplatDiameter = 1.5
                App.Console.PrintMessage(f"  After fix: MeplatDiameter=1.5mm\n")
            
            # Check if BandLength is wrong and fix it
            if band_length_val < 0.5 or band_length_val > 10.0:
                App.Console.PrintWarning(f"BandLength is incorrect ({band_length_val}mm), fixing to 2.25mm\n")
                obj.BandLength = 2.25
                band_length_val = get_mm_value(obj.BandLength)
                App.Console.PrintMessage(f"  After fix: BandLength={band_length_val}mm\n")
            
            # Check if BandSpacing is wrong and fix it
            if band_spacing_val < 0.5 or band_spacing_val > 10.0:
                App.Console.PrintWarning(f"BandSpacing is incorrect ({band_spacing_val}mm), fixing to 3.0mm\n")
                obj.BandSpacing = 3.0
                band_spacing_val = get_mm_value(obj.BandSpacing)
                App.Console.PrintMessage(f"  After fix: BandSpacing={band_spacing_val}mm\n")
            
            # Check if BoatTailLength is wrong and fix it
            if boat_tail_length_val < 0.5 or boat_tail_length_val > 15.0:
                App.Console.PrintWarning(f"BoatTailLength is incorrect ({boat_tail_length_val}mm), fixing to 5.0mm\n")
                obj.BoatTailLength = 5.0
                boat_tail_length_val = get_mm_value(obj.BoatTailLength)
                App.Console.PrintMessage(f"  After fix: BoatTailLength={boat_tail_length_val}mm\n")
            
            # Calculate if bands fit (same logic as validation)
            if num_bands_val > 0:
                total_band_space = num_bands_val * band_length_val
                if num_bands_val > 1:
                    total_band_space += (num_bands_val - 1) * band_spacing_val
                ogive_length = (ogive_ratio_val * diameter_val) / 2.0
                available_length = length_val - ogive_length - boat_tail_length_val
                App.Console.PrintMessage(f"  Band space needed: {total_band_space}mm, Available: {available_length}mm\n")
                
                if total_band_space > available_length:
                    App.Console.PrintError(f"ERROR: Bands don't fit! Adjusting parameters...\n")
                    # Auto-adjust: reduce band spacing or length
                    if available_length > 0:
                        # Try to fit by reducing spacing
                        max_spacing = (available_length - (num_bands_val * band_length_val)) / max(1, num_bands_val - 1)
                        if max_spacing > 0:
                            obj.BandSpacing = max(0.5, max_spacing)
                            App.Console.PrintMessage(f"  Adjusted BandSpacing to {obj.BandSpacing}mm\n")
        except Exception as e:
            App.Console.PrintWarning(f"Error verifying values: {e}\n")
            import traceback
            App.Console.PrintWarning(traceback.format_exc())
        
        # NOW mark initialization complete - values are set
        if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, '_initializing'):
            obj.Proxy._initializing = False
            App.Console.PrintMessage("=== Initialization complete - values set ===\n")
        
    except Exception as e:
        App.Console.PrintError(f"=== ERROR setting default values: {e} ===\n")
        import traceback
        App.Console.PrintError("=== FULL TRACEBACK ===\n")
        App.Console.PrintError(traceback.format_exc())
        App.Console.PrintError("=== END TRACEBACK ===\n")
        # Still mark initialization complete even on error
        if hasattr(obj, 'Proxy') and hasattr(obj.Proxy, '_initializing'):
            obj.Proxy._initializing = False
    
    # Set view provider
    if App.GuiUp:
        from Objects.ViewProviders import ViewProviderBullet
        ViewProviderBullet(obj.ViewObject)
    
    return obj
