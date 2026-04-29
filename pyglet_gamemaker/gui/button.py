"""Module holding Button widget class.

Use `~pgm.gui.Button` instead of `~pgm.gui.button.Button`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.gui import PushButton as _PushButton

from ..sprite.sprite_sheet import SpriteSheet
from .widget import Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group
	from pyglet.image import AbstractImage

	from ..resources import DefaultResources
	from ..scene import Scene
	from ..types import Anchor, AnchorX, AnchorY, ButtonStatus, EventHandler, Point2D
	from ..window import Window


class Button(_PushButton, Widget):
	"""A basic 2D button with custom anchor support. Supports anchoring with specific pixel values or dynamic.

	Dynamic Anchors:
	- `AnchorX`: 'left', 'center', 'right'
	- `AnchorY`: 'bottom', 'center', 'top'

	Button has three statuses: 'unpressed', 'hover', and 'pressed'.

	Takes a sprite sheet (using `sprite.Spritesheet`) to render the button.
	Sprite sheet must have images in a row for all of the statuses in above order.

	When creating object, give the starting index of the button images.
	For example, passing in 0 will take 0 as the unpressed image, 1 as the hovered, and 2 as the pressed.

	Dispatches:
	- `on_half_click` when pressed.
	- `on_full_click` when pressed and released without mouse moving off.

	Use kwargs to attach event handlers.
	"""

	EVENT_TYPES = 'on_half_click', 'on_full_click'

	unpressed_img: AbstractImage
	"""Image of unpressed button"""
	hover_img: AbstractImage
	"""Image of hovered button"""
	pressed_img: AbstractImage
	"""Image of pressed button"""
	status: ButtonStatus
	"""Status of button"""

	_last_mouse_pos: tuple[int, int] = 0, 0
	"""Holds the last mouse position registered by button"""

	def __init__(
		self,
		ID: str,
		x: float,
		y: float,
		image_sheet: SpriteSheet | DefaultResources,
		image_start: str | int,
		window: Window,
		scene: Scene,
		batch: Batch,
		group: Group,
		anchor: Anchor = (0, 0),
		dispatch: bool = True,
		attach_events: bool = True,
		**kwargs: EventHandler,
	) -> None:
		"""Create a button.

		Args:
			ID (str):
				Name/ID of widget
			x (float):
				Anchored x position of button
			y (float):
				Anchored y position of button
			image_sheet (SpriteSheet):
				SpriteSheet with the button images
			image_start (str | int):
				The starting index of the button images.
			window (Window):
				Window for attaching self
			scene (Scene):
				The scene the widget is from. None if widget is a template.
			batch (Batch):
				Batch for rendering
			group (Group):
				Group for rendering
			anchor (Anchor):
				Anchor position. See `~pgm.gui.Button` for more info on anchor values.
				Defaults to (0, 0).
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.gui.Button` for more info.
				Defaults to True.
			attach_events (bool, optional):
				If False, don't attach mouse events to window.
				Event handlers can still be manually invoked.
				Defaults to True.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		# Extract images from sheet
		self._parse_sheet(
			image_sheet if isinstance(image_sheet, SpriteSheet) else image_sheet.value,
			image_start,
		)

		super().__init__(
			x,  # type: ignore[arg-type]
			y,  # type: ignore[arg-type]
			self.pressed_img,
			self.unpressed_img,
			self.hover_img,
			batch,
			group,
		)
		Widget.__init__(self)

		self.window, self.scene = window, scene
		self.ID = ID
		self.status = 'Unpressed'

		self.start_pos = x, y
		self.start_anchor = self.anchor = anchor
		self.dispatch = dispatch
		self.attach_events = attach_events

		# Adds event handler for mouse events
		if attach_events:
			self._bind_mouse()

		self._bind_events(**kwargs)

	def update_sheet(self, image_sheet: SpriteSheet, image_start: str | int) -> None:
		"""Update the sheet of the button."""
		self._parse_sheet(image_sheet, image_start)
		self._calc_anchor()

	def _parse_sheet(self, image_sheet: SpriteSheet, image_start: str | int) -> None:
		"""Parse a sheet into individual images and store them."""
		start = (
			image_sheet.lookup[image_start]
			if isinstance(image_start, str)
			else image_start
		)
		self.unpressed_img, self.hover_img, self.pressed_img = image_sheet[
			start : start + 3
		]  # type: ignore[misc] # Because mypy cannot determine I am using slice and it will ALWAYS return a list

	def _update_status(self, x: int, y: int) -> None:
		# Update the status of the button given mouse position

		if self.value:
			if self.dispatch and self.status != 'Pressed':
				self.dispatch_event('on_half_click', self)
			self.status = 'Pressed'
		elif self._check_hit(x, y):
			if self.dispatch and self.status == 'Pressed':
				self.dispatch_event('on_full_click', self)
			self.status = 'Hover'
		else:
			self.status = 'Unpressed'

	def _calc_anchor(self) -> None:
		prev_pos = self.pos
		self._anchor = (
			(
				self.CONVERT_DYNAMIC[self.raw_anchor[0]] * self.hover_img.width
				if isinstance(self.raw_anchor[0], str)
				else self.raw_anchor[0]
			) * self.scale,
			(
				self.CONVERT_DYNAMIC[self.raw_anchor[1]] * self.hover_img.height
				if isinstance(self.raw_anchor[1], str)
				else self.raw_anchor[1]
			) * self.scale,
		)
		# Refresh position
		self.pos = prev_pos

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		if not self.enabled:
			return False
		self._last_mouse_pos = x, y
		super().on_mouse_press(x, y, buttons, modifiers)
		self._update_status(x, y)

		# Check for successful hit: Do not allow click to propagate through handlers
		return self.status == 'Pressed'

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
		if not self.enabled:
			return False
		self._last_mouse_pos = x, y
		super().on_mouse_motion(x, y, dx, dy)
		self._update_status(x, y)

		# Check for successful hit: Do not allow click to propagate through handlers
		return self.status == 'Hover'

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		if not self.enabled:
			return False
		self._last_mouse_pos = x, y
		super().on_mouse_release(x, y, buttons, modifiers)
		self._update_status(x, y)

		return False

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> bool:
		if not self.enabled:
			return False
		self._last_mouse_pos = x, y
		super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._update_status(x, y)

		# Check for successful hit: Do not allow click to propagate through handlers
		return self.status == 'Hover'

	def enable(self) -> None:  # noqa: D102
		self.enabled = True

	def disable(self) -> None:  # noqa: D102
		self.enabled = False

	@property  # type: ignore[override]
	def x(self) -> float:
		"""X position of the anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""
		return self._x + self._anchor[0]

	@x.setter
	def x(self, val: float) -> None:
		_PushButton.x.fset(self, val - self._anchor[0])  # type: ignore[attr-defined]
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property  # type: ignore[override]
	def y(self) -> float:
		"""Y position of the anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""
		return self._y + self._anchor[1]

	@y.setter
	def y(self, val: float) -> None:
		_PushButton.y.fset(self, val - self._anchor[1])  # type: ignore[attr-defined]
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def pos(self) -> Point2D:
		"""The anchor position."""
		return self._x + self._anchor[0], self._y + self._anchor[1]

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.position = val[0] - self._anchor[0], val[1] - self._anchor[1]  # type: ignore[assignment] # bro widget can take float
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def anchor_x(self) -> float:
		"""X position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self._anchor[0]

	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self.raw_anchor = val, self._anchor[1]
		self._calc_anchor()
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def anchor_y(self) -> float:
		"""Y position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self._anchor[1]

	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self.raw_anchor = self._anchor[0], val
		self._calc_anchor()
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

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
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def width(self) -> int:  # noqa: D102
		return self._width

	@property
	def height(self) -> int:  # noqa: D102
		return self._height

	@property
	def visible(self) -> bool:
		"""If True, button will be visible."""
		return self._sprite.visible

	@visible.setter
	def visible(self, val: bool) -> None:
		self._sprite.visible = val

	@property
	def scale(self) -> float:
		"""The scale factor of the button."""
		return self._sprite.scale

	@scale.setter
	def scale(self, val: float) -> None:
		self._width = int(self.unpressed_img.width * val)
		self._height = int(self.unpressed_img.height * val)
		self._sprite.scale = val
		self._calc_anchor()
