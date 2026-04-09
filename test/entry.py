from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

from pyglet_gamemaker.gui.entry import Entry
from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.types import Color
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	WIDGET_POS = {'Test': (0.5, 0.5)}

	def initialize(self):
		self.create_entry(
			'Test',
			'Hi or hello...',
			250,
			color=Color.GRAY,
		)

	def on_submit(self, entry: Entry, text: str):
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
