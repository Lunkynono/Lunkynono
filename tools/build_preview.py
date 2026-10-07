"""Build the self-contained local preview and the static SVG. Python standard library only."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
svg = (ROOT / "assets/hatch-banner.svg").read_text(encoding="utf-8")
ET.fromstring(svg)
template = (ROOT / "tools/preview.template.html").read_text(encoding="utf-8")
(ROOT / "preview.html").write_text(template.replace("__BANNER_SVG__", svg), encoding="utf-8")
static = svg.replace("</style>", "\n/* Frozen open composition for static use. */\n*{animation:none!important}\n</style>")
(ROOT / "assets/hatch-banner-static.svg").write_text(static, encoding="utf-8")
print("Built preview.html and assets/hatch-banner-static.svg; SVG XML is valid.")
