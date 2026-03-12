"""Module holding window class.

Use `~pgm.Window` instead of `~pgm.window.Window`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyglet
from pyglet.window import Window as PygletWin

if TYPE_CHECKING:
	from typing import Any

	from pyglet.display.base import Display, Screen, ScreenMode
	from pyglet.gl.base import Config, Context

	from .scene import Scene
	from .types import EventHandler


class Window(PygletWin):
	"""The main window that stores the scenes and runs the game.

	The way scenes communicate is through event dispatches. Each scene dispatches
	`on_scene_change` to the window with the new Scene name. extra arguments can also be passed
	if data transfer is necessary. Each Scene also gets a copy of the window object, so data can be
	transferred in that way as well.

	Add scenes using `.add_scene` and remove using `.pop_scenes`.

	Use `.run` to run the game.
	"""

	scenes: dict[str, Scene] = {}
	"""Stores all the scenes in the game"""
	scene: str = ''
	"""The currently running scene"""

	centered: bool
	"""If True, the window is centered. Do not set."""

	def __init__(
		self,
		width: int | None = None,
		height: int | None = None,
		center_window: bool = True,
		caption: str | None = None,
		resizable: bool = False,
		style: str | None = PygletWin.WINDOW_STYLE_DEFAULT,
		fullscreen: bool = False,
		visible: bool = True,
		vsync: bool = True,
		file_drops: bool = False,
		display: Display | None = None,
		screen: Screen | None = None,
		config: Config | None = None,
		context: Context | None = None,
		mode: ScreenMode | None = None,
		**kwargs: EventHandler,
	) -> None:
		"""Create a Window object.

		Copied from `~pyglet.window.BaseWindow`

		Args:
			width (int | None, optional):
				Width of the window, in pixels.
				Defaults to 960, or the screen width if ``fullscreen`` is True.
			height (int | None, optional):
				Height of the window, in pixels.
				Defaults to 540, or the screen height if ``fullscreen`` is True.
			center_window (bool, optional):
				If True, center the window on the screen.
				Defaults to True.
			caption (str | None, optional):
				Initial caption (title) of the window.
				Defaults to ``sys.argv[0]``.
			resizable (bool | None, optional):
				If True, the window will be resizable.
				Defaults to False.
			style (str | None, optional):
				One of the ``~pyglet.window.Window.WINDOW_STYLE_*`` constants specifying
				the border style of the window.
			fullscreen (bool | None, optional):
				If True, the window will cover the entire screen rather than floating.
				Defaults to False.
			visible (bool | None, optional):
				Determines if the window is visible immediately after creation.
				Defaults to True.
				Set this to False if you would like to change attributes of the window
				before having it appear to the user.
			vsync (bool | None, optional):
				If True, buffer flips are synchronised to the primary screen's
				vertical retrace, eliminating flicker.
			file_drops (bool | None, optional):
				If True, the Window will accept files being dropped into it and call
				the ``on_file_drop`` event.
			display (Display, optional):
				The display device to use. Useful only under X11.
			screen (Screen, optional):
				The screen to use, if in fullscreen.
			config (Config, optional):
				Either a template from which to create a complete config, or a
				complete config.
			context (Context, optional):
				The context to attach to this window. The context must not already
				be attached to another window.
			mode (ScreenMode, optional):
				The screen will be switched to this mode if `fullscreen` is True.
				If None, an appropriate mode is selected to accommodate ``width``
				and ``height``.
			**kwargs (EventHandler):
				Any extra arguments to add to pyglet window constructor.
				Read `pyglet.window.Window` documentation or see
				https://pyglet.readthedocs.io/en/latest/programming_guide/windowing.html
				for more.
		"""
		super().__init__(
			width,
			height,
			caption,
			resizable,
			style,
			fullscreen,
			visible,
			vsync,
			file_drops,
			display,
			screen,
			config,
			context,
			mode,
			**kwargs,
		)

		# Center if requested
		self.centered = center_window
		if center_window:
			self.set_location(
				(self.screen.width - self.width) // 2,
				(self.screen.height - self.height) // 2,
			)

	def run(self, start_scene: str | None = None) -> None:
		"""Run the game.

		Args:
			start_scene (str | None, optional):
				The scene to start on.
				Defaults to None.
		"""
		if not self.scenes:
			raise RuntimeError('Window.scenes must have at least 1 scene!')

		# Set start scene if needed
		if start_scene:
			self.scene = start_scene

		# Enable beginning scene
		self.scenes[self.scene].enable()

		pyglet.app.run()

	def on_draw(self) -> None:  # noqa: D102
		self.clear()
		self.scenes[self.scene].batch.draw()

	def add_scene(self, name: str, obj: Scene) -> None:
		"""Add a scene to the game.

		Args:
			name (str): The name of the scene
			obj (Scene): The Scene object
		"""
		self.scenes[name] = obj
		obj.set_window(self)
		obj.add_event_handlers(on_scene_change=self._on_scene_change)
		obj.disable()

		# Sets default scene
		if self.scene == '':
			self.scene = name

	def pop_scene(self, name: str) -> Scene:
		"""Pop and return a scene from the game.

		Args:
			name (str): The name of the scene

		Returns:
			Scene: The Scene object removed
		"""
		return self.scenes.pop(name)

	def _on_scene_change(self, new_scene: str, *args: Any, **kwargs: Any) -> None:
		# Runs when the scene needs to be changed to a new one
		# 	Arbitrary data can be passed if more information is needed

		# Disable previous scene
		self.scenes[self.scene].disable()
		# Update scene
		self.scene = new_scene
		# Enable new scene
		self.scenes[self.scene].enable(*args, **kwargs)
