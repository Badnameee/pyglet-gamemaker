from __future__ import annotations

import os
from pathlib import Path


def clear_terminal() -> None:
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')


skip = {'__init__', 'run_tests'}

clear_terminal()
for test_num, test in enumerate(Path('test').iterdir(), 1):
	test = test.stem
	if test in skip:
		continue

	print(f'\n-----------------------------\nStarting test #{test_num}: "{test}"\n\n')
	exec(f'import {test}')  # Run actual test # noqa: S102
