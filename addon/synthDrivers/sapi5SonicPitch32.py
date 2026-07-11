# SAPI5 32-bit Sonic Pitch synth driver.

from __future__ import annotations

import importlib
import os

try:
	import addonHandler

	addonHandler.initTranslation()
except Exception:
	pass

try:
	_
except NameError:
	_ = lambda message: message

from logHandler import log
from synthDriverHandler import SynthDriver as NVDASynthDriver

from ._sapi5SonicPitchCommon import (
	Sapi5SonicPitchMixin,
	getBaseCompatibilityProblem,
	getPythonBitness,
	getSonicCompatibilityProblem,
	logBaseUnavailable,
)


DRIVER_NAME = "sapi5SonicPitch32"
DESCRIPTION = _("SAPI5 32-bit Sonic Pitch")
BASE_MODULE_NAME = "synthDrivers.sapi5"
EXPECTED_DESCRIPTION_BITNESS = None
HOST32_MODULE_NAME = "_sapi5SonicPitch32Host"


class _UnavailableSynthDriver(NVDASynthDriver):
	name = DRIVER_NAME
	description = DESCRIPTION
	supportedSettings = ()
	supportedCommands = set()
	supportedNotifications = set()

	@classmethod
	def check(cls):
		logBaseUnavailable(cls.name, getattr(cls, "_unavailableReason", "unknown reason"))
		return False

	def __init__(self, *args, **kwargs):
		raise RuntimeError(f"{self.name} is unavailable: {self._unavailableReason}")

	def speak(self, speechSequence):
		pass

	def cancel(self):
		pass

	def pause(self, switch: bool):
		pass


def _buildUnavailable(reason: str):
	class SynthDriver(_UnavailableSynthDriver):
		_unavailableReason = reason

	return SynthDriver


if getPythonBitness() == 64:
	try:
		from _bridge.clients.synthDriverHost32.synthDriver import SynthDriverProxy32
	except Exception as exc:
		SynthDriver = _buildUnavailable(
			f"failed to import SynthDriverProxy32: {type(exc).__name__}: {exc}",
		)
	else:

		class SynthDriver(SynthDriverProxy32):
			name = DRIVER_NAME
			description = DESCRIPTION
			synthDriver32Path = os.path.dirname(__file__)
			synthDriver32Name = HOST32_MODULE_NAME

			@classmethod
			def check(cls):
				hostModulePath = os.path.join(cls.synthDriver32Path, f"{cls.synthDriver32Name}.py")
				if not os.path.isfile(hostModulePath):
					logBaseUnavailable(cls.name, f"32-bit host module missing: {hostModulePath}")
					return False
				try:
					import globalVars

					builtIn32Path = os.path.join(globalVars.appDir, "_synthDrivers32", "sapi5.py")
					builtIn32SonicPath = os.path.join(globalVars.appDir, "_synthDrivers32", "_sonic.py")
				except Exception as exc:
					logBaseUnavailable(cls.name, f"failed to locate NVDA appDir: {type(exc).__name__}: {exc}")
					return False
				if not os.path.isfile(builtIn32Path):
					logBaseUnavailable(cls.name, f"32-bit base SAPI5 module missing: {builtIn32Path}")
					return False
				if not os.path.isfile(builtIn32SonicPath):
					logBaseUnavailable(cls.name, f"32-bit Sonic wrapper missing: {builtIn32SonicPath}")
					return False
				try:
					return bool(super().check())
				except Exception:
					log.error(f"{cls.name}: 32-bit synth driver host check failed", exc_info=True)
					return False

else:
	try:
		_baseModule = importlib.import_module(BASE_MODULE_NAME)
	except Exception as exc:
		SynthDriver = _buildUnavailable(
			f"failed to import local 32-bit {BASE_MODULE_NAME}: {type(exc).__name__}: {exc}",
		)
	else:
		_problem = getBaseCompatibilityProblem(_baseModule, EXPECTED_DESCRIPTION_BITNESS)
		if _problem:
			SynthDriver = _buildUnavailable(_problem)
		else:

			class SynthDriver(Sapi5SonicPitchMixin, _baseModule.SynthDriver):
				name = DRIVER_NAME
				description = DESCRIPTION
				sapi5SonicPitchBitness = "32-bit"
				sapi5SonicPitchBaseModuleName = BASE_MODULE_NAME

				@classmethod
				def check(cls):
					if getPythonBitness() != 32:
						logBaseUnavailable(cls.name, "local path requires 32-bit NVDA/Python")
						return False
					problem = getBaseCompatibilityProblem(_baseModule, EXPECTED_DESCRIPTION_BITNESS)
					if problem:
						logBaseUnavailable(cls.name, problem)
						return False
					sonicProblem = getSonicCompatibilityProblem()
					if sonicProblem:
						logBaseUnavailable(cls.name, sonicProblem)
						return False
					try:
						return bool(super().check())
					except Exception:
						log.error(f"{cls.name}: base 32-bit SAPI5 check failed", exc_info=True)
						return False

				def __init__(self, *args, **kwargs):
					if getPythonBitness() != 32:
						raise RuntimeError("32-bit direct SAPI5 path requires 32-bit NVDA/Python")
					super().__init__(*args, **kwargs)
					self._applySonicPitch()
