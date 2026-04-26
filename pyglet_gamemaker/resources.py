"""Module storing default resources used in the package.

Use `~pgm.DefaultResources` instead of `~pgm.resources.DefaultResources`.
"""

from __future__ import annotations

from enum import Enum
from importlib import resources
from pathlib import Path

import pyglet

from .sprite.sprite_sheet import SpriteSheet

_package = resources.files('pyglet_gamemaker')
_media_folder = resources.files('pyglet_gamemaker.media')
_button_path = 'Default Button.png'
_circle_button_path = 'Default Circle Button.png'

pyglet.resource.path.append(str(_package))
pyglet.resource.reindex()


class DefaultResources(Enum):
	"""The default resources of the package, are instances of SpriteSheet."""

	button = SpriteSheet(
		Path(_media_folder.joinpath(_button_path)).relative_to(_package).as_posix(),
		3,
		1,
	)
	circle_button = SpriteSheet(
		Path(_media_folder.joinpath(_circle_button_path))
		.relative_to(_package)
		.as_posix(),
		3,
		1,
	)
