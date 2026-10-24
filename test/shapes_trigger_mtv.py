from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import math

import pyglet
from pyglet.window import key

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.rect import Rect
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.r1 = Rect(
			'Test',
			100,
			100,
			100,
			100,
			(255, 0, 0),
			scene=self,
			mouse_detection=True,
		)
		self.r2 = Rect(
			'Test bg',
			320,
			240,
			80,
			110,
			(0, 0, 255, 100),
			scene=self,
			mouse_detection=False,
		)
		self.objs = []

		self.pressed = key.KeyStateHandler()

		self.window.push_handlers(self.on_mouse_motion)
		self.window.push_handlers(self.pressed)

	def update(self, dt) -> None:
		if (data := self.r1.collide(self.r2))[0]:
			self.r1.render.opacity = self.r2.render.opacity = 255
			self.r1.pos += data[1]
		else:
			self.r1.render.opacity = self.r2.render.opacity = 100

		if self.pressed[key.LEFT]:
			self.r1.angle += math.pi * dt
		if self.pressed[key.RIGHT]:
			self.r1.angle -= math.pi * dt

		if self.pressed[key.A]:
			self.r2.angle += math.pi * dt
		if self.pressed[key.D]:
			self.r2.angle -= math.pi * dt

	def on_mouse_motion(self, x, y, dx, dy) -> None:
		self.r1.pos = x, y

	def disable(self):
		pyglet.clock.unschedule(self.update)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 1200)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
