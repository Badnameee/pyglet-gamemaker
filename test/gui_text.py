from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import random
import string

import pyglet
from pyglet.shapes import Circle
from pyglet.window import key

from pyglet_gamemaker.gui.text import Text
from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	WIDGET_POS = {'Test': (0, 0)}

	def initialize(self):
		self.txt = Text(
			'Test',
			'Hello World',
			scene=self,
			anchor=('.5', '.5'),
			font_info=('Arial', 50),
		)

		self.txt_anchor = Circle(
			*self.txt.pos,
			10,
			color=(0, 255, 255),
			batch=self.batch,
			group=self.GUI_group,
		)

		self.pressed = key.KeyStateHandler()

		self.window.push_handlers(self)
		self.window.push_handlers(self.pressed)

		self.rotation_speed = 180 # deg/s
		self.anchor_speed = 100 # px/s
		self.scale_speed = 2 # factor/s

	def update(self, dt):
		if self.pressed[key.LEFT]:
			self.txt.anchor_x += self.anchor_speed * dt
		if self.pressed[key.RIGHT]:
			self.txt.anchor_x -= self.anchor_speed * dt
		if self.pressed[key.UP]:
			self.txt.anchor_y += self.anchor_speed * dt
		if self.pressed[key.DOWN]:
			self.txt.anchor_y -= self.anchor_speed * dt
		if self.pressed[key.A]:
			self.txt.rotation -= self.rotation_speed * dt
		if self.pressed[key.D]:
			self.txt.rotation += self.rotation_speed * dt
		if self.pressed[key.BRACKETLEFT]:
			self.txt.scale *= (self.scale_speed-1) * dt + 1
		if self.pressed[key.BRACKETRIGHT]:
			self.txt.scale /= (self.scale_speed-1) * dt + 1
		print(self.txt)

	def on_mouse_motion(self, x, y, dx, dy):
		self.txt.pos = x, y
		self.txt_anchor.position = self.txt.pos

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.txt.pos = x, y
		self.txt_anchor.position = self.txt.pos

	def on_key_press(self, symbol, modifiers):
		if symbol == key.R:
			self.txt.reset(pos=False)
		elif symbol == key.P:
			self.txt.text += random.choice(string.ascii_lowercase)
		elif symbol == key.O:
			self.txt.text = self.txt.text[:-1]
		else:
			return

		print(self.txt)
		self.txt_anchor.position = self.txt.pos

	def disable(self):
		self.txt.disable()
		pyglet.clock.unschedule(self.update)

	def enable(self):
		self.txt.enable()
		pyglet.clock.schedule_interval(self.update, 1/60)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
