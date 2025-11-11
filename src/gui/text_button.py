from __future__ import annotations
from typing import TYPE_CHECKING

from ..types import *
from .text import Text
from .button import Button
if TYPE_CHECKING:
	from pyglet.customtypes import AnchorX, AnchorY
	from pyglet.window import Window
	from pyglet.graphics import Batch, Group
	from ..sprite import SpriteSheet


class TextButton(Button):
	"""Both a 2D button and 2D text in one. Refer to `gui.Button` and `gui.Text`.

	Dispatches: Refer to `gui.Button`.

	Note: Use `.text.text` to get text, as `.text` is the `Text` object
	
	Use kwargs to attach event handlers.
	"""

	# Store as property to reset size when manually changing
	_hover_enlarge = 0

	def __init__(self,
			ID: str,
			text: str,
			x: float, y: float,
			window: Window, batch: Batch, group: Group,

			# Button params
			image_sheet: SpriteSheet, image_start: str | int,
			button_anchor: tuple[AnchorX | float, AnchorY | float]=(0, 0),
			
			# Text params
			text_anchor: tuple[AnchorX | float, AnchorY | float]=(0, 0),
			font_info: FontInfo=(None, None),
			color: Color=Color.WHITE,

			hover_enlarge: int = 0, **kwargs
	) -> None:
		"""Create a button with text

		Args:
			ID (str): Name/ID of widget
			text (str): Label text
			x (float): Anchored x position of button
			y (float): Anchored y position of button
			window (Window): Window for attaching self
			batch (Batch): Batch for rendering
			group (Group): Group for rendering
			image_sheet (SpriteSheet): SpriteSheet with the button images
			image_start (str | int): The starting index of the button images
			button_anchor (tuple[AnchorX | float, AnchorY | float], optional): Anchor for the button.
				*Float* -- static anchor, *AnchorX/Y* -- dynamic anchor.
				Defaults to (0, 0).
			text_anchor (tuple[AnchorX | float, AnchorY | float], optional): Anchor for the text.
				*Float* -- static anchor, *AnchorX/Y* -- dynamic anchor.
				Defaults to (0, 0).
			font_info (FontInfo, optional): Font name and size.
				Defaults to (None, None).
			color (Color, optional): Color of text.
				Defaults to Color.WHITE.
			hover_enlarge (int, optional): How much to enlarge text when hovered over.
				Defaults to 0.

			**kwargs: Any event handlers to attach (such as 'on_full_click')
		"""
		
		super().__init__(
			ID, x, y, button_anchor, image_sheet, image_start,
			window, batch, group, **kwargs
		)
		self.enlarged = False
		self.hover_enlarge = hover_enlarge

		self.text = Text(
			text,
			x, y,
			batch, group,
			text_anchor,
			font_info,
			color,
		)

	def _enlarge(self) -> None:
		"""Enlarge the text based on button status."""

		# Hovering
		if self.status == 'Hover':
			# First frame hover: enlarge text
			if not self.enlarged:
				self.enlarged = True
				self.text.font_size += self.hover_enlarge

				# If anchor is dynamic, update
				if self.text.dynamic_any:
					self.text._calc_anchor_pos()
		else:
			# First frame unhover: enlarge text
			if self.enlarged:
				self.enlarged = False
				self.text.font_size -= self.hover_enlarge

				# If anchor is dynamic, update
				if self.text.dynamic_any:
					self.text._calc_anchor_pos()

	def on_mouse_press(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		super().on_mouse_press(x, y, buttons, modifiers)
		self._enlarge()

	def on_mouse_motion(self,
			x: int, y: int,
			dx: int, dy: int
	) -> None:
		super().on_mouse_motion(x, y, dx, dy)
		self._enlarge()

	def on_mouse_release(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		super().on_mouse_release(x, y, buttons, modifiers)
		self._enlarge()

	def on_mouse_drag(self,
			x: int, y: int, dx: int, dy: int,
			buttons: int, modifiers: int
	) -> None:
		super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._enlarge()

	@property # type: ignore[override]
	def x(self) -> float:
		"""Anchored x position"""
		return self._x + self.anchor_pos[0]
	@x.setter
	def x(self, val: float) -> None:
		Button.x.fset(self, val) # type: ignore[attr-defined]
		self.text.x = val 

	@property # type: ignore[override]
	def y(self) -> float:
		return self._y + self.anchor_pos[1]
	@y.setter
	def y(self, val: float) -> None:
		"""Anchored y position"""
		Button.y.fset(self, val) # type: ignore[attr-defined]
		self.text.y = val

	@property
	def hover_enlarge(self) -> int:
		"""How much to enlarge text when hovered over."""
		return self._hover_enlarge
	@hover_enlarge.setter
	def hover_enlarge(self, size: int) -> None:
		# If need to be resized
		if self.enlarged:
			# Resize to new enlarge
			self.text.font_size -= self.hover_enlarge - size
		self._hover_enlarge = size
