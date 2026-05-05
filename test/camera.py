from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

from pyglet.shapes import Circle, Rectangle

from pyglet_gamemaker.camera import Camera
from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.window import Window

window = Window(camera=Camera(anchor_x=640, anchor_y=360))


class Scene1(Scene):
	def initialize(self):
		self.items = [
			Rectangle(100, 100, 300, 300, (255, 255, 255, 255), batch=self.batch),
			Rectangle(50, 500, 150, 50, (0, 255, 255, 255), batch=self.batch),
			Circle(640, 360, 300, color=(255, 255, 0), batch=self.batch),
		]
		self.items[0].z = -250
		self.window.on_text = self.on_text

	def on_text(self, txt):
		if txt == 'a':
			self.window.camera.move(x=-5)
		if txt == 'd':
			self.window.camera.move(x=5)
		if txt == 'w':
			self.window.camera.move(y=5)
		if txt == 's':
			self.window.camera.move(y=-5)
		if txt == 'j':
			self.window.camera.zoom(x=1 / 2)
		if txt == 'l':
			self.window.camera.zoom(x=2)
		if txt == 'i':
			self.window.camera.zoom(y=2)
		if txt == 'k':
			self.window.camera.zoom(y=1 / 2)
		if txt == '=':
			self.window.camera.zoom(2, 2, 0)
		if txt == '-':
			self.window.camera.zoom(1 / 2, 1 / 2, 0)
		if txt == ',':
			self.window.camera.rotate(z=-0.1)
		if txt == '.':
			self.window.camera.rotate(z=0.1)

	def enable(self): ...
	def disable(self): ...


scene1 = Scene1('Scene1')
window.add_scene('Scene1', scene1)
window.run()
