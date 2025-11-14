import pyglet
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from src.gui import Text

window = Window(640, 480, caption=__name__)
batch = Batch()
group = Group()

@window.event
def on_key_press(symbol: int, modifiers: int):
	if symbol == key.LEFT:
		txt.x -= 10
	elif symbol == key.RIGHT:
		txt.x += 10
	elif symbol == key.DOWN:
		txt.y -= 10
	elif symbol == key.UP:
		txt.y += 10
	elif symbol == key.A:
		txt2.x -= 10
	elif symbol == key.D:
		txt2.x += 10
	elif symbol == key.S:
		txt2.y -= 10
	elif symbol == key.W:
		txt2.y += 10
	elif symbol == key.R:
		txt.reset()
		txt2.reset()
	else:
		return

	print(f'New txt pos: txt={txt.pos}, txt2={txt2.pos}')
	print(f'New txt font: txt={txt.font_name, txt.font_size}, txt2={txt2.font_name, txt2.font_size}')

@window.event
def on_draw():
	window.clear()
	batch.draw()

txt = Text(
	'Hello World', 0, 0, font_info=('Arial', None), anchor=('center', 'center'),
	batch=batch, group=group
)
txt2 = Text.from_scale(
	(0.5, 0.5), window, 'Hello World', font_info=('Times New Roman', 50), anchor=('center', 'center'),
	batch=batch, group=group
)

pyglet.app.run()
