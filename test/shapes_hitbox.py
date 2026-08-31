from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet
from pyglet.window import key

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.hitbox import HitboxRender, HitboxRenderCircle
from pyglet_gamemaker.types import Color
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.hitbox = HitboxRender.from_rect(
			'hb1',
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
			'hb2',
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
		self.circle = HitboxRenderCircle(
			'hbc1',
			100,
			100,
			50,
			Color.WHITE,
			self.window,
			None,
			self.batch,
			self.main_group,
		)
		self.circle.render.visible = False

		self.mode = 'rect'

		self.window.push_handlers(self)

	def update(self, dt):
		if self.mode == 'rect':
			if self.hitbox.collide(self.hitbox2)[0]:
				self.hitbox.render.opacity = 128
			else:
				self.hitbox.render.opacity = 255
		elif self.mode == 'circle':
			if self.hitbox2.collide(self.circle)[0]:
				self.circle.render.opacity = 128
			else:
				self.circle.render.opacity = 255

	def on_mouse_motion(self, x, y, dx, dy):
		self.hitbox.pos = x, y
		self.circle.pos = x, y
		print(self.hitbox if self.mode == 'rect' else self.circle)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.A:
			self.hitbox.anchor_x -= 10
			self.circle.anchor_x -= 10
		elif symbol == key.D:
			self.hitbox.anchor_x += 10
			self.circle.anchor_x += 10
		elif symbol == key.W:
			self.hitbox.anchor_y += 10
			self.circle.anchor_y += 10
		elif symbol == key.S:
			self.hitbox.anchor_y -= 10
			self.circle.anchor_y -= 10
		elif symbol == key.LEFT:
			self.hitbox.angle -= 0.1
			self.circle.angle -= 0.1
		elif symbol == key.RIGHT:
			self.hitbox.angle += 0.1
			self.circle.angle += 0.1

		if symbol == key.C:
			self.mode = 'circle' if self.mode == 'rect' else 'rect'
			if self.mode == 'rect':
				self.hitbox.render.visible = True
				self.circle.render.visible = False
			elif self.mode == 'circle':
				self.hitbox.render.visible = False
				self.circle.render.visible = True

		print(self.rect)

	def disable(self):
		pyglet.clock.unschedule(self.update)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 60)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
