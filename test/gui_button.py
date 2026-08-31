from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

from pyglet.shapes import Circle
from pyglet.window import key

from pyglet_gamemaker.resources import DefaultResources
from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.types import Color
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	WIDGET_POS = {'Test': (0.5, 0.5)}

	def initialize(self):
		self.bg = self.create_bg(Color.WHITE)

		self.button = self.create_button(
			'Test',
			DefaultResources.button,
			0,
			('.5', '.5'),
			add_to_widget_dict=False,
		)

		self.button_anchor = Circle(
			*self.button.pos,
			10,
			color=(0, 255, 255),
			batch=self.batch,
			group=self.UI_group,
		)

		self.window.push_handlers(self)

	def on_half_click(self, button):
		print(f'{button.ID} pressed down on!')

	def on_full_click(self, button):
		print(f'{button.ID} fully pressed and released!')

	def on_key_press(self, symbol, modifiers):
		if symbol == key.A:
			self.button.x -= 10
		elif symbol == key.D:
			self.button.x += 10
		elif symbol == key.W:
			self.button.y += 10
		elif symbol == key.S:
			self.button.y -= 10
		elif symbol == key.LEFT:
			self.button.anchor_x -= 10
		elif symbol == key.RIGHT:
			self.button.anchor_x += 10
		elif symbol == key.UP:
			self.button.anchor_y += 10
		elif symbol == key.DOWN:
			self.button.anchor_y -= 10
		elif symbol == key.R:
			self.button.reset()
		elif symbol == key.H:
			self.button.visible = not self.button.visible
		elif symbol == key.BRACKETLEFT:
			self.button.scale -= 1
		elif symbol == key.BRACKETRIGHT:
			self.button.scale += 1
		else:
			return

		print(self.button)
		self.button_anchor.position = self.button.pos

	def disable(self):
		self.button.disable()

	def enable(self):
		self.button.enable()


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
