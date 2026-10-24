from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

from pyglet.shapes import Rectangle

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.collision.trigger import Trigger
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.t = Trigger.from_rect(
			'Test',
			100,
			100,
			300,
			300,
			scene=self,
		)
		self.objs = []

	def on_mouse_trigger_enter(self, trigger, x, y, MTV):
		print(f'Mouse entered {trigger.ID} @ ({x}, {y})')

	def on_mouse_trigger_motion(self, trigger, x, y, MTV):
		self.objs.append(
			Rectangle(*self.t._last_mouse_info[:2], 1, 1, batch=self.batch)
		)

	def on_mouse_trigger_exit(self, trigger, x, y):
		print(f'Mouse exited {trigger.ID} @ ({x}, {y})')

	def disable(self): ...

	def enable(self): ...


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
