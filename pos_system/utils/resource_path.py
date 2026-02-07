"""
Resource Path Utility for PyInstaller Bundled Applications

This module provides a helper function to correctly resolve file paths
for both development (script mode) and production (PyInstaller EXE mode).

When PyInstaller bundles the application, it extracts files to a temporary
directory and sets sys._MEIPASS to that location. This function automatically
handles the path resolution for both scenarios.
"""

import os
import sys


def resource_path(relative_path):
    """
    Get the absolute path to a resource file.
    
    This function works for both development and PyInstaller bundled modes:
    - In development: Uses the directory containing this file as the base
    - In PyInstaller EXE: Uses sys._MEIPASS (the temporary extraction folder)
    
    Args:
        relative_path (str): The relative path to the resource file
                            (e.g., 'assets/logos/billLogo.png')
    
    Returns:
        str: The absolute path to the resource file
    
    Example:
        >>> logo_path = resource_path('assets/logos/billLogo.png')
        >>> # Returns: 'C:/path/to/assets/logos/billLogo.png' (development)
        >>> # Returns: 'C:/Users/.../temp/assets/logos/billLogo.png' (EXE)
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Development mode: use the project root directory
        # Go up two levels from utils/resource_path.py to get to pos_system/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)
