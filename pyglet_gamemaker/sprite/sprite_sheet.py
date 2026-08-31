"""Module holding SpriteSheet class.

Use `~pgm.sprite.SpriteSheet` instead of `~pgm.sprite.sprite_sheet.SpriteSheet`
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pyglet
import yaml

from ..errors import InvalidConfigFile
from .image_grid import ImageGrid
from .yaml_validator import YAMLValidator

if TYPE_CHECKING:
	from typing import Any, Self, SupportsIndex

	from pyglet.image import Texture, TextureRegion


class SpriteSheet:
	"""An object holding a rectangular sheet of common sprites.

	Index to get specific sprite to render.
	Allows indexing by name using `.name()`.
	"""

	path: Path
	"""Path of original image"""
	yaml_path: Path | None = None
	"""Path of .yaml config file"""
	has_yaml: bool
	"""If True, SpriteSheet created with .yaml data"""
	yaml: Any | None = None
	"""The yaml data"""
	rows: int
	"""Number of rows in sheet"""
	cols: int
	"""Number of cols in sheet"""
	row_padding: int
	"""Padding between sprite rows"""
	col_padding: int
	"""Padding between sprite columns"""
	top_down: bool
	"""If True, parse spritesheet from top-to-bottom.
	If False, parse from bottom-to-top.
	"""
	atlas: bool
	"""If True, spritesheet is stored in a global atlas. False if not.
	See `~pgm.sprite.SpriteSheet` for more info."""
	img: Texture
	"""Stores the original image"""
	image_grid: ImageGrid
	"""Stores the unoptimized image grid"""
	lookup: dict[str, int] = {}
	"""The lookup table to convert aliases to integers for indexing"""

	def __init__(
		self,
		file_path: Path | str,
		rows: int,
		cols: int,
		row_padding: int = 0,
		col_padding: int = 0,
		top_down: bool = True,
		atlas: bool = True,
		_yaml: bool = False,
		_yaml_path: Path | str | None = None,
	) -> None:
		"""Create a sprite sheet from a file.

		Args:
			file_path (Path | str):
				The path to the sprite sheet
			rows (int):
				The number of rows for sprites
			cols (int):
				The number of columns for sprites
			row_padding (int, optional):
				The amount to pad between rows of sprites. Does not include edge of sheet.
				Defaults to 0.
			col_padding (int, optional):
				The amount to pad between columns of sprites. Does not include edge of sheet.
				Defaults to 0.
			top_down (bool, optional):
				If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.
				Defaults to True.
			atlas (bool, optional):
				If True, add spritesheet to atlas for more efficient rendering but less fine control.
				Ex. Cannot set texture parameters without setting for entire atlas.
				If False, create separate texture. Slower but allows for more customization.
				Defaults to True.
			_yaml (bool, optional):
				If True, add yaml file path to `.yaml_path`.
				Used by `._name_with_yaml()`.
			_yaml_path (Path | str, optional):
				Used
		"""
		self.path, self.rows, self.cols = Path(file_path), rows, cols
		self.row_padding, self.col_padding = row_padding, col_padding
		self.top_down = top_down
		self.img = pyglet.resource.image(file_path, atlas=atlas)  # type: ignore[arg-type] # Should work as it uses some variation of open()
		self.image_grid = ImageGrid(
			self.img, rows, cols, row_padding, col_padding, self.top_down
		)

		self.has_yaml = _yaml
		if _yaml:
			self.yaml_path = (
				Path(_yaml_path)
				if _yaml_path
				else self.path.absolute().with_suffix('.yaml')
			)

	@classmethod
	def from_yaml(
		cls,
		file_path: Path | str,
		yaml_path: Path | str,
		top_down: bool = True,
		atlas: bool = True,
	) -> Self:
		"""Load a spritesheet using the associated .yaml file.

		Args:
			file_path (Path | str):
				The path to the sprite sheet
			yaml_path (Path | str):
				The path to the .yaml file
			top_down (bool, optional):
				If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.
				Defaults to True.
			atlas (bool, optional):
				If True, add spritesheet to atlas for more efficient rendering but less fine control.
				Ex. Cannot set texture parameters without setting for entire atlas.
				If False, create separate texture. Slower but allows for more customization.
				Defaults to True.
		"""
		if isinstance(yaml_path, str):
			yaml_path = Path(yaml_path)

		validator = YAMLValidator(yaml_path, 'Anim')
		errors = validator.validate()
		if errors:
			raise InvalidConfigFile(str(yaml_path), validator.validation_mode, errors)

		yaml = cls._raw_yaml(yaml_path)
		self = cls(
			file_path,
			yaml['rows'],
			yaml['cols'],
			yaml['row-padding'],
			yaml['col-padding'],
			top_down,
			atlas,
			_yaml=True,
			_yaml_path=yaml_path,
		)
		self._name_from_yaml()

		return self

	def name(self, *args: str) -> None:
		"""Name all of the grid parts instead of indexing with numbers.

		Args:
			*args (str):
				The names of the grid parts. Must be in same order as regular indexing.
		"""
		# Must be same number of names as parts of the grid
		if len(args) != len(self.image_grid):
			raise ValueError(
				f'SpriteSheet.name() takes {len(self.image_grid)} args, but {len(args)} were given.'
			)

		# Add all to lookup table
		self.lookup = {name: i for i, name in enumerate(args)}

	@staticmethod
	def _raw_yaml(file_path: Path) -> Any:
		with open(file_path) as file:
			return yaml.safe_load(file)

	def _name_from_yaml(self) -> None:
		if not self.has_yaml:
			raise NotImplementedError(
				'Should not run SpriteSheet.name_with_yaml on a SpriteSheet with no yaml'
			)
		with open(self.yaml_path) as file:  # type: ignore[arg-type] # self.yaml_path guaranteed to be Path if self.has_yaml
			self.yaml = yaml.safe_load(file)

			# Parse data for names
			self.lookup.clear()
			for row_num, row in enumerate(self.yaml['data']):
				for col_num, id in enumerate(row):
					# Void, not a sprite
					if id == self.yaml['void']:
						continue
					self.lookup[id] = row_num * self.cols + col_num

	def __getitem__(
		self,
		index: str
		| int
		| slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
	) -> TextureRegion:
		"""Get the sprite at position `index`.

		Either a normal index or a string matching an index (using `.name()`) can be used.
		"""
		# Note: guaranteed to return TextureRegion because
		# 	resource.image returns a Texture, and image grid takes region of it

		# Slice and int can be directly used
		if isinstance(index, slice | int):
			return self.image_grid[index]  # type: ignore[return-value]
		# Use lookup table if string
		if isinstance(index, str):
			return self.image_grid[self.lookup[index]]  # type: ignore[return-value]
		raise ValueError(f'SpriteSheet[] recieved bad value: {index}')

	@property
	def item_width(self) -> int:
		"""Width of single sprite."""
		return self.image_grid.item_width

	@property
	def item_height(self) -> int:
		"""Height of single sprite."""
		return self.image_grid.item_height

	@property
	def item_dim(self) -> tuple[int, int]:
		"""Dimensions of single sprite."""
		return self.image_grid.item_width, self.image_grid.item_height

	def __repr__(self) -> str:
		return f'SpriteSheet @ "{self.path}": {self.rows}r {self.cols}c | {"has" if self.has_yaml else "does not have"} yaml'
