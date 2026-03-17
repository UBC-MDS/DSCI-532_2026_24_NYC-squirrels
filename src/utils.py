def color_for_fur(fur: str) -> str:
    """Returns a hex color string based on the squirrel's primary fur color."""
    palette = {
        "Gray": "#808080",
        "Cinnamon": "#B87333",
        "Black": "#1F1F1F",
        "Unknown": "#4AA3DF",
    }
    return palette.get(fur, "#6E8BAA")

def color_for_shift(shift: str) -> str:
    """Returns a hex color string based on the observation shift."""
    palette = {
        "AM": "#D9C27A",
        "PM": "#5B87D9"
    }
    return palette.get(shift, "#A0A0A0")