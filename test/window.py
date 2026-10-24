from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

from pyglet_gamemaker import colors
from pyglet_gamemaker.gui.button import Button
from pyglet_gamemaker.gui.text import Text
from pyglet_gamemaker.gui.text_button import TextButton
from pyglet_gamemaker.resources import DefaultResources
from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.rect import Rect
from pyglet_gamemaker.window import Window


class TestScene(Scene):
	WIDGET_POS = {'Test1': (0.2, 0.1), 'Test2': (0.5, 0.5), 'Test3': (0.7, 0.7)}

	DEFAULT_FONT_INFO = None, 40, None

	def __init__(self, name, bg_color):
		super().__init__(name)
		self.bg_color = bg_color

	def initialize(self):
		self.bg = Rect(
			'BG',
			0,
			0,
			self.window.width,
			self.window.height,
			self.bg_color,
			scene=self,
		)

		self.txt = Text(
			'Test1',
			'Hi',
			scene=self,
			anchor=('center', 'center'),
		)
		self.button = Button(
			'Test2',
			DefaultResources.button,
			0,
			scene=self,
			anchor=('center', 'center'),
		)
		self.text_button = TextButton(
			'Test3',
			DefaultResources.button,
			0,
			'Hi2',
			scene=self,
			button_anchor=('center', 'center'),
			text_anchor=('center', 'center'),
			hover_enlarge=5,
		)

	def on_half_click(self, button):
		print(f'{self.__class__.__name__}: "{button.ID}" was clicked!')

	def on_full_click(self, button):
		print(f'{self.__class__.__name__}: "{button.ID}" was fully pressed!')
		if button.ID == 'Test3':
			self.dispatch_event('on_scene_change', 'TestScene2')

	def enable(self):
		print(f'{self.__class__.__name__} enabled')
		self.txt.enable()
		self.button.enable()
		self.text_button.enable()

	def disable(self):
		print(f'{self.__class__.__name__} disabled')
		self.txt.disable()
		self.button.disable()
		self.text_button.disable()


class TestScene2(Scene):
	WIDGET_POS = {
		'Test1': (0, 0.3),
		'Test2': (0.4, 0.6),
		'Test3': (0.6, 0.8),
	}

	DEFAULT_FONT_INFO = None, 40, None

	def __init__(self, name, bg_color):
		super().__init__(name)
		self.bg_color = bg_color

	def initialize(self):
		self.bg = Rect(
			'BG',
			0,
			0,
			self.window.width,
			self.window.height,
			self.bg_color,
			scene=self,
		)

		self.txt = Text(
			'Test1',
			'Hi',
			scene=self,
			anchor=('center', 'center'),
		)
		self.button = Button(
			'Test2',
			DefaultResources.button,
			0,
			scene=self,
			anchor=('center', 'center'),
		)
		self.text_button = TextButton(
			'Test3',
			DefaultResources.button,
			0,
			'Hi2',
			scene=self,
			button_anchor=('center', 'center'),
			text_anchor=('center', 'center'),
			hover_enlarge=5,
		)

	def on_half_click(self, button):
		print(f'{self.__class__.__name__}: "{button.ID}" was clicked!')

	def on_full_click(self, button):
		print(f'{self.__class__.__name__}: "{button.ID}" was fully pressed!')
		if button.ID == 'Test3':
			self.dispatch_event('on_scene_change', 'TestScene')

	def enable(self):
		print(f'{self.__class__.__name__} enabled')
		self.txt.enable()
		self.button.enable()
		self.text_button.enable()

	def disable(self):
		print(f'{self.__class__.__name__} disabled')
		self.txt.disable()
		self.button.disable()
		self.text_button.disable()


window = Window(640, 480)
window.add_scene(TestScene('TestScene', colors.ORANGE))
window.add_scene(TestScene2('TestScene2', colors.WHITE))
window.run()
