from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

from pyglet.graphics import Group
from pyglet.shapes import Circle
from pyglet.window import key

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.types import Color
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	WIDGET_POS = {'Test': (0.5, 0.5)}

	def initialize(self):
		self.entry = self.create_entry(
			'Test',
			'Start Test!',
			250,
			('.5', '.5'),
			font_info=(None, None),
			color=Color.GRAY,
		)

		self.debug_group = Group(3, self.UI_group)

		self.anchor = Circle(
			*self.entry.pos,
			10,
			color=(0, 255, 255),
			batch=self.batch,
			group=self.debug_group,
		)

		self.window.push_handlers(self.on_key_press)

	def on_key_press(self, symbol, modifiers):
		if self.entry.focus:
			return

		if symbol == key.A:
			self.entry.x -= 10
		elif symbol == key.D:
			self.entry.x += 10
		elif symbol == key.W:
			self.entry.y += 10
		elif symbol == key.S:
			self.entry.y -= 10
		elif symbol == key.LEFT:
			self.entry.anchor_x -= 10
		elif symbol == key.RIGHT:
			self.entry.anchor_x += 10
		elif symbol == key.UP:
			self.entry.anchor_y += 10
		elif symbol == key.DOWN:
			self.entry.anchor_y -= 10
		elif symbol == key.C:
			self.entry.clear()
		elif symbol == key.V:
			self.entry.reset(pos=False)
		elif symbol == key.R:
			self.entry.reset()
		elif symbol == key.BRACKETLEFT:
			self.entry.scale -= 1
		elif symbol == key.BRACKETRIGHT:
			self.entry.scale += 1
		else:
			return

		print(self.entry)
		self.anchor.position = self.entry.pos

	def on_submit(self, entry, text):
		print(f'{self.__class__.__name__}: {entry.ID} submitted! "{text}"')

	def enable(self):
		for widget in self.widgets.values():
			widget.enable()

	def disable(self):
		for widget in self.widgets.values():
			widget.disable()


scene1 = Scene1('Scene1')

window = Window(640, 480)
window.add_scene(scene1)
window.run()
