"""Module holding Scene class.

Use `~pgm.Scene` instead of `~pgm.scene.Scene`
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pyglet.graphics import Batch, Group

from .event_dispatcher import EventDispatcher

if TYPE_CHECKING:
	from typing import Any

	from .gui.widget import Widget
	from .types import EventHandler, FontInfo
	from .window import Window


class Scene(EventDispatcher, ABC):
	"""Abstract class for a Scene in the game, inherit to create own scenes.

	`~pgm.Window` object should hold all scenes in window.scenes dictionary.

	Creates its own batch and groups:
	- `.batch`
	- `.bg_group` - For backgrounds and stuff in the back
	- `.main_group` - Main purpose group
	- `.UI_group` - For all UI
		- `.button_group`
		- `.entry_group`
		- `.text_group`

	Required Variables:
	- `.WIDGET_POS`: Positions of widgets as scale to window (see `.WIDGET_POS`)
	- `.DEFAULT_FONT_INFO`: The default font information used if none passed into methods

	Required Methods (**do not override `.__init__`**):
	- `.initialize()`: The initializer that runs when adding scene to window
	- `.enable()`: Enable scene (not rendering, just logic)
	- `.disable()`: Disable scene (not rendering, just logic)

	Dispatches:
	- `on_scene_change` (to window) when program wishes to switch scenes.
		- Args:
			- Name of new scene to switch to
			- Any args for extra data to be sent to `.enable(...)`. Note scenes have access to window and can retrieve data manually from there.

	Use kwargs to attach event handlers.
	"""

	# * Constant vars
	WIDGET_POS: dict[str, tuple[float, float]]
	"""Stores the position of every widget as a scale {id: (scale_x, scale_y)}.

	Ex. `'Test': (0.5, 0.5)` is the center of the window.
	"""
	DEFAULT_FONT_INFO: FontInfo = None, None, None
	"""The default font info if none passed to widget, overrides `~pgm.gui.Widget.DEFAULT_FONT_INFO`. Scene must be passed into widget to function."""
	EVENT_TYPES = ('on_scene_change',)

	# * Instance vars
	name: str
	"""The name of the scene"""
	window: Window
	"""Window scene is a part of"""
	batch: Batch
	"""Batch scene is drawn on"""
	main_group: Group
	"""Rendering group for everything not UI"""
	bg_group: Group
	"""Rendering subgroup for the background"""
	UI_group: Group
	"""Rendering group for all UI"""
	button_group: Group
	"""Rendering subgroup for buttons"""
	text_group: Group
	"""Rendering subgroup for text"""
	entry_group: Group
	"""Rendering subgroup for entries"""
	widgets: dict[str, Widget]
	"""Stores all widgets in the menu"""

	def __init__(self, name: str, **kwargs: EventHandler) -> None:
		"""Create a scene.

		Args:
			name (str):
				The name of the scene (used to identity scene by name)
			**kwargs (EventHandler):
				Event handlers to attach (name=func)
		"""
		self.name = name
		self.widgets = {}

		self.batch = Batch()
		self.bg_group = Group(0)
		self.main_group = Group(1)
		self.UI_group = Group(2)
		self.button_group = Group(0, self.UI_group)
		self.entry_group = Group(1, self.UI_group)
		self.text_group = Group(2, self.UI_group)

		# Adds any event handlers passed through kwargs
		self.register_events(**kwargs)
		self.set_handlers(**kwargs)

	def set_window(self, window: Window) -> None:
		"""Set the window the Scene will use.

		Args:
			window (Window):
				The screen window
		"""
		self.window = window

		# Call user method initialize
		self.initialize()

	def on_scene_change(self, new_scene: str, *args: Any, **kwargs: Any) -> None:
		"""A middleman between event dispatch and `window._on_scene_change`.

		Args:
			new_scene (str):
				The new scene name
			*args (Any):
				Any extra data
			**kwargs (Any):
				Any extra data
		"""  # noqa: D401
		self.window._on_scene_change(new_scene, *args, **kwargs)

	@abstractmethod
	def initialize(self) -> None:
		"""Initialize the scene."""

	@abstractmethod
	def enable(self) -> None:
		"""Enable this scene (does not enable rendering)."""

	@abstractmethod
	def disable(self) -> None:
		"""Disable this scene (does not disable rendering)."""
