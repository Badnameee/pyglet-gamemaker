"""Module holding all hitbox classes.

Currently holds `.Hitbox`, `.HitboxRCircle`.

Use `~pgm.shapes.{class}` instead of `~pgm.shapes.hitbox.{class}`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.graphics import Batch, Group
from pyglet.math import Vec2
from pyglet.shapes import Circle, Polygon

from ..types import CollisionSubType
from .trigger import HasHitbox, Trigger, TriggerCircle

if TYPE_CHECKING:
	from typing import Self

	from ..scene import Scene
	from ..types import Color, Point2D
	from ..window import Window


class Hitbox:
	"""Holds a Hitbox with `.trigger` and `.render` objects."""

	#* Instance vars
	ID: str
	"""The unique ID of the hitbox to distinguish it"""
	trigger: Trigger
	"""The trigger object"""
	render: Polygon
	"""The render object"""
	subtype: CollisionSubType
	"""Subtype (ex. 'rect') of hitbox"""

	#* Property vars
	_hitbox_color: Color

	def __init__(
		self,
		ID: str,
		coords: tuple[Point2D, ...],
		color: Color,
		window: Window,
		scene: Scene | None,
		batch: Batch,
		group: Group,
		anchor: Point2D = (0, 0),
		*,
		_subtype: CollisionSubType = CollisionSubType.NONE,
	) -> None:
		"""Create a hitbox render.

		Args:
			ID (str):
				Name/ID of hitbox
			coords (tuple[Point2D, ...]):
				The coordinates of the hitbox
			color (Color):
				The color of the hitbox
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
			_subtype (CollisionSubType, optional):
				The subtype of the hitbox. Ex: 'RECT', 'CIRCLE'.
				Defaults to CollisionSubType.NONE.
		"""
		self.render = Polygon(*coords, color=color, batch=batch, group=group)
		self.trigger = Trigger(ID, coords, window, scene, anchor, _subtype=_subtype)

		self.ID = ID
		self.subtype = _subtype
		self._hitbox_color = color

	@classmethod
	def from_rect(
		cls,
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
	) -> Self:
		"""Create a hitbox render from rectangle dimensions.

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
			anchor (Point2D):
				Anchor position
		"""
		return cls(
			ID,
			((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
			color,
			window,
			scene,
			batch,
			group,
			anchor,
			_subtype=CollisionSubType.RECT,
		)

	def collide(
		self,
		other: Trigger,
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm to determine if 2 objects are colliding.

		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Hitbox | Hitbox | HitboxCircle):
				The other hitbox to detect collision with
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[bool, Vec2 | None]: Whether
				collision passed and MTV (None if no collision)
		"""
		return self.trigger.collide(other, sacrifice_MTV)

	def collide_any(
		self,
		others: list[Trigger | HasHitbox],
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm on a list of others.

		Args:
			others (list[Hitbox | HasHitbox]):
				List of others to check collision with self
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[bool, Vec2 | None]: Whether collision passed and MTV (None if no collision)
		"""
		return self.trigger.collide_any(others, sacrifice_MTV)

	def _calc_coords(self) -> None:
		self.trigger._calc_coords()

		# Update polygon render
		self.render._coordinates = self.trigger.coords  # type: ignore[assignment]
		self.render._update_vertices()
		self.render.x = self.trigger.coords[0][0]
		self.render.y = self.trigger.coords[0][1]

	@property
	def x(self) -> float:
		"""The x position of the anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.trigger._trans_pos[0]

	@x.setter
	def x(self, val: float) -> None:
		self.trigger._trans_pos = val, self.trigger._trans_pos[1]
		self._calc_coords()

	@property
	def y(self) -> float:
		"""The y position of the anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.trigger._trans_pos[1]

	@y.setter
	def y(self, val: float) -> None:
		self.trigger._trans_pos = self.trigger._trans_pos[0], val
		self._calc_coords()

	@property
	def pos(self) -> Point2D:
		"""The position of the anchor point."""
		return self.trigger._trans_pos

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.trigger._trans_pos = val
		self._calc_coords()

	@property
	def anchor_x(self) -> float:
		"""The x anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.trigger.anchor_x

	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self.trigger._anchor = val, self.anchor_y
		self._calc_coords()

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.trigger.anchor_y

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self.trigger._anchor = self.anchor_x, val
		self._calc_coords()

	@property
	def anchor(self) -> Point2D:
		"""The anchor of the hitbox."""
		return self.trigger._anchor

	@anchor.setter
	def anchor(self, val: Point2D) -> None:
		self.trigger._anchor = val
		self._calc_coords()

	@property
	def angle(self) -> float:
		"""Angle, in radians, of hitbox."""
		return self.trigger._angle

	@angle.setter
	def angle(self, val: float) -> None:
		self.trigger._angle = val
		self._calc_coords()

	@property
	def hitbox_color(self) -> Color:
		"""Color of hitbox."""
		return self._hitbox_color

	@hitbox_color.setter
	def hitbox_color(self, val: Color) -> None:
		self._hitbox_color = val
		self.render.color = val

	def __repr__(self) -> str:
		return repr(self.trigger)


class HitboxCircle:
	"""Holds a Circle Hitbox with `.trigger` and `.render` objects."""

	#* Instance vars
	ID: str
	"""The unique ID of the hitbox to distinguish it"""
	trigger: TriggerCircle
	"""The trigger object"""
	render: Circle
	"""The render object"""
	subtype: str | None
	"""Subtype (ex. 'rect') of hitbox"""

	#* Property vars
	_hitbox_color: Color

	def __init__(
		self,
		ID: str,
		x: float,
		y: float,
		radius: float,
		color: Color,
		window: Window,
		scene: Scene | None,
		batch: Batch,
		group: Group,
		anchor: Point2D = (0, 0),
	) -> None:
		"""Create a circular hitbox.

		Args:
			ID (str):
				Name/ID of hitbox
			x (float):
				Center x
			y (float):
				Center y
			radius (float):
				The radius of the circle
			color (Color):
				The color of the hitbox
			window (Window):
				Window for attaching self
			scene (Scene | None):
				The scene the hitbox is from. None if hitbox is a template or not in a scene.
			batch (Batch):
				The batch for rendering
			group (Group):
				The group for rendering
			anchor (Point2D, optional):
				The anchor position.
				Defaults to (0, 0).
		"""
		self.render = Circle(x, y, radius, color=color, batch=batch, group=group)
		self.trigger = TriggerCircle(ID, x, y, radius, window, scene, anchor)

		self.ID = ID
		self.subtype = 'circle'
		self._hitbox_color = color

	def collide(
		self,
		other: Hitbox | HasHitbox,
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm to determine if 2 objects are colliding.

		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Hitbox | HasHitbox):
				The other hitbox to detect collision with
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[bool, Vec2 | None]: Whether collision passed and MTV (None if no collision)
		"""
		return self.trigger.collide(other, sacrifice_MTV)

	def collide_any(
		self,
		others: list[Trigger | HasHitbox],
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm on a list of others.

		Args:
			others (list[Trigger | HasHitbox]):
				List of others to check collision with self
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[bool, Vec2 | None]: Whether collision passed and MTV (None if no collision)
		"""
		return self.trigger.collide_any(others, sacrifice_MTV)

	def _calc_coords(self) -> None:
		self.trigger._calc_coords()
		self.render.position = self.trigger.coords[0]

	@property
	def x(self) -> float:
		"""The x position of the anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.trigger.x

	@x.setter
	def x(self, val: float) -> None:
		self.trigger.x = val
		self._calc_coords()

	@property
	def y(self) -> float:
		"""The y position of the anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.trigger.y

	@y.setter
	def y(self, val: float) -> None:
		self.trigger.y = val
		self._calc_coords()

	@property
	def pos(self) -> Point2D:
		"""The position of the anchor point."""
		return self.trigger.pos

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.trigger.pos = val
		self._calc_coords()

	@property
	def anchor_x(self) -> float:
		"""The x anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.trigger.anchor_x

	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self.trigger._anchor = val, self.anchor_y
		self._calc_coords()

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.trigger.anchor_y

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self.trigger._anchor = self.anchor_x, val
		self._calc_coords()

	@property
	def anchor(self) -> Point2D:
		"""The anchor of the hitbox."""
		return self.trigger._anchor

	@anchor.setter
	def anchor(self, val: Point2D) -> None:
		self.trigger._anchor = val
		self._calc_coords()

	@property
	def angle(self) -> float:
		"""The angle, in radians, of the hitbox."""
		return self.trigger._angle

	@angle.setter
	def angle(self, val: float) -> None:
		self.trigger._angle = val
		self._calc_coords()

	@property
	def hitbox_color(self) -> Color:
		"""The color of the hitbox."""
		return self._hitbox_color

	@hitbox_color.setter
	def hitbox_color(self, val: Color) -> None:
		self._hitbox_color = val
		self.render.color = val

	def __repr__(self) -> str:
		return repr(self.trigger)
