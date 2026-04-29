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
		
		entry = self.widgets['Test']

		if symbol == key.A:
			entry.offset((-10, 0))
		elif symbol == key.D:
			entry.offset((10, 0))
		elif symbol == key.W:
			entry.offset((0, 10))
		elif symbol == key.S:
			entry.offset((0, -10))
		elif symbol == key.LEFT:
			entry.anchor_x -= 10
		elif symbol == key.RIGHT:
			entry.anchor_x += 10
		elif symbol == key.UP:
			entry.anchor_y += 10
		elif symbol == key.DOWN:
			entry.anchor_y -= 10
		elif symbol == key.C:
			entry.clear()
		elif symbol == key.V:
			entry.reset(pos=False)
		elif symbol == key.R:
			entry.reset()
		elif symbol == key.BRACKETLEFT:
			entry.scale -= 1
		elif symbol == key.BRACKETRIGHT:
			entry.scale += 1
		else:
			return

		print(f'{entry.ID} ("{entry.text}") is at {entry.pos} @ {entry.scale}x scale')
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
