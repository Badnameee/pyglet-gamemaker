from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet

from pyglet_gamemaker.scene import Scene
from pyglet_gamemaker.shapes.rect import Rect
from pyglet_gamemaker.types import TriggerInteractType
from pyglet_gamemaker.window import Window


class Scene1(Scene):
	def initialize(self):
		self.main = Rect(
			'Main',
			320,
			240,
			200,
			400,
			(255, 0, 0, 100),
			scene=self,
			anchor=(100, 200),
			mouse_detection=True,
			target_tags={'Custom2': TriggerInteractType.OVERLAP},
		)
		self.small = [
			Rect(
				'Small1',
				-50,
				340,
				50,
				50,
				(255, 255, 0, 100),
				scene=self,
				anchor=(0, 25),
				mouse_detection=False,
			),
			Rect(
				'Small2',
				-50,
				240,
				50,
				50,
				(0, 255, 0, 100),
				scene=self,
				anchor=(0, 25),
				mouse_detection=False,
				tags={'Custom1'},
			),
			Rect(
				'Small3',
				-50,
				140,
				50,
				50,
				(0, 255, 255, 100),
				scene=self,
				anchor=(0, 25),
				mouse_detection=False,
				tags={'Custom1', 'Custom2'},
			),
		]
		self.speed = 200  # px/s

	def update(self, dt) -> None:
		for small in self.small:
			small.x += self.speed * dt
			small.x += self.speed * dt

			if small.x >= self.window.width:
				small.x = -small.width
			small.render.opacity = 255 if self.main.collide(small)[0] else 100

	def disable(self):
		pyglet.clock.unschedule(self.update)

	def enable(self):
		pyglet.clock.schedule_interval(self.update, 1 / 60)


window = Window(640, 480)
window.add_scene(Scene1('Scene'))
window.run()
