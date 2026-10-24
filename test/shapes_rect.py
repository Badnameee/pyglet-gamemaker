from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import math

import pyglet
from pyglet.window import key

from pyglet_gamemaker import colors
from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.collision.hitbox import Hitbox
from pyglet_gamemaker.collision.rect import Rect
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.rect = Rect(
			'r1',
			100,
			100,
			100,
			50,
			colors.WHITE,
			scene=self,
		)
		self.hitbox = Hitbox.from_rect(
			'hb1',
			300,
			300,
			100,
			50,
			colors.RED,
			scene=self,
		)

		self.pressed = key.KeyStateHandler()

		self.window.push_handlers(self)
		self.window.push_handlers(self.pressed)

	def update(self, dt):
		if self.pressed[key.LEFT]:
			self.rect.angle += math.pi * dt
		if self.pressed[key.RIGHT]:
			self.rect.angle -= math.pi * dt

		if self.rect.collide(self.hitbox)[0]:
			self.rect.render.opacity = 128
		else:
			self.rect.render.opacity = 255

	def on_mouse_motion(self, x, y, dx, dy):
		self.rect.pos = x, y
		# print(self.rect)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.A:
			self.rect.anchor_x -= 10
		elif symbol == key.D:
			self.rect.anchor_x += 10
		elif symbol == key.W:
			self.rect.anchor_y += 10
		elif symbol == key.S:
			self.rect.anchor_y -= 10

		elif symbol == key.J:
			self.rect.width -= 10
		elif symbol == key.L:
			self.rect.width += 10
		elif symbol == key.I:
			self.rect.height += 10
		elif symbol == key.K:
			self.rect.height -= 10
		else:
			return

		print(self.rect)

	def on_trigger_enter(self, t1, t2, MTV):
		print(f'{t1.ID} entered {t2.ID}!')

	def on_trigger_exit(self, t1, t2):
		print(f'{t1.ID} exited {t2.ID}!')

	def disable(self):
		pyglet.clock.unschedule(self.update)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 60)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
