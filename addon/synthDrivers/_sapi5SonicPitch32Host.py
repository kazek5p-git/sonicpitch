# Private 32-bit host-side driver for SAPI5 32-bit Sonic Pitch.

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


class _UnavailableSynthDriver(NVDASynthDriver):
	name = DRIVER_NAME
	description = DESCRIPTION
	supportedSettings = ()
	supportedCommands = set()
	supportedNotifications = set()
	_unavailableReason = "unknown reason"

	@classmethod
	def check(cls):
		logBaseUnavailable(cls.name, cls._unavailableReason)
		return False

	def __init__(self, *args, **kwargs):
		raise RuntimeError(f"{self.name} is unavailable in the 32-bit host: {self._unavailableReason}")

	def speak(self, speechSequence):
		pass

	def cancel(self):
		pass

	def pause(self, switch: bool):
		pass


def _buildUnavailable(reason: str):
	log.error(f"{DRIVER_NAME}: unavailable in 32-bit host: {reason}")

	class SynthDriver(_UnavailableSynthDriver):
		_unavailableReason = reason

	return SynthDriver


def _registerBuiltIn32SynthDriversPath() -> str | None:
	try:
		import globalVars
		import synthDrivers
	except Exception as exc:
		return f"failed to import globalVars/synthDrivers in 32-bit host: {type(exc).__name__}: {exc}"

	builtInPath = os.path.join(globalVars.appDir, "_synthDrivers32")
	if not os.path.isdir(builtInPath):
		return f"built-in 32-bit synthDrivers path is missing: {builtInPath}"
	if builtInPath not in synthDrivers.__path__:
		synthDrivers.__path__.append(builtInPath)
		log.info(f"{DRIVER_NAME}: registered built-in 32-bit synthDrivers path: {builtInPath}")
	return None


if getPythonBitness() != 32:
	SynthDriver = _buildUnavailable("host-side driver was imported outside 32-bit NVDA/Python")
else:
	_pathProblem = _registerBuiltIn32SynthDriversPath()
	if _pathProblem:
		SynthDriver = _buildUnavailable(_pathProblem)
	else:
		try:
			_baseModule = importlib.import_module(BASE_MODULE_NAME)
		except Exception as exc:
			SynthDriver = _buildUnavailable(
				f"failed to import 32-bit {BASE_MODULE_NAME}: {type(exc).__name__}: {exc}",
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
					sapi5SonicPitchBaseModuleName = f"{BASE_MODULE_NAME} in 32-bit host"

					@classmethod
					def check(cls):
						if getPythonBitness() != 32:
							logBaseUnavailable(cls.name, "32-bit host driver requires 32-bit NVDA/Python")
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
							log.error(f"{cls.name}: 32-bit host SAPI5 check failed", exc_info=True)
							return False

					def __init__(self, *args, **kwargs):
						if getPythonBitness() != 32:
							raise RuntimeError("32-bit SAPI5 Sonic Pitch host driver requires 32-bit NVDA/Python")
						super().__init__(*args, **kwargs)
						self._applySonicPitch()
