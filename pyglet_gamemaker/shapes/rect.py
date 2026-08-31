"""Module holding Rect class.

Use `~pgm.shapes.Rect` instead of `~pgm.shapes.rect.Rect`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.graphics import Batch, Group

from ..types import Color, Point2D
from .hitbox import HitboxRender

if TYPE_CHECKING:
	from ..scene import Scene
	from ..window import Window


class Rect(HitboxRender):
	"""A rendered rectangular hitbox.

	Has attributes for each vertex position (`.bottomleft`, `.bottomright`, `.topright`, `.topleft`)

	To create a rectangle without a render, use `~pgm.shapes.Hitbox.from_rect()`.
	"""

	def __init__(
		self,
		ID: str,
		x: float,
		y: float,
		width: float,
		height: float,
		color: Color,
		window: Window,
		scene: Scene | None,
		batch: Batch,
		group: Group,
		anchor: Point2D = (0, 0),
	) -> None:
		"""Create a rectangle.

		Args:
			ID (str):
				Name/ID of hitbox
			x (float):
				x position
			y (float):
				y position
			width (float):
				Width of rect
			height (float):
				Height of rect
			color (Color):
				The color of the hitbox render
			window (Window):
				Window for attaching self
			scene (Scene | None):
				The scene the hitbox is from. None if hitbox is a template or not in a scene.
			batch (Batch):
				The batch for rendering
			group (Group):
				The group for rendering
			anchor (Point2D, optional):
				The starting anchor position.
				Defaults to (0, 0).
		"""
		super().__init__(
			ID,
			((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
			color,
			window,
			scene,
			batch,
			group,
			anchor,
			subtype='rect',
		)

	@property
	def bottomleft(self) -> Point2D:
		"""The bottomleft vertex position of rect after all transformations."""
		return self.hitbox.coords[0]

	@property
	def bottomright(self) -> Point2D:
		"""The bottomright vertex position of rect after all transformations."""
		return self.hitbox.coords[1]

	@property
	def topright(self) -> Point2D:
		"""The topright vertex position of rect after all transformations."""
		return self.hitbox.coords[2]

	@property
	def topleft(self) -> Point2D:
		"""The topleft vertex position of rect after all transformations."""
		return self.hitbox.coords[3]

	@property
	def width(self) -> float:
		"""The width of *unrotated* rectangle."""
		return self.hitbox._raw_coords[1][0] - self.hitbox._raw_coords[0][0]

	@width.setter
	def width(self, val: float) -> None:
		# Set raw coords instead of local coords because ._calc_coords
		# updates local coords. Updates to local coords would
		# get overwritten when calling ._calc_coords
		self.hitbox._raw_coords = (
			self.hitbox._raw_coords[0],
			(self.hitbox._raw_coords[0][0] + val, self.hitbox._raw_coords[1][1]),
			(self.hitbox._raw_coords[3][0] + val, self.hitbox._raw_coords[2][1]),
			self.hitbox._raw_coords[3],
		)
		self._calc_coords()

	@property
	def height(self) -> float:
		"""The height of *unrotated* rectangle."""
		return self.hitbox._raw_coords[3][1] - self.hitbox._raw_coords[0][1]

	@height.setter
	def height(self, val: float) -> None:
		# Set raw coords instead of local coords because ._calc_coords
		# updates local coords. Updates to local coords would
		# get overwritten when calling ._calc_coords
		self.hitbox._raw_coords = (
			self.hitbox._raw_coords[0],
			self.hitbox._raw_coords[1],
			(self.hitbox._raw_coords[2][0], self.hitbox._raw_coords[1][1] + val),
			(self.hitbox._raw_coords[3][0], self.hitbox._raw_coords[0][1] + val),
		)
		self._calc_coords()

	def __repr__(self) -> str:
		return (
			f'Rect ({self.ID}): {self.width}x{self.height} rect @ {self.hitbox._trans_pos} @ {self.angle} rad | {self.anchor} anchored\n'
		)
