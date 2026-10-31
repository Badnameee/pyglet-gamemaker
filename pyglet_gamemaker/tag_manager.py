"""Holds general utility functions used internally by pyglet-gamemaker."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .types import TriggerInteractType

if TYPE_CHECKING:
	...


class TargetTagManager:
	"""Manages tags for what tags an object can target / possibly interact with.

	Adds functionality for removing tags when value is NONE.
	"""

	_set: set[str]
	_dict: dict[str, TriggerInteractType]

	def __init__(self, d: dict[str, TriggerInteractType] | None) -> None:  # noqa: D107
		self._dict = d or {}
		# Immediately remove items with 'NONE'
		self._set = (
			{k for k, v in d.items() if v != TriggerInteractType.NONE} if d else set()
		)

	def intersection(self, tags: set[str]) -> set[str]:
		"""Return interesction of target tags with trigger tags of other trigger.

		Args:
			tags (set[str]):
				Trigger tags of other trigger

		Returns:
			set[str]: All tags that allow for collision between both triggers
		"""
		return self._set.intersection(tags)

	def __getitem__(self, key: str) -> TriggerInteractType:
		return self._dict.get(key, TriggerInteractType.NONE)

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
		return f'TargetTagManager={self._dict}'

	def __repr__(self) -> str:
		return f'{self._dict=}, {self._set=}'


class TagManager:
	"""Manages both tags and the target tags of an object.

	- `.tags`: Holds tags this object is a part of
	- `.target_tags`: Holds tags this object can possibly interact with, as well as the max level of collision possible, see `~pgm.tag_manager.TargetTagManager`
	"""

	tags: set[str]
	"""Holds tags this object possesses"""
	target_tags: TargetTagManager
	"""Manages the object can interact with, as well as the interaction level, see `~pgm.types.TriggerInteractType`."""

	def __init__(
		self, tags: set[str] | None, target_tags: dict[str, TriggerInteractType] | None
	) -> None:
		"""Create a tag manager from tags and target tags.

		Args:
			tags (set[str] | None):
				Tags the object should possess.
				Uses 'Default' if None passed.
			target_tags (dict[str, TriggerInteractType] | None):
				Tags the object can interact with, as well as the interaction level, see `~pgm.types.TriggerInteractType`.
				Uses 'Default': 'OVERLAP' if not overriden.
		"""
		self.tags = tags if tags is not None else {'Default'}
		# Use Default first so that target_tags can overwrite
		self.target_tags = TargetTagManager(
			{'Default': TriggerInteractType.OVERLAP} | (target_tags or {})
		)

	def _get_one_sided_collision_level(self, other: TagManager) -> TriggerInteractType:
		colliding_tags = self.target_tags.intersection(other.tags)
		if not colliding_tags:
			return TriggerInteractType.NONE

		for tag in colliding_tags:
			# Overlap takes precedence
			if (
				self.target_tags[tag] == TriggerInteractType.OVERLAP
				or other.target_tags[tag] == TriggerInteractType.OVERLAP
			):
				return TriggerInteractType.OVERLAP
		# If entire loop passes, then all tags were only collide
		return TriggerInteractType.COLLIDE

	def get_collision_level(self, other: TagManager) -> TriggerInteractType:
		"""Get the collision level according to another object's tag manager.

		Args:
			other (TagManager):
				The other tag manager

		Returns:
			TriggerInteractType: The level of collision. See `~pgm.types.TriggerInteractType`.
		"""
		return min(
			self._get_one_sided_collision_level(other),
			other._get_one_sided_collision_level(self),
		)

	def __str__(self) -> str:
		return f'TagManager:\nTags: {self.tags}\nTarget Tags: {self.target_tags._dict}'
