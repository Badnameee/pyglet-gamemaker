# 📦 pyglet-gamemaker

<!-- (add your badges here) -->
[![PyPI version](https://badge.fury.io/py/pyglet-gamemaker.svg)](https://badge.fury.io/py/pyglet-gamemaker)

<!-- > *Your documentation is a direct reflection of your software, so hold it to the same standards.* -->


## ℹ️ Overview

<!-- A paragraph explaining your work, who you are, and why you made it. -->

**pyglet-gamemaker** is an extension of Pyglet that simplifies the process of making games! This project began when I became frustrated at the boilerplate I had to write all the time, and I wanted a cleaner system to quickly add features.


## 🌟 Features

- Triggers/Hitboxes
  - Fully working convex polygon collision using SAT algorithm
  - Includes circles + points
  - Can interact with mouse (toggleable)
  - Can possess tags and tags it can collide with
  - 3 collision types: `None`, `Overlap`, and `Collide`
  - Can be setup to automatically detect collision
  - Dispatch events on different types of collision
- Spritesheets:
  - Can label to allow indexing by string
  - Can have several animations present in a single sheet
  - Uses yaml config file
- Widgets:
  - Can use spritesheet instead of individual images
  - Widgets can be added to the HUD automatically
- Camera:
  - Can easily transform, rotate, and zoom
- Scenes:
  - Enabling and disabling handled automatically
  - Event handlers can be written in scene and automatically detected by objects at creation
- Window:
  - Handles switching of scenes
  - Handles physics backend
- Anchoring (all objects):
    - Static: raw pixel value
    - Dynamic Preset: `left`, `center`, `right`, etc. like pyglet
    - Dynamic: ratios of width/height, changes automatically as widget scales
- Event dispatching (all objects):
  - Event handlers can be passed into any object's `.__init__()` as a kwarg
  - Handlers are also automatically detected in the scene

### ✍️ Authors

I'm [Steven Robles](https://github.com/Badnameee) and I am a high school student with a moderate passion for making games.


## 🚀 Usage

<!-- *Show off what your software looks like in action! Try to limit it to one-liners if possible and don't delve into API specifics.* -->

A simple program to render an empty Scene with button detection:
```py
>>> import pyglet_gamemaker as pgm
>>> 
>>> 
>>> class Menu(pgm.Scene):
>>>     # Create widgets here
>>>     def initialize(self): ...
>>>     # Code that runs when button is pressed down
>>>     def on_half_click(self, button): ...
>>>     # Code that runs when button is fully clicked and released
>>>     def on_full_click(self, button): ...
>>>     # Code that runs when scene is enabled
>>>     def enable(self, *args, **kwargs): ...
>>>     # Code that runs when scene is disabled
>>>     def disable(self): ...
>>> 
>>> 
>>> window = pgm.Window(width=640, height=480)
>>> window.add_scene(Menu(name='Menu'))
>>> window.run()
```

Creating a spritesheet
```py
>>> # Create a sprite sheet with image assets
>>> #   This image, found in /test, has 3 images (bottom to top):
>>> #   Unpressed, Hover, and Pressed
>>> pgm.sprite.SpriteSheet(
>>>     file_path='test/Test Button SpriteSheet.png',
>>>     rows=3, cols=1
>>> )
```

Creating a rectangle hitbox
```py
>>> # In addition to Rect, there is also Hitbox and Trigger
>>> pgm.collision.Rect(
>>>     ID='TextButton',
>>>     x=100, y=100, width=90, height=60,
>>>     tags={'MyTag1'},
>>>     target_tags={'MyTag1': pgm.types.TriggerInteractType.OVERLAP},
>>> )
```

Creating an AnimationList
```py
>>> # Copied from tests/sprite.py
>>> pgm.sprite.AnimationList(
>>> 	'media/AnimationList.png',
>>> 	'tests/media/AnimationList.yaml',
>>> )
```

Widget creation should go in `Menu.initialize()`:

- Creating text
```py
>>> pgm.gui.Text(
>>>     ID='Text', text='Test',
>>>     anchor=('center', 'center'), color=pgm.colors.RED,
>>> )
```

- Creating a button
```py
>>> pgm.gui.Button(
>>>     ID='Button', image_sheet=self.sheet,
>>>     anchor=('center', 'center'),
>>>     # Event handlers automatically added from Menu class
>>> )
```

- Creating a text and button in one
```py
>>> # A textbutton combines text and a button
>>> #   Hover enlarge makes text larger when hovering
>>> #   Works well with using larger hover sprite for button
>>> pgm.gui.TextButton(
>>>     ID='TextButton', image_sheet=self.sheet,
>>>     text='Text', 
>>>     button_anchor=('center', 'center'),
>>>     # Event handlers automatically added from Menu class
>>> )
```


## ⬇️ Installation

<!-- Simple, understandable installation instructions! -->

```bash
pip install pyglet-gamemaker
```

<!-- And be sure to specify any other minimum requirements like Python versions or operating systems. -->
**Works in Python >=3.10**

<!-- *You may be inclined to add development instructions here, don't.* -->


## 💭 Feedback and Contributing

<!--Add a link to the Discussions tab in your repo and invite users to open issues for bugs/feature requests. -->

To request features or report bugs, open an issue [here](https://github.com/Badnameee/pyglet-gamemaker/issues).

[Contact me directly](mailto:stevenrrobles13@gmail.com)

<!-- This is also a great place to invite others to contribute in any ways that make sense for your project. Point people to your DEVELOPMENT and/or CONTRIBUTING guides if you have them. -->