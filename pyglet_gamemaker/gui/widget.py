"""Module holding base Widget class.

Use `~pgm.gui.Widget` instead of `~pgm.gui.widget.Widget`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pyglet.event import EventDispatcher

if TYPE_CHECKING:
	from ..scene import Scene
	from ..types import Anchor, AnchorX, AnchorY, Point2D
	from ..window import Window


class Widget(ABC):
	"""The base class for a Widget. Inherit to create own widget.

	Required Methods:
	- `._calc_anchor()`: Calculate the static anchor with raw_anchor

	Required Properties:
	- `.x`
	- `.y`
	- `.pos`
	- `.anchor_x`
	- `.anchor_y`
	- `.anchor`

	Optional Methods:
	- `_on_mouse_...`: `...press`, `...release`, `...motion`, `...drag`
		- Mouse events to attach when creating widget.
	"""

	CONVERT_DYNAMIC: dict[AnchorX | AnchorY, float] = {
		'left': 0,
		'bottom': 0,
		'center': 0.5,
		'right': 1,
		'top': 1,
	}
	"""Converts dynamic anchor to multiplier"""
	_ALL_EVENT_TYPES: tuple[str, ...] = 'on_half_click', 'on_full_click', 'on_submit'
	"""This are all event types in all widgets to register them, used internally"""
	EVENT_TYPES: tuple[str, ...] = ()
	"""The event names that a widget can dispatch"""

	# Register all event types beforehand
	# 	Comprehension prevents name clashing with multiinheritance
	[EventDispatcher.register_event_type(event) for event in _ALL_EVENT_TYPES]

	_anchor: Point2D = 0, 0
	"""Internally holds anchor offset of widget"""

	window: Window
	"""Window widget is associated with. Currently has no functionality."""
	scene: Scene
	"""The scene the widget is from. None if widget is a template."""
	ID: str
	"""The unique ID of the widget to distinguish it"""
	raw_anchor: Anchor = 0, 0
	"""Holds the raw anchor position (static + dynamic) of widget"""
	start_pos: Point2D = 0, 0
	"""Original (*unanchored* AND *unrotated*) position of widget"""
	start_anchor: Anchor = 0, 0
	"""Original anchor offset of widget"""
	dispatch: bool = True
	"""If False, don't dispatch events to handlers"""
	attach_events: bool = True
	"""If False, don't attach events to window"""

	def offset(self, val: Point2D) -> None:  # noqa: D102
		"""Add offset to widget."""
		self.x += val[0]
		self.y += val[1]

	def set_offset(self, val: Point2D) -> None:  # noqa: D102
		"""Set the offset of widget."""
		self.pos = self.start_pos[0] + val[0], self.start_pos[1] + val[1]

	def reset(self) -> None:  # noqa: D102
		"""Reset widget to initial state."""
		self.pos = self.start_pos
		self.anchor = self.start_anchor

	def _bind_mouse(self) -> None:
		self.window.push_handlers(
			on_mouse_press=self._on_mouse_press,
			on_mouse_release=self._on_mouse_release,
			on_mouse_motion=self._on_mouse_motion,
			on_mouse_drag=self._on_mouse_drag,
		)

	def _bind_events(self, **kwargs: EventDispatcher) -> None:
		"""Bind scene and kwarg events to widget.

		Args:
			kwargs (EventDispatcher): The event handlers to attach. Has priority over scene implementation.
		"""
		if not isinstance(self, EventDispatcher):
			raise NotImplementedError(
				f'Widget "{self.__class__.__name__}" cannot have events bound to it.'
			)

		# First check for kwargs to overwrite
		for event, func in kwargs.items():
			if event in self.EVENT_TYPES:
				self.set_handler(event, func) # type: ignore[arg-type] # Why do kwargs do this???
			else:
				raise ValueError(
					f'Event name {event} not in {self.__class__.__name__}.EVENT_TYPES = {self.EVENT_TYPES}.'
				)

		# Next check for scene-wide implementation
		for event in set(self.EVENT_TYPES).difference(kwargs):
			# Check if scene has an implementation with same name
			if callable(func := getattr(self.scene, event, None)): # type: ignore[assignment]
				self.set_handler(event, func)

	@abstractmethod
	def _calc_anchor(self) -> None:
		"""Calculate new anchor and sync position."""

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_press() method.'
		)

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_release() method.'
		)

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_motion() method.'
		)

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> bool:
		raise NotImplementedError(
			f'Widget "{self.__class__.__name__}" does not contain ._on_mouse_drag() method.'
		)

	@abstractmethod
	def enable(self) -> None:
		"""Enable widget."""

	@abstractmethod
	def disable(self) -> None:
		"""Disable widget."""

	@property
	@abstractmethod
	def x(self) -> float:
		"""X position of widget's anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""

	@x.setter
	@abstractmethod
	def x(self, val: float) -> None: ...

	@property
	@abstractmethod
	def y(self) -> float:
		"""Y position of widget's anchor point.

		To set both `.x` and `.y`, use `.pos`
		"""

	@y.setter
	@abstractmethod
	def y(self, val: float) -> None: ...

	@property
	@abstractmethod
	def pos(self) -> Point2D:
		"""Widget's anchor point."""

	@pos.setter
	@abstractmethod
	def pos(self, val: Point2D) -> None: ...

	@property
	@abstractmethod
	def anchor_x(self) -> float:
		"""X position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""

	@anchor_x.setter
	@abstractmethod
	def anchor_x(self, val: float) -> None: ...

	@property
	@abstractmethod
	def anchor_y(self) -> float:
		"""Y position of widget anchor offset.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""

	@anchor_y.setter
	@abstractmethod
	def anchor_y(self, val: float) -> None: ...

	@property
	@abstractmethod
	def anchor(self) -> Point2D:
		"""Widget anchor offset.

		Can be set in px or dynamic.
		"""

	@anchor.setter
	@abstractmethod
	def anchor(self, val: Anchor) -> None: ...

	@property
	@abstractmethod
	def width(self) -> int | float:
		"""Width of widget."""

	@property
	@abstractmethod
	def height(self) -> int | float:
		"""Height of widget."""
