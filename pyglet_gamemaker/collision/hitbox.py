"""Module holding all hitbox classes.

Currently holds `.Hitbox`, `.HitboxRCircle`.

Use `~pgm.shapes.{class}` instead of `~pgm.shapes.hitbox.{class}`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.graphics import Batch, Group
from pyglet.math import Vec2
from pyglet.shapes import Circle, Polygon

from pyglet_gamemaker.base_object import BaseObject

from .. import colors
from ..types import (
	Anchor,
	AnchorX,
	AnchorY,
	EventHandler,
	TriggerInteractType,
	TriggerSubType,
)
from .trigger import Trigger, TriggerCircle

if TYPE_CHECKING:
	from typing import Self

	from ..scene import Scene
	from ..types import Color, HasHitbox, Point2D
	from ..window import Window


class Hitbox(BaseObject):
	"""Holds a Hitbox with `.trigger` and `.render` objects."""

	# * Instance vars
	trigger: Trigger
	"""The trigger object"""
	render: Polygon
	"""The render object"""
	subtype: TriggerSubType
	"""Subtype (ex. 'rect') of hitbox"""

	# * Property vars
	_hitbox_color: Color

	def __init__(
		self,
		ID: str,
		coords: tuple[Point2D, ...],
		color: Color = colors.WHITE,
		window: Window | None = None,
		scene: Scene | None = None,
		batch: Batch | None = None,
		group: Group | None = None,
		anchor: Anchor = (0, 0),
		dispatch: bool = True,
		mouse_detection: bool = False,
		tags: set[str] | None = None,
		target_tags: dict[str, TriggerInteractType] | None = None,
		*,
		_subtype: TriggerSubType = TriggerSubType.NONE,
		**kwargs: EventHandler,
	) -> None:
		"""Create a hitbox render.

		Args:
			ID (str):
				Name/ID of hitbox
			coords (tuple[Point2D, ...]):
				The coordinates of the hitbox
			color (Color, optional):
				Color of hitbox.
				Defaults to Color.WHITE.
			window (Window, optional):
				Window for attaching self. Required if binding mouse events.
				Defaults to `scene.window` if scene is provided, else None.
			scene (Scene, optional):
				The scene the hitbox is from.
				Defaults to None.
			batch (Batch, optional):
				Batch for rendering.
				Defaults to `scene.batch` if scene is provided, else None.
			group (Group, optional):
				Group for rendering.
				Defaults to `scene.main_group` if scene is provided, else None.
			anchor (Point2D, optional):
				The starting anchor position.
				Defaults to (0, 0).
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.gui.Button` for more info.
				Defaults to True.
			mouse_detection (bool, optional):
				If True, detect mouse collision + attach mouse events to window. Window must be set.
				Event handlers can still be manually invoked.
				Defaults to False.
			tags (set[str], optional):
				Tags hitbox should possess, used for controlling collision more closely.
				Uses 'Default' tag if None passed.
				Defaults to None.
			target_tags (dict[str, TriggerInteractType], optional):
				Tags hitbox interacts with as well as the type of interaction. see `~pgm.types.TriggerInteractType`.
				Uses 'Default': 'OVERLAP' if not overriden.
				Defaults to None.
			_subtype (TriggerSubType, optional):
				The subtype of the hitbox. Ex: 'RECT', 'CIRCLE'.
				Defaults to TriggerSubType.NONE.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		self.ID = ID
		self.scene = scene
		self.window = self._verify_window(window, necessary=mouse_detection)

		self.render = Polygon(
			*coords,
			color=color,
			batch=self._verify_batch(batch),
			group=self._verify_group(group, attr_name='main_group'),
		)
		self.trigger = Trigger(
			ID,
			coords,
			self.window,
			scene,
			anchor,
			dispatch,
			mouse_detection,
			tags,
			target_tags,
			_subtype=_subtype,
			**kwargs,
		)

		self.subtype = _subtype
		self._hitbox_color = color
		# Refresh anchor to make sure correct ._calc_coords is called
		self.anchor = self.anchor

	@classmethod
	def from_rect(
		cls,
		ID: str,
		x: float,
		y: float,
		width: float,
		height: float,
		color: Color = colors.WHITE,
		window: Window | None = None,
		scene: Scene | None = None,
		batch: Batch | None = None,
		group: Group | None = None,
		anchor: Point2D = (0, 0),
		dispatch: bool = True,
		mouse_detection: bool = False,
		tags: set[str] | None = None,
		target_tags: dict[str, TriggerInteractType] | None = None,
		**kwargs: EventHandler,
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
			color (Color, optional):
				Color of text.
				Defaults to Color.WHITE.
			window (Window, optional):
				Window for attaching self. Required if binding mouse events.
				Defaults to `scene.window` if scene is provided, else None.
			scene (Scene, optional):
				The scene the hitbox is from.
				Defaults to None.
			batch (Batch, optional):
				Batch for rendering.
				Defaults to `scene.batch` if scene is provided, else None.
			group (Group, optional):
				Group for rendering.
				Defaults to `scene.main_group` if scene is provided, else None.
			anchor (Point2D):
				Anchor position
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.gui.Button` for more info.
				Defaults to True.
			mouse_detection (bool, optional):
				If True, detect mouse collision + attach mouse events to window. Window must be set.
				Event handlers can still be manually invoked.
				Defaults to False.
			tags (set[str], optional):
				Tags trigger should possess, used for controlling collision more closely.
				Uses 'Default' tag if None passed.
				Defaults to None.
			target_tags (dict[str, TriggerInteractType], optional):
				Tags trigger interacts with as well as the type of interaction. see `~pgm.types.TriggerInteractType`.
				Uses 'Default': 'OVERLAP' if not overriden.
				Defaults to None.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
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
			dispatch,
			mouse_detection,
			tags,
			target_tags,
			_subtype=TriggerSubType.RECT,
			**kwargs,
		)

	def collide(
		self,
		other: Trigger | HasHitbox,
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm to determine if 2 objects are colliding.

		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Trigger):
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
		"""Run the SAT algorithm on a list of others. Return on the first overlap/collision.

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

		# Update polygon render
		self.render._coordinates = self.trigger.coords  # type: ignore[assignment]
		self.render._update_vertices()
		self.render.x = self.trigger.coords[0][0]
		self.render.y = self.trigger.coords[0][1]

	def _calc_anchor(self) -> None:
		self.trigger._calc_anchor()
		self._calc_coords()

	def enable(self) -> None: ... # noqa: D102
	def disable(self) -> None: ... # noqa: D102

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
	def anchor_x(self, val: AnchorX) -> None:
		self.trigger.anchor_x = val
		self._calc_anchor()

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.trigger.anchor_y

	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self.trigger.anchor_y = val
		self._calc_anchor()

	@property
	def anchor(self) -> Point2D:
		"""The anchor of the hitbox."""
		return self.trigger._anchor

	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self.trigger.anchor = val
		self._calc_anchor()

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

	def __str__(self) -> str:
		return (
			f'Hitbox("{self.ID}"): Subtype "{self.subtype}" @ {self.trigger._trans_pos} @ {self.angle} rad | {self.anchor} anchored\n'
			f'- Coords: {self.trigger.coords}'
		)


class HitboxCircle:
	"""Holds a Circle Hitbox with `.trigger` and `.render` objects."""

	# * Instance vars
	ID: str
	"""The unique ID of the hitbox to distinguish it"""
	trigger: TriggerCircle
	"""The trigger object"""
	render: Circle
	"""The render object"""
	subtype = TriggerSubType.CIRCLE
	"""Subtype (ex. 'rect') of hitbox"""

	# * Property vars
	_hitbox_color: Color

	def __init__(
		self,
		ID: str,
		x: float,
		y: float,
		radius: float,
		color: Color = colors.WHITE,
		window: Window | None = None,
		scene: Scene | None = None,
		batch: Batch | None = None,
		group: Group | None = None,
		anchor: Anchor = (0, 0),
		dispatch: bool = True,
		mouse_detection: bool = False,
		tags: set[str] | None = None,
		target_tags: dict[str, TriggerInteractType] | None = None,
		**kwargs: EventHandler,
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
			color (Color, optional):
				Color of text.
				Defaults to Color.WHITE.
			window (Window, optional):
				Window for attaching self. Required if binding mouse events.
				Defaults to `scene.window` if scene is provided, else None.
			scene (Scene, optional):
				The scene the hitbox is from.
				Defaults to None.
			batch (Batch, optional):
				Batch for rendering.
				Defaults to `scene.batch` if scene is provided, else None.
			group (Group, optional):
				Group for rendering.
				Defaults to `scene.main_group` if scene is provided, else None.
			anchor (Point2D, optional):
				The anchor position.
				Defaults to (0, 0).
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `~pgm.gui.Button` for more info.
				Defaults to True.
			mouse_detection (bool, optional):
				If True, detect mouse collision + attach mouse events to window. Window must be set.
				Event handlers can still be manually invoked.
				Defaults to False.
			tags (set[str], optional):
				Tags trigger should possess, used for controlling collision more closely.
				Defaults to None.
			target_tags (dict[str, TriggerInteractType], optional):
				Tags trigger interacts with as well as the type of interaction. see `~pgm.types.TriggerInteractType`.
				Defaults to None.
			_subtype (TriggerSubType, optional):
				The subtype of the hitbox. Ex: 'RECT', 'CIRCLE'.
				Defaults to TriggerSubType.NONE.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		self.render = Circle(
			x,
			y,
			radius,
			color=color,
			batch=batch if batch else scene.batch if scene else None,
			group=group if group else scene.main_group if scene else None,
		)
		self.trigger = TriggerCircle(
			ID,
			x,
			y,
			radius,
			window,
			scene,
			anchor,
			dispatch,
			mouse_detection,
			tags,
			target_tags,
			**kwargs,
		)

		self.ID = ID
		self._hitbox_color = color

	def collide(
		self,
		other: Trigger | HasHitbox,
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm to determine if 2 objects are colliding.

		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Trigger | HasHitbox):
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
		"""Run the SAT algorithm on a list of others. Return on the first overlap/collision.

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

	def __str__(self) -> str:
		return f'HitboxCircle("{self.ID}"): Subtype "Circle" @ {self.trigger._trans_pos} @ {self.trigger.radius} size @ {self.angle} rad | {self.anchor} anchored'
