import argparse
import workarounds
import subprocess
import sys
import os

def main():
	cmdlist = {
		'help': (show_usage, False),
		'status': (show_status, True),
		'on': (turn_on, True),
		'off': (turn_off, True)
	}
	wkarglist = list(workarounds.avail.keys())
	wkarglist.append('all')

	parser = argparse.ArgumentParser()
	parser.add_argument("command", choices=cmdlist.keys())
	parser.add_argument("workaround", choices=wkarglist, nargs='?')
	arg = parser.parse_args()

	fn, need_root = cmdlist.get(arg.command)
	if need_root and os.getuid() != 0:
		return rerun_as_root()
	return fn(arg)

def show_status(arg):
	wks = parse_workaround_arg(arg, default_all=True)
	for i, wk in enumerate(wks):
		inst = workarounds.avail[wk]()
		print(TermColor.BOLD, wk, TermColor.ENDC, sep="")
		inst.print_status()
		# if i < len(wks) - 1:
		# 	print()

def turn_on(arg):
	_apply_workaround(arg, True)

def turn_off(arg):
	_apply_workaround(arg, False)

def _apply_workaround(arg, turnon):
	wks = parse_workaround_arg(arg)
	if not wks:
		print("Please select workaround to apply!")
		return
	msg = "Applying" if turnon else "Disabling"
	for i, wk in enumerate(wks):
		inst = workarounds.avail[wk]()
		print(f"{msg} workaround", wk, "...")
		if turnon:
			inst.turn_on()
		else:
			inst.turn_off()

def show_usage(*_):
	print("Usage: aww (command) (workaround)")
	print()
	print("(command) can be one of the following:")
	print(" on   - Activate the specified workarounds.")
	print(" off  - Deactivate the specified workarounds.")
	print(" stat - View the status of the workarounds.")
	print(" help - Print this help.")
	print()
	print("Workarounds can be comma separated, or specify 'all' to apply all workarounds.")
	print()
	print("Available workarounds:")
	for k, v in workarounds.avail.items():
		print("- ", TermColor.BOLD, k, TermColor.ENDC, sep="")
		print(v.desc)
	return 0

def parse_workaround_arg(arg, default_all=False):
	v = arg.workaround
	if (v is None and default_all) or v == 'all':
		return workarounds.avail.keys()
	if v is None:
		return []
	v = v.split(',')
	for i in v:
		if i not in workarounds.avail:
			print(f"Unsupported workaround '{i}'", file=sys.stderr)
			return 1
	return v

def rerun_as_root():
	args = ['sudo', sys.executable]
	args.extend(sys.argv)
	return subprocess.run(args).returncode

class TermColor:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

if __name__ == "__main__":
	exit(main())
