from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())


from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.rect import Rect
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.r1 = Rect(
			'Test',
			100,
			100,
			300,
			300,
			(255, 0, 0),
			self.window,
			self,
			self.batch,
			self.main_group,
			mouse_detection=True,
		)
		self.r2 = Rect(
			'Test bg',
			100,
			100,
			300,
			300,
			(255, 0, 0, 100),
			self.window,
			self,
			self.batch,
			self.main_group,
			mouse_detection=False,
		)
		self.objs = []

	def on_mouse_trigger_enter(self, trigger, x, y, MTV):
		print(f'Mouse entered {trigger.ID} @ ({x}, {y})')
		self.r1.pos += MTV

	def on_mouse_trigger_motion(self, trigger, x, y, MTV):
		print(f'Mouse moved in {trigger.ID} @ ({x}, {y})')
		self.r1.pos += MTV

	def on_mouse_trigger_exit(self, trigger, x, y):
		print(f'Mouse exited {trigger.ID} @ ({x}, {y})')
		self.r1.pos = self.r2.pos
		self.r1.trigger._update_mouse_collision(x, y)

	def disable(self): ...

	def enable(self): ...


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
