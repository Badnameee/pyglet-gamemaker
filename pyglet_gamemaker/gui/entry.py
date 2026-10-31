"""Module holding Entry widget class.

Use `~pgm.gui.Entry` instead of `~pgm.gui.entry.Entry`.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pyglet.gui import TextEntry

from .. import colors
from ..types import (
	FLOAT_REGEX,
	AnchorXDynamicPresetValues,
	AnchorYDynamicPresetValues,
)
from .widget import Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group

	from ..scene import Scene
	from ..types import (
		Anchor,
		AnchorX,
		AnchorY,
		Color,
		EventHandler,
		FontInfo,
		Point2D,
	)
	from ..window import Window


class Entry(TextEntry, Widget):
	"""A text entry with custom anchor support. Supports anchoring with specific pixel values or dynamic.

	See `~pgm.gui.widget.Widget` for information regarding anchoring.

	Dispatches:
	- `on_submit()` when enter/return key is pressed on the entry.
	"""

	# * CONSTS
	EVENT_TYPES = ('on_submit',)

	# * Instance Vars
	initial_text: str
	"""Initial text to display"""
	edited: bool = False
	"""If True, entry text has been edited. If False, remove default text when focused."""
	font_info: FontInfo
	"""The font information"""
	base_width: int
	"""The width without scaling"""
	base_height: int
	"""The height without scaling"""

	# * Property vars
	_color: Color

	def __init__(
		self,
		ID: str,
		text: str = '',
		x: float | None = None,
		y: float | None = None,
		width: int | None = None,
		window: Window | None = None,
		scene: Scene | None = None,
		batch: Batch | None = None,
		group: Group | None = None,
		anchor: Anchor = (0, 0),
		font_info: FontInfo = (None, None, None),
		color: Color = colors.WHITE,
		text_color: Color = colors.BLACK,
		caret_color: Color = colors.BLACK,
		mouse_detection: bool = True,
		dispatch: bool = True,
		**kwargs: EventHandler,
	) -> None:
		"""Create a text entry widget. Note most of the arguments and docstring were copied from `~pyglet.gui.TextEntry.__init__`.

		Args:
			ID (str):
				Name/ID of widget.
			text (str, optional):
				Initial display text.
				Defaults to ''.
			x (float, optional):
				Anchored x position. Can be set through `Scene.WIDGET_POS` if scene is provided.
				Defaults to None.
			y (float, optional):
				Anchored y position. Can be set through `Scene.WIDGET_POS` if scene is provided.
				Defaults to None.
			width (int, optional):
				The width of text entry widget. Height determined by font size.
				Defaults to 15 times the font size.
			window (Window, optional):
				Window for attaching self. Required if binding mouse events.
				Defaults to `scene.window` if scene is provided, else None.
			scene (Scene, optional):
				The scene the widget is from.
				Defaults to None.
			batch (Batch, optional):
				Batch for rendering.
				Defaults to None.
			group (Group, optional):
				Group for rendering.
				Defaults to None.
			anchor (Anchor, optional):
				Anchor position. See `~pgm.gui.Entry` for more info on anchor values.
				Defaults to (0, 0).
			font_info (FontInfo, optional):
				Font name, size, (and optional weight).
				Defaults to (None, None, None).
			color (Color, optional):
				The color of the outline box in RGBA format.
				Defaults to (255, 255, 255, 255).
			text_color (Color, optional):
				The color of the text in RGBA format.
				Defaults to (0, 0, 0, 255).
			caret_color (Color, optional):
				The color of the caret (when it is visible) in RGBA or RGB format.
				Defaults to (0, 0, 0, 255).
			mouse_detection (bool, optional):
				If False, don't attach events (e.g. mouse) to window.
				Event handlers can still be manually invoked.
				Defaults to True.
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.gui.Entry` for more info.
				Defaults to True.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		self.ID = ID
		self.scene = scene

		# Verify scene attrs
		self.font_info = self._process_font_info(font_info)
		x, y = self._verify_pos(x, y)
		self.window = self._verify_window(window, necessary=mouse_detection)
		batch = self._verify_batch(batch)
		group = self._verify_group(group, attr_name='entry_group')

		super().__init__(
			text,
			x,  # type: ignore[arg-type]
			y,  # type: ignore[arg-type]
			width
			if width is not None
			else 15 * (self.font_info[1] or self.DEFAULT_FONT_SIZE),
			color,  # type: ignore[arg-type]
			text_color,  # type: ignore[arg-type]
			caret_color,  # type: ignore[arg-type]
			batch,
			group,
		)

		self.dispatch = dispatch
		self.mouse_detection = mouse_detection
		self._color = color
		self.initial_pos = x, y
		self.initial_anchor = self.anchor = anchor
		self.initial_text = text
		self.base_width = self._width
		self.base_height = self._height

		# Restyle for font customization
		self._doc.set_style(
			0,
			len(self._doc.text),
			{
				'color': text_color,
				'font_name': self.font_info[0],
				'font_size': self.font_info[1],
				'weight': self.font_info[2],  # type: ignore[misc]
			},
		)

		# Automatically adjust height to font size
		if self.font_info[1] is not None:
			self.height *= self.font_info[1] / self.DEFAULT_FONT_SIZE  # type: ignore[assignment] # Don't care if it's a float

		# Register events
		self.register_events()
		# Adds event handler for mouse events
		if mouse_detection:
			self.window.push_handlers(self)  # type: ignore[union-attr] # window should be real window by here
		# Bind user kwargs
		if dispatch:
			self.bind_events(**kwargs)

	def clear(self) -> None:
		"""Clear the entry."""
		self._layout.document.delete_text(0, len(self._layout.document.text))

	def reset(
		self,
		pos: bool = True,
		anchor: bool = True,
		scale: bool = True,
		text: bool = True,
		font: bool = True,
	) -> None:
		"""Reset entry to initial state. Optional arguments control which parts get reset.

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
			text (bool, optional):
				If True, reset the text.
				Defaults to True.
			font (bool, optional):
				If True, reset the font information.
				Defaults to True.
		"""
		if pos:
			self.pos = self.initial_pos
		if anchor:
			self.anchor = self.initial_anchor
		if scale:
			self.scale = 1
		if text:
			self.clear()
			self._layout.document.insert_text(0, self.initial_text)
			self.edited = False
		if font:
			self.font_name, self.font_size = self.font_info[:2]  # type: ignore[assignment]

	def on_commit(self, widget: TextEntry, text: str) -> None:  # noqa: D102
		if self.dispatch:
			self.dispatch_event('on_submit', self, text)

	def _set_focus(self, value: bool) -> None:
		# Get previous value to detect first click-off
		prev_value = self._focus
		super()._set_focus(value)

		if value and not self.edited:
			self.clear()

		# First click-off
		elif not value and prev_value:
			# If empty, bring back text and clear when focused
			self.edited = len(self._layout.document.text) != 0
			if not self.edited:
				self._layout.document.insert_text(0, self.initial_text)

	def _calc_anchor(self) -> None:
		# Get pos before messing with anchor
		prev_pos = self.pos

		anchor_x: float = self._anchor[0]
		anchor_y: float = self._anchor[1]

		# Dynamic
		if isinstance(self.raw_anchor[0], str):
			# Original dynamic anchor
			if self.raw_anchor[0] in AnchorXDynamicPresetValues:
				anchor_x = self.CONVERT_DYNAMIC[self.raw_anchor[0]] * self.width  # type: ignore[index]
			elif re.fullmatch(FLOAT_REGEX, self.raw_anchor[0]):
				anchor_x = float(self.raw_anchor[0]) * self.width
			else:
				raise ValueError(
					f'"Text.anchor_x" must be either one of {AnchorXDynamicPresetValues} or a string representing a float, not "{self.raw_anchor[0]}".'
				)
		# Static
		if isinstance(self.raw_anchor[0], float | int):
			anchor_x = self.raw_anchor[0]

		# Dynamic
		if isinstance(self.raw_anchor[1], str):
			# Original dynamic anchor
			if self.raw_anchor[1] in AnchorYDynamicPresetValues:
				anchor_y = self.CONVERT_DYNAMIC[self.raw_anchor[1]] * self.height  # type: ignore[index]
			elif re.fullmatch(FLOAT_REGEX, self.raw_anchor[1]):
				anchor_y = float(self.raw_anchor[1]) * self.height
			else:
				raise ValueError(
					f'"Text.anchor_y" must be either one of {AnchorYDynamicPresetValues} or a string representing a float, not "{self.raw_anchor[1]}".'
				)
		# Static
		if isinstance(self.raw_anchor[1], float | int):
			anchor_y = self.raw_anchor[1]

		self._anchor = anchor_x, anchor_y

		# Refresh position
		self.pos = prev_pos

	def enable(self) -> None:  # noqa: D102
		self.enabled = True

	def disable(self) -> None:  # noqa: D102
		self.enabled = True

	@property  # type: ignore[override]
	def x(self) -> float:  # noqa: D102
		return self._x + self.anchor[0]

	@x.setter
	def x(self, val: float) -> None:
		self._x = val - self.anchor[0]  # type: ignore[assignment]
		self._update_position()

	@property  # type: ignore[override]
	def y(self) -> float:  # noqa: D102
		return self._y + self.anchor[1]

	@y.setter
	def y(self, val: float) -> None:
		self._y = val - self.anchor[1]  # type: ignore[assignment]
		self._update_position()

	@property
	def pos(self) -> Point2D:  # noqa: D102
		return self._x + self._anchor[0], self._y + self._anchor[1]

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self._x, self._y = val[0] - self._anchor[0], val[1] - self._anchor[1]  # type: ignore[assignment]
		self._update_position()

	@property
	def anchor_x(self) -> float:  # noqa: D102
		return self._anchor[0]

	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self.raw_anchor = val, self.raw_anchor[1]
		self._calc_anchor()

	@property
	def anchor_y(self) -> float:  # noqa: D102
		return self._anchor[1]

	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self.raw_anchor = self.raw_anchor[0], val
		self._calc_anchor()

	@property
	def anchor(self) -> Point2D:  # noqa: D102
		return self._anchor

	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self.raw_anchor = val
		self._calc_anchor()

	@property
	def text(self) -> str:
		"""The text currently in the entry. Can return default text."""
		return self._layout.document.text

	@property
	def font_name(self) -> str | list[str]:
		"""Font family name.

		The font name, as passed to :py:func:`pyglet.font.load`.  A list of names can
		optionally be given: the first matching font will be used.
		"""
		return self._doc.get_style('font_name')  # type: ignore[no-any-return]

	@font_name.setter
	def font_name(self, val: str | list[str]) -> None:
		self._doc.set_style(0, len(self._doc.text), {'font_name': val})

	@property
	def font_size(self) -> float:
		"""Font size, in points."""
		return self._doc.get_style('font_size')  # type: ignore[no-any-return]

	@font_size.setter
	def font_size(self, val: float) -> None:
		self._doc.set_style(0, len(self._doc.text), {'font_size': val})

	@property
	def weight(self) -> str:
		"""The font weight (boldness or thickness), as a string.

		See the :py:class:`~Weight` enum for valid cross-platform
		string values.
		"""
		return self._doc.get_style('weight')  # type: ignore[no-any-return]

	@weight.setter
	def weight(self, val: str) -> None:
		self.font_info = *self.font_info[:2], val
		self._doc.set_style(0, len(self._doc.text), {'weight': val})

	@property
	def color(self) -> Color:
		"""The color of the text."""
		return self._color

	@color.setter
	def color(self, val: Color) -> None:
		self._color = val
		self._doc.set_style(0, len(self._doc.text), {'color': str(val)})

	@property
	def scale(self) -> float:  # noqa: D102
		return self._scale

	@scale.setter
	def scale(self, val: float) -> None:
		if val <= 0:
			raise ValueError(f'"Entry.scale" must be a positive number, not {val}.')

		self.font_size = (self.font_info[1] or self.DEFAULT_FONT_SIZE) * val
		self.width = int(self.base_width * val)
		self.height = int(self.base_height * val)
		self._scale = val
		self._calc_anchor()

	def __str__(self) -> str:
		return f'Entry ({self.ID}): "{self.text}" @ {self.pos} @ {self.scale}x scale | {self.raw_anchor} anchored'
