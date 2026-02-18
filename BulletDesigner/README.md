# Bullet Designer Workbench for FreeCAD

A comprehensive FreeCAD workbench for parametric bullet and projectile design with ballistic calculations, material database, and export capabilities.

![Bullet Designer Workbench](Resources/screenshots/screenshot.png)

## Quick Links

- **[User Manual](USER_MANUAL.md)** - Complete guide with step-by-step instructions
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)

## Features

### Core Functionality

- **Parametric Bullet Design**: Create fully parametric bullets with live updates
- **Multiple Bullet Types**: Support for land-riding, flat-base, boat-tail, and hollow-point designs ( hole must be added manually)
- **Driving Bands**: Configurable number, spacing, and dimensions for driving bands
- **Ogive Profiles**: Three ogive types (tangent, secant, elliptical) with customizable caliber ratios
- **Ballistic Calculations**: 
  - Stability factor (Miller's formula)
  - Ballistic coefficient estimation (G1)
  - Sectional density
  - Recommended twist rate (Greenhill)
- **Material Database**: Built-in materials (copper, lead, brass, gilding metal) with customizable properties
- **Export Capabilities**: Export to STEP and STL formats for manufacturing

### User Interface

- **Task Panel**: Comprehensive parameter editing with tabbed interface
- **Live Preview**: Real-time geometry updates as parameters change
- **Ballistic Calculator**: Standalone calculator dialog for stability analysis
- **Preferences**: Customizable defaults and units

##  Important: Bands Must Fit on Bullet

**CRITICAL**: Driving bands must fit within the body length, or **a solid will NOT be generated**.

The body length is: `Total Length - Ogive Length - Boat Tail Length`

Where Ogive Length = `(Ogive Caliber Ratio × Diameter) / 2`

Total band space needed = `(Number of Bands × Band Length) + ((Number of Bands - 1) × Band Spacing)`

**Rule**: Total Band Space ≤ Body Length

If bands don't fit, reduce bands/band length/spacing, increase total length, or reduce ogive/boat tail length.

See the [User Manual](USER_MANUAL.md#important-constraints) for detailed explanation and examples.

## Visual Appearance: Sectional Lines on Ogive

You may notice visible sectional lines (segments) on the ogive (nose) section of the bullet. This is **normal and expected** behavior.

### Why Ogive Sectional Lines Appear

The ogive is created by revolving a 2D profile around the Z-axis. The ogive profile consists of line segments connecting points along the curved ogive shape:

- The ogive curve (tangent, secant, or elliptical) is approximated using multiple line segments
- One of these segments is **always positioned at the middle** of the ogive (at 50% of the ogive length)
- These segments are necessary to accurately represent the mathematical curves that define the ogive shape

When revolved, these line segments create visible sectional lines on the ogive surface in the 3D view.

### Do Sectional Lines Affect Functionality?

**No, the visible sectional lines do NOT affect:**

- **Sectional views**: Cross-sections and cut views work perfectly - the lines are purely visual
- **Geometry accuracy**: The solid geometry is mathematically correct and precise
- **Export quality**: Exported STL and STEP files maintain full geometric accuracy
- **Measurements**: All dimensions and calculations are accurate
- **3D printing**: The exported geometry is suitable for manufacturing

The sectional lines are a **visual artifact** of how FreeCAD displays revolved surfaces created from line segments. The underlying solid geometry is continuous and accurate. When you create sectional views or export the bullet, FreeCAD uses the actual solid geometry, not the visual representation with lines.

### Technical Note

The ogive is generated with multiple points (typically 20+ points depending on ogive length), ensuring one point is always at the exact middle (t=0.5) for accurate representation. These points are connected with line segments, which when revolved create the visible sectional lines you see.

## Screenshots

![Bullet Designer](Resources/screenshots/screenshot.png)
*Bullet Designer workbench and bullet creation*

![Bullet Designer](Resources/screenshots/screenshot2.png)
*Parametric bullet design and task panel*

## Installation

### Method 1: FreeCAD Addon Manager (Recommended)

1. Open FreeCAD
2. Go to `Tools` → `Addon Manager`
3. Search for "Bullet Designer"
4. Click `Install`

### Method 2: Manual Installation

1. Clone or download this repository
2. Copy the `BulletDesigner` folder to your FreeCAD Mods directory:
   - **Linux**: `~/.FreeCAD/Mod/`
   - **Windows**: `C:\Users\<username>\AppData\Roaming\FreeCAD\Mod\`
   - **macOS**: `~/Library/Preferences/FreeCAD/Mod/`
3. Restart FreeCAD
4. Select "Bullet Designer" from the workbench dropdown

## Usage

For detailed step-by-step instructions, see the **[User Manual](USER_MANUAL.md)**.

### Creating a Bullet

1. Switch to the "Bullet Designer" workbench
2. Click the "Create Bullet" button (or use menu: `Bullet Designer` → `Create` → `Create Bullet`)
3. The task panel opens with default parameters
4. Adjust parameters in the tabs:
   - **Basic**: Diameter, length, weight
   - **Ogive**: Type, caliber ratio, meplat diameter
   - **Bands**: Number, length, spacing (** Ensure bands fit!**)
   - **Base**: Flat or boat tail configuration
   - **Material**: Material selection and density
5. Enable "Live Preview" to see changes in real-time
6. **Verify bands fit** (see warning above)
7. Click "OK" to create the bullet object

### Using the Ballistic Calculator

1. Select a bullet object (optional)
2. Click "Ballistic Calculator" button
3. Enter or adjust parameters:
   - Bullet dimensions (or select from document)
   - Barrel twist rate
   - Muzzle velocity
   - Atmospheric conditions
4. Click "Calculate" to see results:
   - Stability factor (Sg ≥ 1.8 for monolithic copper/brass, Sg ≥ 1.5 for lead-core)
   - Ballistic coefficient
   - Sectional density
   - Recommended twist rate

### Exporting Bullets

1. Select a bullet object in the tree view
2. Use menu: `Bullet Designer` → `Export` → `Export to STL` or `Export to STEP`
3. Choose save location and filename
4. The geometry will be exported for use in other CAD software or 3D printing

## Parameter Reference

### Basic Dimensions

- **Diameter**: Overall bullet diameter (groove diameter) in mm
- **Land Diameter**: Land riding diameter (must be < groove diameter) in mm
- **Length**: Total bullet length in mm
- **Weight**: Target weight in grains

### Ogive Settings

- **Ogive Type**: 
  - **Tangent**: Standard tangent ogive (most common)
  - **Secant**: More aggressive secant ogive
  - **Elliptical**: Optimal aerodynamic shape
- **Ogive Caliber Ratio**: Length of ogive in calibers (typically 5-12)
- **Meplat Diameter**: Tip diameter in mm

### Driving Bands

- **Number of Bands**: 0-6 driving bands
- **Band Length**: Length of each band in mm
- **Band Spacing**: Space between bands in mm
- **Band Diameter**: Usually equals groove diameter

**CRITICAL**: Bands must fit within the body length (total length minus ogive and boat tail), or a solid will not be generated. See [Important Constraints](#-important-bands-must-fit-on-bullet) above.

### Base Configuration

- **Base Type**: 
  - **Flat**: Traditional flat base
  - **Boat Tail**: Tapered base for reduced drag
- **Boat Tail Length**: Length of taper in mm
- **Boat Tail Angle**: Taper angle in degrees (typically 8-10°)

### Material Properties

- **Material**: Select from database or use custom
- **Density**: Material density in g/cm³ (auto-updated from material selection)

## Ballistic Calculations

### Stability Factor (Miller's Formula)

The stability factor (Sg) indicates bullet stability using Miller's formula with modified thresholds for monolithic bullets.

**FORMULA:**
```
Sg = (30 × m × (V/2800)^(1/3)) / ((T/d)² × d³ × l × (1 + l²))
```

**WHERE:**
- `m` = bullet mass (grains)
- `V` = muzzle velocity (ft/sec)
- `T` = twist rate (inches per turn)
- `d` = effective bullet diameter (inches) - **use bearing band diameter for land-riding bullets**
- `l` = bullet length in calibers = L/d
- `L` = bullet length (inches)

**STABILITY THRESHOLDS:**
- **Monolithic copper/brass bullets**: Sg ≥ 1.8 (stable)
- **Lead-core bullets**: Sg ≥ 1.5 (stable)
- **1.0 < Sg < threshold**: Marginally stable
- **Sg < 1.0**: Unstable

**CRITICAL:** Use **effective diameter** (diameter at bearing bands) for land-riding/banded bullets, not nominal diameter. The effective diameter is the groove diameter where the bands engage the rifling.

**Atmospheric Corrections:**
- Temperature correction: `√((T_F + 459.67) / 518.67)`
- Pressure correction: `√(P_inHg / 29.92)`
- Velocity correction: `(V_fps / 2800)^(1/3)`

**Sources:** Litz, Applied Ballistics; Courtney & Courtney (2012)

### Ballistic Coefficient (G1)

Estimated G1 ballistic coefficient based on:
- Sectional density: `SD = Weight (lbs) / Diameter² (inches)`
- Form factor (based on ogive type):
  - Tangent: 0.85
  - Secant: 0.80
  - Elliptical: 0.75
- Length corrections for long bullets (>4:1 ratio)
- Meplat and boat tail corrections

**Formula:** `BC = SD / Form_Factor`

### Sectional Density

**Formula:** `SD = Weight (lbs) / Diameter² (inches)`

Where:
- Weight in pounds = `Weight (grains) / 7000`
- Diameter in inches = `Diameter (mm) / 25.4`

Sectional density is a dimensionless number indicating the bullet's ability to retain velocity and energy.

### Weight and Volume Calculations

**Volume from Weight:**
```
Volume (mm³) = (Weight (grains) / 15.4323584) / Density (g/cm³) × 1000
```

**Weight from Volume:**
```
Weight (grains) = Volume (mm³) / 1000 × Density (g/cm³) × 15.4323584
```

### Ogive Geometry

**Radius of Curvature (Circular Arc Ogive):**
```
ρ = (R² + L²) / (2L)
```

Where:
- `ρ` = radius of curvature (mm)
- `R` = bullet radius at junction (mm)
- `L` = ogive length (mm)

**Ogive Length:**
```
L = (Ogive Caliber Ratio × Diameter) / 2
```

### Recommended Twist Rate

**For Monolithic Copper/Brass Bullets:**
```
T_required = d × √[(30 × m) / (1.8 × d³ × l × (1 + l²))] × (2800/V)^(1/6)
```

**For Lead-Core Bullets (Greenhill Formula):**
- Standard (V ≤ 2800 fps): `T = 150 × D² / L`
- High velocity (V > 2800 fps): `T = 150 × D² / L × √(V/2800)`

Where:
- `T` = twist rate (inches per turn)
- `D` = diameter (inches)
- `L` = length (inches)
- `m` = mass (grains)
- `V` = velocity (fps)
- `d` = effective diameter (inches)
- `l` = length in calibers

## Material Database

Built-in materials with densities:

| Material | Density (g/cm³) | Description |
|----------|----------------|-------------|
| **Pure Copper** | 8.96 | Pure copper, excellent for monolithic bullets |
| **Gilding Metal (95/5)** | 8.86 | 95% copper, 5% zinc - common bullet jacket material |
| **Brass (70/30)** | 8.53 | 70% copper, 30% zinc - harder than gilding metal |
| **Copper Alloy** | 8.70 | General purpose copper alloy |
| **Lead Core** | 11.34 | Pure lead - traditional bullet core material |
| **Jacketed Lead Core** | 10.8 | Jacketed bullet with lead core - typical FMJ construction (gilding metal jacket + lead core) |
| **Lead-Tin Alloy (95/5)** | 11.20 | 95% lead, 5% tin - common cast bullet alloy |
| **Steel** | 7.85 | Steel core for armor-piercing bullets |

**Material Selection for Stability Calculations:**
- Materials with density **7.0-9.5 g/cm³** are treated as **monolithic copper/brass** (stability threshold: Sg ≥ 1.8)
- Materials with density **> 10 g/cm³** are treated as **lead-core** bullets (stability threshold: Sg ≥ 1.5)

Custom materials can be added through the material selection interface.

## File Structure

```
BulletDesigner/
├── Init.py                 # Workbench initialization
├── InitGui.py             # GUI initialization
├── package.xml            # Addon metadata
├── README.md              # This file
├── LICENSE                # MIT License
├── Commands/              # Command implementations
│   ├── CreateBullet.py
│   ├── BallisticCalculator.py
│   ├── CreateCartridge.py
│   ├── BulletLibrary.py
│   └── ExportTools.py
├── Objects/               # Feature objects
│   ├── BulletFeature.py
│   └── ViewProviders.py
├── Gui/                   # GUI components
│   ├── BulletTaskPanel.py
│   └── PreferencesPage.py
├── Utils/                 # Utilities
│   ├── Calculations.py
│   ├── MaterialDatabase.py
│   └── GeometryHelpers.py
├── Resources/
│   ├── icons/             # SVG icons
│   └── ui/               # UI files (future)
└── Data/                  # Data files
    ├── materials.json
    └── bullet_templates.json
```

## Requirements

- FreeCAD 0.21 or later
- Python 3.8 or later
- PySide2 (included with FreeCAD)

## Documentation

- **[User Manual](USER_MANUAL.md)**: Complete guide with step-by-step instructions, parameter explanations, troubleshooting, and best practices
- **README.md**: This file - overview and quick reference

## Limitations and Known Issues

- Cartridge design is not yet implemented (placeholder)
- Bullet library browser is not yet implemented (placeholder)
- Advanced analysis features (trajectory, drag coefficient plots) are planned
- Technical drawing generation is planned
- **Bands must fit on bullet**: If bands don't fit within body length, solid generation will fail (this is by design to prevent invalid geometry)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This workbench is licensed under the MIT License. See LICENSE file for details.

## Credits

Developed for the FreeCAD community. Uses standard ballistic formulas (Greenhill, Miller) and FreeCAD's Part module for geometry generation.

## Support

For issues, questions, or feature requests, please use the GitHub issue tracker.

## Version History

### Version 1.0.0 (2025-02-16)
- Initial release
- Parametric bullet creation
- Ballistic calculator
- Material database
- Export to STL/STEP
- Basic preferences

## Possible future Enhancements

- Complete cartridge design module
- Bullet library browser with presets


