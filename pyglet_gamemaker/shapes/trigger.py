"""Module holding trigger class.

Use `~pgm.shapes.Trigger` instead of `~pgm.shapes.trigger.Trigger`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..event_dispatcher import EventDispatcher
from .hitbox import Hitbox

if TYPE_CHECKING:
	from typing import Self

	from ..scene import Scene
	from ..types import EventHandler, Point2D
	from ..window import Window


class Trigger(Hitbox, EventDispatcher):
	"""An invisible hitbox that dispatches events on mouse events that interact with it.

	Cannot detect other hitboxes for now.
	"""

	EVENT_TYPES = (
		'on_mouse_trigger_press',
		'on_mouse_trigger_release',
		'on_mouse_trigger_enter',
		'on_mouse_trigger_exit',
	)

	enabled: bool = True
	"""If True, trigger is enabled and dispatches events"""
	mouse_status = 'None'
	"""Status of mouse in trigger:
	- 'None': not in trigger
	- 'Hover': in trigger.
	- 'Pressed': pressed and in trigger

	Can also use `.mouse_in` and `.mouse_clicked` to get status.
	"""

	_last_mouse_info: tuple[int, int, bool] = 0, 0, False
	"""Holds the last mouse position and press status registered by trigger"""

	def __init__(
		self,
		ID: str,
		coords: tuple[Point2D, ...],
		window: Window,
		scene: Scene | None,
		anchor: Point2D = (0, 0),
		dispatch: bool = True,
		attach_events: bool = True,
		*,
		_subtype: str | None = None,
		**kwargs: EventHandler,
	) -> None:
		"""Create a trigger.

		Args:
			ID (str):
				Name/ID of trigger.
			coords (tuple[Point2D, ...]):
				The coordinates of the hitbox. Can create point by putting a single coordinate.
			window (Window):
				Window for attaching self
			scene (Scene | None):
				The scene the hitbox is from. None if hitbox is a template or not in a scene.
			anchor (Point2D, optional):
				The starting anchor position.
				Defaults to (0, 0).
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.gui.Button` for more info.
				Defaults to True.
			attach_events (bool, optional):
				If False, don't attach events (e.g. mouse) to window.
				Event handlers can still be manually invoked.
				Defaults to True.
			_subtype (str, optional)
				The subtype of the hitbox. Ex: 'rect', 'circle'.
				Defaults to None.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		super().__init__(ID, coords, window, scene, anchor, _subtype=_subtype)

		self.window, self.scene = window, scene
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

	@classmethod
	def from_rect(
		cls,
		ID: str,
		x: float,
		y: float,
		width: float,
		height: float,
		window: Window,
		scene: Scene | None,
		anchor: Point2D = (0, 0),
		dispatch: bool = True,
		attach_events: bool = True,
		**kwargs: EventHandler,
	) -> Self:
		"""Create a hitbox from rectangle args.

		Args:
			ID (str):
				Name/ID of hitbox
			x (float):
				x position
			y (float):
				y position
			width (float):
				Width of rect
			height (float):
				Height of rect
			window (Window):
				Window for attaching self
			scene (Scene | None):
				The scene the trigger is from. None if trigger is a template or not in a scene.
			anchor (Point2D, optional):
				Anchor position.
				Defaults to (0, 0).
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.shapes.Trigger` for more info.
				Defaults to True.
			attach_events (bool, optional):
				If False, don't attach events (e.g. mouse) to window.
				Event handlers can still be manually invoked.
				Defaults to True.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		return cls(
			ID,
			((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
			window,
			scene,
			anchor,
			dispatch,
			attach_events,
			_subtype='rect',
			**kwargs,
		)

	def colliding_point(self, x: float, y: float) -> bool:
		"""Check if point is inside trigger.

		Args:
			x (float): x-coord of point
			y (float): y-coord of point

		Returns:
			bool: If True, point is inside trigger
		"""
		return self.collide(Hitbox('', ((x, y),), self.window, self.scene))[0]

	def _update_mouse_collision(
		self, x: int, y: int, pressed: bool | None = None
	) -> None:
		# Update the status of the mouse given new info

		# If true, user just pressed or released button
		mouse_press_change = pressed and pressed != self._last_mouse_info[-1]

		if pressed is None:
			pressed = self._last_mouse_info[-1]

		collided = self.colliding_point(x, y)

		# Pressed
		if pressed and mouse_press_change and collided:
			if self.dispatch and self.mouse_status != 'Pressed':
				self.dispatch_event('on_mouse_trigger_press', self, x, y)
				self.mouse_status = 'Pressed'

		# Hovered
		elif collided:
			if self.dispatch and self.mouse_status != 'Hover':
				# Released mouse
				if self.mouse_status == 'Pressed':
					self.dispatch_event('on_mouse_trigger_release', self, x, y)
				# Started hovering
				else:
					self.dispatch_event('on_mouse_trigger_enter', self, x, y)
				self.mouse_status = 'Hover'

		# None
		else:
			if self.dispatch and self.mouse_status != 'None':
				self.dispatch_event('on_mouse_trigger_exit', self, x, y)
				self.mouse_status = 'None'

		self._last_mouse_info = x, y, pressed

	def bind_mouse(self) -> None:
		"""Bind mouse events to widget."""
		self.window.push_handlers(
			on_mouse_press=self._on_mouse_press,
			on_mouse_release=self._on_mouse_release,
			on_mouse_motion=self._on_mouse_motion,
			on_mouse_drag=self._on_mouse_drag,
		)

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y, True)
		return False

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y)
		return False

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y, False)
		return False

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y)
		return False

	@property
	def mouse_in(self) -> bool:
		"""If True, mouse is within trigger."""
		return self.mouse_status != 'None'

	@property
	def mouse_clicked(self) -> bool:
		"""If True, mouse is pressed and in trigger."""
		return self.mouse_status == 'Pressed'
