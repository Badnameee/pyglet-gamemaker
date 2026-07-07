"""Module holding Camera class.

Use `~pgm.Camera` instead of `~pgm.camera.Camera`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.math import Vec3

if TYPE_CHECKING:
	from .window import Window


class Camera:
	"""A camera for the window that can control transformations.

	Currently supports:
	- Translation
	- Scale
	- Rotation
	- Anchor point (only static)

	Call appropriate functions to either transform by an amount or transformation to an amount.
	- NOTE: These transformations are **relative** to the default settings provided at creation.
	"""

	def __init__(
		self,
		window: Window | None = None,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
		scale_x: float | None = None,
		scale_y: float | None = None,
		scale_z: float | None = None,
		angle_x: float | None = None,
		angle_y: float | None = None,
		angle_z: float | None = None,
		anchor_x: float | None = None,
		anchor_y: float | None = None,
		anchor_z: float | None = None,
	) -> None:
		"""Create a Camera object with optional default parameters.

		These default parameters are what the camera resets to when calling `.reset`.

		Args:
			window (Window, optional):
				The window the camera is attached to.
				Leave as None if passing to `pgm.Window`.
				Defaults to None.
			x (float | None, optional):
				x translation.
				Defaults to None.
			y (float | None, optional):
				y translation.
				Defaults to None.
			z (float | None, optional):
				z translation.
				Defaults to None.
			scale_x (float | None, optional):
				x scale factor.
				Defaults to None.
			scale_y (float | None, optional):
				y scale factor.
				Defaults to None.
			scale_z (float | None, optional):
				z scale factor.
				Defaults to None.
			angle_x (float | None, optional):
				angle on x axis.
				Defaults to None.
			angle_y (float | None, optional):
				angle on y axis.
				Defaults to None.
			angle_z (float | None, optional):
				angle on z axis.
				Defaults to None.
			anchor_x (float | None, optional):
				x anchor position.
				Defaults to None.
			anchor_y (float | None, optional):
				y anchor position.
				Defaults to None.
			anchor_z (float | None, optional):
				z anchor position.
				Defaults to None.
		"""
		self.window = window
		self.og_mat = window.view if window else None

		self._initial_pos = self._pos = (x or 0), (y or 0), (z or 0)
		self._start_scale = self._scale = (scale_x or 1), (scale_y or 1), (scale_z or 1)
		self._start_angle = self._angle = (angle_x or 0), (angle_y or 0), (angle_z or 0)
		self._initial_anchor = self._anchor = (
			(anchor_x or 0),
			(anchor_y or 0),
			(anchor_z or 0),
		)

		# Account for initial conditions
		self.transform(x, y, z, scale_x, scale_y, scale_z, angle_x, angle_y, angle_z)

	def update(self) -> None:
		"""Update the camera view with previously changed values."""
		if self.og_mat is None:
			raise TypeError(
				'"Camera.og_mat" must be set using "Camera.set_window(...)".'
			)

		# SRT: Scale, rotate, translate
		# 	However, in order to rotate around a point, translate so the point is @ (0, 0),
		# 	then rotate, then translate back
		if not self.window:
			return
		self.window.view = (
			self.og_mat.scale(Vec3(*self._scale))
			.translate(Vec3(*self._anchor))
			.rotate(self._angle[0], Vec3(1, 0, 0))
			.rotate(self._angle[1], Vec3(0, 1, 0))
			.rotate(self._angle[2], Vec3(0, 0, 1))
			.translate(-Vec3(*self._anchor))
			.translate(-Vec3(*self._pos))
		)

	def set_window(self, window: Window) -> None:
		"""Set the window the camera is following."""
		self.window = window
		self.og_mat = window.view
		self.update()

	def reset(self) -> None:
		"""Reset the camera to default transformation."""
		self._pos = self._initial_pos
		self._scale = self._start_scale
		self._angle = self._start_angle
		self._anchor = self._initial_anchor
		self.update()

	def transform(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
		scale_x: float | None = None,
		scale_y: float | None = None,
		scale_z: float | None = None,
		angle_x: float | None = None,
		angle_y: float | None = None,
		angle_z: float | None = None,
		anchor_x: float | None = None,
		anchor_y: float | None = None,
		anchor_z: float | None = None,
	) -> None:
		"""Transform camera in several ways at once. More efficient as it requires less redundant update calls.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x translation.
				Defaults to None.
			y (float | None, optional):
				y translation.
				Defaults to None.
			z (float | None, optional):
				z translation.
				Defaults to None.
			scale_x (float | None, optional):
				x scale factor.
				Defaults to None.
			scale_y (float | None, optional):
				y scale factor.
				Defaults to None.
			scale_z (float | None, optional):
				z scale factor.
				Defaults to None.
			angle_x (float | None, optional):
				angle on x axis.
				Defaults to None.
			angle_y (float | None, optional):
				angle on y axis.
				Defaults to None.
			angle_z (float | None, optional):
				angle on z axis.
				Defaults to None.
			anchor_x (float | None, optional):
				x anchor position.
				Defaults to None.
			anchor_y (float | None, optional):
				y anchor position.
				Defaults to None.
			anchor_z (float | None, optional):
				z anchor position.
				Defaults to None.
		"""
		self._pos = (
			self._pos[0] + (x or 0),
			self._pos[1] + (y or 0),
			self._pos[2] + (z or 0),
		)
		self._scale = (
			self._scale[0] * (scale_x or 1),
			self._scale[1] * (scale_y or 1),
			self._scale[2] * (scale_z or 1),
		)
		self._angle = (
			self._angle[0] + (angle_x or 0),
			self._angle[1] + (angle_y or 0),
			self._angle[2] + (angle_z or 0),
		)
		self._anchor = (
			self._anchor[0] + (anchor_x or 0),
			self._anchor[1] + (anchor_y or 0),
			self._anchor[2] + (anchor_z or 0),
		)
		self.update()

	def transform_to(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
		scale_x: float | None = None,
		scale_y: float | None = None,
		scale_z: float | None = None,
		angle_x: float | None = None,
		angle_y: float | None = None,
		angle_z: float | None = None,
		anchor_x: float | None = None,
		anchor_y: float | None = None,
		anchor_z: float | None = None,
	) -> None:
		"""Set transformation of camera in several ways at once. More efficient as it requires less redundant update calls.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x translation.
				Defaults to None.
			y (float | None, optional):
				y translation.
				Defaults to None.
			z (float | None, optional):
				z translation.
				Defaults to None.
			scale_x (float | None, optional):
				x scale factor.
				Defaults to None.
			scale_y (float | None, optional):
				y scale factor.
				Defaults to None.
			scale_z (float | None, optional):
				z scale factor.
				Defaults to None.
			angle_x (float | None, optional):
				angle on x axis.
				Defaults to None.
			angle_y (float | None, optional):
				angle on y axis.
				Defaults to None.
			angle_z (float | None, optional):
				angle on z axis.
				Defaults to None.
			anchor_x (float | None, optional):
				x anchor position.
				Defaults to None.
			anchor_y (float | None, optional):
				y anchor position.
				Defaults to None.
			anchor_z (float | None, optional):
				z anchor position.
				Defaults to None.
		"""
		self._pos = (
			(self._initial_pos[0] + x) if x is not None else self._pos[0],
			(self._initial_pos[1] + y) if y is not None else self._pos[1],
			(self._initial_pos[2] + z) if z is not None else self._pos[2],
		)
		self._scale = (
			(self._start_scale[0] * scale_x) if scale_x is not None else self._scale[0],
			(self._start_scale[1] * scale_y) if scale_y is not None else self._scale[1],
			(self._start_scale[2] * scale_z) if scale_z is not None else self._scale[2],
		)
		self._angle = (
			(self._start_angle[0] + angle_x) if angle_x is not None else self._angle[0],
			(self._start_angle[1] + angle_y) if angle_y is not None else self._angle[1],
			(self._start_angle[2] + angle_z) if angle_z is not None else self._angle[2],
		)
		self._anchor = (
			(self._initial_anchor[0] + anchor_x)
			if anchor_x is not None
			else self._anchor[0],
			(self._initial_anchor[1] + anchor_y)
			if anchor_y is not None
			else self._anchor[1],
			(self._initial_anchor[2] + anchor_z)
			if anchor_z is not None
			else self._anchor[2],
		)
		self.update()

	def move(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Translate the camera by an amount.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x translation.
				Defaults to None.
			y (float | None, optional):
				y translation.
				Defaults to None.
			z (float | None, optional):
				z translation.
				Defaults to None.
		"""
		self._pos = (
			self._pos[0] + (x or 0),
			self._pos[1] + (y or 0),
			self._pos[2] + (z or 0),
		)
		self.update()

	def move_to(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Set camera translation.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x translation.
				Defaults to None.
			y (float | None, optional):
				y translation.
				Defaults to None.
			z (float | None, optional):
				z translation.
				Defaults to None.
		"""
		self._pos = (
			(self._initial_pos[0] + x) if x is not None else self._pos[0],
			(self._initial_pos[1] + y) if y is not None else self._pos[1],
			(self._initial_pos[2] + z) if z is not None else self._pos[2],
		)
		self.update()

	def move_anchor(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Translate anchor position of camera by an amount.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x anchor position.
				Defaults to None.
			y (float | None, optional):
				y anchor position.
				Defaults to None.
			z (float | None, optional):
				z anchor position.
				Defaults to None.
		"""
		self._anchor = (
			self._anchor[0] + (x or 0),
			self._anchor[1] + (y or 0),
			self._anchor[2] + (z or 0),
		)
		self.update()

	def move_anchor_to(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Set anchor point of camera.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x anchor position.
				Defaults to None.
			y (float | None, optional):
				y anchor position.
				Defaults to None.
			z (float | None, optional):
				z anchor position.
				Defaults to None.
		"""
		self._anchor = (
			(self._initial_anchor[0] + x) if x is not None else self._anchor[0],
			(self._initial_anchor[1] + y) if y is not None else self._anchor[1],
			(self._initial_anchor[2] + z) if z is not None else self._anchor[2],
		)
		self.update()

	def zoom(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Zoom camera by a factor.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x scale factor.
				Defaults to None.
			y (float | None, optional):
				y scale factor.
				Defaults to None.
			z (float | None, optional):
				z scale factor.
				Defaults to None.
		"""
		self._scale = (
			self._scale[0] * (x or 1),
			self._scale[1] * (y or 1),
			self._scale[2] * (z or 1),
		)
		self.update()

	def zoom_to(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Set zoom of camera.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				x scale factor.
				Defaults to None.
			y (float | None, optional):
				y scale factor.
				Defaults to None.
			z (float | None, optional):
				z scale factor.
				Defaults to None.
		"""
		self._scale = (
			(self._start_scale[0] * x) if x is not None else self._scale[0],
			(self._start_scale[1] * y) if y is not None else self._scale[1],
			(self._start_scale[2] * z) if z is not None else self._scale[2],
		)
		self.update()

	def rotate(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Rotate camera around anchor point by an amount.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				angle on x axis.
				Defaults to None.
			y (float | None, optional):
				angle on y axis.
				Defaults to None.
			z (float | None, optional):
				angle on z axis.
				Defaults to None.
		"""
		self._angle = (
			self._angle[0] + (x or 0),
			self._angle[1] + (y or 0),
			self._angle[2] + (z or 0),
		)
		self.update()

	def rotate_to(
		self,
		x: float | None = None,
		y: float | None = None,
		z: float | None = None,
	) -> None:
		"""Set rotation of camera around anchor point.

		NOTE: Not passing in an arg will cause no change.

		Args:
			x (float | None, optional):
				angle on x axis.
				Defaults to None.
			y (float | None, optional):
				angle on y axis.
				Defaults to None.
			z (float | None, optional):
				angle on z axis.
				Defaults to None.
		"""
		self._angle = (
			(self._start_angle[0] + x) if x is not None else self._angle[0],
			(self._start_angle[1] + y) if y is not None else self._angle[1],
			(self._start_angle[2] + z) if z is not None else self._angle[2],
		)
		self.update()
