"""Stores all custom types used in pgm.

- Point2D: (float, float) - for 2D points
- FontInfo: (type, size, weight). See `pyglet.text.Weight` for weight values.
- Axis: Either 'x' or 'y'
- AnchorXDynamicType: The possible **values** of the dynamic anchor on x-axis
- AnchorYDynamicType: The possible **values** of the dynamic anchor on y-axis
- AnchorXDynamicType: Only the dynamic anchor on x-axis
- AnchorYDynamicType: Only the dynamic anchor on y-axis
- AnchorX: Static, dynamic, or true-dynamic anchor on x-axis
- AnchorY: Static, dynamic, or true-dynamic anchor on y-axis
- Anchor: (`.AnchorX`, `.AnchorY`)
- Color: Enum that stores a bunch of preset colors. See `~pgm.colors` for color values.
- Eventhandler: Type for user-made event handlers
- YAMLDict: Type for parsed YAML files
- YAMLIterable: Type for iterable YAML values for custom parsing
- YAMLValidationMode: Types of validation currently supposed by custom YAML parser
- FLOAT_REGEX: Reggular expression used to check if string is simple float
- Color: Type used for RGB(A) colors
- Weight: Possible weight values (taken from pyglet)
- TriggerSubType: All possible subtypes for hitboxes
- ButtonStatus: All possible button pressing statuses
- TriggerStatus: A bit flag for trigger statuses
- TriggerInteractType: All types of trigger interaction types
"""

from __future__ import annotations

from enum import Enum, Flag, auto

__all__ = [
	'Point2D',
	'FontInfo',
	'Axis',
	'AnchorXDynamicValues',
	'AnchorYDynamicValues',
	'AnchorXDynamicType',
	'AnchorYDynamicType',
	'AnchorX',
	'AnchorY',
	'Anchor',
	'EventHandler',
	'YAMLDict',
	'YAMLIterable',
	'YAMLValidationMode',
	'FLOAT_REGEX',
	'Color',
	'TriggerSubType',
	'ButtonStatus',
	'TriggerStatus',
	'TriggerInteractType',
]


from collections.abc import Callable
from typing import Any, Literal, Protocol, runtime_checkable

Point2D = tuple[float, float]
FontInfo = tuple[str | None, int | None] | tuple[str | None, int | None, str | None]
Axis = Literal['x', 'y']
AnchorXDynamicValues = 'left', 'center', 'right'
AnchorYDynamicValues = 'top', 'bottom', 'center'
AnchorXDynamicType = Literal['left', 'center', 'right']
AnchorYDynamicType = Literal['top', 'bottom', 'center']
AnchorX = AnchorXDynamicType | str | float
AnchorY = AnchorYDynamicType | str | float
Anchor = tuple[AnchorX, AnchorY]
EventHandler = Callable[..., Any]
YAMLDict = dict[Any, Any] | None
YAMLIterable = dict[Any, Any] | list[Any]
YAMLValidationMode = Literal['Anim']
FLOAT_REGEX = r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
Color = tuple[int, int, int] | tuple[int, int, int, int]


class TriggerSubType(Enum):
	"""All possible subtypes for hitboxes."""

	NONE = auto()
	RECT = auto()
	CIRCLE = auto()
	POINT = auto()


class ButtonStatus(Enum):
	"""All possible button pressing statuses."""

	UNPRESSED = auto()
	HOVER = auto()
	PRESSED = auto()


class TriggerStatus(Flag):
	"""All possible trigger statuses, as a bit flag.

	`.MOUSE_NOHIT` or `.MOUSE_HIT`: Whether mouse is overlapping trigger
	`.TRIGGER_NOHIT` or `.TRIGGER_HIT`: Whether anything is overlapping trigger
	"""

	MOUSE_NOHIT = auto()
	MOUSE_HIT = auto()
	TRIGGER_NOHIT = auto()
	TRIGGER_HIT = auto()


class TriggerInteractType(Enum):
	"""All possible trigger collision types."""

	NONE = auto()
	OVERLAP = auto()
	COLLIDE = auto()


@runtime_checkable
class HasHitbox(Protocol):
	"""Class Protocol for an object with a trigger attribute."""

	trigger: Trigger


@runtime_checkable
class HasID(Protocol):
	"""Class Protocol for an object with an ID attribute."""

	ID: str


from .shapes.trigger import Trigger
