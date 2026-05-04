from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet
from pyglet.graphics import Batch, Group
from pyglet.shapes import Rectangle
from pyglet.window import Window

from pyglet_gamemaker.shapes.trigger import Trigger


def on_mouse_trigger_press(trigger, x, y):
	print(f'{trigger.ID} pressed @ ({x}, {y})')


def on_mouse_trigger_release(trigger, x, y):
	print(f'{trigger.ID} released @ ({x}, {y})')


def on_mouse_trigger_enter(trigger, x, y):
	print(f'{trigger.ID} entered @ ({x}, {y})')


def on_mouse_trigger_exit(trigger, x, y):
	print(f'{trigger.ID} exited @ ({x}, {y})')


window = Window(640, 480, caption=__name__)
batch = Batch()
group = Group()

t = Trigger.from_rect(
	'Test',
	100,
	100,
	300,
	300,
	window,
	None,
	on_mouse_trigger_press=on_mouse_trigger_press,
	on_mouse_trigger_release=on_mouse_trigger_release,
	on_mouse_trigger_enter=on_mouse_trigger_enter,
	on_mouse_trigger_exit=on_mouse_trigger_exit,
)
l = []


def update(dt):
	# print(t._last_mouse_info)
	if t.mouse_in:
		l.append(Rectangle(*t._last_mouse_info[:2], 1, 1, batch=batch))


@window.event
def on_draw():
	window.clear()
	batch.draw()


pyglet.app.run()
