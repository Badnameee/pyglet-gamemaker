"""Module holding trigger classes, as well as hitbox-esque protocol class for runtime checking.

Currently holds `.HasHitbox`, `.Trigger`, `.TriggerCircle`.

Use `~pgm.shapes.{class}` instead of `~pgm.shapes.trigger.{class}`.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pyglet
from pyglet.math import Vec2

from ..event_dispatcher import EventDispatcher
from ..types import HasHitbox, TriggerInteractType, TriggerStatus, TriggerSubType

if TYPE_CHECKING:
	from typing import Self

	from ..scene import Scene
	from ..types import Axis, EventHandler, Point2D
	from ..window import Window


class TargetTagManager:
	"""Manages tags for what tags a trigger, hitbox, etc. can interact with.

	Adds functionality for removing tags when value is NONE.
	"""

	_set: set[str]
	_dict: dict[str, TriggerInteractType]

	def __init__(self, d: dict[str, TriggerInteractType] | None) -> None:  # noqa: D107
		self._dict = d or {}
		self._set = set(d) if d else set()

	def __getitem__(self, key: str) -> TriggerInteractType:
		return self._dict[key]

	def __setitem__(self, key: str, value: TriggerInteractType) -> None:
		# Remove item
		if key in self._set and value == TriggerInteractType.NONE:
			self._set.remove(key)
			self._dict.pop(key)
			return

		# Add new entry in set
		if key not in self._set:
			self._set.add(key)
		# Add/set value
		self._dict[key] = value

	def __str__(self) -> str:
		return str(self._dict)

	def __repr__(self) -> str:
		return f'{self._dict=}, {self._set=}'


class Trigger(EventDispatcher):
	"""Store a convex trigger that uses SAT (Separating Axis Theorem) method for collision.

	Can use `.from_rect()` to create rectangular trigger, and `.from_point()` to create point trigger.
	Use `~pgm.shapes.TriggerCircle` for circle collisions.

	For _coord vars (ex. `._local_coords`), there are 3 types of transformation
	- translated: Adding global position of trigger to local position (moving in 2D space)
	- rotated: Adding the rotation of the trigger
	- anchored: Shifting global position to account for anchor position of trigger

	Dispatches:
	- `on_mouse_trigger_enter(self, x, y, MTV)` when mouse enters trigger
	- `on_mouse_trigger_motion(self, x, y, MTV)` when mouse moves in trigger
	- `on_mouse_trigger_exit(self, x, y)` when mouse exits trigger
	- `on_trigger_enter(self, other, MTV)` when trigger enters trigger
	- `on_trigger_exit(self, other, MTV)` when trigger exits trigger
	"""

	# * Constant vars
	EVENT_TYPES = (
		'on_mouse_trigger_enter',
		'on_mouse_trigger_motion',
		'on_mouse_trigger_exit',
		'on_trigger_enter',
		'on_trigger_exit',
	)

	# * Instance vars
	ID: str
	"""The unique ID of trigger to distinguish it"""
	coords: tuple[Point2D, ...]
	"""The final coordinates of the trigger"""
	window: Window | None
	"""Window trigger is associated with"""
	scene: Scene | None
	"""The scene the trigger is from."""
	_trans_pos: Point2D
	"""Holds the translation amount from (0, 0)"""
	subtype: TriggerSubType
	"""Subtype (ex. 'RECT') of trigger"""
	enabled: bool = True
	"""If True, trigger is enabled and dispatches events"""
	status = TriggerStatus.MOUSE_NOHIT | TriggerStatus.TRIGGER_NOHIT
	"""Flag for status of trigger. See `~pgm.types.TriggerStatus`."""
	dispatch: bool
	"""If False, don't dispatch events to handlers"""
	mouse_detection: bool
	"""If True, detect mouse collision + attach mouse events to window"""
	hit_triggers: set[Trigger]
	"""Stores all overlapping hitboxes"""
	tags: set[str]
	"""All tags this trigger possesses"""

	# * Property vars
	_anchor: Point2D = 0, 0
	_angle: float = 0

	# * Private vars
	_local_coords: tuple[Point2D, ...] = ()
	"""Holds the *untransformed* coords relative to first coordinate"""
	_raw_coords: tuple[Point2D, ...] = ()
	"""Holds the *unrotated* AND *unanchored*, but *translated/global* coords"""
	_unanchored_coords: tuple[Point2D, ...] = ()
	"""Holds the *unanchored*, *translated/global* coords"""
	_anchor_coords: tuple[Point2D, ...] = ()
	"""Holds the *untransformed* coords relative to anchor pos"""
	_rotation_amount: tuple[Point2D, ...] = ()
	"""Holds the translation due to rotation of each point"""
	_last_mouse_info: Point2D = 0, 0
	_mouse_trigger: Trigger | None = None
	"""Trigger on the mouse for mouse detection"""
	_target_tags: TargetTagManager

	def __init__(
		self,
		ID: str,
		coords: tuple[Point2D, ...],
		window: Window | None = None,
		scene: Scene | None = None,
		anchor: Point2D = (0, 0),
		dispatch: bool = True,
		mouse_detection: bool = False,
		tags: set[str] | None = None,
		target_tags: dict[str, TriggerInteractType] | None = None,
		*,
		_subtype: TriggerSubType = TriggerSubType.NONE,
		**kwargs: EventHandler,
	) -> None:
		"""Create a trigger.

		Args:
			ID (str):
				Name/ID of trigger
			coords (tuple[Point2D, ...]):
				The coordinates of the trigger. Use `.from_point` to create from a single point.
			window (Window, optional):
				Window for attaching self. Required if binding mouse events.
				Defaults to None.
			scene (Scene | None):
				The scene the trigger is from.
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
				Tags trigger should possess, used for controlling collision more closely.
				Uses 'Default' tag by default.
				Defaults to None.
			target_tags (dict[str, TriggerInteractType], optional):
				Tags trigger interacts with as well as the type of interaction. see `~pgm.types.TriggerInteractType`.
				Uses 'Default': 'OVERLAP' if not overriden.
				Defaults to None.
			_subtype (TriggerSubType, optional)
				The subtype of the trigger (i.e. 'RECT').
				Defaults to TriggerSubType.NONE.
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		self.ID = ID
		self.window, self.scene = window, scene
		self._trans_pos = coords[0]
		self._raw_coords = coords
		self.anchor = anchor
		self.subtype = _subtype
		self.hit_triggers = set()
		self.tags = tags or {'Default'}
		# Use Default first so that target_tags can overwrite
		self._target_tags = TargetTagManager(
			{'Default': TriggerInteractType.OVERLAP} | (target_tags or {})
		)

		self.dispatch = dispatch
		self.mouse_detection = mouse_detection

		# Register events
		self.register_events()
		# Adds event handler for mouse events
		if mouse_detection:
			self.bind_mouse()
		# Bind user kwargs
		if dispatch:
			self.bind_events(**kwargs)

	@classmethod
	def from_rect(
		cls,
		ID: str,
		x: float,
		y: float,
		width: float,
		height: float,
		window: Window | None = None,
		scene: Scene | None = None,
		anchor: Point2D = (0, 0),
		dispatch: bool = True,
		mouse_detection: bool = True,
		tags: set[str] | None = None,
		target_tags: dict[str, TriggerInteractType] | None = None,
		**kwargs: EventHandler,
	) -> Self:
		"""Create a trigger from rectangle args.

		Args:
			ID (str):
				Name/ID of trigger
			x (float):
				x position
			y (float):
				y position
			width (float):
				Width of rect
			height (float):
				Height of rect
			window (Window, optional):
				Window for attaching self
				Defaults to None.
			scene (Scene | None):
				The scene the trigger is from.
			anchor (Point2D, optional):
				Anchor position.
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
			window,
			scene,
			anchor,
			dispatch,
			mouse_detection,
			tags,
			target_tags,
			_subtype=TriggerSubType.RECT,
			**kwargs,
		)

	@classmethod
	def from_point(
		cls,
		ID: str,
		x: float,
		y: float,
		window: Window | None = None,
		scene: Scene | None = None,
		anchor: Point2D = (0, 0),
		dispatch: bool = True,
		mouse_detection: bool = True,
		tags: set[str] | None = None,
		target_tags: dict[str, TriggerInteractType] | None = None,
		**kwargs: EventHandler,
	) -> Self:
		"""Create a trigger from a point.

		Args:
			ID (str):
				Name/ID of trigger
			x (float):
				x position
			y (float):
				y position
			width (float):
				Width of rect
			height (float):
				Height of rect
			window (Window, optional):
				Window for attaching self.
				Defaults to None.
			scene (Scene | None):
				The scene the trigger is from.
			anchor (Point2D, optional):
				Anchor position.
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
			((x, y),),
			window,
			scene,
			anchor,
			dispatch,
			mouse_detection,
			tags,
			target_tags,
			_subtype=TriggerSubType.POINT,
			**kwargs,
		)

	def _get_axes(self, remove_dupes: bool) -> list[Vec2]:
		# Get the normal axes of the trigger as Vec2 (for SAT).

		# * Special case: point trigger has no axes
		if self.subtype == TriggerSubType.POINT:
			return []

		axes = []

		# Loops through vertices and gets all adjacent pairs
		for i in range(
			len(self.coords)
			// (2 if remove_dupes and self.subtype == TriggerSubType.RECT else 1)
		):
			# Grabbing vertex positions
			p1, p2 = self.coords[i], self.coords[(i + 1) % len(self.coords)]

			# Calculates the vector between them
			vec = p1[0] - p2[0], p1[1] - p2[1]
			# Gets perpendicular vector and normalizes it
			# Normalizing helps get MTV
			axes.append(Vec2(-vec[1], vec[0]).normalize())

		return axes

	def _project(self, axis: Vec2, remove_dupes: bool) -> tuple[float, float]:
		# Project the trigger onto an axis (use self._get_axes()) (for SAT).
		# 	Returns a line

		# Stores the left (minimum) and right (maximum) of line
		maximum = minimum = axis.dot(self.coords[0])

		# Gets projections for each vertice
		# Vertice with lowest and highest projections are used in line
		for i in range(
			len(self.coords)
			// (2 if remove_dupes and self.subtype == TriggerSubType.RECT else 1)
		):
			# Projection using dot product
			pos = axis.dot(self.coords[i])
			maximum = max(maximum, pos)
			minimum = min(minimum, pos)

		return minimum, maximum

	@staticmethod
	def _get_intersection_length(
		l1: tuple[float, float], l2: tuple[float, float]
	) -> float:
		# Get the length of intersection between 2 lines (for SAT).

		# Line1 cannot possibly intersect
		if l1[0] >= l2[1] or l1[1] < l2[0]:
			return 0

		# Left of line1 inside line2
		if l2[0] <= l1[0] < l2[1]:
			return min(l1[1], l2[1]) - l1[0]

		# Right of line1 inside line2
		if l2[0] < l1[1] <= l2[1]:
			return min(l1[0], l2[0]) - l1[1]

		# Line2 in line1
		return l2[1] - l2[0]

	@staticmethod
	def _contains(l1: tuple[float, float], l2: tuple[float, float]) -> bool:
		# Check if one of the lines in completely contained inside the other (for SAT).
		return (l1[0] < l2[0] and l1[1] > l2[1]) or (l2[0] < l1[0] and l2[1] > l1[1])

	@staticmethod
	def _shorter_than(l1: tuple[float, float], l2: tuple[float, float]) -> bool:
		# Check if l1 shorter than l2
		return abs(l1[1] - l1[0]) < abs(l2[1] - l2[0])

	def collide(
		self,
		other: Trigger | HasHitbox,
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm to determine if 2 objects are colliding.

		The object the method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Trigger):
				The other trigger to detect collision with
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[bool, Vec2 | None]: Whether collision passed and MTV (None if no collision)
		"""
		# Get trigger if not subclass
		if not isinstance(other, Trigger):
			if isinstance(other, HasHitbox):
				other = other.trigger
			else:
				raise TypeError(
					f'Hitbox passed to "Trigger.collide()" method is of type {other.__class__.__name__}, which does not contain a `.trigger` attribute.'
				)

		if not self.enabled or not other.enabled:
			return False, None

		# Check other has at least one tag
		if not self._target_tags._set.intersection(other.tags):
			return False, None

		# Do not try to check 2 points
		if (
			self.subtype == TriggerSubType.POINT
			and other.subtype == TriggerSubType.POINT
		):
			raise ValueError(
				f'Colliders "{self.ID}" and "{other.ID}" cannot both be points.'
			)

		if self.subtype == TriggerSubType.POINT:
			return other._collide_point(self, sacrifice_MTV)
		if other.subtype == TriggerSubType.POINT:
			return self._collide_point(other, sacrifice_MTV)

		# Get circle collision axis
		if isinstance(self, TriggerCircle):
			self._set_collision_axis(other)
		if isinstance(other, TriggerCircle):
			other._set_collision_axis(self)

		# * Step 1: Get the normal axes of each edge
		axes = self._get_axes(sacrifice_MTV)
		other_axes = other._get_axes(sacrifice_MTV)

		MTV_len = float('inf')
		MTV_axis = Vec2(0, 0)

		# * Step 2: Project the shapes onto each axis
		for axis in axes + other_axes:
			l1 = self._project(axis, sacrifice_MTV)
			l2 = other._project(axis, sacrifice_MTV)

			# * Step 3: Check for intersection
			# * 	If the projections do not intersect, there cannot be a collision
			if not (overlap := self._get_intersection_length(l1, l2)):
				# Run post collision to update triggers
				self._post_trigger_collision(other, TriggerStatus.TRIGGER_NOHIT)
				other._post_trigger_collision(self, TriggerStatus.TRIGGER_NOHIT)
				return False, None

			# * Step 4: If line completely contained, find nearest exit
			if self._contains(l1, l2):
				# Check which direction is less distance
				left_diff = abs(l1[0] - l2[0])
				right_diff = abs(l1[1] - l2[1])

				if left_diff < right_diff:
					overlap = overlap + left_diff
				else:
					overlap = -(overlap + right_diff)

			# * Step 5: For MTV - Get the smallest intersection length
			# *	and store it along with the axis
			if abs(overlap) < abs(MTV_len):
				MTV_len = overlap
				MTV_axis = axis

		MTV = MTV_axis * MTV_len

		# Run post collision to update triggers
		self._post_trigger_collision(other, TriggerStatus.TRIGGER_HIT, MTV)
		other._post_trigger_collision(self, TriggerStatus.TRIGGER_HIT, MTV)

		return True, MTV

	def collide_any(
		self,
		others: list[Trigger | HasHitbox],
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm on a list of others. Return on the first overlap/collision.

		Args:
			others (list[Trigger]):
				List of others to check collision with self
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[bool, Vec2 | None]: Whether collision passed and MTV (None if no collision)
		"""
		if not self.enabled:
			return False, None

		for rect in others:
			if (collision_info := self.collide(rect, sacrifice_MTV))[0]:
				return collision_info

		return False, None

	def _collide_point(
		self, other: Trigger, sacrifice_MTV: bool
	) -> tuple[bool, Vec2 | None]:
		"""Run the SAT algorithm on a polygon and a point. Do not invoke manually.

		Args:
			other (Trigger):
				The other trigger to detect collision with
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[bool, Vec2 | None]: Whether collision passed and MTV (None if no collision)
		"""
		if not self.enabled:
			return False, None

		# * Step 1: Get the normal axes of each edge
		axes = self._get_axes(sacrifice_MTV)

		# These store the length and axis for the MTV
		MTV_len = float('inf')
		MTV_axis = Vec2(0, 0)

		# * Step 2: Project the shapes onto each axis
		for axis in axes:
			l1 = self._project(axis, sacrifice_MTV)
			l2 = other._project(axis, sacrifice_MTV)

			# * Step 3: Check for intersection
			# * 	If the projections do not intersect, there cannot be a collision
			if not self._contains(l1, l2):
				return False, None

			# * Step 4: Line is always containing point, so simplified overlap algorithm
			left_diff = abs(l1[0] - l2[0])
			right_diff = abs(l1[1] - l2[1])

			if left_diff < right_diff:
				overlap = left_diff
			else:
				overlap = -right_diff

			# * Step 5: For MTV - Get the smallest intersection length
			# *	and store it along with the axis
			if abs(overlap) < abs(MTV_len):
				MTV_len = overlap
				MTV_axis = axis

		MTV = MTV_axis * MTV_len

		return True, MTV

	def _post_trigger_collision(
		self, other: Trigger, hit_status: TriggerStatus, MTV: Vec2 | None = None
	) -> None:
		# Update internals after collision, not just enter or exit
		# 	Also dispatch events

		# First hit
		if hit_status & TriggerStatus.TRIGGER_HIT and other not in self.hit_triggers:
			self.hit_triggers.add(other)
			self.dispatch_event('on_trigger_enter', self, other, MTV)

		# First nohit
		elif hit_status & TriggerStatus.TRIGGER_NOHIT and other in self.hit_triggers:
			self.hit_triggers.remove(other)
			self.dispatch_event('on_trigger_exit', self, other)

		# Flip bit according to if intersecting any other triggers
		if self.status & TriggerStatus.TRIGGER_HIT and not self.hit_triggers:
			self.status &= ~TriggerStatus.TRIGGER_HIT
			self.status |= TriggerStatus.TRIGGER_NOHIT
		elif self.status & TriggerStatus.TRIGGER_NOHIT and self.hit_triggers:
			self.status &= ~TriggerStatus.TRIGGER_NOHIT
			self.status |= TriggerStatus.TRIGGER_HIT

	def _calc_coords(self) -> None:
		# Updates coordinates based on new position, angle, and/or anchor.

		# Steps:
		# 1. Update local coords
		# 2. Update anchor coords
		# 3. Get displacement caused by rotation of anchor coords
		# 4. Add translation to local to get raw
		# 5. Add anchor rotation displacement to raw to get unanchored
		# 6. Add anchor to unanchored to get final

		# Use the raw coords, which are precalculated in __init__
		# before first ._calc_coords call

		self._local_coords = tuple(
			(
				coord[0] - self._raw_coords[0][0],
				coord[1] - self._raw_coords[0][1],
			)
			for coord in self._raw_coords
		)

		self._anchor_coords = tuple(
			(coord[0] - self.anchor_x, coord[1] - self.anchor_y)
			for coord in self._local_coords
		)

		self._rotation_amount = tuple(
			(
				self._get_rotated_pos(coord, 'x') - coord[0],
				self._get_rotated_pos(coord, 'y') - coord[1],
			)
			for coord in self._anchor_coords
		)

		self._raw_coords = tuple(
			(coord[0] + self._trans_pos[0], coord[1] + self._trans_pos[1])
			for coord in self._local_coords
		)

		self._unanchored_coords = tuple(
			(coord[0] + rotation[0], coord[1] + rotation[1])
			for coord, rotation in zip(
				self._raw_coords, self._rotation_amount, strict=True
			)
		)

		self.coords = tuple(
			(coord[0] - self.anchor_x, coord[1] - self.anchor_y)
			for coord in self._unanchored_coords
		)

	def _get_rotated_pos(self, coord: Point2D, axis: Axis) -> float:
		# Gets position of point if it were rotated
		if axis == 'x':
			return coord[0] * math.cos(self.angle) - coord[1] * math.sin(self.angle)
		if axis == 'y':
			return coord[0] * math.sin(self.angle) + coord[1] * math.cos(self.angle)

	def _update_mouse_collision(self, x: int, y: int) -> None:
		# Update the status of the mouse given new info

		if not self._mouse_trigger:
			self._mouse_trigger = Trigger.from_point('MOUSE', x, y)
		else:
			self._mouse_trigger.pos = x, y

		collided, MTV = self.collide(self._mouse_trigger, False)

		# Enter
		if collided:
			# First time
			if self.status & TriggerStatus.MOUSE_NOHIT:
				self.status &= ~TriggerStatus.MOUSE_NOHIT
				self.status |= TriggerStatus.MOUSE_HIT
				if self.dispatch:
					self.dispatch_event('on_mouse_trigger_enter', self, x, y, MTV)
			# Repeat offender
			elif self.dispatch:
				self.dispatch_event('on_mouse_trigger_motion', self, x, y, MTV)

		# Exit
		else:
			if self.status & TriggerStatus.MOUSE_HIT:
				self.status &= ~TriggerStatus.MOUSE_HIT
				self.status |= TriggerStatus.MOUSE_NOHIT
				if self.dispatch:
					self.dispatch_event('on_mouse_trigger_exit', self, x, y)

		self._last_mouse_info = x, y

	def bind_mouse(self) -> None:
		"""Bind mouse events to widget."""
		if not self.window:
			return
		self.window.push_handlers(
			on_mouse_press=self._on_mouse_press,
			on_mouse_release=self._on_mouse_release,
			on_mouse_motion=self._on_mouse_motion,
			on_mouse_drag=self._on_mouse_drag,
		)

	def _on_mouse_press(self, x: int, y: int, _buttons: int, _modifiers: int) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y)
		return False

	def _on_mouse_motion(self, x: int, y: int, _dx: int, _dy: int) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y)
		return False

	def _on_mouse_release(self, x: int, y: int, _buttons: int, _modifiers: int) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y)
		return False

	def _on_mouse_drag(
		self, x: int, y: int, _dx: int, _dy: int, _buttons: int, _modifiers: int
	) -> bool:
		if not self.enabled:
			return False
		self._update_mouse_collision(x, y)
		return False

	@property
	def x(self) -> float:
		"""The x position of anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._trans_pos[0]

	@x.setter
	def x(self, val: float) -> None:
		self._trans_pos = val, self._trans_pos[1]
		self._calc_coords()

	@property
	def y(self) -> float:
		"""The y position of anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._trans_pos[1]

	@y.setter
	def y(self, val: float) -> None:
		self._trans_pos = self._trans_pos[0], val
		self._calc_coords()

	@property
	def pos(self) -> Point2D:
		"""The position of anchor point."""
		return self._trans_pos

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self._trans_pos = val
		self._calc_coords()

	@property
	def anchor_x(self) -> float:
		"""The x anchor of trigger.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self._anchor[0]

	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self._anchor = val, self.anchor_y
		self._calc_coords()

	@property
	def anchor_y(self) -> float:
		"""The y anchor of trigger.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self._anchor[1]

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self._anchor = self.anchor_x, val
		self._calc_coords()

	@property
	def anchor(self) -> Point2D:
		"""The anchor of trigger."""
		return self._anchor

	@anchor.setter
	def anchor(self, val: Point2D) -> None:
		self._anchor = val
		self._calc_coords()

	@property
	def angle(self) -> float:
		"""Angle, in radians, of trigger."""
		return self._angle

	@angle.setter
	def angle(self, val: float) -> None:
		self._angle = val
		self._calc_coords()

	@property
	def target_tags(self) -> TargetTagManager:
		"""Get the tags this trigger targets. See `~pgm.shapes.TargetTagManager`."""
		return self._target_tags

	def __str__(self) -> str:
		return (
			f'Trigger ({self.ID}): Subtype "{self.subtype}" @ {self._trans_pos} @ {self.angle} rad | {self.anchor} anchored\n'
			f'- Coords: {self.coords}'
		)


class TriggerCircle(Trigger):
	"""Holds a trigger for circle-polygon collisions.

	Do not try to access `.coords` as they are not real coords.
	"""

	# * Instance vars
	axis: Vec2
	"""The axis between the center and the closest point on last trigger checked for collision."""
	radius: float
	"""The radius of the circle"""

	def __init__(
		self,
		ID: str,
		x: float,
		y: float,
		radius: float,
		window: Window | None = None,
		scene: Scene | None = None,
		anchor: Point2D = (0, 0),
		dispatch: bool = True,
		mouse_detection: bool = False,
		tags: set[str] | None = None,
		target_tags: dict[str, TriggerInteractType] | None = None,
		**kwargs: EventHandler,
	) -> None:
		"""Create a trigger from a circle.

		Args:
			ID (str):
				Name/ID of trigger
			x (float):
				Center x
			y (float):
				Center y
			radius (float):
				The radius of the circle
			window (Window, optional):
				Window for attaching self
				Defaults to None.
			scene (Scene | None):
				The scene the trigger is from.
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
			kwargs (EventHandler):
				Event handlers to attach. Has priority over scene implementation. (name=func, see `.EVENT_TYPES` for event names)
		"""
		super().__init__(
			ID,
			((x, y), (radius, 0)),
			window,
			scene,
			anchor,
			dispatch,
			mouse_detection,
			tags,
			target_tags,
			_subtype=TriggerSubType.CIRCLE,
			**kwargs,
		)
		self.axis = Vec2(0, 0)
		self.radius = radius

	def _get_axes(self, _sacrifice_MTV: bool) -> list[Vec2]:
		return [self.axis.normalize()]

	def _project(self, axis: Vec2, _remove_dupes: bool) -> tuple[float, float]:
		proj = axis.dot(Vec2(*self.coords[0]))
		return proj - self.radius, proj + self.radius

	def collide_any(  # noqa: D102
		self,
		others: list[Trigger | HasHitbox],
		sacrifice_MTV: bool = False,
	) -> tuple[bool, Vec2 | None]:
		for rect in others:
			if (collision_info := self.collide(rect, sacrifice_MTV))[0]:
				return collision_info

		return False, None

	def _set_collision_axis(self, trigger: Trigger) -> None:
		"""Get closest point on trigger to circle.

		Args:
			trigger (Trigger): Trigger to get axis to
		"""

		def get_projection(v1: Vec2, v2: Vec2) -> Vec2:
			# Clamping forces the projection to be within the 2 vertices of the polygon
			# (or 2 endpoints of v2) by forcing scale factor to be from 0-1
			# This facilitates finding closest points on polygon to circle center
			return pyglet.math.clamp(v1.dot(v2) / v2.length_squared(), 0, 1) * v2

		# Get trigger if not subclass
		if not isinstance(trigger, Trigger):
			trigger = trigger.trigger

		# * Special case: circle-circle collision
		# *	To calculate collision axis, use line between centers
		if isinstance(trigger, TriggerCircle):
			# Get vector pointing from the center of circle # 1 to the edge of circle # 2
			self.axis = Vec2(
				self.coords[0][0] - trigger.coords[0][0],
				self.coords[0][1] - trigger.coords[0][1],
			)
			self.axis = self.axis.normalize() * (self.axis.length() - trigger.radius)
			return

		# Get closest point to other trigger
		least = Vec2(0, 0), float('inf')
		# Loop through each axis on polygon
		for i in range(len(trigger.coords)):
			# Grab vertex positions
			p1, p2 = trigger.coords[i], trigger.coords[(i + 1) % len(trigger.coords)]

			# Calculate the vector between vertices
			vec = Vec2(p2[0] - p1[0], p2[1] - p1[1])

			# Vector from vertex to center of circle
			pre_proj = Vec2(self.coords[0][0] - p1[0], self.coords[0][1] - p1[1])

			# Proj holds the vector from p1 to the closest point
			# 	on the polygon to the circle center
			proj = get_projection(pre_proj, vec)
			# Subtracting pre_proj gives vector from circle center to closest point
			diff = proj - pre_proj

			# Update least
			if (length := diff.length()) < least[1]:
				least = diff, length

		self.axis = least[0]

	def _calc_coords(self) -> None:
		# Same algorithm as in Trigger, but optimized for single center coordinate of circle
		self._local_coords = ((0, 0),)
		self._anchor_coords = ((-self.anchor_x, -self.anchor_y),)
		self._rotation_amount = (
			(
				self._get_rotated_pos(self._anchor_coords[0], 'x')
				- self._anchor_coords[0][0],
				self._get_rotated_pos(self._anchor_coords[0], 'y')
				- self._anchor_coords[0][1],
			),
		)
		self._raw_coords = (self._trans_pos,)
		self._unanchored_coords = (
			(
				self._raw_coords[0][0] + self._rotation_amount[0][0],
				self._raw_coords[0][1] + self._rotation_amount[0][1],
			),
		)
		self.coords = (
			(
				self._unanchored_coords[0][0] - self.anchor_x,
				self._unanchored_coords[0][1] - self.anchor_y,
			),
		)

	def __str__(self) -> str:
		return f'Trigger ({self.ID}): Subtype "Circle" @ {self._trans_pos} @ {self.radius} size @ {self.angle} rad | {self.anchor} anchored\n'
