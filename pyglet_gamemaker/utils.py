"""Holds general utility functions used internally by pyglet-gamemaker."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .gui.widget import Widget
	from .scene import Scene
	from .types import FontInfo, Point2D


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

	# Set weight if weight was None
	if new[2] is None:
		new[2] = 'normal'

	return tuple(new)  # type: ignore[return-value]


def get_scene_widget_pos(
	widget: Widget, ID: str, x: float | None, y: float | None, scene: Scene | None
) -> Point2D:
	"""Attempt to extract the position of widget from scene.WIDGET_POS. If x/y are set then nothing happens.

	Args:
		widget (Widget):
			Widget object (for displaying class name on error)
		ID (str):
			ID of widget
		x (float | None):
			x pos of widget
		y (float | None):
			y pos of widget
		scene (Scene | None):
			Scene passed into widget

	Returns:
		Point2D: New xy pos
	"""
	if x is None:
		if scene is None:
			raise TypeError(
				f'"{widget.__class__.__name__}()" must receive an x value or a scene to extract widget position from.'
			)
		if ID not in scene.WIDGET_POS:
			raise ValueError(f'"{ID}" is not in {scene.WIDGET_POS}.')
		x = scene.WIDGET_POS[ID][0]
	if y is None:
		if scene is None:
			raise TypeError(
				f'"{widget.__class__.__name__}()" must receive an y value or a scene to extract widget position from.'
			)
		if ID not in scene.WIDGET_POS:
			raise ValueError(f'"{ID}" is not in {scene.WIDGET_POS}.')
		y = scene.WIDGET_POS[ID][1]

	return x, y
