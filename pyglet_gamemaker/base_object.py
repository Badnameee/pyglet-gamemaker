"""."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pyglet_gamemaker.errors import MissingAttr
from pyglet_gamemaker.event_dispatcher import EventDispatcher

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group

	from pyglet_gamemaker.scene import Scene
	from pyglet_gamemaker.types import Anchor, AnchorX, AnchorY, FontInfo, Point2D
	from pyglet_gamemaker.window import Window


class BaseObject(EventDispatcher, ABC):
	"""Base class for objects, implemented basic variables and utility methods.

	Vars:
	- `.DEFAULT_FONT_SIZE`: 12pt.
	- `.DEFAULT_FONT_INFO`: (None, 12pt., 'normal')
	- `.ID`
	- `.window`
	- `.scene`

	Methods:
	- `._process_font_info()`
	- `.verify_...()`: 'pos', 'window', 'batch', 'group'
	"""

	# * CONSTS
	DEFAULT_FONT_SIZE: int = 12
	"""Default pyglet/pgm font size"""
	DEFAULT_FONT_INFO: FontInfo = None, DEFAULT_FONT_SIZE, 'normal'
	"""The default font info"""

	# * Instance vars
	ID: str
	"""The unique ID of the widget to distinguish it"""
	window: Window | None
	"""Window object is associated with"""
	scene: Scene | None
	"""The scene the object is from."""

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
		"""Verify pos is set either in arg or in scene, reterning verified pos.

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

	def _verify_window(self, window: Window | None, name: str = 'window', necessary: bool=True) -> Window | None:
		"""Verify window is set either in arg or in scene, reterning verified window.

		Args:
			window (Window | None):
				Window of widget
			name (str, optional):
				Name of arg to propagate to error.
				Defaults to 'window'.
			necessary (bool, optional):
				If True, window is necessary, if False, can return None.

		Returns:
			Window | None: New window, or None if not necessary and not found
		"""
		if not window and not self.scene:
			if necessary:
				raise MissingAttr(self, name)
			return None
		return window or self.scene.window  # type: ignore[union-attr]

	def _verify_batch(self, batch: Batch | None, name: str = 'batch') -> Batch:
		"""Verify batch is set either in arg or in scene, reterning verified batch.

		Args:
			batch (Batch | None):
				Batch of widget
			name (str, optional):
				Name of arg to propagate to error.
				Defaults to 'batch'.

		Returns:
			Batch: New batch
		"""
		if not batch and not self.scene:
			raise MissingAttr(self, name)
		return batch or self.scene.batch  # type: ignore[union-attr]

	def _verify_group(
		self, group: Group | None, name: str = 'group', attr_name: str = 'GUI_group'
	) -> Group:
		"""Verify group is set either in args or in scene, reterning verified group.

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
		if not group and not self.scene and not hasattr(self.scene, attr_name):
			raise MissingAttr(self, name)
		return group or getattr(self.scene, attr_name)

	@abstractmethod
	def _calc_anchor(self) -> None:
		"""Calculate new anchor and sync position."""

	@abstractmethod
	def enable(self) -> None:
		"""Enable object."""

	@abstractmethod
	def disable(self) -> None:
		"""Disable object."""

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
