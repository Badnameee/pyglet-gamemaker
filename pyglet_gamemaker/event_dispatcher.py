from __future__ import annotations

from pyglet.event import EventDispatcher as _EventDispatcher


class EventDispatcher(_EventDispatcher):
	EVENT_TYPES: tuple[str, ...] = ()
	"""The event names that a widget can dispatch"""
