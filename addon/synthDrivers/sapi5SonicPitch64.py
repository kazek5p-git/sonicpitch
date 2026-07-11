# SAPI5 64-bit Sonic Pitch synth driver.

from __future__ import annotations

import importlib

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


DRIVER_NAME = "sapi5SonicPitch64"
DESCRIPTION = _("SAPI5 64-bit Sonic Pitch")
BASE_MODULE_NAME = "synthDrivers.sapi5"
EXPECTED_DESCRIPTION_BITNESS = None


def _loadBaseModule():
	if getPythonBitness() != 64:
		return None, "64-bit SAPI5 cannot be used from 32-bit NVDA/Python"
	try:
		return importlib.import_module(BASE_MODULE_NAME), None
	except Exception as exc:
		return None, f"failed to import {BASE_MODULE_NAME}: {type(exc).__name__}: {exc}"


_baseModule, _baseUnavailableReason = _loadBaseModule()
if _baseModule is not None:
	_baseUnavailableReason = getBaseCompatibilityProblem(_baseModule, EXPECTED_DESCRIPTION_BITNESS)


class _UnavailableSynthDriver(NVDASynthDriver):
	name = DRIVER_NAME
	description = DESCRIPTION
	supportedSettings = ()
	supportedCommands = set()
	supportedNotifications = set()

	@classmethod
	def check(cls):
		logBaseUnavailable(cls.name, _baseUnavailableReason or "unknown reason")
		return False

	def __init__(self, *args, **kwargs):
		raise RuntimeError(f"{self.name} is unavailable: {_baseUnavailableReason}")

	def speak(self, speechSequence):
		pass

	def cancel(self):
		pass

	def pause(self, switch: bool):
		pass


if _baseUnavailableReason:
	SynthDriver = _UnavailableSynthDriver
else:

	class SynthDriver(Sapi5SonicPitchMixin, _baseModule.SynthDriver):
		name = DRIVER_NAME
		description = DESCRIPTION
		sapi5SonicPitchBitness = "64-bit"
		sapi5SonicPitchBaseModuleName = BASE_MODULE_NAME

		@classmethod
		def check(cls):
			if getPythonBitness() != 64:
				logBaseUnavailable(cls.name, "running under 32-bit NVDA/Python")
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
				log.error(f"{cls.name}: base SAPI5 check failed", exc_info=True)
				return False

		def __init__(self, *args, **kwargs):
			if getPythonBitness() != 64:
				raise RuntimeError("64-bit SAPI5 Sonic Pitch cannot run under 32-bit NVDA/Python")
			super().__init__(*args, **kwargs)
			self._applySonicPitch()
