from abc import ABC, abstractmethod
from typing import Callable

from pyglet.window import Window
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch

class Scene(ABC, EventDispatcher):
	"""Abstract class for a Scene in the game, inherit to create own scenes.
	`Window` object should hold all scenes in window.scenes dictionary.

	When inheriting, a batch must be created for automatic rendering.
	
	Dispatches:
	- 'on_scene_change' (to window) when program wishes to switch scenes.

	`enable` and `disable` run from `Window` class when enabling and disabling scene.
	These enable and disable the scene, but not rendering. This happens in `Window`.

	Use kwargs to attach event handlers.
	"""

	batch: Batch
	"""Batch scene is drawn on"""
	name: str
	"""The name of the scene"""
	window: Window
	"""Window scene is a part of"""
	event_handlers: dict[str, Callable] = {}

	def __init__(self, name: str, window: Window, **kwargs) -> None:
		"""Create a scene.

		Args:
			name (str):
				The name of the scene (used to identity scene by name)
			window (Window):
				The screen window
			**kwargs:
				Event handlers to attach (name=func)
		"""
		self.name, self.window = name, window
		
		# Adds any event handlers passed through kwargs
		self.add_events(**kwargs)
		
	def add_events(self, **kwargs: Callable) -> None:
		for name, handler in kwargs.items():
			self.event_handlers[name] = handler
			self.register_event_type(name)
		self.push_handlers(**kwargs)

	def remove_events(self, *args: str) -> None:
		for name in args:
			self.remove_handler(name, self.event_handlers.pop(name))

	@abstractmethod
	def enable(self) -> None:
		"""Enables this scene. (does not enable rendering)"""
	@abstractmethod
	def disable(self) -> None:
		"""Disables this scene. (does not disable rendering)"""
