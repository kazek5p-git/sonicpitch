# Global Sonic pitch processing for NVDA WavePlayer speech audio.

from __future__ import annotations

import ctypes
from typing import Any

import addonHandler
import config
import globalPluginHandler
import gui
import nvwave
import wx
from gui import guiHelper
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from logHandler import log
from scriptHandler import script

try:
	import synthDriverHandler
	import ui
except Exception:
	synthDriverHandler = None
	ui = None

try:
	addonHandler.initTranslation()
except Exception:
	pass

try:
	_
except NameError:
	_ = lambda message: message


CONFIG_SECTION = "sapi5SonicPitchGlobal"
CONFIG_SPEC = {
	"enabled": "boolean(default=False)",
	"pitch": "integer(default=50, min=0, max=100)",
	"processOwnSapi5SonicSynths": "boolean(default=False)",
	"debugLogging": "boolean(default=False)",
}

NEUTRAL_PITCH = 50
MAX_SEMITONES = 6.0
MIN_SONIC_PITCH_RATIO = 0.70
MAX_SONIC_PITCH_RATIO = 1.45

_ORIGINAL_FEED_ATTR = "_sapi5SonicPitchGlobalOriginalFeed"
_PATCHED_ATTR = "_sapi5SonicPitchGlobalFeedPatched"
_sonicModule = None
_processingLogKeys: set[tuple[Any, ...]] = set()
_sonicUnavailableReason: str | None = None


def _ensureConfigSpec() -> None:
	config.conf.spec[CONFIG_SECTION] = CONFIG_SPEC


def _getConfigValue(key: str, default: Any) -> Any:
	try:
		_ensureConfigSpec()
		return config.conf[CONFIG_SECTION].get(key, default)
	except Exception:
		return default


def _setConfigValue(key: str, value: Any) -> None:
	_ensureConfigSpec()
	config.conf[CONFIG_SECTION][key] = value


def _clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def _pitchPercentToSonicRatio(pitchPercent: int | float) -> float:
	pitchPercent = _clamp(float(pitchPercent), 0.0, 100.0)
	semitones = ((pitchPercent - 50.0) / 50.0) * MAX_SEMITONES
	ratio = 2.0 ** (semitones / 12.0)
	return _clamp(ratio, MIN_SONIC_PITCH_RATIO, MAX_SONIC_PITCH_RATIO)


def _isDebugLoggingEnabled() -> bool:
	return bool(_getConfigValue("debugLogging", False))


def _getCurrentSynthName() -> str:
	if synthDriverHandler is None:
		return ""
	try:
		synth = synthDriverHandler.getSynth()
	except Exception:
		return ""
	return str(getattr(synth, "name", "") or "")


def _isSpeechPlayer(player: nvwave.WavePlayer) -> bool:
	try:
		return getattr(player, "_purpose", None) == nvwave.AudioPurpose.SPEECH
	except Exception:
		return False


def _getWaveFormat(player: nvwave.WavePlayer) -> tuple[int, int, int] | None:
	try:
		waveFormat = player._format
		channels = int(waveFormat.nChannels)
		sampleRate = int(waveFormat.nSamplesPerSec)
		bitsPerSample = int(waveFormat.wBitsPerSample)
	except Exception:
		return None
	if channels <= 0 or sampleRate <= 0:
		return None
	return channels, sampleRate, bitsPerSample


def _shouldProcess(player: nvwave.WavePlayer, rawSize: int) -> bool:
	if rawSize <= 0:
		return False
	if not bool(_getConfigValue("enabled", False)):
		return False
	if int(_getConfigValue("pitch", NEUTRAL_PITCH)) == NEUTRAL_PITCH:
		return False
	if not _isSpeechPlayer(player):
		return False
	synthName = _getCurrentSynthName()
	if synthName.startswith("sapi5SonicPitch") and not bool(
		_getConfigValue("processOwnSapi5SonicSynths", False),
	):
		return False
	return True


def _getRawBytes(data: Any, size: int | None) -> bytes | None:
	try:
		if size is not None:
			size = int(size)
			if size < 0:
				return None
			if isinstance(data, (bytes, bytearray, memoryview)):
				return bytes(data)[:size]
			return ctypes.string_at(data, size)
		if isinstance(data, bytes):
			return data
		if isinstance(data, (bytearray, memoryview)):
			return bytes(data)
		return bytes(data)
	except Exception:
		return None


def _getSonicModule():
	global _sonicModule, _sonicUnavailableReason
	if _sonicModule is not None:
		return _sonicModule
	try:
		from synthDrivers import _sonic

		_sonic.initialize()
		_sonicModule = _sonic
		_sonicUnavailableReason = None
	except Exception as exc:
		_sonicUnavailableReason = f"{type(exc).__name__}: {exc}"
		if _isDebugLoggingEnabled():
			log.debugWarning("sapi5SonicPitchGlobal: Sonic is unavailable", exc_info=True)
		return None
	return _sonicModule


def _ctypesArrayToBytes(value: Any) -> bytes:
	try:
		return ctypes.string_at(ctypes.addressof(value), ctypes.sizeof(value))
	except Exception:
		return bytes(value)


def _processPcm16Block(raw: bytes, channels: int, sampleRate: int, pitchPercent: int) -> bytes | None:
	frameSize = channels * 2
	if len(raw) < frameSize or len(raw) % frameSize:
		return None
	sonic = _getSonicModule()
	if sonic is None:
		return None
	frameCount = len(raw) // frameSize
	sampleCount = frameCount * channels
	inputSamples = (ctypes.c_short * sampleCount).from_buffer_copy(raw)
	stream = sonic.SonicStream(sampleRate, channels)
	stream.pitch = _pitchPercentToSonicRatio(pitchPercent)
	stream.writeShort(inputSamples, frameCount)
	stream.flush()
	processedSamples = stream.readShort()
	if not processedSamples:
		return None
	processed = _ctypesArrayToBytes(processedSamples)
	return processed or None


def _logProcessedOnce(synthName: str, channels: int, sampleRate: int, pitch: int, inSize: int, outSize: int) -> None:
	key = (synthName, channels, sampleRate, pitch)
	if key in _processingLogKeys and not _isDebugLoggingEnabled():
		return
	_processingLogKeys.add(key)
	log.info(
		"sapi5SonicPitchGlobal: processed speech audio; "
		f"synth={synthName or 'unknown'}; pitch={pitch}; "
		f"channels={channels}; sampleRate={sampleRate}; bytes={inSize}->{outSize}",
	)


def _patchedFeed(self, data, size=None, onDone=None):
	originalFeed = getattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR)
	if callable(size) and onDone is None:
		onDone = size
		size = None
	raw = _getRawBytes(data, size)
	try:
		if raw is not None and _shouldProcess(self, len(raw)):
			waveFormat = _getWaveFormat(self)
			if waveFormat is not None:
				channels, sampleRate, bitsPerSample = waveFormat
				if bitsPerSample == 16:
					pitch = int(_getConfigValue("pitch", NEUTRAL_PITCH))
					processed = _processPcm16Block(raw, channels, sampleRate, pitch)
					if processed:
						_logProcessedOnce(
							_getCurrentSynthName(),
							channels,
							sampleRate,
							pitch,
							len(raw),
							len(processed),
						)
						return originalFeed(self, processed, len(processed), onDone)
				elif _isDebugLoggingEnabled():
					log.debug(f"sapi5SonicPitchGlobal: bypassing non-16-bit audio: {bitsPerSample}")
	except Exception:
		log.debugWarning("sapi5SonicPitchGlobal: failed to process WavePlayer feed; bypassing", exc_info=True)
	return originalFeed(self, data, size, onDone)


def installWavePlayerHook() -> None:
	if getattr(nvwave.WavePlayer, _PATCHED_ATTR, False):
		return
	setattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR, nvwave.WavePlayer.feed)
	nvwave.WavePlayer.feed = _patchedFeed
	setattr(nvwave.WavePlayer, _PATCHED_ATTR, True)
	log.info("sapi5SonicPitchGlobal: installed WavePlayer speech feed hook")


def uninstallWavePlayerHook() -> None:
	if not getattr(nvwave.WavePlayer, _PATCHED_ATTR, False):
		return
	originalFeed = getattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR, None)
	if originalFeed is not None and nvwave.WavePlayer.feed is _patchedFeed:
		nvwave.WavePlayer.feed = originalFeed
	try:
		delattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR)
	except Exception:
		pass
	setattr(nvwave.WavePlayer, _PATCHED_ATTR, False)
	log.info("sapi5SonicPitchGlobal: removed WavePlayer speech feed hook")


class Sapi5SonicPitchSettingsPanel(SettingsPanel):
	title = _("SAPI5 Sonic Pitch")

	def makeSettings(self, settingsSizer):
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = config.conf[CONFIG_SECTION]
		self.enableCheckbox = helper.addItem(
			wx.CheckBox(self, label=_("Enable global Sonic pitch processing")),
		)
		self.enableCheckbox.SetValue(bool(conf["enabled"]))
		self.pitchSlider = helper.addLabeledControl(
			_("Global Sonic pitch"),
			wx.Slider,
			minValue=0,
			maxValue=100,
			style=wx.SL_HORIZONTAL | wx.SL_LABELS,
		)
		self.pitchSlider.SetValue(int(conf["pitch"]))
		self.processOwnCheckbox = helper.addItem(
			wx.CheckBox(
				self,
				label=_("Also process SAPI5 Sonic Pitch synthesizers (not recommended)"),
			),
		)
		self.processOwnCheckbox.SetValue(bool(conf["processOwnSapi5SonicSynths"]))
		self.debugCheckbox = helper.addItem(
			wx.CheckBox(self, label=_("Enable debug logging for global Sonic processing")),
		)
		self.debugCheckbox.SetValue(bool(conf["debugLogging"]))
		self.enableCheckbox.Bind(wx.EVT_CHECKBOX, self._updateControlState)
		self._updateControlState()

	def _updateControlState(self, event=None):
		enabled = self.enableCheckbox.IsChecked()
		self.pitchSlider.Enable(enabled)
		self.processOwnCheckbox.Enable(enabled)
		self.debugCheckbox.Enable(enabled)

	def onSave(self):
		_setConfigValue("enabled", self.enableCheckbox.IsChecked())
		_setConfigValue("pitch", self.pitchSlider.GetValue())
		_setConfigValue("processOwnSapi5SonicSynths", self.processOwnCheckbox.IsChecked())
		_setConfigValue("debugLogging", self.debugCheckbox.IsChecked())
		config.conf.save()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("SAPI5 Sonic Pitch")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		_ensureConfigSpec()
		installWavePlayerHook()
		if Sapi5SonicPitchSettingsPanel not in NVDASettingsDialog.categoryClasses:
			NVDASettingsDialog.categoryClasses.append(Sapi5SonicPitchSettingsPanel)

	def terminate(self):
		try:
			if Sapi5SonicPitchSettingsPanel in NVDASettingsDialog.categoryClasses:
				NVDASettingsDialog.categoryClasses.remove(Sapi5SonicPitchSettingsPanel)
		finally:
			uninstallWavePlayerHook()
			super().terminate()

	@script(
		description=_("Toggle global Sonic pitch processing"),
		category=scriptCategory,
	)
	def script_toggleGlobalSonicPitch(self, gesture):
		enabled = not bool(_getConfigValue("enabled", False))
		_setConfigValue("enabled", enabled)
		config.conf.save()
		if ui is not None:
			ui.message(_("Global Sonic pitch on") if enabled else _("Global Sonic pitch off"))

	@script(
		description=_("Report global Sonic pitch processing status"),
		category=scriptCategory,
	)
	def script_reportGlobalSonicPitch(self, gesture):
		enabled = bool(_getConfigValue("enabled", False))
		pitch = int(_getConfigValue("pitch", NEUTRAL_PITCH))
		message = _("Global Sonic pitch on, pitch {pitch}").format(pitch=pitch) if enabled else _(
			"Global Sonic pitch off",
		)
		if _sonicUnavailableReason:
			message = f"{message}. Sonic unavailable: {_sonicUnavailableReason}"
		if ui is not None:
			ui.message(message)
