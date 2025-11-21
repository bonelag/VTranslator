from __future__ import annotations

import argparse
import ctypes
import json
import logging
import re
#import signal
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Sequence

from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

_overlays = []

# Default configuration
CONFIG = {
	"enable": 1,
	"text_color": "white",
	"stroke_color": "black",
	"stroke_width": 3,
	"min_font_size": 5,
	"max_font_size": 48,
	"font_family": "",
	"background_color": "rgba(0, 0, 0, 180)",
	"box_expansion": 6,
	"timeout_ms": 10000,
	"horizontal_padding": 4,
	"vertical_padding": 4
}

def load_config():
	global CONFIG
	try:
		# Try to find the config file relative to the script or current working directory
		config_path = Path("userconfig/overlay.json")
		if not config_path.exists():
			# Fallback to looking relative to this file if run from elsewhere
			config_path = Path(__file__).parent.parent / "userconfig" / "overlay.json"
		
		if config_path.exists():
			with open(config_path, "r", encoding="utf-8") as f:
				user_config = json.load(f)
				CONFIG.update(user_config)
			logging.info(f"Loaded overlay config from {config_path}")
		else:
			logging.warning("Overlay config file not found, using defaults")
	except Exception as e:
		logging.error(f"Error loading overlay config: {e}")

def parse_color(color_str: str) -> QColor:
	color_str = str(color_str).strip().lower()
	if color_str.startswith("rgba"):
		try:
			content = color_str[color_str.find('(')+1 : color_str.rfind(')')]
			parts = [x.strip() for x in content.split(',')]
			if len(parts) == 4:
				r = int(parts[0])
				g = int(parts[1])
				b = int(parts[2])
				a_str = parts[3]
				if '.' in a_str:
					a = int(float(a_str) * 255)
				else:
					a = int(a_str)
				return QColor(r, g, b, a)
		except Exception as e:
			logging.warning(f"Error parsing rgba color '{color_str}': {e}")
	return QColor(color_str)

BOX_PATTERN = re.compile(
	r"\[(?P<x>\d+)\s+(?P<y>\d+)\|(?P<w>\d+)\s+(?P<h>\d+)\]\s*(?P<text>.*?)(?=\[\d+\s+\d+\|\d+\s+\d+\]|$)",
	re.DOTALL,
)

def clean_text(text: str) -> str:
	text = re.sub(r"\[Engine\].*?(\n|$)", "", text)
	return text.strip()


SAMPLE_DATA = """
[1330 588|243 29]  Line 1
[1330 655|388 27]  Line 2
[1330 703|406 27]  Line 3
""".strip()


@dataclass
class TextBox:
	x: int
	y: int
	width: int
	height: int
	text: str


def parse_boxes(text: str) -> List[TextBox]:
	boxes: List[TextBox] = []
	# Remove the header line if present before parsing boxes
	text = re.sub(r"^\[Engine\].*?(\n|$)", "", text.strip())
	
	for match in BOX_PATTERN.finditer(text):
		raw_text = match.group("text")
		cleaned_text = clean_text(raw_text)
		if not cleaned_text:
			continue
			
		boxes.append(
			TextBox(
				x=int(match.group("x")),
				y=int(match.group("y")),
				width=int(match.group("w")),
				height=int(match.group("h")),
				text=cleaned_text,
			)
		)
	return boxes

class StrokedLabel(QLabel):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.stroke_color = parse_color(CONFIG["stroke_color"])
		self.stroke_width = CONFIG["stroke_width"]
		self.text_color = parse_color(CONFIG["text_color"])
		self.bg_color = parse_color(CONFIG["background_color"])

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)

		# Draw background
		rect = self.rect()
		painter.setPen(Qt.NoPen)
		painter.setBrush(self.bg_color)
		painter.drawRoundedRect(rect, 4, 4)

		text = self.text()
		if not text:
			return

		font = self.font()
		if CONFIG["font_family"]:
			font.setFamily(CONFIG["font_family"])
		painter.setFont(font)
		metrics = QFontMetrics(font)
		
		# Manual vertical centering to ensure equal top/bottom padding
		# regardless of the specific characters in the text
		text_height = metrics.ascent() + metrics.descent()
		y = rect.top() + (rect.height() - text_height) / 2 + metrics.ascent()
		
		# Horizontal padding
		x = rect.left() + CONFIG["horizontal_padding"] // 2
		
		path = QPainterPath()
		path.addText(x, y, font, text)
		
		# Draw stroke
		painter.setPen(QPen(self.stroke_color, self.stroke_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
		painter.setBrush(Qt.NoBrush)
		painter.drawPath(path)
		
		# Draw fill
		painter.setPen(Qt.NoPen)
		painter.setBrush(self.text_color)
		painter.drawPath(path)


class Overlay(QWidget):
	def __init__(self, boxes: Sequence[TextBox]):
		super().__init__(None, Qt.Window | Qt.FramelessWindowHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setAttribute(Qt.WA_TransparentForMouseEvents)
		self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
		self.setWindowFlag(Qt.Tool, True)
		# Qt>=5.10 provides WindowTransparentForInput; guard for older builds.
		if hasattr(Qt, "WindowTransparentForInput"):
			self.setWindowFlag(Qt.WindowTransparentForInput, True)

		try:
			# WDA_EXCLUDEFROMCAPTURE = 0x00000011
			ctypes.windll.user32.SetWindowDisplayAffinity(int(self.winId()), 0x00000011)
		except Exception as e:
			logging.warning(f"Failed to set window display affinity: {e}")

		screen = QApplication.primaryScreen()
		rect = screen.geometry()
		dpr = screen.devicePixelRatio()
		logging.debug(f"Screen geometry: {rect}, DPR: {dpr}")
		self.setGeometry(rect)
		self.boxes = boxes
		self.labels: List[QLabel] = []
		box_expansion = CONFIG["box_expansion"]
		for i, box in enumerate(boxes):
			scaled_box = TextBox(
				x=int(box.x / dpr) - box_expansion // 2,
				y=int(box.y / dpr) - box_expansion // 2,
				width=int(box.width / dpr) + box_expansion,
				height=int(box.height / dpr) + box_expansion,
				text=box.text,
			)
			logging.debug(f"Creating label {i} for box: {box} (scaled: {scaled_box})")
			self.labels.append(self._create_label(scaled_box))
		
		self.timer = QTimer(self)
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.close)
		self.timer.start(CONFIG["timeout_ms"])
		_overlays.append(self)

	def update_content(self, boxes: Sequence[TextBox]):
		self.timer.start(CONFIG["timeout_ms"])
		
		# Check if content is effectively the same (ignoring small jitter)
		if len(self.boxes) == len(boxes):
			same_content = True
			for b1, b2 in zip(self.boxes, boxes):
				if b1.text != b2.text:
					same_content = False
					break
				if (abs(b1.x - b2.x) > 5 or abs(b1.y - b2.y) > 5 or 
					abs(b1.width - b2.width) > 5 or abs(b1.height - b2.height) > 5):
					same_content = False
					break
			if same_content:
				return

		self.boxes = boxes
		
		# Clear existing labels
		for label in self.labels:
			label.deleteLater()
		self.labels.clear()
		
		screen = QApplication.primaryScreen()
		dpr = screen.devicePixelRatio()
		box_expansion = CONFIG["box_expansion"]
		
		for i, box in enumerate(boxes):
			scaled_box = TextBox(
				x=int(box.x / dpr) - box_expansion // 2,
				y=int(box.y / dpr) - box_expansion // 2,
				width=int(box.width / dpr) + box_expansion,
				height=int(box.height / dpr) + box_expansion,
				text=box.text,
			)
			self.labels.append(self._create_label(scaled_box))
		
		self.show()

	def closeEvent(self, event):
		if self in _overlays:
			_overlays.remove(self)
		super().closeEvent(event)

	def _create_label(self, box: TextBox) -> QLabel:
		label = StrokedLabel(box.text, self)
		label.setWordWrap(False)
		label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		# Background is drawn in paintEvent
		label.setAttribute(Qt.WA_TransparentForMouseEvents)
		
		font = QFont(label.font())
		if CONFIG["font_family"]:
			font.setFamily(CONFIG["font_family"])
			
		min_font_px = CONFIG["min_font_size"]
		max_font_px = CONFIG["max_font_size"]
		vertical_padding = CONFIG["vertical_padding"]
		horizontal_padding = CONFIG["horizontal_padding"]
		
		base_height = max(box.height - vertical_padding, min_font_px)
		pixel_size = int(min(max_font_px, base_height))
		font.setPixelSize(pixel_size)
		
		target_width = max(1, box.width - horizontal_padding)
		target_height = max(1, box.height - vertical_padding)
		metrics = QFontMetrics(font)
		
		while pixel_size > min_font_px:
			# Use width() (advance width) which is safer for layout than boundingRect().width()
			if metrics.width(box.text) <= target_width and metrics.height() <= target_height:
				break
			pixel_size -= 1
			font.setPixelSize(pixel_size)
			metrics = QFontMetrics(font)
			
		label.setFont(font)
		label.setGeometry(QRect(int(box.x), int(box.y), int(box.width), int(box.height)))
		label.show()
		return label


def load_from_file(path: str) -> str:
	with open(path, "r", encoding="utf-8") as handle:
		return handle.read()


def show_overlay(data: str) -> int:
	load_config()
	
	if not CONFIG.get("enable", 1):
		logging.info("Overlay disabled in config.")
		return 0

	if not logging.getLogger().hasHandlers():
		logging.basicConfig(
			level=logging.DEBUG,
			format="%(asctime)s [%(levelname)s] %(message)s",
			datefmt="%H:%M:%S",
		)

	logging.debug(f"Data loaded (length={len(data)}): {data[:100]}...")

	boxes = parse_boxes(data)
	if not boxes:
		logging.warning("No valid boxes to render.")
		print("No valid boxes to render.")
		return 1
	
	logging.info(f"Parsed {len(boxes)} boxes")

	app = QApplication.instance()
	run_loop = False
	if app is None:
		app = QApplication(sys.argv)
		run_loop = True

	# Reuse existing overlay if possible
	if _overlays:
		ovl = _overlays[0]
		ovl.update_content(boxes)
	else:
		#signal.signal(signal.SIGINT, signal.SIG_DFL)
		QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
		overlay = Overlay(boxes)
		overlay.show()
	
	if run_loop:
		return app.exec_()
	return 0


def main(argv: Sequence[str]) -> int:
	logging.basicConfig(
		level=logging.DEBUG,
		format="%(asctime)s [%(levelname)s] %(message)s",
		datefmt="%H:%M:%S",
	)
	logging.info("Application started")

	parser = argparse.ArgumentParser(description="Display OCR boxes on screen")
	parser.add_argument("--data-file", dest="data_file")
	parser.add_argument("--from-string", dest="data_string")
	args = parser.parse_args(argv)
	logging.debug(f"Arguments parsed: {args}")

	data: str
	if args.data_file:
		logging.info(f"Loading data from file: {args.data_file}")
		data = load_from_file(args.data_file)
	elif args.data_string:
		logging.info("Loading data from string argument")
		data = args.data_string
	else:
		default_path = Path(__file__).with_name("text.txt")
		if default_path.exists():
			logging.info(f"Loading data from default file: {default_path}")
			data = load_from_file(str(default_path))
		else:
			logging.info("Loading sample data")
			data = SAMPLE_DATA

	return show_overlay(data)


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
