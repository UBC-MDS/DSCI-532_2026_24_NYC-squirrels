import pytest
from utils import color_for_fur, color_for_shift

def test_color_mapping_logic():
    """Verifies that color mapping functions return correct hex codes for known inputs and handle unknown inputs with a safe fallback."""
    assert color_for_fur("Gray") == "#808080"
    assert color_for_shift("AM") == "#D9C27A"
    
    # Test edge case: Unknown/Unexpected input
    # This ensures the map markers don't disappear if data is messy
    assert color_for_fur("Neon-Green") == "#6E8BAA" 
    assert color_for_shift(None) == "#A0A0A0"