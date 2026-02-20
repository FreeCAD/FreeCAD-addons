"""
Material database for bullet design.

This module loads and manages material properties for bullet design.
"""

import json
import os
import FreeCAD as App
from typing import Dict, List, Optional


class MaterialDatabase:
    """
    Database of bullet materials with properties.
    """
    
    def __init__(self):
        """Initialize the material database."""
        self.materials = {}
        self._load_materials()
    
    def _load_materials(self):
        """Load materials from JSON file."""
        try:
            wb_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            materials_file = os.path.join(wb_path, "Data", "materials.json")
            
            if os.path.exists(materials_file):
                with open(materials_file, 'r') as f:
                    data = json.load(f)
                    for material in data.get("materials", []):
                        name = material.get("name")
                        if name:
                            self.materials[name] = {
                                "name": name,
                                "density": material.get("density", 8.86),
                                "color": material.get("color", [0.8, 0.5, 0.2]),
                                "description": material.get("description", "")
                            }
            else:
                App.Console.PrintWarning(
                    f"Materials file not found: {materials_file}\n"
                )
                # Use default materials
                self._create_default_materials()
        except Exception as e:
            App.Console.PrintError(f"Error loading materials: {e}\n")
            self._create_default_materials()
    
    def _create_default_materials(self):
        """Create default materials if file cannot be loaded."""
        default_materials = [
            {
                "name": "Gilding Metal (95/5)",
                "density": 8.86,
                "color": [0.80, 0.50, 0.20],
                "description": "95% copper, 5% zinc"
            },
            {
                "name": "Pure Copper",
                "density": 8.96,
                "color": [0.72, 0.45, 0.20],
                "description": "Pure copper"
            },
            {
                "name": "Lead Core",
                "density": 11.34,
                "color": [0.40, 0.40, 0.40],
                "description": "Pure lead"
            }
        ]
        
        for material in default_materials:
            self.materials[material["name"]] = material
    
    def get_material(self, name: str) -> Optional[Dict]:
        """
        Get material properties by name.
        
        Args:
            name: Material name
            
        Returns:
            Material dictionary or None if not found
        """
        return self.materials.get(name)
    
    def get_material_names(self) -> List[str]:
        """
        Get list of all material names.
        
        Returns:
            List of material names
        """
        return sorted(self.materials.keys())
    
    def get_density(self, material_name: str) -> float:
        """
        Get density for a material.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Density in g/cm³, or default 8.86 if not found
        """
        material = self.materials.get(material_name)
        if material:
            return material["density"]
        return 8.86  # Default to gilding metal density
    
    def get_color(self, material_name: str) -> List[float]:
        """
        Get color for a material.
        
        Args:
            material_name: Name of the material
            
        Returns:
            RGB color tuple [R, G, B] in range 0-1
        """
        material = self.materials.get(material_name)
        if material:
            return material["color"]
        return [0.8, 0.5, 0.2]  # Default copper color
    
    def add_custom_material(
        self,
        name: str,
        density: float,
        color: List[float],
        description: str = ""
    ):
        """
        Add a custom material to the database.
        
        Args:
            name: Material name
            density: Density in g/cm³
            color: RGB color [R, G, B] in range 0-1
            description: Optional description
        """
        self.materials[name] = {
            "name": name,
            "density": density,
            "color": color,
            "description": description
        }


# Global instance
_material_db = None


def get_material_database() -> MaterialDatabase:
    """
    Get the global material database instance.
    
    Returns:
        MaterialDatabase instance
    """
    global _material_db
    if _material_db is None:
        _material_db = MaterialDatabase()
    return _material_db
