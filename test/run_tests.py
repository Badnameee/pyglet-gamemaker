from __future__ import annotations

import os


def clear_terminal() -> None:
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')


# Holds all imports for tests
tests = [
	'sprite',
	'gui_button',
	'gui_text',
	'gui_text_button',
	'gui_entry',
	'shapes_hitbox',
	'shapes_rect',
	'shapes_circle',
	'shapes_trigger',
	'window',
	'camera',
]

clear_terminal()
for test_num, test in enumerate(tests, 1):
	print(f'\n-----------------------------\nStarting test #{test_num}: "{test}"\n\n')
	exec(f'import {test}')  # Run actual test
