# Bullet Designer User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Creating Your First Bullet](#creating-your-first-bullet)
5. [Parameter Guide](#parameter-guide)
6. [Important Constraints](#important-constraints)
7. [Ballistic Calculator](#ballistic-calculator)
8. [Exporting Bullets](#exporting-bullets)
9. [Tips and Best Practices](#tips-and-best-practices)
10. [Troubleshooting](#troubleshooting)

## Introduction

The Bullet Designer workbench for FreeCAD allows you to create parametric bullet designs with precise control over all dimensions. The workbench generates 3D solid models that can be exported for manufacturing or further analysis.

## Installation

### Method 1: FreeCAD Addon Manager (Recommended)

1. Open FreeCAD
2. Go to `Tools` → `Addon Manager`
3. Search for "Bullet Designer"
4. Click `Install`
5. Restart FreeCAD
6. Select "Bullet Designer" from the workbench dropdown menu

### Method 2: Manual Installation

1. Download or clone this repository
2. Copy the `BulletDesigner` folder to your FreeCAD Mods directory:
   - **Linux**: `~/.local/share/FreeCAD/Mod/` or `~/.FreeCAD/Mod/`
   - **Windows**: `C:\Users\<username>\AppData\Roaming\FreeCAD\Mod\`
   - **macOS**: `~/Library/Preferences/FreeCAD/Mod/`
3. Restart FreeCAD
4. Select "Bullet Designer" from the workbench dropdown

## Getting Started

After installation, you'll see the Bullet Designer toolbar with the following commands:

- **Create Bullet**: Create a new parametric bullet object
- **Ballistic Calculator**: Calculate stability and ballistic coefficients
- **Create Cartridge**: (Placeholder - coming soon)
- **Bullet Library**: (Placeholder - coming soon)
- **Export Tools**: Export bullets to STL or STEP format

## Creating Your First Bullet

### Step-by-Step Guide

1. **Switch to Bullet Designer Workbench**
   - Select "Bullet Designer" from the workbench dropdown (top toolbar)

2. **Create a New Bullet**
   - Click the "Create Bullet" button (or use menu: `Bullet Designer` → `Create` → `Create Bullet`)
   - The task panel will open on the left side

3. **Set Basic Dimensions**
   - Go to the "Basic" tab
   - Enter:
     - **Diameter**: Groove diameter (e.g., 6.5 mm)
     - **Land Diameter**: Land riding diameter (must be less than groove diameter)
     - **Length**: Total bullet length (e.g., 30 mm)
     - **Weight**: Target weight in grains (e.g., 140)

4. **Configure Ogive**
   - Go to the "Ogive" tab
   - Select ogive type:
     - **Tangent**: Most common, smooth transition
     - **Secant**: More aggressive curve
     - **Elliptical**: Optimal aerodynamic shape
   - Set **Ogive Caliber Ratio**: Typically 5-12 (length of ogive in calibers)
   - Set **Meplat Diameter**: Tip diameter (usually 0.1-0.5 mm)

5. **Set Driving Bands**
   - Go to the "Bands" tab
   - **CRITICAL**: Ensure bands fit on the bullet (see Important Constraints section)
   - Set:
     - **Number of Bands**: 0-6
     - **Band Length**: Length of each band
     - **Band Spacing**: Space between bands
   - The bands must fit within the body length (total length minus ogive and boat tail)

6. **Configure Base**
   - Go to the "Base" tab
   - Choose base type:
     - **Flat**: Traditional flat base
     - **Boat Tail**: Tapered base for reduced drag
   - If boat tail:
     - Set **Boat Tail Length**: Typically 2-5 mm
     - Set **Boat Tail Angle**: Typically 8-10 degrees

7. **Select Material**
   - Go to the "Material" tab
   - Choose from built-in materials or enter custom density
   - Material affects weight calculations

8. **Enable Live Preview** (Optional)
   - Check "Live Preview" checkbox
   - The bullet will update in real-time as you change parameters

9. **Create the Bullet**
   - Click "OK" to create the bullet object
   - The bullet will appear in the 3D view and tree view

## Parameter Guide

### Basic Dimensions

- **Diameter (Groove Diameter)**: Overall bullet diameter, typically matches barrel groove diameter
- **Land Diameter**: Smaller diameter for land riding bullets, must be less than groove diameter
- **Length**: Total bullet length from base to tip (meplat)
- **Weight**: Target weight in grains (1 grain = 0.0648 grams)

### Ogive Settings

- **Ogive Type**:
  - **Tangent**: Standard ogive where the curve is tangent to the body cylinder
  - **Secant**: More aggressive curve that intersects the body cylinder
  - **Elliptical**: Optimal aerodynamic shape based on elliptical curve
- **Ogive Caliber Ratio**: Length of ogive section expressed in calibers (diameters)
  - Typical range: 5-12 calibers
  - Higher values = longer, more gradual curve
  - Lower values = shorter, sharper curve
- **Meplat Diameter**: Diameter of the flat tip (meplat)
  - Usually 0.1-0.5 mm for match bullets
  - Must be less than land diameter

### Driving Bands

- **Number of Bands**: 0-6 driving bands
  - 0 = no bands (smooth body)
  - 1-3 = typical for most bullets
  - 4-6 = for very long bullets or special designs
- **Band Length**: Length of each individual band in mm
- **Band Spacing**: Space between bands in mm
- **Band Diameter**: Automatically set to groove diameter

**How Bands Work**: Bands are annular expansions on the body. The body runs at land diameter, and bands expand to groove diameter. Bands must fit within the body section (between ogive and base).

### Base Configuration

- **Base Type**:
  - **Flat**: Traditional flat base, easier to manufacture
  - **Boat Tail**: Tapered base reduces drag, improves long-range performance
- **Boat Tail Length**: Length of the tapered section (typically 2-5 mm)
- **Boat Tail Angle**: Taper angle in degrees (typically 8-10°)

### Material Properties

Built-in materials:
- Pure Copper (8.96 g/cm³)
- Gilding Metal 95/5 (8.86 g/cm³)
- Brass 70/30 (8.53 g/cm³)
- Lead Core (11.34 g/cm³)
- Copper Alloy (8.70 g/cm³)
- Lead-Tin Alloy 95/5 (11.20 g/cm³)
- Steel (7.85 g/cm³)

You can also enter a custom density in g/cm³.

## Important Constraints

### CRITICAL: Bands Must Fit on the Bullet

**If bands do not fit within the body length, a solid will NOT be generated.**

The body length is calculated as:
```
Body Length = Total Length - Ogive Length - Boat Tail Length
```

Where:
- **Ogive Length** = (Ogive Caliber Ratio × Diameter) / 2

The total space needed for bands is:
```
Total Band Space = (Number of Bands × Band Length) + ((Number of Bands - 1) × Band Spacing)
```

**Rule**: `Total Band Space` must be ≤ `Body Length`

**Example**:
- Total Length: 30 mm
- Diameter: 6.5 mm
- Ogive Caliber Ratio: 6
- Ogive Length: (6 × 6.5) / 2 = 19.5 mm
- Boat Tail Length: 3 mm
- Body Length: 30 - 19.5 - 3 = 7.5 mm

For 3 bands of 1.5 mm each with 0.5 mm spacing:
- Total Band Space: (3 × 1.5) + (2 × 0.5) = 4.5 + 1.0 = 5.5 mm
- 5.5 mm ≤ 7.5 mm ✓ **Bands fit!**

**If bands don't fit**, you can:
1. Reduce the number of bands
2. Reduce band length
3. Reduce band spacing
4. Increase total bullet length
5. Reduce ogive caliber ratio (shorter ogive = more body length)
6. Reduce boat tail length

### Other Constraints

- **Land Diameter** must be less than **Groove Diameter**
- **Meplat Diameter** must be less than **Land Diameter**
- **Boat Tail Length** should not exceed 30% of total length
- **Ogive Caliber Ratio** should be between 2 and 15

## Ballistic Calculator

The ballistic calculator helps you analyze bullet stability and performance.

### Using the Calculator

1. Select a bullet object in the tree view (optional - will auto-fill dimensions)
2. Click "Ballistic Calculator" button
3. Enter or adjust parameters:
   - Bullet dimensions (auto-filled if bullet is selected)
   - Barrel twist rate (e.g., 1:8 means 1 turn per 8 inches)
   - Muzzle velocity (feet per second)
   - Atmospheric conditions (altitude, temperature, pressure)
4. Click "Calculate"

### Understanding Results

- **Stability Factor (Sg)**: 
  - **> 1.5**: Stable (good)
  - **1.0 - 1.5**: Marginally stable
  - **< 1.0**: Unstable (will tumble)
- **Ballistic Coefficient (BC)**: Higher is better (less drag)
- **Sectional Density**: Weight per unit of frontal area
- **Recommended Twist Rate**: Calculated using Greenhill formula

## Exporting Bullets

### Export Formats

1. **STL (Stereolithography)**: For 3D printing
   - Use menu: `Bullet Designer` → `Export` → `Export to STL`
   - Choose save location
   - The bullet geometry will be exported as an STL file

2. **STEP (Standard for Exchange of Product Data)**: For CAD software
   - Use menu: `Bullet Designer` → `Export` → `Export to STEP`
   - Choose save location
   - The bullet geometry will be exported as a STEP file

### Export Process

1. Select the bullet object in the tree view
2. Choose export format from menu
3. Select save location and filename
4. Click "Save"
5. The geometry is exported and ready for use in other software

## Tips and Best Practices

### Design Workflow

1. **Start with Basic Dimensions**: Set diameter, length, and weight first
2. **Configure Ogive**: Choose type and caliber ratio based on your application
3. **Plan Bands Carefully**: Calculate if bands will fit before setting parameters
4. **Add Boat Tail Last**: Boat tail affects body length available for bands
5. **Use Live Preview**: Enable to see changes in real-time
6. **Check Ballistic Calculator**: Verify stability before finalizing design

### Common Design Patterns

**Match Bullet (6.5mm, 140gr)**:
- Diameter: 6.5 mm
- Land Diameter: 6.0 mm
- Length: 30-32 mm
- Weight: 140 grains
- Ogive: Tangent, 6-8 caliber ratio
- Meplat: 0.1-0.2 mm
- Bands: 2-3 bands, 1-1.5 mm each
- Base: Boat tail, 3-4 mm, 9°

**Hunting Bullet (30 cal, 180gr)**:
- Diameter: 7.62 mm
- Land Diameter: 7.0 mm
- Length: 35-40 mm
- Weight: 180 grains
- Ogive: Tangent or Secant, 7-9 caliber ratio
- Meplat: 0.2-0.5 mm
- Bands: 2-3 bands, 1.5-2 mm each
- Base: Flat or boat tail

### Parameter Relationships

- **Longer ogive** = less body length available for bands
- **Longer boat tail** = less body length available for bands
- **More bands** = need more body length
- **Larger diameter** = longer ogive (if caliber ratio stays same)
- **Higher weight** = may need longer bullet (if diameter fixed)

## Troubleshooting

### Bullet Not Generating / No Solid Created

**Problem**: No 3D geometry appears after clicking OK

**Solutions**:
1. **Check bands fit**: This is the most common cause!
   - Verify: `(num_bands × band_length) + ((num_bands-1) × spacing)` ≤ `body_length`
   - Reduce bands, band length, or spacing
   - Increase total length or reduce ogive/boat tail
2. Check console for error messages (View → Panels → Report View)
3. Verify all parameters are positive and valid
4. Ensure land diameter < groove diameter
5. Ensure meplat diameter < land diameter

### Bullet Looks Wrong

**Problem**: Bullet shape doesn't match expectations

**Solutions**:
1. Check ogive type (tangent vs secant vs elliptical)
2. Verify ogive caliber ratio (higher = longer ogive)
3. Check meplat position (should be at tip)
4. Verify band positions (should be on body, not on ogive)
5. Check boat tail configuration

### Weight Doesn't Match Target

**Problem**: Calculated weight differs from target weight

**Solutions**:
1. Weight calculation is approximate - adjust length to fine-tune
2. Check material density is correct
3. Verify all dimensions are correct
4. Note: Weight calculation assumes perfect geometry

### Can't Attach Sketch to Bullet

**Problem**: "Make independent copy" dialog appears or "Need active body" error

**Solutions**:
1. Create a PartDesign Body manually:
   - Switch to PartDesign workbench
   - Create Body (PartDesign menu → Create Body)
   - Select the bullet object
   - In Body properties, set "Base Feature" to the bullet
   - Set Body as active (double-click Body in tree)
2. Now you can attach sketches to bullet faces

### Workbench Not Appearing

**Problem**: Bullet Designer not in workbench list

**Solutions**:
1. Verify installation directory is correct
2. Check folder name is exactly "BulletDesigner" (case-sensitive)
3. Restart FreeCAD completely
4. Check FreeCAD console for import errors
5. Verify Python files are not corrupted

### Parameters Not Updating

**Problem**: Changes in task panel don't update the bullet

**Solutions**:
1. Enable "Live Preview" checkbox
2. Click "OK" to apply changes
3. Manually recompute: Select bullet → Right-click → Recompute
4. Check console for errors

## Advanced Usage

### Using with PartDesign

To use the bullet as a base feature for PartDesign operations:

1. Create your bullet using Bullet Designer
2. Switch to PartDesign workbench
3. Create a new Body (PartDesign → Create Body)
4. Select the bullet object
5. In the Body's properties panel, set "Base Feature" to the bullet object
6. Set the Body as active (double-click Body in tree view)
7. Now you can:
   - Attach sketches to bullet faces
   - Add PartDesign features (pockets, pads, etc.)
   - Create technical drawings

### Batch Operations

For multiple bullets with similar parameters:

1. Create first bullet with desired parameters
2. Use FreeCAD's "Duplicate Selection" to create copies
3. Modify parameters in each copy's properties panel
4. Recompute each bullet

### Custom Materials

To add custom materials:

1. Open Material tab in task panel
2. Select "Custom" from material dropdown
3. Enter density in g/cm³
4. Material will be saved with the bullet object

## Support

For issues, questions, or feature requests:
- GitHub Issues: [Repository URL]
- FreeCAD Forum: [Forum Link]

## Version Information

This manual is for Bullet Designer version 1.0.0 and FreeCAD 0.21+.

---

**Remember**: Always verify that bands fit on the bullet before finalizing your design. If bands don't fit, a solid will not be generated!
