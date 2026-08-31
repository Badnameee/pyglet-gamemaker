from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet
from pyglet.shapes import Rectangle

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.trigger import Trigger
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.t = Trigger.from_rect(
			'Test',
			100,
			100,
			300,
			300,
			self.window,
			None,
			on_mouse_trigger_press=self.on_mouse_trigger_press,
			on_mouse_trigger_release=self.on_mouse_trigger_release,
			on_mouse_trigger_enter=self.on_mouse_trigger_enter,
			on_mouse_trigger_exit=self.on_mouse_trigger_exit,
		)
		self.objs = []

	def update(self, dt):
		# print(t._last_mouse_info)
		if self.t.mouse_in:
			self.objs.append(
				Rectangle(*self.t._last_mouse_info[:2], 1, 1, batch=self.batch)
			)

	def on_mouse_trigger_press(self, trigger, x, y):
		print(f'{trigger.ID} pressed @ ({x}, {y})')

	def on_mouse_trigger_release(self, trigger, x, y):
		print(f'{trigger.ID} released @ ({x}, {y})')

	def on_mouse_trigger_enter(self, trigger, x, y):
		print(f'{trigger.ID} entered @ ({x}, {y})')

	def on_mouse_trigger_exit(self, trigger, x, y):
		print(f'{trigger.ID} exited @ ({x}, {y})')

	def disable(self):
		pyglet.clock.unschedule(self.update)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 60)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
