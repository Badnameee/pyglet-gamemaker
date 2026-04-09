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
	"""A wrapper for TextEntry that adds a couple of things, including adding font info and an ID."""

	EVENT_TYPES = ('on_submit',)

	def __init__(
		self,
		ID: str,
		text: str,
		x: float,
		y: float,
		width: int,
		window: Window,
		scene: Scene,
		batch: Batch,
		group: Group,
		font_info: FontInfo = (None, None),
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
				X coordinate of the text entry widget
			y (int):
				Y coordinate of the text entry widget
			width (int):
				The width of the text entry widget
			window (Window):
				Window for attaching self
			scene (Scene):
				Scene entry is attached to
			batch (Batch):
				Optional batch to add the text entry widget to
			group (Group):
				Optional parent group of text entry widget
			font_info (FontInfo, optional):
				The font name and size.
				Defaults to (None, None).
			color (tuple[int, int, int, int], optional):
				The color of the outline box in RGBA format.
				Defaults to (255, 255, 255, 255).
			text_color (tuple[int, int, int, int], optional):
				The color of the text in RGBA format.
				Defaults to (0, 0, 0, 255).
			caret_color (tuple[int, int, int, int], optional):
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

		# Restyle for font customization
		self._doc.set_style(
			0,
			len(self._doc.text),
			{'color': text_color.value, 'font_name': font_info[0], 'font_size': font_info[1]},
		)

		# Automatically adjust height to font size
		if font_info[1]:
			self.height *= font_info[1] / 12  # type: ignore[assignment] # Don't care if it's a float

		# Attach events
		self.window.push_handlers(self)
		self._bind_events(**kwargs)  # type: ignore[arg-type] # Mypy has some kwarg issues :P
		print(self._event_stack)

	def on_commit(self, widget: TextEntry, text: str) -> None:  # noqa: D102
		if self.dispatch:
			self.dispatch_event('on_submit', self, text)

	def _calc_anchor(self) -> None: ...

	def enable(self) -> None:  # noqa: D102
		self.enabled = True

	def disable(self) -> None:  # noqa: D102
		self.enabled = True

	@property  # type: ignore[override]
	def x(self) -> float:  # noqa: D102
		return self.x

	@x.setter
	def x(self, val: float) -> None:
		self.x = val

	@property  # type: ignore[override]
	def y(self) -> float:  # noqa: D102
		return self.y

	@y.setter
	def y(self, val: float) -> None:
		self.y = val

	@property
	def pos(self) -> Point2D:  # noqa: D102
		return self.x, self.y

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.x, self.y = val

	@property
	def anchor_x(self) -> float:  # noqa: D102
		return 0

	@anchor_x.setter
	def anchor_x(self, val: float) -> None: ...

	@property
	def anchor_y(self) -> float:  # noqa: D102
		return 0

	@anchor_y.setter
	def anchor_y(self, val: float) -> None: ...

	@property
	def anchor(self) -> Point2D:  # noqa: D102
		return 0, 0

	@anchor.setter
	def anchor(self, val: Anchor) -> None: ...

	@property
	def text(self) -> str:
		"""The text currently in the entry. Can return default text."""
		return self._layout.document.text
