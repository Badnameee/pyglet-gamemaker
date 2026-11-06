"""pgm demo."""

from __future__ import annotations

import functools
import os
import sys

from pyglet_gamemaker.collision.rect import Rect
from pyglet_gamemaker.gui import Button, Entry

sys.path.append(os.getcwd())

import pyglet
from pyglet.shapes import Circle

from pyglet_gamemaker import DefaultResources, Scene, Window, colors
from pyglet_gamemaker.gui import Text, TextButton


class TextScene(Scene):
	"""Scene with text boxes and stuff."""

	WIDGET_POS = {
		'HUD': ('.005', '1'),
		'Welcome': ('.5', '.5'),
		'Next': (1270, 10),
		'Prev': (10, 10),
		'Name: ': ('.4', '.1'),
		'Name': ('.4', '.1'),
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
			"Welcome to pgm's demo!",
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

		# Create name entering gui
		self.name_label = Text(
			'Name: ',
			'Name: ',
			color=colors.RED,
			scene=self,
			anchor=('right', 'center'),
			font_info=(None, 30, None),
		)
		self.name_label.y+=2
		self.name_entry = Entry(
			'Name',
			'',
			scene=self,
			anchor=('left', 'center'),
			color=colors.ORANGE,
			font_info=(None, 30, None),
		)

		# Create circle background
		self.circles = [
			Circle(self.window.width/2, self.window.height/2, 25 * n**2, color=(colors.RED if n % 2 == 0 else colors.BLACK), batch=self.batch, group=self.bg_group)
			for n in range(0, 10)
		]

		# Create navigation buttons
		self.next_button = NAV_BUTTON(
			ID='Next', text='>', scene=self, button_anchor=('right', 'bottom')
		)
		self.prev_button = NAV_BUTTON(
			ID='Prev', text='<', scene=self, button_anchor=('left', 'bottom')
		)
		# Account for the fact that it's a single half-height character rotating, not full text
		self.next_button.text.anchor = self.prev_button.text.anchor = '.5', '.4'

	def update(self, dt: float) -> None:
		"""Update scene."""
		# Rotate welcome text
		self.welcome.rotation += self.rotation_speed * dt
		self.welcome_anchor.position = self.welcome.pos

	def on_submit(self, entry: Entry, text: str) -> None:
		"""Run when entry submitted (pressed Enter)."""
		print(f'Hello {text}!')

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
	font_info=(None, 20, 'bold'),
	hover_enlarge=30,
)

window.add_scene(TextScene('TextScene'))
window.run()
