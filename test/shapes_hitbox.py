import math

import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from pyglet.shapes import Circle
from src.shapes import HitboxRender
from src.types import Color

window = Window(640, 480, caption=__name__)
batch = Batch()
group = Group()

hitbox = HitboxRender.from_rect(100, 100, 100, 50, Color.WHITE, batch, group)
hitbox2 = HitboxRender.from_rect(300, 300, 100, 50, Color.RED, batch, group)
circle = Circle(100, 100, 50, color=Color.WHITE.value, batch=batch, group=group)
circle.visible = False

mode = 'rect'

@window.event
def on_mouse_motion(x, y, dx, dy):
	hitbox.move_to(x, y)
	circle.position = x, y

@window.event
def on_key_press(symbol, modifiers):
	global mode

	if symbol == key.LEFT:
		hitbox.anchor_x += 10
		circle.anchor_x += 10
	elif symbol == key.RIGHT:
		hitbox.anchor_x -= 10
		circle.anchor_x -= 10
	elif symbol == key.UP:
		hitbox.anchor_y -= 10
		circle.anchor_y -= 10
	elif symbol == key.DOWN:
		hitbox.anchor_y += 10
		circle.anchor_y += 10
	elif symbol == key.A:
		hitbox.angle -= 0.1
		circle.rotation -= 0.1 * 180 / math.pi
	elif symbol == key.D:
		hitbox.angle += 0.1
		circle.rotation += 0.1 * 180 / math.pi

	if symbol == key.C:
		mode = 'circle' if mode == 'rect' else 'rect'
		if mode == 'rect':
			hitbox.render.visible = True
			circle.visible = False
		elif mode == 'circle':
			hitbox.render.visible = False
			circle.visible = True

def update(dt):
	if hitbox.collide(hitbox2)[0]:
		hitbox.render.opacity = 128
	else:
		hitbox.render.opacity = 255
	if HitboxRender.circle_collide(circle, hitbox2)[0]:
		circle.opacity = 128
	else:
		circle.opacity = 255

@window.event
def on_draw():
	window.clear()
	batch.draw()

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
