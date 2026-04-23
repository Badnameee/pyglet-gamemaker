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
		self.create_entry(
			'Test',
			'Start Test!',
			250,
			font_info=(None, None),
			color=Color.GRAY,
		)

		self.debug_group = Group(3, self.UI_group)

		self.anchor = Circle(
			*self.widgets['Test'].pos,
			10,
			color=(0, 255, 255),
			batch=self.batch,
			group=self.debug_group,
		)

		self.window.push_handlers(self.on_key_press)

	def on_key_press(self, symbol, modifiers):
		if self.widgets['Test'].focus:
			return
		if symbol == key.A:
			self.widgets['Test'].offset((-10, 0))
		elif symbol == key.D:
			self.widgets['Test'].offset((10, 0))
		elif symbol == key.W:
			self.widgets['Test'].offset((0, 10))
		elif symbol == key.S:
			self.widgets['Test'].offset((0, -10))
		elif symbol == key.LEFT:
			self.widgets['Test'].anchor_x -= 10
		elif symbol == key.RIGHT:
			self.widgets['Test'].anchor_x += 10
		elif symbol == key.UP:
			self.widgets['Test'].anchor_y += 10
		elif symbol == key.DOWN:
			self.widgets['Test'].anchor_y -= 10
		elif symbol == key.C:
			self.widgets['Test'].clear()
		elif symbol == key.V:
			self.widgets['Test'].reset(pos=False)
		elif symbol == key.R:
			self.widgets['Test'].reset()
		else:
			return

		print(f'New entry pos: {self.widgets["Test"].pos}')
		self.anchor.position = self.widgets['Test'].pos

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
window.add_scene('Scene1', scene1)
window.run()
