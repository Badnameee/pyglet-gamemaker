from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

import pyglet
from pyglet.gl import *
from pyglet.graphics import Batch, Group
from pyglet.shapes import Circle
from pyglet.window import Window, key

from pyglet_gamemaker.gui.button import Button
from pyglet_gamemaker.sprite.sprite_sheet import SpriteSheet

window = Window(640, 480, caption=__name__)
pyglet.gl.glClearColor(1, 1, 1, 1)
batch = Batch()
button_group = Group()
UI_group = Group(1)

sheet = SpriteSheet('media/Button SpriteSheet.png', 3, 1)
sheet.name('Unpressed', 'Hover', 'Pressed')
glBindTexture(GL_TEXTURE_2D, 1)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


def on_half_click(button):
	print(f'{button.ID} pressed down on!')


def on_full_click(button):
	print(f'{button.ID} fully pressed and released!')


@window.event
def on_key_press(symbol, modifiers):
	if symbol == key.A:
		button.offset((-10, 0))
	elif symbol == key.D:
		button.offset((10, 0))
	elif symbol == key.W:
		button.offset((0, 10))
	elif symbol == key.S:
		button.offset((0, -10))
	elif symbol == key.LEFT:
		button.anchor_x -= 10
	elif symbol == key.RIGHT:
		button.anchor_x += 10
	elif symbol == key.UP:
		button.anchor_y += 10
	elif symbol == key.DOWN:
		button.anchor_y -= 10
	elif symbol == key.R:
		button.reset()
	elif symbol == key.H:
		button.visible = not button.visible
	elif symbol == key.BRACKETLEFT:
		button.scale -= 1
	elif symbol == key.BRACKETRIGHT:
		button.scale += 1
	else:
		return

	print(f'New button pos: {button.pos}')
	button_anchor.position = button.pos


@window.event
def on_draw():
	window.clear()
	batch.draw()

button = Button(
	'Hi',
	320,
	240,
	sheet,
	0,
	window,
	None,
	batch,
	button_group,
	('.25', '.25'),
	#on_half_click=on_half_click,
	on_full_click=on_full_click,
)
button_anchor = Circle(
	*button.pos, 10, color=(0, 255, 255), batch=batch, group=UI_group
)

pyglet.app.run()
