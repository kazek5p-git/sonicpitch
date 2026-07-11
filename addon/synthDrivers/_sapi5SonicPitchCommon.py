# A prototype NVDA add-on for SAPI5 Sonic pitch post-processing.
# This file is intentionally pure Python and uses NVDA's existing Sonic stream.

from __future__ import annotations

import math
import struct
import importlib
import threading
from typing import Any

from logHandler import log


MAX_SEMITONES = 6.0
MIN_SONIC_PITCH_RATIO = 0.70
MAX_SONIC_PITCH_RATIO = 1.45

NEUTRAL_PITCH_PERCENT = 50


def getPythonBitness() -> int:
	return struct.calcsize("P") * 8


def clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def pitchPercentToSemitones(pitchPercent: int | float) -> float:
	pitchPercent = clamp(float(pitchPercent), 0.0, 100.0)
	return ((pitchPercent - 50.0) / 50.0) * MAX_SEMITONES


def pitchPercentToSonicRatio(pitchPercent: int | float) -> float:
	"""Convert NVDA's 0..100 pitch setting to a safe Sonic pitch ratio."""
	semitones = pitchPercentToSemitones(pitchPercent)
	ratio = math.pow(2.0, semitones / 12.0)
	return clamp(ratio, MIN_SONIC_PITCH_RATIO, MAX_SONIC_PITCH_RATIO)


def _formatException(exc: BaseException) -> str:
	return f"{type(exc).__name__}: {exc}"


def hasUsableSonicPitchSetter(sonicStream: Any) -> bool:
	pitchDescriptor = getattr(type(sonicStream), "pitch", None)
	return isinstance(pitchDescriptor, property) and pitchDescriptor.fset is not None


class SynchronizedSonicStream:
	"""Serialize access to NVDA's SonicStream.

	The SAPI5 audio callback writes to Sonic from a worker thread, while synth
	settings are changed from the main thread. Sonic's C stream is not safe to
	mutate concurrently, so property setters and stream operations share one lock.
	"""

	def __init__(self, sonicStream: Any):
		self._sonicStream = sonicStream
		self._lock = threading.RLock()

	def __getattr__(self, attrName: str) -> Any:
		return getattr(self._sonicStream, attrName)

	def writeFloat(self, data, numSamples: int) -> None:
		with self._lock:
			return self._sonicStream.writeFloat(data, numSamples)

	def writeShort(self, data, numSamples: int) -> None:
		with self._lock:
			return self._sonicStream.writeShort(data, numSamples)

	def writeUnsignedChar(self, data, numSamples: int) -> None:
		with self._lock:
			return self._sonicStream.writeUnsignedChar(data, numSamples)

	def readFloat(self):
		with self._lock:
			return self._sonicStream.readFloat()

	def readShort(self):
		with self._lock:
			return self._sonicStream.readShort()

	def readUnsignedChar(self):
		with self._lock:
			return self._sonicStream.readUnsignedChar()

	def flush(self) -> None:
		with self._lock:
			return self._sonicStream.flush()

	@property
	def samplesAvailable(self) -> int:
		with self._lock:
			return self._sonicStream.samplesAvailable

	@property
	def speed(self) -> float:
		with self._lock:
			return self._sonicStream.speed

	@speed.setter
	def speed(self, value: float):
		with self._lock:
			self._sonicStream.speed = value

	@property
	def pitch(self) -> float:
		with self._lock:
			return self._sonicStream.pitch

	@pitch.setter
	def pitch(self, value: float):
		with self._lock:
			self._sonicStream.pitch = value

	@property
	def rate(self) -> float:
		with self._lock:
			return self._sonicStream.rate

	@rate.setter
	def rate(self, value: float):
		with self._lock:
			self._sonicStream.rate = value

	@property
	def volume(self) -> float:
		with self._lock:
			return self._sonicStream.volume

	@volume.setter
	def volume(self, value: float):
		with self._lock:
			self._sonicStream.volume = value

	@property
	def quality(self) -> int:
		with self._lock:
			return self._sonicStream.quality

	@quality.setter
	def quality(self, value: int):
		with self._lock:
			self._sonicStream.quality = value

	@property
	def sampleRate(self) -> int:
		with self._lock:
			return self._sonicStream.sampleRate

	@sampleRate.setter
	def sampleRate(self, value: int):
		with self._lock:
			self._sonicStream.sampleRate = value

	@property
	def channels(self) -> int:
		with self._lock:
			return self._sonicStream.channels

	@channels.setter
	def channels(self, value: int):
		with self._lock:
			self._sonicStream.channels = value


def getBaseCompatibilityProblem(baseModule: Any, expectedBitnessText: str | None) -> str | None:
	baseClass = getattr(baseModule, "SynthDriver", None)
	if baseClass is None:
		return "base module has no SynthDriver class"
	if not hasattr(baseClass, "_set_pitch"):
		return "base SynthDriver has no _set_pitch"
	if not hasattr(baseClass, "_percentToPitch"):
		return "base SynthDriver has no _percentToPitch"
	if not hasattr(baseClass, "_initWasapiAudio"):
		return "base SynthDriver has no _initWasapiAudio"

	if expectedBitnessText:
		description = str(getattr(baseClass, "description", "")).lower()
		expected = expectedBitnessText.lower()
		if expected not in description:
			return f"base SynthDriver description does not contain {expectedBitnessText!r}: {description!r}"
	return None


def getSonicCompatibilityProblem(sonicModuleName: str = "synthDrivers._sonic") -> str | None:
	try:
		sonicModule = importlib.import_module(sonicModuleName)
	except Exception as exc:
		return f"failed to import {sonicModuleName}: {_formatException(exc)}"
	sonicStreamClass = getattr(sonicModule, "SonicStream", None)
	if sonicStreamClass is None:
		return f"{sonicModuleName} has no SonicStream class"
	pitchDescriptor = getattr(sonicStreamClass, "pitch", None)
	if not isinstance(pitchDescriptor, property) or pitchDescriptor.fset is None:
		return f"{sonicModuleName}.SonicStream has no writable pitch property"
	return None


class Sapi5SonicPitchMixin:
	"""Mixin that routes global SAPI5 pitch through Sonic instead of SAPI XML pitch."""

	sapi5SonicPitchBitness = "unknown"
	sapi5SonicPitchBaseModuleName = "unknown"

	@property
	def pitch(self):
		try:
			return super()._get_pitch()
		except AttributeError:
			return self._getCurrentPitchPercent()

	@pitch.setter
	def pitch(self, value):
		self._set_pitch(value)

	def _wrapSonicStreamIfNeeded(self) -> None:
		sonicStream = getattr(self, "sonicStream", None)
		if sonicStream is None or isinstance(sonicStream, SynchronizedSonicStream):
			return
		self.sonicStream = SynchronizedSonicStream(sonicStream)

	def _logSonicPitchUnavailable(self, reason: str) -> None:
		if getattr(self, "_sapi5SonicPitchUnavailableReason", None) == reason:
			return
		self._sapi5SonicPitchUnavailableReason = reason
		log.debug(
			f"{self.name}: Sonic pitch unavailable for {self.sapi5SonicPitchBitness} "
			f"SAPI5 path: {reason}",
		)

	def _getCurrentPitchPercent(self) -> int:
		try:
			return int(getattr(self, "_pitch", NEUTRAL_PITCH_PERCENT))
		except (TypeError, ValueError):
			return NEUTRAL_PITCH_PERCENT

	def _applySonicPitch(self) -> bool:
		self._wrapSonicStreamIfNeeded()
		sonicStream = getattr(self, "sonicStream", None)
		if sonicStream is None:
			self._logSonicPitchUnavailable("self.sonicStream is not available")
			return False
		if not hasUsableSonicPitchSetter(sonicStream):
			self._logSonicPitchUnavailable("SonicStream.pitch setter is not available")
			return False

		pitchPercent = clamp(float(self._getCurrentPitchPercent()), 0.0, 100.0)
		semitones = pitchPercentToSemitones(pitchPercent)
		ratio = pitchPercentToSonicRatio(pitchPercent)
		try:
			sonicStream.pitch = ratio
		except Exception as exc:
			self._logSonicPitchUnavailable(f"failed to set SonicStream.pitch: {_formatException(exc)}")
			log.debugWarning(f"{self.name}: failed to apply Sonic pitch", exc_info=True)
			return False

		log.info(
			f"{self.name}: applied Sonic pitch for {self.sapi5SonicPitchBitness} SAPI5 "
			f"path; pitchPercent={pitchPercent:.1f}; semitones={semitones:.3f}; "
			f"ratio={ratio:.4f}; base={self.sapi5SonicPitchBaseModuleName}",
		)
		self._sapi5SonicPitchUnavailableReason = None
		return True

	def _set_pitch(self, value):
		oldPitch = self._getCurrentPitchPercent()
		try:
			super()._set_pitch(value)
		except AttributeError:
			self._pitch = value
		newPitch = self._getCurrentPitchPercent()
		if oldPitch == newPitch:
			return
		log.info(f"{self.name}: pitch setting changed {oldPitch}->{newPitch}")
		if getattr(self, "sonicStream", None) is None:
			self._applySonicPitch()
			return
		if not getattr(self, "useWasapi", False):
			self._applySonicPitch()
			return
		if getattr(self, "tts", None) is None:
			self._applySonicPitch()
			return
		try:
			currentVoice = self.voice
			log.info(
				f"{self.name}: recreating WASAPI/Sonic stream for pitch change "
				f"{oldPitch}->{newPitch}",
			)
			try:
				self.cancel()
			except Exception:
				log.debugWarning(f"{self.name}: failed to cancel before Sonic pitch reload", exc_info=True)
			self.voice = currentVoice
		except Exception:
			log.error(f"{self.name}: failed to recreate SAPI5 audio path for Sonic pitch", exc_info=True)
			self._applySonicPitch()

	def _percentToPitch(self, percent):
		# Sonic is the MVP pitch mechanism. Keep SAPI XML pitch neutral to avoid double pitch.
		return 0

	def _initWasapiAudio(self):
		result = super()._initWasapiAudio()
		self._applySonicPitch()
		return result

	def loadSettings(self, *args, **kwargs):
		result = super().loadSettings(*args, **kwargs)
		self._applySonicPitch()
		return result



def logBaseUnavailable(driverName: str, reason: str) -> None:
	log.debug(f"{driverName}: unavailable: {reason}")
