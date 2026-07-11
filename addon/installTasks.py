# Installation tasks for Global Sonic Pitch.

from __future__ import annotations

import addonHandler

addonHandler.initTranslation()

SUPPORT_URL = "https://buycoffee.to/kazimierz-parzych"


def _isMinimalMode() -> bool:
	try:
		import globalVars

		return bool(getattr(globalVars.appArgs, "minimal", False))
	except Exception:
		return False


def onInstall() -> None:
	if _isMinimalMode():
		return
	import gui
	import webbrowser
	import wx
	from logHandler import log

	parent = getattr(gui, "mainFrame", None)
	style = wx.YES_NO | getattr(wx, "NO_DEFAULT", 0) | wx.ICON_INFORMATION
	result = gui.messageBox(
		_(
			"If you like Sonic Pitch and want to support my work, "
			"you can buy me a coffee.\n\n"
			"Do you want to open the support page now?",
		),
		_("Support Sonic Pitch"),
		style,
		parent,
	)
	if result != wx.YES:
		return
	try:
		opened = webbrowser.open_new_tab(SUPPORT_URL)
	except Exception:
		opened = False
		log.debugWarning("globalSonicPitch: failed to open support page during install", exc_info=True)
	if not opened:
		gui.messageBox(
			_("Cannot open support page. Open this address manually: {url}").format(url=SUPPORT_URL),
			_("Support Sonic Pitch"),
			wx.OK | wx.ICON_WARNING,
			parent,
		)
