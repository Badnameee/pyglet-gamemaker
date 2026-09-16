from __future__ import annotations

from typing import TYPE_CHECKING

from . import colors, errors, event_dispatcher, resources, types, utils
from .camera import Camera
from .resources import DefaultResources
from .scene import Scene
from .window import Window

if TYPE_CHECKING:
	from .types import Color, ColorType, FontInfo
