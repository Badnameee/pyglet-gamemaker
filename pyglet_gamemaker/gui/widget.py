"""Module holding base Widget class.

Use `~pgm.gui.Widget` instead of `~pgm.gui.widget.Widget`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pyglet_gamemaker.base_object import BaseObject

if TYPE_CHECKING:
	from ..types import (
		Anchor,
		AnchorXDynamicPresetType,
		AnchorYDynamicPresetType,
		FontInfo,
		Point2D,
	)


class Widget(BaseObject, ABC):
	"""The base class for a Widget. Inherit to create own widget.

	NOTE: Must call `~pgm.gui.Widget.register_events()` for event handler names to be registered.

	Widgets support 3 types of anchor types:
	- Static - A static pixel value that does not scale
	- Dynamic Preset - Specific dynamic values with preset scales (e.g. **'left', 'center', 'right'**)
		- See `~pgm.types.AnchorXDynamicPresetValues` and `~pgm.types.AnchorYDynamicPresetValues` for all values.
	- Dynamic - A float representing the ratio of width/height the anchor should be
		- e.g. **('0.5', '0.5')** is equivalent to a center anchor

	Required Methods:
	- `._calc_anchor()`: Calculate the static anchor with raw_anchor
	- `.enable()`: Enable logic of widget (not rendering)
	- `.disable()`: Disable logic of widget (not rendering)

	Required Properties:
	- `.x`
	- `.y`
	- `.pos`
	- `.anchor_x`
	- `.anchor_y`
	- `.anchor`
	- `.width`
	- `.height`
	- `.scale`

	Optional Methods:
	- `_on_mouse_...`: `...press()`, `...release()`, `...motion()`, `...drag()`
		- Mouse events to attach when creating widget.

	Optional Vars:
	- `.EVENT_TYPES`: Put event names that may be dispatched
	"""

	# * CONSTS
	CONVERT_DYNAMIC: dict[
		AnchorXDynamicPresetType | AnchorYDynamicPresetType, float
	] = {
		'left': 0,
		'bottom': 0,
		'center': 0.5,
		'right': 1,
		'top': 1,
	}
	"""Converts dynamic anchor to multiplier"""
	DEFAULT_FONT_SIZE: int = 12
	"""Default pyglet/pgm font size"""
	DEFAULT_FONT_INFO: FontInfo = None, DEFAULT_FONT_SIZE, 'normal'
	"""The default font info,"""

	# * Instance vars
	ID: str
	"""The unique ID of the widget to distinguish it"""
	raw_anchor: Anchor = 0, 0
	"""Holds the raw anchor position (static + dynamic) of widget"""
	initial_pos: Point2D = 0, 0
	"""Original (*unanchored* AND *unrotated*) position of widget"""
	initial_anchor: Anchor = 0, 0
	"""Original anchor offset of widget"""
	dispatch: bool
	"""If False, don't dispatch events to handlers"""
	mouse_detection: bool
	"""If False, don't attach events (e.g. mouse) to window"""

	# * Property vars
	_pos: Point2D = 0, 0
	_anchor: Point2D = 0, 0
	_scale: float = 1

	def offset(self, val: Point2D) -> None:
		"""Add offset to widget."""
		self.x += val[0]
		self.y += val[1]

	def set_offset(self, val: Point2D) -> None:
		"""Set the offset of widget."""
		self.pos = self.initial_pos[0] + val[0], self.initial_pos[1] + val[1]

	def reset(
		self,
		pos: bool = True,
		anchor: bool = True,
		scale: bool = True,
	) -> None:
		"""Reset widget to initial state. Args control which parts get reset.

		Args:
			pos (bool, optional):
				If True, reset the position.
				Defaults to True.
			anchor (bool, optional):
				If True, reset the anchoring.
				Defaults to True.
			scale (bool, optional):
				If True, reset the scale.
				Defaults to True.
		"""
		if pos:
			self.pos = self.initial_pos
		if anchor:
			self.anchor = self.initial_anchor
		if scale:
			self.scale = 1

	def bind_mouse(self) -> None:
		"""Bind mouse events to widget."""
		self.window.push_handlers(  # type: ignore[union-attr]
			on_mouse_press=self._on_mouse_press,
			on_mouse_release=self._on_mouse_release,
			on_mouse_motion=self._on_mouse_motion,
			on_mouse_drag=self._on_mouse_drag,
		)

	@abstractmethod
	def _calc_anchor(self) -> None:
		"""Calculate new anchor and sync position."""

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not implement "._on_mouse_press()" method.'
		)

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not implement "._on_mouse_release()" method.'
		)

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not implement "._on_mouse_motion()" method.'
		)

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not implement "._on_mouse_drag()" method.'
		)

	@property
	@abstractmethod
	def width(self) -> int | float:
		"""Width of widget."""

	@property
	@abstractmethod
	def height(self) -> int | float:
		"""Height of widget."""

	@property
	@abstractmethod
	def scale(self) -> float:
		"""Scale of widget."""

	@scale.setter
	@abstractmethod
	def scale(self, val: float) -> None: ...
