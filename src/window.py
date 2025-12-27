from typing import TYPE_CHECKING

import pyglet
from pyglet.window import Window as PygletWin
if TYPE_CHECKING:
	from .scene import Scene


class Window(PygletWin):

	scenes: dict[str, Scene] = {}
	scene: str = ''

	centered: bool

	def __init__(self,
			window_dim: tuple[int, int],
			center_window: bool=True,
			**kwargs
	) -> None:
		super().__init__(*window_dim, **kwargs) # type: ignore[call-arg]

		# Center if requested
		self.centered = center_window
		if center_window:
			self.set_location(
				(self.screen.width - window_dim[0]) // 2,
				(self.screen.height - window_dim[1]) // 2
			)

	def start(self, start_scene: str | None=None) -> None:
		if not self.scenes:
			raise RuntimeError('Window.scenes must have at least 1 scene!')
		
		# Set start scene if needed
		if start_scene:
			self.scene = start_scene
		
		# Enable beginning scene
		self.scenes[self.scene].enable()

		pyglet.app.run()

	def on_draw(self) -> None:
		self.clear()
		self.scenes[self.scene].batch.draw()

	def add_scene(self, name: str, obj: Scene) -> None:
		self.scenes[name] = obj
		obj.add_event_handlers(on_scene_change=self.on_scene_change)
		if self.scene == '':
			self.scene = name
		obj.disable()

	def pop_scene(self, name: str) -> Scene:
		return self.scenes.pop(name)

	def on_scene_change(self, new_scene: str) -> None:
		# Disable previous scene
		self.scenes[self.scene].disable()
		# Update scene
		self.scene = new_scene
		# Enable new scene
		self.scenes[self.scene].enable()
