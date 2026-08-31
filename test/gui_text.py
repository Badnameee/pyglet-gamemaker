from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import random
import string

from pyglet.shapes import Circle
from pyglet.window import key

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	WIDGET_POS = {'Test': (0, 0)}

	def initialize(self):
		self.txt = self.create_text(
			'Test',
			'Hello World',
			('.5', '.5'),
			('Arial', 50),
			add_to_widget_dict=False,
		)

		self.txt_anchor = Circle(
			*self.txt.pos,
			10,
			color=(0, 255, 255),
			batch=self.batch,
			group=self.UI_group,
		)

		self.window.push_handlers(self)

	def on_mouse_motion(self, x, y, dx, dy):
		self.txt.pos = x, y
		self.txt_anchor.position = self.txt.pos
		print(self.txt)

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.txt.pos = x, y
		self.txt_anchor.position = self.txt.pos
		print(self.txt)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.LEFT:
			self.txt.anchor_x -= 10
		elif symbol == key.RIGHT:
			self.txt.anchor_x += 10
		elif symbol == key.UP:
			self.txt.anchor_y += 10
		elif symbol == key.DOWN:
			self.txt.anchor_y -= 10
		elif symbol == key.A:
			self.txt.rotation -= 10
		elif symbol == key.D:
			self.txt.rotation += 10
		elif symbol == key.R:
			self.txt.reset(pos=False)
		elif symbol == key.P:
			self.txt.text += random.choice(string.ascii_lowercase)
		elif symbol == key.O:
			self.txt.text = self.txt.text[:-1]
		elif symbol == key.BRACKETLEFT:
			self.txt.scale -= 1
		elif symbol == key.BRACKETRIGHT:
			self.txt.scale += 1
		else:
			return

		print(self.txt)
		self.txt_anchor.position = self.txt.pos

	def disable(self):
		self.txt.disable()

	def enable(self):
		self.txt.enable()


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
