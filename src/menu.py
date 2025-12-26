from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING

from pyglet.window import Window
from pyglet.graphics import Batch, Group
from .scene import Scene
from .types import *
from .shapes import Rect
from .gui import *
if TYPE_CHECKING:
	from .sprite import SpriteSheet


class Menu(Scene, ABC):

	WIDGET_POS: dict[str, tuple[float, float]] = {}
	widgets: dict[str, Text | Button | TextButton] = {}

	batch: Batch
	bg_group: Group
	button_group: Group
	text_group: Group

	bg: Rect

	font_name: str = ''

	def __init__(self, name: str, window: Window, **kwargs) -> None:
		super().__init__(name, window, **kwargs)
		
		self.batch = Batch()
		self.bg_group = Group(0)
		self.button_group = Group(1)
		self.text_group = Group(2)
	
	def create_bg(self, color: Color) -> None:
		self.bg = Rect(
			0, 0, self.window.width, self.window.height,
			color, self.batch, self.bg_group
		)

	def create_text(self,
			widget_name: str, text: str,
			anchor_pos: Anchor=(0, 0),
			font_info: FontInfo=(None, None),
			color: Color=Color.WHITE,
	) -> Text:
		
		self.widgets[widget_name] = text = Text(
			text,
			self.WIDGET_POS[widget_name][0] * self.window.width,
			self.WIDGET_POS[widget_name][1] * self.window.width,
			self.batch, self.text_group,
			anchor_pos,
			font_info,
			color
		)
		text.disable()
	
	def create_button(self,
			widget_name: str,
			image_sheet: SpriteSheet, image_start: str | int,
			anchor: Anchor=(0, 0),
			*, attach_events: bool=True,
			**kwargs
	) -> None:
		self.widgets[widget_name] = button = Button(
			widget_name,
			self.WIDGET_POS[widget_name][0] * self.window.width,
			self.WIDGET_POS[widget_name][1] * self.window.height,
			image_sheet, image_start,
			self.window, self.batch, self.button_group,
			anchor, attach_events=attach_events, **kwargs
		)
		button.disable()

	def create_text_button(self,
			widget_name: str, text: str,
			image_sheet: SpriteSheet, image_start: str | int,
			button_anchor: Anchor=(0, 0),
			text_anchor: Anchor=(0, 0),
			font_info: FontInfo=(None, None),
			color: Color=Color.WHITE,
			hover_enlarge: int=0, **kwargs
	) -> TextButton:

		self.widgets[widget_name] = text_button = TextButton(
			widget_name, text,
			self.WIDGET_POS[widget_name][0] * self.window.width,
			self.WIDGET_POS[widget_name][1] * self.window.width,
			self.window, self.batch, self.button_group, self.text_group,
			image_sheet, image_start,
			button_anchor, text_anchor,
			font_info, color, hover_enlarge,
			**kwargs
		)
		text_button.disable()
