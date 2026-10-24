"""Module holding base Widget class.

Use `~pgm.gui.Widget` instead of `~pgm.gui.widget.Widget`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pyglet.graphics import Batch, Group

from ..errors import MissingAttr
from ..event_dispatcher import EventDispatcher

if TYPE_CHECKING:
	from ..scene import Scene
	from ..types import (
		Anchor,
		AnchorX,
		AnchorXDynamicPresetType,
		AnchorY,
		AnchorYDynamicPresetType,
		FontInfo,
		Point2D,
	)
	from ..window import Window


class Widget(EventDispatcher, ABC):
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
	attach_events: bool
	"""If False, don't attach events (e.g. mouse) to window"""
	window: Window | None
	"""Window widget is associated with"""
	scene: Scene | None
	"""The scene the widget is from."""

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

	def _process_font_info(self, font: FontInfo) -> FontInfo:
		"""Add default values to font info, can use scene.

		Args:
			font (FontInfo):
				The user-provided font

		Returns:
			FontInfo: The processed font info
		"""
		# Get default font
		default_font = (
			self.scene.DEFAULT_FONT_INFO if self.scene else self.DEFAULT_FONT_INFO
		)

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

	def _verify_pos(
		self, x: float | None, y: float | None, x_name: str = 'x', y_name: str = 'y'
	) -> Point2D:
		"""Verify pos is set either in arg or in scene.

		Args:
			x (float | None):
				x pos of widget
			y (float | None):
				y pos of widget
			x_name (str, optional):
				Name of arg to propagate to error.
				Defaults to 'x'.
			y_name (str, optional):
				Name of arg to propagate to error.
				Defaults to 'y'.

		Returns:
			Point2D: New xy pos
		"""
		if x is None:
			if self.scene is None:
				raise MissingAttr(self, x_name)
			if self.ID not in self.scene.WIDGET_POS:
				raise ValueError(
					f'"{self.ID}" is not in `{self.scene.__class__.__name__}.WIDGET_POS` = {self.scene.WIDGET_POS}.'
				)
			x = self.scene.WIDGET_POS[self.ID][0] * self.scene.window.width
		if y is None:
			if self.scene is None:
				raise MissingAttr(self, y_name)
			if self.ID not in self.scene.WIDGET_POS:
				raise ValueError(
					f'"{self.ID}" is not in `{self.scene.__class__.__name__}.WIDGET_POS` = {self.scene.WIDGET_POS}.'
				)
			y = self.scene.WIDGET_POS[self.ID][1] * self.scene.window.height

		return x, y

	def _verify_window(self, window: Window | None, name: str = 'window') -> Window:
		"""Verify window is set either in arg or in scene.

		Args:
			window (Window | None):
				Window of widget
			name (str, optional):
				Name of arg to propagate to error.
				Defaults to 'window'.

		Returns:
			Window: Window
		"""
		if not window and not self.scene:
			raise MissingAttr(self, name)
		return window or self.scene.window  # type: ignore[union-attr]

	def _verify_batch(self, batch: Batch | None, name: str = 'batch') -> Batch:
		"""Verify batch is set either in arg or in scene.

		Args:
			batch (Batch | None):
				Batch of widget
			name (str, optional):
				Name of arg to propagate to error.
				Defaults to 'batch'.

		Returns:
			Group: New group
		"""
		if not batch and not self.scene:
			raise MissingAttr(self, name)
		return batch or self.scene.batch  # type: ignore[union-attr]

	def _verify_group(
		self, group: Group | None, name: str = 'group', attr_name: str = 'GUI_group'
	) -> Group:
		"""Verify group is set either in args or in scene.

		Args:
			group (Group | None):
				Group of widget
			name (str, optional):
				Name of arg to propagate to error.
				Defaults to 'group'.
			attr_name (str, optional):
				If True, use scene.{attr_name} to get default group.
				Defaults to 'GUI_group'.

		Returns:
			Group: New group
		"""
		if not group and not self.scene:
			raise MissingAttr(self, name)
		return group or getattr(self.scene, attr_name)

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

	@abstractmethod
	def enable(self) -> None:
		"""Enable widget."""

	@abstractmethod
	def disable(self) -> None:
		"""Disable widget."""

	@property
	@abstractmethod
	def x(self) -> float:
		"""X position of widget's anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""

	@x.setter
	@abstractmethod
	def x(self, val: float) -> None: ...

	@property
	@abstractmethod
	def y(self) -> float:
		"""Y position of widget's anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""

	@y.setter
	@abstractmethod
	def y(self, val: float) -> None: ...

	@property
	@abstractmethod
	def pos(self) -> Point2D:
		"""Widget's anchor point."""

	@pos.setter
	@abstractmethod
	def pos(self, val: Point2D) -> None: ...

	@property
	@abstractmethod
	def anchor_x(self) -> float:
		"""X position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""

	@anchor_x.setter
	@abstractmethod
	def anchor_x(self, val: AnchorX) -> None: ...

	@property
	@abstractmethod
	def anchor_y(self) -> float:
		"""Y position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""

	@anchor_y.setter
	@abstractmethod
	def anchor_y(self, val: AnchorY) -> None: ...

	@property
	@abstractmethod
	def anchor(self) -> Point2D:
		"""Widget anchor offset.

		Can be set in px or dynamic.
		"""

	@anchor.setter
	@abstractmethod
	def anchor(self, val: Anchor) -> None: ...

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
