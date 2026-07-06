from __future__ import annotations

from typing import TYPE_CHECKING

from . import errors, event_dispatcher, resources, types
from .resources import DefaultResources
from .scene import Scene
from .window import Window

if TYPE_CHECKING:
	from .types import FontInfo


def pad_font_info(font: FontInfo, default_font: FontInfo) -> FontInfo:
	"""Clean up font info to be uniform size (using default values).

	Args:
		font (FontInfo):
			The user-provided font
		default_font (FontInfo):
			The default font values

	Returns:
		FontInfo: The cleaned up font info
	"""
	# Applies defaults to font info if needed
	new = []
	for i, default in enumerate(default_font):
		# In range, use default is no data in user-given info
		if i < len(font):
			new.append(font[i] or default)
		# Out of range, use default
		else:
			new.append(default)
	return tuple(new)  # type: ignore[return-value]
