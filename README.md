# VTranslator

VTranslator is a Windows desktop assistant that instantly converts on-screen text into readable translations without interrupting gameplay. Point at a game, hold the capture hotkey, and the app uses OCR plus cloud/local translators to show subtitles directly on your screen.

## Why people use VTranslator

- **Live captures with overlays**: Draw a region to capture text and see translated subtitles rendered over that window, so you can follow foreign dialogs while playing.
- **Custom hotkeys**: Control capture, toggle overlays, switch languages, or trigger TTS without touching the mouse—configure shortcuts in the Settings panel.
- **Flexible translation engines**: Combine offline dictionaries with online APIs for accuracy across genres like visual novels, JRPGs, or learning tools.
- **Multilingual packs**: `files/lang/` stores ready-to-use localization files, and additional dictionaries can be loaded as needed.
- **Optional audio output**: Pair translated text with Edge or Windows TTS to hear lines read aloud.

## Getting started

1. Run `venv.bat` one time to prepare the bundled Python environment.
2. Launch the app with `run.bat`; the overlay controller and status window appear.
3. Adjust hotkeys, OCR settings, and translation providers from the Settings UI, then capture text in any application using the assigned shortcut.

```powershell
venv.bat  # prepares the virtual environment
run.bat   # starts the VTranslator UI and overlay helper
```

## Tips

- Hover your capture cursor over the text area before triggering the hotkey to keep the overlay aligned.
- Save translation history from the Records view so you can review past captures.
- Tweak `userconfig/config.json` if you need more aggressive OCR, alternate dictionaries, or custom post-processing.

## Need help?

- Logs are written to the console window that opens alongside the UI—inspect them for OCR or translator errors.
- If overlays look off, confirm Windows scaling is set to 100% or adjust the capture region manually.
- For new OCR models, drop ONNX weights into `ocrengines/` and restart the app.

VTranslator stays quietly behind the scenes so you can translate on the fly. Let me know if you want assistance tuning a workflow or adding a new language pack.
