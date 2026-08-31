from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet
from pyglet.window import key

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.hitbox import HitboxRenderCircle
from pyglet_gamemaker.types import Color
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.circle = HitboxRenderCircle(
			'hbc1', 100, 100, 50, Color.WHITE, window, None, self.batch, self.main_group
		)
		self.circle2 = HitboxRenderCircle(
			'hbc2', 300, 300, 50, Color.RED, window, None, self.batch, self.main_group
		)

		self.window.push_handlers(self)

	def update(self, dt):
		if self.circle.collide(self.circle2)[0]:
			self.circle.render.opacity = 128
		else:
			self.circle.render.opacity = 255

	def on_mouse_motion(self, x, y, dx, dy):
		self.circle.pos = x, y
		print(self.circle)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.A:
			self.circle.anchor_x -= 10
		elif symbol == key.D:
			self.circle.anchor_x += 10
		elif symbol == key.W:
			self.circle.anchor_y += 10
		elif symbol == key.S:
			self.circle.anchor_y -= 10
		elif symbol == key.LEFT:
			self.circle.angle -= 0.1
		elif symbol == key.RIGHT:
			self.circle.angle += 0.1
		print(self.circle)

	def disable(self):
		pyglet.clock.unschedule(self.update)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 60)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
