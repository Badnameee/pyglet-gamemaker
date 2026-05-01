from __future__ import annotations

from typing import TYPE_CHECKING

from ..gui.widget import Widget
from . import Hitbox

if TYPE_CHECKING:
	from ..types import Point2D


class Trigger(Hitbox, EventDispatcher):
	def __init__(
		self,
		coords: tuple[Point2D, ...],
		anchor_pos: Point2D = (0, 0),
		dispatch: bool = True,
		attach_mouse_events: bool = True,
		*,
		_subtype: str | None = None,
	) -> None:
		super().__init__(coords, anchor_pos, _subtype=_subtype)
		Widget.__init__(self)

		self.dispatch = dispatch
		self.attach_mouse_events = attach_mouse_events
