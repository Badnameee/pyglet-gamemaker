from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet
from pyglet.window import key

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.hitbox import HitboxRender
from pyglet_gamemaker.shapes.rect import Rect
from pyglet_gamemaker.types import Color
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.rect = Rect(
			'r1',
			100,
			100,
			100,
			50,
			Color.WHITE,
			self.window,
			None,
			self.batch,
			self.main_group,
		)
		self.hitbox2 = HitboxRender.from_rect(
			'hb1',
			300,
			300,
			100,
			50,
			Color.RED,
			self.window,
			None,
			self.batch,
			self.main_group,
		)

		self.window.push_handlers(self)

	def update(self, dt):
		if self.rect.collide(self.hitbox2)[0]:
			self.rect.render.opacity = 128
		else:
			self.rect.render.opacity = 255

	def on_mouse_motion(self, x, y, dx, dy):
		self.rect.pos = x, y
		print(self.rect)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.A:
			self.rect.anchor_x -= 10
		elif symbol == key.D:
			self.rect.anchor_x += 10
		elif symbol == key.W:
			self.rect.anchor_y += 10
		elif symbol == key.S:
			self.rect.anchor_y -= 10
		elif symbol == key.LEFT:
			self.rect.angle -= 0.1
		elif symbol == key.RIGHT:
			self.rect.angle += 0.1

		elif symbol == key.J:
			self.rect.width -= 10
		elif symbol == key.L:
			self.rect.width += 10
		elif symbol == key.I:
			self.rect.height += 10
		elif symbol == key.K:
			self.rect.height -= 10

		print(self.rect)

	def disable(self):
		pyglet.clock.unschedule(self.update)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 60)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
