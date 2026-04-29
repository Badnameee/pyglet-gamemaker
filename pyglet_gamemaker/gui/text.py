"""Module holding Text widget class.

Use `~pgm.gui.Text` instead of `~pgm.gui.text.Text`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.text import Label

from ..types import Color
from .widget import Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group

	from ..scene import Scene
	from ..types import (
		Anchor,
		AnchorX,
		AnchorY,
		FontInfo,
		Point2D,
	)
	from ..window import Window


class Text(Label, Widget):
	"""A 2D label with scrolling and custom anchor support. Supports anchoring with specific pixel values or dynamic.

	Dynamic Anchors:
	- `AnchorX`: 'left', 'center', 'right'
	- `AnchorY`: 'bottom', 'center', 'top'

	Does not support rotating around anchor point (rotates about bottomleft)

	Use kwargs to attach event handlers.
	"""

	_text: str = ''
	_pos: Point2D = 0, 0

	font_info: FontInfo = None, None, None
	"""The font information"""

	def __init__(
		self,
		ID: str,
		text: str,
		x: float,
		y: float,
		window: Window,
		scene: Scene,
		batch: Batch,
		group: Group,
		anchor: Anchor = (0, 0),
		font_info: FontInfo = (None, None, None),
		color: Color = Color.WHITE,
	) -> None:
		"""Create a text label.

		Args:
			ID (str):
				Name/ID of widget
			text (str):
				Label text
			x (float):
				Anchored x position
			y (float):
				Anchored y position
			window (Window):
				Window for attaching self
			scene (Scene):
				The scene the widget is from. None if widget is a template.
			batch (Batch):
				Batch for rendering
			group (Group):
				Group for rendering
			anchor (Anchor, optional):
				Anchor position. See `~pgm.gui.Text` for more info on anchor values.
				Defaults to (0, 0).
			font_info (FontInfo, optional):
				Font name, size, (and optional weight).
				Defaults to (None, None, None).
			color (Color, optional):
				Color of text.
				Defaults to Color.WHITE.
		"""
		# Applies defaults to font info if needed
		new_font_info = []
		for i, default in enumerate(self.DEFAULT_FONT_INFO):
			# In range, choose default is info is None
			if i < len(font_info):
				new_font_info.append(font_info[i] or default)
			# Out of range, choose default
			else:
				new_font_info.append(default)
		self.font_info = tuple(new_font_info)  # type: ignore[assignment]

		super().__init__(
			text,
			x,
			y,
			0,
			font_name=self.font_info[0],
			font_size=self.font_info[1],
			color=color.value,
			batch=batch,
			group=group,
			weight=self.font_info[2] if self.font_info[2] is not None else 'normal',  # type: ignore[misc] # Guaranteed 3 items long by here
		)
		Widget.__init__(self)

		self.window, self.scene = window, scene
		self.ID = ID
		self.start_anchor = self.anchor = anchor
		self.start_pos = self.pos = x, y
		self.text = text

	def reset(self) -> None:  # noqa: D102
		super().reset()
		self.font_name, self.font_size = self.font_info[:2]  # type: ignore[assignment]

	def _calc_anchor(self) -> None:
		self._anchor = (
			(
				# Convert if AnchorX, else use raw int value
				self.CONVERT_DYNAMIC[self.raw_anchor[0]] * self.content_width
				if isinstance(self.raw_anchor[0], str)
				else self.raw_anchor[0]
			),
			(
				# Convert if AnchorY, else use raw int value
				self.CONVERT_DYNAMIC[self.raw_anchor[1]] * self.content_height
				if isinstance(self.raw_anchor[1], str)
				else self.raw_anchor[1]
			),
		)
		# Refresh position
		self.pos = self.pos

	def enable(self) -> None: ...  # noqa: D102

	def disable(self) -> None: ...  # noqa: D102

	@property
	def text(self) -> str:
		"""The text string."""
		return self._text

	@text.setter
	def text(self, txt: str | int) -> None:
		self.document.text = self._text = str(txt)
		self._calc_anchor()

	@property
	def x(self) -> float:
		"""The *unrotated* x position of the anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""
		return self._pos[0]

	@x.setter
	def x(self, val: float) -> None:
		self._pos = val, self._pos[1]
		self._set_x(val - self._anchor[0])

	@property
	def y(self) -> float:
		"""The *unrotated* y position of the anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""
		return self._pos[1]

	@y.setter
	def y(self, val: float) -> None:
		self._pos = self._pos[0], val
		self._set_y(val - self._anchor[1] - self._descent)  # Fixes y not centering

	@property
	def pos(self) -> Point2D:
		"""The *unrotated* anchor position."""
		return self._pos

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self._pos = val
		self._set_position(
			(
				val[0] - self._anchor[0],
				val[1] - self._anchor[1] - self._descent,  # Fixes y not centering
				self._z,
			)
		)

	@property  # type: ignore[override]
	def anchor_x(self) -> float:
		"""X position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self._anchor[0]

	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self.raw_anchor = val, self.raw_anchor[1]
		self._calc_anchor()

	@property  # type: ignore[override]
	def anchor_y(self) -> float:
		"""Y position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self._anchor[1]

	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self.raw_anchor = self.raw_anchor[0], val
		self._calc_anchor()

	@property
	def anchor(self) -> Point2D:
		"""Widget anchor offset.

		Can be set in px or dynamic.
		"""
		return self._anchor

	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self.raw_anchor = val
		self._calc_anchor()

	@property
	def width(self) -> int:
		"""Width of text. Equivalent to `~pyglet.text.Label.content_width`.

		To get `~pyglet.text.Label.width`, use `.label_width()`.
		"""
		return Label.content_width.fget(self)  # type: ignore[attr-defined, no-any-return]

	@width.setter
	def width(self, val: int) -> None:
		return Label.content_width.fset(self, val)  # type: ignore[attr-defined, no-any-return]

	@property
	def height(self) -> int:
		"""Height of text. Equivalent to `~pyglet.text.Label.content_height`.

		To get `~pyglet.text.Label.height`, use `.label_height()`.
		"""
		return Label.content_height.fget(self)  # type: ignore[attr-defined, no-any-return]

	@height.setter
	def height(self, val: int) -> None:
		return Label.content_height.fset(self, val)  # type: ignore[attr-defined, no-any-return]

	@property
	def label_width(self) -> int | None:
		"""The defined maximum width of the layout in pixels, or None.

		If `multiline` and `wrap_lines` is True, the `width` defines where the
		text will be wrapped. If `multiline` is False or `wrap_lines` is False,
		this property has no effect.
		"""
		return Label.width.fget(self)  # type: ignore[attr-defined, no-any-return]

	@property
	def label_height(self) -> int | None:
		"""The defined maximum height of the layout in pixels, or None.

		When `height` is not None, it affects the positioning of the
		text when :py:attr:`~pyglet.text.layout.TextLayout.anchor_y` and
		:py:attr:`~pyglet.text.layout.TextLayout.content_valign` are
		used.
		"""
		return Label.width.fget(self)  # type: ignore[attr-defined, no-any-return]

	@property
	def scale(self) -> float:
		"""Scale of widget.

		NOTE: Will account for `TextButton.hover_enlarge` if using `~pgm.gui.TextButton`.
		"""
		# 12 is default font size, in pt.
		return self.font_size / (self.font_info[1] or 12)

	@scale.setter
	def scale(self, val: float) -> None:
		if val <= 0:
			raise ValueError(f'"Text.scale" must be a positive number, not {val}.')
		# 12 is default font size, in pt.
		self.font_size = (self.font_info[1] or 12) * val
		self._calc_anchor()
