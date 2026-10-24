from __future__ import annotations

import weakref

from pyglet.graphics import Group
from pyglet.math import Mat4

from .button import Button
from .entry import Entry
from .text import Text
from .text_button import TextButton
from .widget import Widget

from ..window import Window  # isort: skip


class HUDGroup(Group):
	"""A group tailored to draw objects regardless of view matrix, similar to a HUD."""

	window: Window | None
	_old_view: Mat4

	def __init__(
		self, order: int = 0, parent: Group | None = None, window: Window | None = None
	) -> None:
		"""Initialize a rendering group.

		Args:
			order (int, optional):
				Set the order to render above or below other Groups.
				Lower orders are drawn first.
				Defaults to 0.
			parent (Group, optional):
				Group to contain this Group; its state will be set before this Group's state.
				Defaults to None.
			window (Window, optional):
				The window to render on (window to switch view matrix of).
				Defaults to None.
		"""
		super().__init__(order, parent)
		self.window = window

	def set_state(self) -> None:
		"""Apply the OpenGL state change by temporarily removing view matrix for UI drawing."""
		if not self.window:
			raise TypeError('HUDGroup.window not set.')
		self._old_view = self.window.view
		self.window.view = Mat4()  # Identity matrix

	def unset_state(self) -> None:
		"""Repeal the OpenGL state change by replacing view matrix after UI drawing."""
		if not self.window:
			raise TypeError('HUDGroup.window not set.')
		self.window.view = self._old_view
