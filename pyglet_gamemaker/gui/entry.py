from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.gui import TextEntry

from .widget import Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group

	from ..scene import Scene
	from ..types import FontInfo
	from ..window import Window


class Entry(TextEntry, Widget):
	"""A wrapper for TextEntry that adds a couple of things, including adding font info and an ID."""

	EVENT_TYPES = ()

	def __init__(  # noqa: D107
		self,
		ID: str,
		text: str,
		x: int,
		y: int,
		width: int,
		window: Window,
		scene: Scene,
		batch: Batch,
		group: Group,
		font_info: FontInfo = (None, None),
		color: tuple[int, int, int, int] = (255, 255, 255, 255),
		text_color: tuple[int, int, int, int] = (0, 0, 0, 255),
		caret_color: tuple[int, int, int, int] = (0, 0, 0, 255),
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
		"""  # noqa: D205
		super().__init__(
			text, x, y, width, color, text_color, caret_color, batch, group
		)

		self.ID = ID
		self.window, self.scene = window, scene

		# Restyle for font customization
		self._doc.set_style(
			0,
			len(self._doc.text),
			{'color': text_color, 'font_name': font_info[0], 'font_size': font_info[1]},
		)

		# Automatically adjust height to font size
		if font_info[1]:
			self.height *= font_info[1] / 12

	def on_commit(self, widget: TextEntry, text: str) -> None:  # noqa: D102
		self.scene.on_commit(self, text)
