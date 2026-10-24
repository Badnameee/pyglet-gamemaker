from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet
from pyglet.shapes import Circle, Rectangle
from pyglet.window import key

from pyglet_gamemaker.camera import Camera
from pyglet_gamemaker.gui.text import Text
from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.window import Window

window = Window(camera=Camera(anchor_x=640, anchor_y=360))


class Scene1(Scene):
	WIDGET_POS = {'hud': (0, 1)}

	def initialize(self):
		self.items = [
			Rectangle(100, 100, 300, 300, (255, 255, 255, 255), batch=self.batch),
			Rectangle(50, 500, 150, 50, (0, 255, 255, 255), batch=self.batch),
			Circle(640, 360, 300, color=(255, 255, 0), batch=self.batch),
		]
		self.items[0].z = -250

		self.txt = Text(
			'hud',
			'This is HUD!',
			scene=self,
			group=self.HUD_group,
			anchor=('left', 'top'),
			font_info=(None, 30),
		)

		self.speed = 500

		self.pressed = key.KeyStateHandler()
		self.window.push_handlers(self.pressed)

	def update(self, dt):
		move = self.speed * dt
		scale = 1 + dt
		rotate = dt

		if self.pressed[key.A]:
			self.window.camera.move(x=-move)
		if self.pressed[key.D]:
			self.window.camera.move(x=move)
		if self.pressed[key.W]:
			self.window.camera.move(y=move)
		if self.pressed[key.S]:
			self.window.camera.move(y=-move)
		if self.pressed[key.J]:
			self.window.camera.zoom(x=1 / scale)
		if self.pressed[key.L]:
			self.window.camera.zoom(x=scale)
		if self.pressed[key.I]:
			self.window.camera.zoom(y=scale)
		if self.pressed[key.K]:
			self.window.camera.zoom(y=1 / scale)
		if self.pressed[key.EQUAL]:
			self.window.camera.zoom(scale, scale)
		if self.pressed[key.MINUS]:
			self.window.camera.zoom(1 / scale, 1 / scale)
		if self.pressed[key.COMMA]:
			self.window.camera.rotate(z=-rotate)
		if self.pressed[key.PERIOD]:
			self.window.camera.rotate(z=rotate)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 60)

	def disable(self):
		pyglet.clock.unschedule(self.update)


scene1 = Scene1('Scene1')
window.add_scene(scene1)
window.run()
