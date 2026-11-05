"""Module holding Scene class.

Use `~pgm.Scene` instead of `~pgm.scene.Scene`
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pyglet.graphics import Batch, Group

from pyglet_gamemaker.base_object import BaseObject
from pyglet_gamemaker.types import DynamicPoint2D

from .gui import HUDGroup

if TYPE_CHECKING:
	from typing import Any

	from .gui.widget import Widget
	from .types import EventHandler, FontInfo
	from .window import Window


class Scene(ABC):
	"""Abstract class for a Scene in the game, inherit to create own scenes.

	`~pgm.Window` object should hold all scenes in window.scenes dictionary.

	Creates its own batch and groups:
	- `.batch`
	- `.bg_group` - For backgrounds and stuff in the back
	- `.main_group` - Main purpose group
	- `.GUI_group` - For all UI
		- `.button_group`
		- `.entry_group`
		- `.text_group`
	- `.HUD_group` - All HUD items, special as it ignores view matrix

	Vars:
	- `.WIDGET_POS`: Positions of widgets as scale to window (see `.WIDGET_POS`)
	- `.DEFAULT_FONT_INFO`: The default font information used if none passed into methods

	Methods:
	- `.change_scene()`: Change the scene to a new one. Can pass in extra data that gets passed to `new_scene.enable()`.
		Additionally, scenes can access the window, scenes can directly see other scene data.

	Required Methods (**do not override `.__init__`**):
	- `.initialize()`: The initializer that runs when adding scene to window
	- `.enable()`: Enable scene (not rendering, just logic)
	- `.disable()`: Disable scene (not rendering, just logic)

	Use kwargs to attach event handlers.
	"""

	#* CONSTS
	WIDGET_POS: dict[str, DynamicPoint2D]
	"""Stores the position of every widget as a static/dynamic position.

	Does not implement dynamic presets. See `~pgm.gui.widget.Widget` for more information.

	Ex. `'Test': ('0.5', '0.5')` is the center of the window.
	"""
	DEFAULT_FONT_INFO: FontInfo = BaseObject.DEFAULT_FONT_INFO
	"""The default font info if none passed to widget, overrides `~pgm.gui.Widget.DEFAULT_FONT_INFO`. Scene must be passed into widget to function."""

	#* Instance vars
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
	GUI_group: Group
	"""Rendering group for all UI"""
	button_group: Group
	"""Rendering subgroup for buttons"""
	text_group: Group
	"""Rendering subgroup for text"""
	entry_group: Group
	"""Rendering subgroup for entries"""
	HUD_group: HUDGroup
	"""Rendering group for HUD objects, ignores view matrix"""
	widgets: dict[str, Widget]
	"""Stores all widgets in the menu"""

	def __init__(self, name: str) -> None:
		"""Create a scene.

		Args:
			name (str):
				The name of the scene (used to identity scene by name)
		"""
		self.name = name
		self.widgets = {}

		self.batch = Batch()
		self.bg_group = Group(0)
		self.main_group = Group(1)
		self.GUI_group = Group(2)
		self.button_group = Group(0, self.GUI_group)
		self.entry_group = Group(1, self.GUI_group)
		self.text_group = Group(2, self.GUI_group)
		self.HUD_group = HUDGroup(3)

	def set_window(self, window: Window) -> None:
		"""Set the window the Scene will use.

		Args:
			window (Window):
				The screen window
		"""
		self.HUD_group.window = self.window = window

		# Call user method initialize
		self.initialize()

	def change_scene(self, new_scene: str, *args: Any, **kwargs: Any) -> None:
		"""Switch scene to new scene.

		Args:
			new_scene (str):
				The new scene name
			*args (Any):
				Any extra data
			**kwargs (Any):
				Any extra data
		"""
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
