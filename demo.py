"""pgm demo."""

from __future__ import annotations

import functools
import os
import sys

from pyglet_gamemaker.collision.rect import Rect
from pyglet_gamemaker.gui.button import Button

sys.path.append(os.getcwd())

import pyglet
from pyglet.shapes import Circle

from pyglet_gamemaker import DefaultResources, Scene, Window, colors
from pyglet_gamemaker.gui import Text, TextButton


class TextScene(Scene):
	"""Scene with text boxes and stuff."""

	WIDGET_POS = {
		'HUD': ('0.005', '1'),
		'Welcome': ('0.5', '0.5'),
		'Next': (1270, 10),
		'Prev': (10, 10),
	}

	def initialize(self) -> None:  # noqa: D102

		# Create background color
		self.bg = Rect(
			'BG', 0, 0, self.window.width, self.window.height, colors.WHITE, scene=self
		)

		# Create hud text (in top left)
		self.hud = Text(
			'HUD',
			'This is HUD!',
			color=colors.BLACK,
			scene=self,
			group=self.HUD_group,
			anchor=('left', 'top'),
			font_info=(None, 20),
		)

		# Create spinning welcome text
		self.welcome = Text(
			'Welcome',
			"Welcome to pyglet_gamemaker's demo!",
			color=colors.BLACK,
			scene=self,
			anchor=('center', 'center'),
			font_info=(None, 30),
		)
		# Visual for center of rotation of text
		self.welcome_anchor = Circle(
			*self.welcome.pos,
			10,
			color=colors.RED,
			batch=self.batch,
			group=self.main_group,
		)
		self.rotation_speed = 60  # deg/s

		# Create navigation buttons
		self.next_button = NAV_BUTTON(
			ID='Next', text='>', scene=self, button_anchor=('right', 'bottom')
		)
		self.prev_button = NAV_BUTTON(
			ID='Prev', text='<', scene=self, button_anchor=('left', 'bottom')
		)
		# Account for the fact that it's a single half-height character rotating, not full text
		self.next_button.text.anchor = '.5', '.4'
		self.prev_button.text.anchor = '.5', '.4'

	def update(self, dt: float) -> None:
		"""Update scene."""
		# Rotate welcome text
		self.welcome.rotation += self.rotation_speed * dt
		self.welcome_anchor.position = self.welcome.pos

	def on_full_click(self, button: Button) -> None:
		"""Run when button pressed + released."""
		if button.ID == 'Next':
			print('next')
		elif button.ID == 'Prev':
			print('prev')

	def enable(self) -> None:  # noqa: D102
		self.hud.enable()
		self.welcome.enable()
		pyglet.clock.schedule_interval(self.update, 1 / 60)

	def disable(self) -> None:  # noqa: D102
		self.hud.disable()
		self.welcome.disable()
		pyglet.clock.unschedule(self.update)


window = Window()

# Create most of a navigation button
# 	Only missing ID, text, scene, and anchor
NAV_BUTTON = functools.partial(
	TextButton,
	image_sheet=DefaultResources.circle_button,
	image_start=0,
	color=colors.WHITE,
	font_info=(None, None, 'bold'),
	hover_enlarge=30,
)

window.add_scene(TextScene('TextScene'))
window.run()
