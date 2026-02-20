"""
Geometry generation helpers for bullet shapes.

This module provides functions to generate bullet profiles and 3D geometry
using FreeCAD's Part module.
"""

import FreeCAD as App
import Part
import math
from typing import List, Tuple, Optional


def generate_bullet_profile_points(
    diameter_mm: float,
    land_diameter_mm: float,
    length_mm: float,
    ogive_type: str,
    ogive_caliber_ratio: float,
    meplat_diameter_mm: float,
    num_bands: int,
    band_length_mm: float,
    band_spacing_mm: float,
    base_type: str,
    boat_tail_length_mm: float,
    boat_tail_angle_deg: float,
    land_riding: bool = True
) -> List[Tuple[float, float]]:
    """
    Generate 2D profile points for bullet (half-profile for revolution).
    
    Points are in (Z, R) format where Z is along bullet axis and R is radius.
    Z=0 is at the base, Z increases toward the tip.
    
    Args:
        diameter_mm: Overall bullet diameter (groove diameter)
        land_diameter_mm: Land riding diameter (ignored if land_riding=False)
        length_mm: Total bullet length
        ogive_type: Type of ogive ("Tangent", "Secant", "Elliptical")
        ogive_caliber_ratio: Ogive length in calibers
        meplat_diameter_mm: Tip diameter
        num_bands: Number of driving bands
        band_length_mm: Length of each band
        band_spacing_mm: Space between bands
        base_type: "Flat" or "BoatTail"
        boat_tail_length_mm: Length of boat tail
        boat_tail_angle_deg: Boat tail angle in degrees
        land_riding: If True, body uses land diameter; if False, uses groove diameter
        
    Returns:
        List of (Z, R) tuples representing the profile
    """
    points = []
    radius_groove = diameter_mm / 2.0
    
    # Determine body radius based on land_riding
    if land_riding:
        radius_land = land_diameter_mm / 2.0
        # Validate inputs
        if radius_land >= radius_groove:
            radius_land = radius_groove * 0.98  # Ensure land < groove
        body_radius = radius_land  # Use land diameter for body
    else:
        # Non-land-riding: body uses groove diameter
        body_radius = radius_groove
        radius_land = radius_groove  # Not used, but set for ogive calculations
    
    # Meplat validation
    meplat_radius = meplat_diameter_mm / 2.0
    if meplat_radius >= body_radius:
        meplat_radius = body_radius * 0.5
        meplat_diameter_mm = meplat_radius * 2.0
    
    # Start from base (Z=0) - always start on axis for proper wire closing
    z_pos = 0.0
    points.append((z_pos, 0.0))
    
    # Base section
    if base_type == "BoatTail" and boat_tail_length_mm > 0:
        # Boat tail
        boat_tail_angle_rad = math.radians(boat_tail_angle_deg)
        base_radius = radius_groove - boat_tail_length_mm * math.tan(boat_tail_angle_rad)
        base_radius = max(base_radius, radius_groove * 0.3)  # Don't go too small
        
        points.append((z_pos, base_radius))
        z_pos += boat_tail_length_mm
        points.append((z_pos, radius_groove))
    else:
        # Flat base - go from axis to base radius
        points.append((z_pos, radius_groove))
    
    # Body section with driving bands
    # IMPORTANT: When num_bands=0, create smooth body (no bands visible)
    if land_riding:
        # IMPORTANT: The body is a CONTINUOUS cylinder at land diameter
        # Bands are RADIAL EXPANSIONS on this continuous body, not separate sections
        body_start_z = z_pos
        
        # Calculate ogive length
        ogive_length = ((ogive_caliber_ratio * diameter_mm) / 2.0)
        
        # Calculate body length (continuous axle from base to ogive start)
        body_length = length_mm - z_pos - ogive_length
        
        if body_length <= 0:
            # Not enough space - adjust ogive or boat tail
            body_length = max(0.1, length_mm - z_pos - ogive_length)
        
        # Create continuous body cylinder at land diameter
        # This is the "axle" that runs the full length
        body_end_z = z_pos + body_length
        
        # Start of body (at land diameter)
        points.append((z_pos, body_radius))
        
        if num_bands > 0:
            # Calculate band positions along the continuous body
            # Bands are expansions ON the body, not separate sections
            total_band_space = num_bands * band_length_mm
            if num_bands > 1:
                total_band_space += (num_bands - 1) * band_spacing_mm
            
            # Check if bands fit in body length
            if total_band_space > body_length:
                # Bands don't fit - this is a design issue
                # For now, scale spacing to fit
                if num_bands > 1:
                    available_for_spacing = body_length - (num_bands * band_length_mm)
                    band_spacing_mm = max(0.1, available_for_spacing / (num_bands - 1))
            
            # Position bands along the body
            current_z = z_pos
            
            for i in range(num_bands):
                # Calculate band start position
                if i == 0:
                    band_start_z = current_z
                else:
                    # Space from previous band
                    band_start_z = current_z + band_spacing_mm
                
                # Don't exceed body length
                if band_start_z >= body_end_z:
                    break
                
                # Transition to band (small chamfer)
                if band_start_z > current_z + 0.1:
                    points.append((band_start_z, body_radius))
                
                band_start_expand_z = band_start_z + 0.2
                if band_start_expand_z < body_end_z:
                    points.append((band_start_expand_z, radius_groove))
                
                # Band itself (at groove diameter)
                band_end_z = min(band_start_z + band_length_mm, body_end_z)
                band_end_expand_z = band_end_z - 0.2
                
                if band_end_expand_z > band_start_expand_z:
                    points.append((band_end_expand_z, radius_groove))
                
                # Transition back to land diameter
                if band_end_z < body_end_z:
                    points.append((band_end_z, body_radius))
                
                current_z = band_end_z
            
            # Ensure we have a point at body end (land diameter)
            if current_z < body_end_z:
                points.append((body_end_z, body_radius))
        else:
            # No bands - smooth continuous body at land diameter
            # Create smooth cylinder from start to end
            # Start point already added at line 112, just add end point
            points.append((body_end_z, body_radius))
    else:
        # Non-land-riding bullet: body uses groove diameter
        # Calculate ogive length
        ogive_length = ((ogive_caliber_ratio * diameter_mm) / 2.0)
        
        # Calculate body length
        body_length = length_mm - z_pos - ogive_length
        
        if body_length <= 0:
            body_length = max(0.1, length_mm - z_pos - ogive_length)
        
        body_end_z = z_pos + body_length
        
        if num_bands > 0:
            # Bands on groove-riding bullet: bands are at groove diameter, gaps are also at groove
            # Actually, for groove-riding, bands don't make physical sense
            # But we'll model them as slight expansions if requested
            total_band_space = num_bands * band_length_mm
            if num_bands > 1:
                total_band_space += (num_bands - 1) * band_spacing_mm
            
            if total_band_space > body_length:
                if num_bands > 1:
                    available_for_spacing = body_length - (num_bands * band_length_mm)
                    band_spacing_mm = max(0.1, available_for_spacing / (num_bands - 1))
            
            # Position bands along the body
            current_z = z_pos
            
            for i in range(num_bands):
                if i == 0:
                    band_start_z = current_z
                else:
                    band_start_z = current_z + band_spacing_mm
                
                if band_start_z >= body_end_z:
                    break
                
                # Band at groove diameter (slight expansion)
                band_start_expand_z = band_start_z + 0.2
                if band_start_expand_z < body_end_z:
                    points.append((band_start_expand_z, radius_groove * 1.01))  # Slight expansion
                
                band_end_z = min(band_start_z + band_length_mm, body_end_z)
                band_end_expand_z = band_end_z - 0.2
                
                if band_end_expand_z > band_start_expand_z:
                    points.append((band_end_expand_z, radius_groove * 1.01))
                
                # Back to groove diameter
                if band_end_z < body_end_z:
                    points.append((band_end_z, radius_groove))
                
                current_z = band_end_z
            
            if current_z < body_end_z:
                points.append((body_end_z, radius_groove))
        else:
            # No bands - smooth body at groove diameter
            # Start of body at groove diameter (if not already added by boat tail)
            if base_type != "BoatTail" or boat_tail_length_mm <= 0:
                # Flat base case - start point already added, but ensure we have it
                if not points or points[-1][0] != z_pos:
                    points.append((z_pos, radius_groove))
            # End of body at groove diameter (smooth cylinder)
            points.append((body_end_z, radius_groove))
    
    # Ogive section starts where body ends
    ogive_start_z = body_end_z
    
    # Calculate ogive length - this is the length of the curved ogive section
    ogive_length = (ogive_caliber_ratio * diameter_mm) / 2.0
    
    # The ogive MUST end exactly at the total bullet length
    # Calculate what the ogive end should be to ensure bullet ends at length_mm
    ogive_end_z = length_mm
    
    # Recalculate ogive_length to ensure it reaches the tip
    # This ensures the ogive ends exactly at length_mm
    actual_ogive_length = ogive_end_z - ogive_start_z
    
    # Ogive base radius is the body radius at the transition point
    ogive_base_radius = body_radius
    
    # Generate ogive using endpoints and rim point (for circular arc)
    # Instead of many segments, create a single arc from start to end with a rim point
    
    # Start point: junction with body
    ogive_start_point = (ogive_start_z, ogive_base_radius)
    
    # End point: tip/meplat
    ogive_end_point = (ogive_end_z, meplat_radius)
    
    # Rim point: midpoint of ogive (t=0.5) - defines the curve
    z_rim = ogive_start_z + 0.5 * actual_ogive_length
    if ogive_type == "Tangent":
        radius_rim = generate_tangent_ogive_radius(
            0.5, ogive_base_radius, meplat_radius, actual_ogive_length
        )
    elif ogive_type == "Secant":
        radius_rim = generate_secant_ogive_radius(
            0.5, ogive_base_radius, meplat_radius, actual_ogive_length
        )
    else:  # Elliptical
        radius_rim = generate_elliptical_ogive_radius(
            0.5, ogive_base_radius, meplat_radius, actual_ogive_length
        )
    ogive_rim_point = (z_rim, radius_rim)
    
    # Store ogive points: start, rim (midpoint), end
    # These will be detected in create_bullet_solid and converted to an arc
    points.append(ogive_start_point)  # Start of ogive (junction with body)
    points.append(ogive_rim_point)   # Rim point (midpoint at t=0.5)
    points.append(ogive_end_point)   # End of ogive (tip/meplat)
    
    App.Console.PrintMessage(f"Ogive points: start ({ogive_start_point[0]:.2f}, {ogive_start_point[1]:.2f}), rim ({ogive_rim_point[0]:.2f}, {ogive_rim_point[1]:.2f}), end ({ogive_end_point[0]:.2f}, {ogive_end_point[1]:.2f})\n")
    
    # Tip (meplat) - The ogive end point is already at (length_mm, meplat_radius)
    # We just need to add the axis point to close the wire
    # Only add if meplat_radius > 0 (if meplat is zero, ogive end is already on axis)
    if meplat_radius > 0:
        # Add point on axis at tip to close wire
        points.append((length_mm, 0.0))
    # If meplat_radius is 0, the ogive end point is already on axis, so we're done
    
    return points


def generate_tangent_ogive_radius(
    t: float,
    base_radius: float,
    tip_radius: float,
    length: float
) -> float:
    """
    Generate radius for tangent ogive at parameter t (0-1) using proper radius of curvature formula.
    
    A tangent ogive is defined by a circular arc that is tangent to both the body cylinder and
    the meplat. The formula uses the length parameter to ensure proper geometric scaling.
    
    The formula R(x) = R0 - (R0 - R_tip) * (1 - sqrt(1 - ((L-x)/L)²)) ensures:
    - R(0) = R0 (tangent to body at base)
    - R(L) = R_tip (tangent to meplat at tip)
    - The curve is a circular arc based on radius of curvature
    
    Args:
        t: Parameter from 0 (base) to 1 (tip)
        base_radius: Radius at base of ogive (R0)
        tip_radius: Radius at tip (meplat radius)
        length: Length of ogive (L) - used in the radius calculation
        
    Returns:
        Radius at parameter t
    """
    if length <= 0 or base_radius <= tip_radius:
        # Fallback to linear interpolation if invalid parameters
        return base_radius - (base_radius - tip_radius) * t
    
    delta_r = base_radius - tip_radius
    if delta_r <= 0:
        return base_radius  # No transition if base <= tip
    
    # Distance from base along ogive (x goes from 0 to L)
    x = t * length
    
    # Normalized parameter u: distance from base (u=0 at base, u=1 at tip)
    # This ensures the formula uses the length parameter correctly
    u = x / length
    
    # Tangent ogive formula using circular arc geometry (convex curve)
    # R(x) = R_tip + (R0 - R_tip) * sqrt(1 - u²)
    # When u=0 (base): radius = tip_radius + delta_r * sqrt(1-0) = tip_radius + delta_r = base_radius
    # When u=1 (tip): radius = tip_radius + delta_r * sqrt(1-1) = tip_radius + 0 = tip_radius
    # This gives a convex circular arc that bulges outward (correct ogive shape)
    if u <= 0.0:
        return base_radius
    elif u >= 1.0:
        return tip_radius
    else:
        try:
            radius = tip_radius + delta_r * math.sqrt(1.0 - u * u)
            # Ensure radius is within valid bounds
            return max(tip_radius, min(base_radius, radius))
        except ValueError:
            # If sqrt fails (shouldn't happen with valid u), fallback
            return base_radius - (base_radius - tip_radius) * t


def generate_secant_ogive_radius(
    t: float,
    base_radius: float,
    tip_radius: float,
    length: float
) -> float:
    """
    Generate radius for secant ogive at parameter t (0-1).
    
    Secant ogive is more aggressive (sharper curve).
    """
    # More aggressive curve
    radius = base_radius - (base_radius - tip_radius) * (t ** 1.2)
    return radius


def generate_elliptical_ogive_radius(
    t: float,
    base_radius: float,
    tip_radius: float,
    length: float
) -> float:
    """
    Generate radius for elliptical ogive at parameter t (0-1).
    
    Elliptical ogive provides optimal aerodynamic shape.
    """
    # Elliptical curve
    # Using parametric ellipse equation
    angle = math.pi / 2 * (1 - t)  # From 90° to 0°
    radius = tip_radius + (base_radius - tip_radius) * math.sin(angle)
    return radius


def create_bullet_solid(profile_points: List[Tuple[float, float]]) -> Part.Shape:
    """
    Create a 3D solid from bullet profile points using revolution.
    
    Args:
        profile_points: List of (Z, R) tuples
        
    Returns:
        Part.Shape: The generated bullet solid
    """
    if not profile_points or len(profile_points) < 2:
        raise ValueError("Need at least 2 profile points")
    
    # Remove duplicate points first
    cleaned_points = []
    for i, (z, r) in enumerate(profile_points):
        if i == 0:
            cleaned_points.append((z, r))
        else:
            # Only add if different from previous point
            prev_z, prev_r = cleaned_points[-1]
            if abs(z - prev_z) > 0.001 or abs(r - prev_r) > 0.001:
                cleaned_points.append((z, r))
    
    if len(cleaned_points) < 2:
        raise ValueError("Not enough distinct profile points after cleaning")
    
    profile_points = cleaned_points
    
    # Create wire from points
    # Detect ogive section (3 consecutive points: start, rim, end) and create arc
    edges = []
    i = 0
    ogive_arc_created = False
    
    App.Console.PrintMessage(f"=== Creating wire from {len(profile_points)} profile points ===\n")
    
    while i < len(profile_points) - 1:
        z1, r1 = profile_points[i]
        
        # Check if this is the start of an ogive (3 consecutive points forming ogive)
        # Ogive: start point (junction), rim point (midpoint), end point (tip)
        if i + 2 < len(profile_points):
            z2, r2 = profile_points[i + 1]
            z3, r3 = profile_points[i + 2]
            
            # Check if these 3 points form an ogive (rim point is between start and end)
            # Ogive characteristics: z increases, r decreases from start to end, rim is midpoint
            # More lenient check: allow rim point to be anywhere between start and end
            is_ogive = (
                z1 < z2 < z3 and  # Z increases
                r1 > r2 and r2 > r3 and  # R decreases (convex curve)
                (z2 - z1) > 0.1 and (z3 - z2) > 0.1  # Reasonable spacing
            )
            
            App.Console.PrintMessage(f"  Point {i}: ({z1:.2f}, {r1:.2f}), checking ogive: {is_ogive}\n")
            
            if is_ogive:
                # Create circular arc from 3 points (start, rim, end)
                try:
                    # Points in XZ plane (X = radius, Z = axis)
                    start_point = App.Vector(r1, 0, z1)
                    rim_point = App.Vector(r2, 0, z2)
                    end_point = App.Vector(r3, 0, z3)
                    
                    # Try Part.ArcOfCircle with 3 points constructor
                    try:
                        arc = Part.ArcOfCircle(start_point, rim_point, end_point)
                        arc_shape = arc.toShape()
                        
                        # Verify arc endpoints match expected points
                        arc_start = arc_shape.Vertexes[0].Point
                        arc_end = arc_shape.Vertexes[-1].Point
                        
                        if (arc_start - start_point).Length > 0.01 or (arc_end - end_point).Length > 0.01:
                            App.Console.PrintWarning(f"Arc endpoints don't match: start diff={(arc_start - start_point).Length:.3f}, end diff={(arc_end - end_point).Length:.3f}\n")
                            raise ValueError("Arc endpoints don't match")
                        
                        edges.append(arc_shape)
                        App.Console.PrintMessage(f"Created ogive arc from 3 points: start ({z1:.2f}, {r1:.2f}), rim ({z2:.2f}, {r2:.2f}), end ({z3:.2f}, {r3:.2f})\n")
                        ogive_arc_created = True
                        
                        # After creating arc, we need to connect from arc end (point i+2) to next point (i+3)
                        # Set i to i+2 and update z1, r1 to arc end point so next iteration processes connection correctly
                        i = i + 2
                        z1, r1 = z3, r3  # Update to arc end point
                        # Don't continue - let loop continue to process the connection
                        # The arc ends at (z3, r3), so next iteration will connect (z3, r3) to next point
                    except:
                        # If direct constructor doesn't work, calculate circle from 3 points
                        # Calculate circle center using perpendicular bisector method
                        v1 = rim_point - start_point
                        v2 = end_point - rim_point
                        
                        # Midpoints
                        mid1 = start_point + v1 * 0.5
                        mid2 = rim_point + v2 * 0.5
                        
                        # Perpendicular directions in XZ plane
                        perp1 = App.Vector(-v1.z, 0, v1.x)
                        perp2 = App.Vector(-v2.z, 0, v2.x)
                        
                        if perp1.Length < 1e-6 or perp2.Length < 1e-6:
                            raise ValueError("Points are collinear")
                        
                        perp1.normalize()
                        perp2.normalize()
                        
                        # Solve for circle center: mid1 + t1*perp1 = mid2 + t2*perp2
                        # 2D system in XZ plane
                        A = perp1.x
                        B = -perp2.x
                        C = mid2.x - mid1.x
                        D = perp1.z
                        E = -perp2.z
                        F = mid2.z - mid1.z
                        
                        det = A * E - B * D
                        if abs(det) < 1e-6:
                            raise ValueError("Cannot solve for circle center")
                        
                        t1 = (C * E - B * F) / det
                        center = mid1 + perp1 * t1
                        
                        # Calculate radius
                        radius = (start_point - center).Length
                        
                        # Create circle
                        circle = Part.Circle()
                        circle.Center = center
                        circle.Radius = radius
                        circle.Axis = App.Vector(0, 1, 0)  # Normal to XZ plane
                        
                        # Create arc from start to end
                        arc = Part.ArcOfCircle(circle, start_point, end_point)
                        arc_shape = arc.toShape()
                        
                        # Verify arc endpoints match expected points
                        arc_start = arc_shape.Vertexes[0].Point
                        arc_end = arc_shape.Vertexes[-1].Point
                        
                        if (arc_start - start_point).Length > 0.01 or (arc_end - end_point).Length > 0.01:
                            App.Console.PrintWarning(f"Arc endpoints don't match: start diff={(arc_start - start_point).Length:.3f}, end diff={(arc_end - end_point).Length:.3f}\n")
                            raise ValueError("Arc endpoints don't match")
                        
                        edges.append(arc_shape)
                        App.Console.PrintMessage(f"Created ogive arc: start ({z1:.2f}, {r1:.2f}), rim ({z2:.2f}, {r2:.2f}), end ({z3:.2f}, {r3:.2f}), center ({center.x:.2f}, {center.z:.2f}), radius {radius:.2f}\n")
                        ogive_arc_created = True
                        
                        # After creating arc, we need to connect from arc end (point i+2) to next point (i+3)
                        # Set i to i+2 and update z1, r1 to arc end point so next iteration processes connection correctly
                        i = i + 2
                        z1, r1 = z3, r3  # Update to arc end point
                        # Don't continue - let loop continue to process the connection
                        # The arc ends at (z3, r3), so next iteration will connect (z3, r3) to next point
                except Exception as e:
                    # If arc creation fails, fall back to line segments
                    App.Console.PrintWarning(f"Failed to create ogive arc ({e}), using line segments\n")
                    App.Console.PrintWarning(f"  Will create line segments instead\n")
                    # Fall through to line segment creation - don't skip points
                    is_ogive = False  # Reset flag so we process normally
        
        # Regular line segment
        if i + 1 >= len(profile_points):
            break
            
        z2, r2 = profile_points[i + 1]
        
        # Skip if points are identical
        if abs(z1 - z2) < 0.001 and abs(r1 - r2) < 0.001:
            i += 1
            continue
        
        # Create edge in XZ plane
        point1 = App.Vector(r1, 0, z1)
        point2 = App.Vector(r2, 0, z2)
        
        try:
            edge = Part.makeLine(point1, point2)
            edges.append(edge)
            App.Console.PrintMessage(f"  Created line segment: ({z1:.2f}, {r1:.2f}) -> ({z2:.2f}, {r2:.2f})\n")
        except Exception as e:
            App.Console.PrintError(f"Failed to create line segment: {e}\n")
            raise
        
        i += 1
    
    App.Console.PrintMessage(f"Created {len(edges)} edges total\n")
    
    if len(edges) == 0:
        raise ValueError("No edges created from profile points")
    
    # Create wire from edges
    try:
        wire = Part.Wire(edges)
        App.Console.PrintMessage(f"Wire created with {len(wire.Edges)} edges, closed={wire.isClosed()}\n")
    except Exception as e:
        App.Console.PrintError(f"Failed to create wire from edges: {e}\n")
        App.Console.PrintError(f"  Number of edges: {len(edges)}\n")
        for idx, edge in enumerate(edges):
            try:
                App.Console.PrintError(f"  Edge {idx}: {edge.ShapeType}, length={edge.Length:.3f}\n")
            except:
                App.Console.PrintError(f"  Edge {idx}: invalid\n")
        raise ValueError(f"Failed to create wire: {e}")
    
    # Close the wire if needed - profile should start and end on axis
    if not wire.isClosed():
        App.Console.PrintMessage(f"Wire is not closed, attempting to close it...\n")
        # Get actual wire endpoints
        if wire.Vertexes:
            wire_first = wire.Vertexes[0].Point
            wire_last = wire.Vertexes[-1].Point
            App.Console.PrintMessage(f"  Wire first vertex: ({wire_first.x:.3f}, {wire_first.z:.3f})\n")
            App.Console.PrintMessage(f"  Wire last vertex: ({wire_last.x:.3f}, {wire_last.z:.3f})\n")
        
        # Add closing edge along the axis from tip back to base
        first_z, first_r = profile_points[0]
        last_z, last_r = profile_points[-1]
        
        App.Console.PrintMessage(f"  Profile first point: ({first_z:.3f}, {first_r:.3f})\n")
        App.Console.PrintMessage(f"  Profile last point: ({last_z:.3f}, {last_r:.3f})\n")
        
        # Profile should start and end on axis (r=0), but verify
        if first_r > 0.001 or last_r > 0.001:
            App.Console.PrintMessage(f"  Profile endpoints not on axis, adding closing edges...\n")
            # If not on axis, add edges to close to axis
            first_point = App.Vector(first_r, 0, first_z)
            last_point = App.Vector(last_r, 0, last_z)
            closing_edges = []
            
            # Close to axis at tip if needed
            if last_r > 0.001:
                closing_edges.append(Part.makeLine(last_point, App.Vector(0, 0, last_z)))
            
            # Close along axis from tip to base
            closing_edges.append(Part.makeLine(
                App.Vector(0, 0, last_z),
                App.Vector(0, 0, first_z)
            ))
            
            # Close to profile at base if needed
            if first_r > 0.001:
                closing_edges.append(Part.makeLine(
                    App.Vector(0, 0, first_z),
                    first_point
                ))
            
            all_edges = edges + closing_edges
            App.Console.PrintMessage(f"  Added {len(closing_edges)} closing edges, total edges: {len(all_edges)}\n")
            try:
                wire = Part.Wire(all_edges)
                App.Console.PrintMessage(f"  New wire created, closed={wire.isClosed()}\n")
            except Exception as e:
                App.Console.PrintError(f"  Failed to create wire with closing edges: {e}\n")
                raise
        else:
            # Both ends on axis - just need axis edge to close
            App.Console.PrintMessage(f"  Both endpoints on axis, adding axis edge...\n")
            App.Console.PrintMessage(f"  Creating axis edge from ({last_z:.3f}, 0) to ({first_z:.3f}, 0)\n")
            
            # Get actual wire endpoints to ensure proper connection
            if wire.Vertexes:
                wire_last_pt = wire.Vertexes[-1].Point
                wire_first_pt = wire.Vertexes[0].Point
                App.Console.PrintMessage(f"  Wire last vertex: ({wire_last_pt.z:.3f}, {wire_last_pt.x:.3f})\n")
                App.Console.PrintMessage(f"  Wire first vertex: ({wire_first_pt.z:.3f}, {wire_first_pt.x:.3f})\n")
                
                # Use wire's actual endpoints for axis edge
                axis_edge = Part.makeLine(wire_last_pt, wire_first_pt)
            else:
                # Fallback to profile points
                axis_edge = Part.makeLine(
                    App.Vector(0, 0, last_z),
                    App.Vector(0, 0, first_z)
                )
            
            all_edges = edges + [axis_edge]
            App.Console.PrintMessage(f"  Added axis edge, total edges: {len(all_edges)}\n")
            try:
                wire = Part.Wire(all_edges)
                App.Console.PrintMessage(f"  New wire created, closed={wire.isClosed()}\n")
                if not wire.isClosed():
                    # Try to fix by ensuring edges are properly ordered
                    App.Console.PrintWarning(f"  Wire still not closed, checking edge connectivity...\n")
                    for idx, edge in enumerate(all_edges):
                        if edge.Vertexes:
                            v1 = edge.Vertexes[0].Point
                            v2 = edge.Vertexes[-1].Point
                            App.Console.PrintMessage(f"    Edge {idx}: ({v1.z:.3f}, {v1.x:.3f}) -> ({v2.z:.3f}, {v2.x:.3f})\n")
            except Exception as e:
                App.Console.PrintError(f"  Failed to create wire with axis edge: {e}\n")
                raise
    
    # Validate wire is closed
    if not wire.isClosed():
        App.Console.PrintError(f"Wire is not closed after closing attempt\n")
        if wire.Vertexes:
            App.Console.PrintError(f"  First vertex: {wire.Vertexes[0].Point}\n")
            App.Console.PrintError(f"  Last vertex: {wire.Vertexes[-1].Point}\n")
            first_pt = wire.Vertexes[0].Point
            last_pt = wire.Vertexes[-1].Point
            dist = (first_pt - last_pt).Length
            App.Console.PrintError(f"  Distance between first and last: {dist:.6f}\n")
        raise ValueError("Wire could not be closed - invalid profile")
    
    # Create face from wire - required for proper solid creation
    try:
        face = Part.Face(wire)
        # Validate face
        if face.isNull() or face.Area < 0.001:
            raise ValueError("Face is null or has zero area")
    except Exception as e:
        raise ValueError(f"Failed to create face from wire: {e}. Wire has {len(wire.Edges)} edges, closed={wire.isClosed()}")
    
    # Revolve face around Z-axis (360 degrees) to create solid
    axis = App.Vector(0, 0, 1)
    origin = App.Vector(0, 0, 0)
    
    try:
        revolved_shape = face.revolve(origin, axis, 360.0)
        App.Console.PrintMessage(f"  Revolved shape type: {type(revolved_shape)}\n")
        
        # Ensure we return a proper Solid for section views to work
        # FreeCAD's revolve() can return a Part.Shape wrapper containing a Solid
        solid = None
        
        # First check if it's already a Solid
        if isinstance(revolved_shape, Part.Solid):
            solid = revolved_shape
            App.Console.PrintMessage("  Revolved shape is already a Part.Solid\n")
        # Check if it's a Shape wrapper with Solids inside
        elif isinstance(revolved_shape, Part.Shape):
            App.Console.PrintMessage(f"  Revolved shape is a Part.Shape wrapper\n")
            if hasattr(revolved_shape, 'Solids') and len(revolved_shape.Solids) > 0:
                # Extract the first Solid from the Shape wrapper
                solid = revolved_shape.Solids[0]
                App.Console.PrintMessage(f"  Extracted Solid from Shape wrapper (had {len(revolved_shape.Solids)} Solids)\n")
            elif hasattr(revolved_shape, 'Shells') and len(revolved_shape.Shells) > 0:
                # Try to make a Solid from the Shell
                shell = revolved_shape.Shells[0]
                solid = Part.Solid(shell)
                App.Console.PrintMessage(f"  Created Solid from Shell (had {len(revolved_shape.Shells)} Shells)\n")
            else:
                # Try to make a solid from the shape directly
                try:
                    solid = Part.makeSolid(revolved_shape)
                    App.Console.PrintMessage("  Created Solid using Part.makeSolid()\n")
                except Exception as e2:
                    raise ValueError(f"Failed to convert revolved shape to solid: {e2}. Shape type: {type(revolved_shape)}, has Solids: {hasattr(revolved_shape, 'Solids')}, has Shells: {hasattr(revolved_shape, 'Shells')}")
        else:
            raise ValueError(f"Unexpected revolved shape type: {type(revolved_shape)}")
        
        # Validate solid
        if solid is None:
            raise ValueError("Could not create solid from revolved shape")
        
        # Ensure it's actually a Part.Solid
        if not isinstance(solid, Part.Solid):
            App.Console.PrintWarning(f"  Warning: Solid is not Part.Solid, type: {type(solid)}\n")
            # Try one more conversion attempt
            if isinstance(solid, Part.Shape) and hasattr(solid, 'Solids') and len(solid.Solids) > 0:
                solid = solid.Solids[0]
                App.Console.PrintMessage(f"  Converted to Solid from nested Shape.Solids[0]\n")
            else:
                raise ValueError(f"Result is not a Part.Solid: {type(solid)}")
        
        App.Console.PrintMessage(f"  Final solid type: {type(solid)}, isinstance(Part.Solid): {isinstance(solid, Part.Solid)}\n")
        
        # Validate solid properties
        if solid.Volume < 0.001:
            raise ValueError(f"Solid has zero or negative volume: {solid.Volume}")
        
        # Ensure solid is valid for section views - check bounding box
        bbox = solid.BoundBox
        if not bbox.isValid():
            raise ValueError(f"Solid has invalid bounding box (not valid)")
        if bbox.XLength < 0.001 or bbox.YLength < 0.001 or bbox.ZLength < 0.001:
            raise ValueError(f"Solid has invalid bounding box dimensions: X={bbox.XLength}, Y={bbox.YLength}, Z={bbox.ZLength}")
        
        # Ensure solid is properly formed - critical for section views
        try:
            # Remove any internal splits/edges that might confuse intersection detection
            cleaned_solid = solid.removeSplitter()
            # removeSplitter() may return a Shape wrapper, extract Solid if needed
            if isinstance(cleaned_solid, Part.Solid):
                solid = cleaned_solid
            elif isinstance(cleaned_solid, Part.Shape) and hasattr(cleaned_solid, 'Solids') and len(cleaned_solid.Solids) > 0:
                solid = cleaned_solid.Solids[0]
                App.Console.PrintMessage("  Extracted Solid after removeSplitter()\n")
            else:
                # If removeSplitter returns something unexpected, keep original solid
                App.Console.PrintWarning(f"Warning: removeSplitter() returned unexpected type {type(cleaned_solid)}, keeping original solid\n")
            
            # Re-validate after cleaning
            if solid.Volume < 0.001:
                raise ValueError("Solid volume became invalid after removeSplitter")
            bbox_after = solid.BoundBox
            if not bbox_after.isValid():
                raise ValueError("Solid bounding box became invalid after removeSplitter")
        except Exception as e:
            # If removeSplitter fails, log but continue - the solid might still be valid
            App.Console.PrintWarning(f"Warning: Could not clean solid with removeSplitter: {e}\n")
        
        # Ensure the solid has proper placement (identity) for section views
        # Note: Setting Placement should not wrap it, but verify
        if hasattr(solid, 'Placement'):
            solid.Placement = App.Placement()
        
        # CRITICAL: After operations like removeSplitter() or Placement changes,
        # FreeCAD may wrap the Solid in a Shape container. Extract it one final time.
        if not isinstance(solid, Part.Solid):
            App.Console.PrintWarning(f"  Warning: Solid became Shape wrapper, type: {type(solid)}\n")
            if isinstance(solid, Part.Shape) and hasattr(solid, 'Solids') and len(solid.Solids) > 0:
                solid = solid.Solids[0]
                App.Console.PrintMessage("  Extracted Solid from Shape wrapper before return\n")
            else:
                raise ValueError(f"Cannot return Solid - final type is {type(solid)}")
        
        # Final verification before return - must be a Part.Solid
        if not isinstance(solid, Part.Solid):
            raise ValueError(f"Function returning non-Solid type: {type(solid)}")
        
        App.Console.PrintMessage(f"  Returning Part.Solid (type: {type(solid)}, volume: {solid.Volume:.2f} mm³)\n")
        return solid
        
    except Exception as e:
        raise ValueError(f"Failed to create bullet solid from face: {e}")


def validate_bullet_parameters(
    diameter_mm: float,
    land_diameter_mm: float,
    length_mm: float,
    num_bands: int,
    band_length_mm: float,
    band_spacing_mm: float,
    ogive_caliber_ratio: float,
    meplat_diameter_mm: float,
    boat_tail_length_mm: float
) -> Tuple[bool, Optional[str]]:
    """
    Validate bullet parameters for consistency.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if diameter_mm <= 0:
        return (False, "Diameter must be positive")
    
    if land_diameter_mm >= diameter_mm:
        return (False, "Land diameter must be less than groove diameter")
    
    if length_mm <= 0:
        return (False, "Length must be positive")
    
    if num_bands < 0 or num_bands > 6:
        return (False, "Number of bands must be between 0 and 6")
    
    if num_bands > 0:
        if band_length_mm <= 0:
            return (False, "Band length must be positive")
        if band_spacing_mm < 0:
            return (False, "Band spacing cannot be negative")
    
    if ogive_caliber_ratio < 2.0 or ogive_caliber_ratio > 15.0:
        return (False, "Ogive caliber ratio should be between 2 and 15")
    
    if meplat_diameter_mm >= land_diameter_mm:
        return (False, "Meplat diameter must be less than land diameter")
    
    if boat_tail_length_mm < 0:
        return (False, "Boat tail length cannot be negative")
    
    if boat_tail_length_mm > length_mm * 0.3:
        return (False, "Boat tail length should not exceed 30% of total length")
    
    # Check if bands fit
    # NOTE: Bands are expansions ON a continuous body, not separate sections
    # The body length is: total_length - ogive_length - boat_tail_length
    if num_bands > 0:
        total_band_space = num_bands * band_length_mm
        if num_bands > 1:
            total_band_space += (num_bands - 1) * band_spacing_mm
        
        ogive_length = (ogive_caliber_ratio * diameter_mm) / 2.0
        body_length = length_mm - ogive_length - boat_tail_length_mm
        
        # Bands must fit within the body length (they're expansions on the body)
        if total_band_space > body_length:
            return (False, f"Bands do not fit: need {total_band_space:.2f}mm but body is only {body_length:.2f}mm")
    
    return (True, None)
