# type: ignore

import pyglet
from src.sprite import SpriteSheet

pyglet.resource.path = ['test']
pyglet.resource.reindex()

sheet = SpriteSheet('Default Button.png', 3, 1)
print(sheet.lookup)
sheet.name('Unpressed', 'Hover', 'Pressed')
print(sheet.lookup)
print(sheet.item_dim)
print(sheet.cols, sheet.rows)
print(sheet.img.width, sheet.img.height)
