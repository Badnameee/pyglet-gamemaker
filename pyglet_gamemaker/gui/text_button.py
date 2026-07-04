"""Module holding TextButton widget class.

Use `~pgm.gui.TextButton` instead of `~pgm.gui.text_button.TextButton`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import Color
from .button import Button
from .text import Text
from .widget import Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group

	from ..resources import DefaultResources
	from ..scene import Scene
	from ..sprite.sprite_sheet import SpriteSheet
	from ..types import (
		Anchor,
		EventHandler,
		FontInfo,
		Point2D,
	)
	from ..window import Window


class TextButton(Widget):
	"""Both a 2D button and 2D text in one. Refer to `~pgm.gui.Button` and `~pgm.gui.Text`.

	Dispatches: Refer to `~pgm.gui.Button`.

	Note: `.text` holds Text object, `.button` holds Button object

	Use kwargs to attach event handlers.

	Note: Be cautious if editing button or text attributes directly, as it can cause desync between individual components and tetbutton object
	- ex. do not set position of text manually, set position of TextButton or set anchor of text
	"""

	EVENT_TYPES = Button.EVENT_TYPES + Text.EVENT_TYPES

	_hover_enlarge: float = 0

	button: Button
	"""Button object"""
	text: Text
	"""Text object"""
	start_hover_enlarge: int
	"""Starting hover enlarge value"""

	_enlarged: bool = False
	"""If true, text is currently enlarged. Used internally to enlarge text once."""

	def __init__(
		self,
		ID: str,
		text: str,
		x: float,
		y: float,
		window: Window,
		scene: Scene | None,
		batch: Batch,
		button_group: Group,
		text_group: Group,
		image_sheet: SpriteSheet | DefaultResources,
		image_start: str | int,
		button_anchor: Anchor = (0, 0),
		text_anchor: Anchor = ('center', 'center'),
		font_info: FontInfo = (None, None, None),
		color: Color = Color.WHITE,
		hover_enlarge: int = 0,
		dispatch: bool = True,
		attach_events: bool = True,
		**kwargs: EventHandler,
	) -> None:
		"""Create a button with text.

		Args:
			ID (str):
				Name/ID of widget
			text (str):
				Label text
			x (float):
				Anchored x position of button
			y (float):
				Anchored y position of button
			window (Window):
				Window for attaching self
			scene (Scene | None):
				The scene the widget is from. None if widget is a template or not in a scene.
			batch (Batch):
				Batch for rendering
			button_group (Group):
				Group for rendering button
			text_group (Group):
				Group for rendering text
			image_sheet (SpriteSheet):
				SpriteSheet with the button images
			image_start (str | int):
				The starting index of the button images
			button_anchor (Anchor, optional):
				Anchor position for the button. See `~pgm.gui.Button` for more info on anchor values.
				Defaults to (0, 0).
			text_anchor (Anchor, optional):
				Anchor position for the text. See `~pgm.gui.Text` for more info on anchor values.
				Defaults to ('center', 'center').
			font_info (FontInfo, optional):
				Font name, size, (and optional weight).
				Defaults to (None, None, None).
			color (Color, optional):
				Color of text.
				Defaults to Color.WHITE.
			hover_enlarge (int, optional):
				How much to enlarge text when hovered over.
				Defaults to 0.
			dispatch (bool, optional):
				If False, don't dispatch events to handlers (may also improve performance). See `~pgm.gui.Button` for more info.
				Defaults to True.
			attach_events (bool, optional):
				If False, don't attach events (e.g. mouse) to window.
				Event handlers can still be manually invoked.
				Defaults to True.
			**kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		self.button = Button(
			ID,
			x,
			y,
			image_sheet,
			image_start,
			window,
			scene,
			batch,
			button_group,
			button_anchor,
			False,
			False,
		)
		self.button._will_update_status = False

		self.text = Text(
			ID,
			text,
			*self._shifted_text_pos,
			window,
			scene,
			batch,
			text_group,
			text_anchor,
			font_info,
			color,
		)

		self.window, self.scene = window, scene
		self.ID = ID
		self.start_hover_enlarge = self.hover_enlarge = hover_enlarge
		self.status = 'Unpressed'
		self.dispatch = dispatch
		self.attach_events = attach_events

		# Register events
		self.register_events()
		# Adds event handler for mouse events
		if attach_events:
			self.bind_mouse()
		# Bind user kwargs
		if dispatch:
			self.bind_events(**kwargs)

	def reset(self) -> None:
		"""Reset text and button to initial state."""
		self.text.reset()
		self.button.reset()
		self.hover_enlarge = self.start_hover_enlarge
		# Sync status
		self._on_mouse_motion(*self.button._last_mouse_pos, 0, 0)

	def _update_status(self, x: int, y: int) -> None:
		# Update the status of the button

		# Pressed
		if self.button.value:
			if self.status != 'Pressed':
				self._enlarge()
				self.status = 'Pressed'

				if self.dispatch:
					self.dispatch_event('on_half_click', self)

		# Hovered
		elif self.button._check_hit(x, y):
			if self.dispatch and self.status == 'Pressed':
				self.dispatch_event('on_full_click', self)

			if self.status != 'Hover':
				self._enlarge()
				self.status = 'Hover'

		# Unpressed
		else:
			if self.status != 'Unpressed':
				self._enlarge()
				self.status = 'Unpressed'

	def _calc_anchor(self) -> None:
		self.button._calc_anchor()
		self.text._calc_anchor()

	def _enlarge(self) -> None:
		# Enlarge the text based on button status

		if self.button.status == 'Hover':
			# First frame hover: enlarge text
			if not self._enlarged:
				self._enlarged = True
				self.text.font_size += self._hover_enlarge
		else:
			# First frame unhover: unenlarge text
			if self._enlarged:
				self._enlarged = False
				self.text.font_size -= self._hover_enlarge

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		if not self.button.enabled:
			return False
		self.button._on_mouse_press(x, y, buttons, modifiers)
		self._update_status(x, y)
		self._enlarge()
		return False

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
		if not self.button.enabled:
			return False
		self.button._on_mouse_motion(x, y, dx, dy)
		self._update_status(x, y)
		self._enlarge()
		return False

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		if not self.button.enabled:
			return False
		self.button._on_mouse_release(x, y, buttons, modifiers)
		self._update_status(x, y)
		self._enlarge()
		return False

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> bool:
		if not self.button.enabled:
			return False
		self.button._on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._update_status(x, y)
		self._enlarge()
		return False

	def enable(self) -> None:  # noqa: D102
		self.button.enable()

	def disable(self) -> None:  # noqa: D102
		self.button.disable()

	@property
	def x(self) -> float:
		"""The x position of the anchor point. Setting sets text AND button.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.button.x

	@x.setter
	def x(self, val: float) -> None:
		self.button.x = val
		self.text.x = self._shifted_text_x
		self._enlarge()

	@property
	def y(self) -> float:
		"""The y position of the anchor point. Setting sets text AND button.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.button.y

	@y.setter
	def y(self, val: float) -> None:
		self.button.y = val
		self.text.y = self._shifted_text_y
		self._enlarge()

	@property
	def pos(self) -> Point2D:
		"""The x position of the anchor point. Setting sets text AND button."""
		return self.button.pos

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.button.pos = val
		self.text.pos = self._shifted_text_pos
		self._enlarge()

	@property
	def anchor_x(self) -> float:
		"""The x position of the button anchor point. Equivalent to `.button.anchor_x`.

		Can be set in px or dynamic (see `~pgm.gui.Button`)

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.button.anchor_x

	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self.button.anchor_x = val
		self.text.x = self._shifted_text_x

	@property
	def anchor_y(self) -> float:
		"""The y position of the button anchor point. Equivalent to `.button.anchor_y`.

		Can be set in px or dynamic (see `~pgm.gui.Button`)

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.button.anchor_y

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self.button.anchor_y = val
		self.text.y = self._shifted_text_y

	@property
	def anchor(self) -> Point2D:
		"""The anchor position of the button. Equivalent to `.button.anchor`.

		Can be set in px or dynamic (see `~pgm.gui.Button` and `~pgm.gui.Text`)
		"""
		return self.button.anchor

	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self.button.anchor = val
		self.text.pos = self._shifted_text_pos

	@property
	def hover_enlarge(self) -> float:
		"""How much to enlarge text when hovered over."""
		return self._hover_enlarge

	@hover_enlarge.setter
	def hover_enlarge(self, size: float) -> None:
		# If need to be resized and synced
		if self._enlarged:
			# Trick: Can unhover and rehover button to make changes automatically.
			# 	This way, no copy pasting code needed.
			# 	Because status is being manually set instead of in Button._update_status,
			# 	no dispatches are made.
			self.button.status = 'Unpressed'
			self._enlarge()
			self._hover_enlarge = size
			self.button.status = 'Hover'
			self._enlarge()

		else:
			self._hover_enlarge = size

	@property
	def enabled(self) -> bool:  # noqa: D102
		return self.button.enabled

	@property
	def width(self) -> int:  # noqa: D102
		return self.button.width

	@property
	def height(self) -> int:  # noqa: D102
		return self.button.height

	@property
	def visible(self) -> bool:
		"""If True, text button will be visible."""
		return self.button.visible

	@visible.setter
	def visible(self, val: bool) -> None:
		self.button.visible = val
		self.text.visible = val

	@property
	def scale(self) -> float:
		"""The scale factor of the button."""
		return self.button.scale

	@scale.setter
	def scale(self, val: float) -> None:
		self.button.scale = val
		# Text scale reflects hover
		# 	Therefore, setting text.scale also automatically scales hover_enlarge
		# 	Have to remove enlarge then add it back after scaling
		self.hover_enlarge = 0
		self.text.scale = val
		self.hover_enlarge = self.start_hover_enlarge * val
		self._update_status(*self.button._last_mouse_pos)

	@property
	def _shifted_text_x(self) -> float:
		return self.button.x - self.button.anchor_x + self.button.width / 2

	@property
	def _shifted_text_y(self) -> float:
		return self.button.y - self.button.anchor_y + self.button.height / 2

	@property
	def _shifted_text_pos(self) -> Point2D:
		return self._shifted_text_x, self._shifted_text_y
