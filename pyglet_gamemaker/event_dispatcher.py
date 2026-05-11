"""Module holding event dispatcher class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.event import EventDispatcher as _EventDispatcher

if TYPE_CHECKING:
	from .scene import Scene
	from .types import EventHandler
	from .window import Window


class EventDispatcher(_EventDispatcher):
	"""Fork of `pyglet.event.EventDispatcher` allowing for automatic integration with pgm.

	Methods:
	- `.register_events` : register several events at once
	- `.bind_events` : Bind **kwargs and scene methods
	"""

	EVENT_TYPES: tuple[str, ...] = ()
	"""The event names that a widget can dispatch"""

	_events_registered = False
	"""Holds whether events have been registered yet"""

	window: Window
	"""Window dispatcher is associated with"""
	scene: Scene | None
	"""The scene the dispatcher is from. None if part of a template or not in a scene."""

	@classmethod
	def register_events(cls) -> None:
		"""Register event types for class."""
		# Don't add if None to register or already registered
		if cls._events_registered or not cls.EVENT_TYPES:
			return

		# Register all event types beforehand
		cls._events_registered = True
		for event in cls.EVENT_TYPES:
			cls.register_event_type(event)

	def bind_events(self, **kwargs: EventHandler) -> None:
		"""Bind scene and kwarg events to widget. **kwargs must be in `.EVENT_TYPES`.

		Args:
			kwargs (EventDispatcher):
				The event handlers to attach. Has priority over scene implementation.
		"""
		# First check for kwargs to overwrite
		for event, func in kwargs.items():
			if event in self.EVENT_TYPES:
				self.set_handler(event, func)
			else:
				raise ValueError(
					f'Event name {event} not in {self.__class__.__name__}.EVENT_TYPES = {self.EVENT_TYPES}.'
				)

		# Next check for scene-wide implementation
		for event in self.EVENT_TYPES:
			# Already added above
			if event in kwargs:
				continue
			# Check if scene has an implementation with same name
			if callable(func := getattr(self.scene, event, None)):  # type: ignore[assignment]
				self.set_handler(event, func)
