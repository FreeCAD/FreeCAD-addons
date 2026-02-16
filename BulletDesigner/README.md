# Bullet Designer Workbench for FreeCAD

A comprehensive FreeCAD workbench for parametric bullet and projectile design with ballistic calculations, material database, and export capabilities.

## Features

### Core Functionality

- **Parametric Bullet Design**: Create fully parametric bullets with live updates
- **Multiple Bullet Types**: Support for land-riding, flat-base, boat-tail, and hollow-point designs
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

### Creating a Bullet

1. Switch to the "Bullet Designer" workbench
2. Click the "Create Bullet" button (or use menu: `Bullet Designer` → `Create` → `Create Bullet`)
3. The task panel opens with default parameters
4. Adjust parameters in the tabs:
   - **Basic**: Diameter, length, weight
   - **Ogive**: Type, caliber ratio, meplat diameter
   - **Bands**: Number, length, spacing
   - **Base**: Flat or boat tail configuration
   - **Material**: Material selection and density
5. Enable "Live Preview" to see changes in real-time
6. Click "OK" to create the bullet object

### Using the Ballistic Calculator

1. Select a bullet object (optional)
2. Click "Ballistic Calculator" button
3. Enter or adjust parameters:
   - Bullet dimensions (or select from document)
   - Barrel twist rate
   - Muzzle velocity
   - Atmospheric conditions
4. Click "Calculate" to see results:
   - Stability factor (should be > 1.5 for stable flight)
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

### Stability Factor

The stability factor (Sg) indicates bullet stability:
- **Sg > 1.5**: Stable (good)
- **1.0 < Sg < 1.5**: Marginally stable
- **Sg < 1.0**: Unstable

Calculated using Miller's formula with atmospheric corrections.

### Ballistic Coefficient

Estimated G1 ballistic coefficient based on:
- Sectional density
- Ogive type (form factor)
- Bullet length ratio

### Recommended Twist Rate

Calculated using Greenhill formula:
- Standard: `T = 150 * D² / L`
- High velocity (>2800 fps): Includes velocity correction

## Material Database

Built-in materials include:
- Pure Copper (8.96 g/cm³)
- Gilding Metal 95/5 (8.86 g/cm³)
- Brass 70/30 (8.53 g/cm³)
- Lead Core (11.34 g/cm³)
- Copper Alloy (8.70 g/cm³)
- Lead-Tin Alloy 95/5 (11.20 g/cm³)
- Steel (7.85 g/cm³)

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

## Limitations and Known Issues

- Cartridge design is not yet implemented (placeholder)
- Bullet library browser is not yet implemented (placeholder)
- Advanced analysis features (trajectory, drag coefficient plots) are planned
- Technical drawing generation is planned

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

## Future Enhancements

- Complete cartridge design module
- Bullet library browser with presets
- Advanced trajectory calculations
- Drag coefficient estimation
- Technical drawing generation
- Batch operations and parametric studies
- Integration with external ballistic software
- 3D printing preparation tools
