import os
import signal
import subprocess
import re
from enum import Enum
from nativeapi.nativeapi import get_procs

class MachProcStatus(Enum):
	SIDL = 1
	SRUN = 2
	SSLEEP = 3
	SSTOP = 4
	SZOMB = 5

class ProcessPauseWorkaround:
	def __init__(self):
		self._pfc = _ProcFinderCached.singleton()

	def pause_resume_proc(self, pause):
		for procname in self.procnames:
			tpl = self._pfc.find_proc(procname)
			if tpl is None:
				print(f"{procname} is not running")
				return False
			pid, _, _ = tpl
			sig = signal.SIGSTOP if pause else signal.SIGCONT
			try:
				os.kill(pid, sig)
			except Exception as ex:
				print(f"Error signaling PID {pid}: {ex}")
				return False
		return True

	def print_status(self):
		for procname in self.procnames:
			tpl = self._pfc.find_proc(procname)
			pid = "unknown"
			if tpl is None:
				status = "UNKNOWN"
			elif tpl:
				pid, _, status = tpl
				status = MachProcStatus(status)
				if status == MachProcStatus.SSTOP:
					status = "STOPPED"
				elif status == MachProcStatus.SRUN:
					status = "RUNNING"
				else:
					status = status.name
			print(f"{procname} (PID {pid}) is {status}")

	def turn_on(self):
		self.pause_resume_proc(True)

	def turn_off(self):
		self.pause_resume_proc(False)

class AirportWorkaround(ProcessPauseWorkaround):
	desc = "Suspend 'airportd' to disable Wi-Fi roaming. This workaround have to be turned off " \
		"to make a connection to a new Wi-Fi network, or to reconnect a disconnected network."

	def __init__(self):
		super().__init__()
		self.procnames = ["airportd"]

class AwdlWorkaround(ProcessPauseWorkaround):
	desc = "Suspend AirPlay and disables AWDL. This workaround have to be turned off to activate " \
		"a newly connected bluetooth audio sink."

	def __init__(self):
		super().__init__()
		self.procnames = ["AirPlayXPCHelper", "AirPlayUIAgent"]

	def turn_on(self):
		super().turn_on()
		if subprocess.run(["ifconfig", "awdl0", "down"]).returncode != 0:
			print("Failed to turn off AWDL interface")

class _ProcFinderCached:
	inst = None

	def __init__(self):
		self._data = get_procs()

	def find_proc(self, procname):
		for tpl in self._data:
			if tpl[1] is None:
				continue
			_, fn = os.path.split(tpl[1])
			if fn == procname:
				return tpl
		return None

	@classmethod
	def singleton(cls):
		if cls.inst is None:
			cls.inst = _ProcFinderCached()
		return cls.inst

avail = {
	"airportd": AirportWorkaround,
	"awdl": AwdlWorkaround
}
