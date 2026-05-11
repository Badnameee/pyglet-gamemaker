"""Module holding Entry widget class.

Use `~pgm.gui.Entry` instead of `~pgm.gui.entry.Entry`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.gui import TextEntry

from ..types import Color
from .widget import Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group

	from ..scene import Scene
	from ..types import Anchor, EventHandler, FontInfo, Point2D
	from ..window import Window


class Entry(TextEntry, Widget):
	"""A text entry with custom anchor support. Supports anchoring with specific pixel values or dynamic.

	Dynamic Anchors:
	- `AnchorX`: 'left', 'center', 'right'
	- `AnchorY`: 'bottom', 'center', 'top'

	Dispatches:
	- 'on_commit' when enter/return key is pressed on the entry.
	"""

	EVENT_TYPES = ('on_submit',)

	_color: Color
	_scale: float = 1

	initial_text: str
	"""Initial text to display"""
	edited: bool = False
	"""If True, text has been edited. If False, remove default text when focused"""
	font_info: FontInfo
	"""The font information"""
	base_width: int
	"""The width without scaling"""
	base_height: int
	"""The height without scaling"""

	def __init__(
		self,
		ID: str,
		text: str,
		x: float,
		y: float,
		width: int,
		window: Window,
		scene: Scene | None,
		batch: Batch,
		group: Group,
		anchor: Anchor = (0, 0),
		font_info: FontInfo = (None, None, None),
		color: Color = Color.WHITE,
		text_color: Color = Color.BLACK,
		caret_color: Color = Color.BLACK,
		dispatch: bool = False,
		**kwargs: EventHandler,
	) -> None:
		"""Create a text entry widget. Note most of the arguments and docstring were copied from `~pyglet.gui.TextEntry.__init__`.

		Args:
			ID (str):
				ID of entry for identification
			text (str):
				Initial text to display
			x (int):
				Anchored x coordinate of text entry widget
			y (int):
				Anchored y coordinate of text entry widget
			width (int):
				The width of text entry widget
			window (Window):
				Window for attaching self
			scene (Scene | None):
				The scene the widget is from. None if widget is a template or not in a scene.
			batch (Batch):
				Batch for rendering
			group (Group):
				Group for rendering
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
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.gui.Button` for more info.
				Defaults to True.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)

		"""
		super().__init__(
			text,
			x,  # type: ignore[arg-type]
			y,  # type: ignore[arg-type]
			width,
			color.value,
			text_color.value,
			caret_color.value,
			batch,
			group,
		)

		self.ID = ID
		self.window, self.scene = window, scene
		self.dispatch = dispatch
		self._color = color
		self.font_info = font_info
		self.start_anchor = self.anchor = anchor
		self.initial_text = text

		self.start_pos = x, y
		self.base_width = width
		self.base_height = self._height

		# Pads Nones on right for consistent length
		font_info = *font_info, *[None for _ in range(3 - len(font_info))]

		# Restyle for font customization
		self._doc.set_style(
			0,
			len(self._doc.text),
			{
				'color': text_color.value,
				'font_name': font_info[0],
				'font_size': font_info[1],
				'weight': font_info[2],  # type: ignore[misc] # Guaranteed 3 items long by here
			},
		)

		# Automatically adjust height to font size
		if font_info[1]:
			self.height *= font_info[1] / 12  # type: ignore[assignment] # Don't care if it's a float

		# Attach events
		self.window.push_handlers(self)
		self.bind_events(**kwargs)

	def clear(self) -> None:
		"""Clear the entry."""
		self._layout.document.delete_text(0, len(self._layout.document.text))

	def reset(self, pos: bool = True, text: bool = True) -> None:
		"""Reset entry to initial state. Optional arguments control which parts get reset.

		Args:
			pos (bool, optional):
				If True, reset the position and anchoring. Defaults to True.
			text (bool, optional):
				If True, reset the text. Defaults to True.
		"""
		if pos:
			super().reset()
		if text:
			self.clear()
			self._layout.document.insert_text(0, self.initial_text)
			self.edited = False

	def on_commit(self, widget: TextEntry, text: str) -> None:  # noqa: D102
		if self.dispatch:
			self.dispatch_event('on_submit', self, text)

	def _set_focus(self, value: bool) -> None:
		super()._set_focus(value)
		if value and not self.edited:
			self.edited = True
			self.clear()

	def _calc_anchor(self) -> None:
		# Get pos before messing with anchor
		prev_pos = self.pos
		self._anchor = (
			(
				# Convert if AnchorX, else use raw int value
				self.CONVERT_DYNAMIC[self.raw_anchor[0]] * self.width
				if isinstance(self.raw_anchor[0], str)
				else self.raw_anchor[0]
			),
			(
				# Convert if AnchorY, else use raw int value
				self.CONVERT_DYNAMIC[self.raw_anchor[1]] * self.height
				if isinstance(self.raw_anchor[1], str)
				else self.raw_anchor[1]
			),
		)
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
	def anchor_x(self, val: float) -> None:
		self.raw_anchor = val, self.raw_anchor[1]
		self._calc_anchor()

	@property
	def anchor_y(self) -> float:  # noqa: D102
		return self._anchor[1]

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
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
		self._doc.set_style(0, len(self._doc.text), {'weight': str(val)})

	@property
	def color(self) -> Color:
		"""The color of the text, as a `~pgm.types.Color`."""
		return self._color

	@color.setter
	def color(self, val: Color) -> None:
		self._color = val
		self._doc.set_style(0, len(self._doc.text), {'weight': str(val.value)})

	@property
	def scale(self) -> float:  # noqa: D102
		return self._scale

	@scale.setter
	def scale(self, val: float) -> None:
		if val <= 0:
			raise ValueError(f'"Text.scale" must be a positive number, not {val}.')

		# 12 is default font size, in pt.
		self.font_size = (self.font_info[1] or 12) * val
		self.width = int(self.base_width * val)
		self.height = int(self.base_height * val)
		self._scale = val
		self._calc_anchor()
