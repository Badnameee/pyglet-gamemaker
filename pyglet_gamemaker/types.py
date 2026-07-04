"""Stores all custom types used in library.

- Point2D: (float, float) - for 2D points
- FontInfo: (type, size, weight)
- ButtonStatus: A status for button widgets. See `~pgm.gui.button.Button`
- Axis: Either 'x' or 'y'
- AnchorXDynamicType: The possible **values** of the dynamic anchor on x-axis
- AnchorYDynamicType: The possible **values** of the dynamic anchor on y-axis
- AnchorXDynamicType: Only the dynamic anchor on x-axis
- AnchorYDynamicType: Only the dynamic anchor on y-axis
- AnchorX: Dynamic or static anchor on x-axis
- AnchorY: Dynamic or static anchor on y-axis
- Anchor: (`.AnchorX`, `.AnchorY`)
- Color: Enum that stores a bunch of preset colors. See `~pgm.types.Color`
- Eventhandler: Type for user-made event handlers
- YAMLDict: Type for parsed YAML files
- YAMLIterable: Type for iterable YAML values for custom parsing
- YAMLValidationMode: Types of validation currently supposed by custom YAML parser
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Literal, SupportsFloat

from pyglet.text import Weight

Point2D = tuple[float, float]
FontInfo = tuple[str | None, int | None] | tuple[str | None, int | None, Weight | None]
ButtonStatus = Literal['Unpressed', 'Hover', 'Pressed']
Axis = Literal['x', 'y']
AnchorXDynamicValues = "left", "center", "right"
AnchorYDynamicValues = "top", "bottom", "center"
AnchorXDynamicType = Literal["left", "center", "right"]
AnchorYDynamicType = Literal["top", "bottom", "center"]
AnchorX = AnchorXDynamicType | SupportsFloat | float
AnchorY = AnchorYDynamicType | SupportsFloat | float
Anchor = tuple[AnchorX, AnchorY]
EventHandler = Callable[..., Any]
YAMLDict = dict[Any, Any] | None
YAMLIterable = dict[Any, Any] | list[Any]
YAMLValidationMode = Literal['Anim']
FLOAT_REGEX = r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'


class Color(Enum):
	"""A bunch of colors in the form (int, int, int, int)."""

	RED = 255, 0, 0, 255
	ORANGE = 255, 167, 0, 255
	YELLOW = 255, 255, 0, 255
	GREEN = 0, 255, 0, 255
	CYAN = 0, 255, 255, 255
	BLUE = 0, 0, 255, 255
	PURPLE = 167, 0, 255, 255
	MAGENTA = 255, 0, 255, 255
	WHITE = 255, 255, 255, 255
	GRAY = 128, 128, 128, 255
	BLACK = 0, 0, 0, 255
