"""Render local SVG motion samples in Chrome's headless image renderer.

Usage: python tools/render_checks.py
Outputs stay in ignored .preview-qa/. Uses installed Chrome, no browser downloads.
No existing browser session or user profile is accessed.
"""
import base64
import html
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / ".preview-qa"
QA.mkdir(exist_ok=True)
CHROME = Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe"
if not CHROME.exists():
    raise SystemExit("Chrome not found; open preview.html to review manually.")

svg = (ROOT / "assets/hatch-banner.svg").read_text(encoding="utf-8")
xml = ET.fromstring(svg)
ns = {"s": "http://www.w3.org/2000/svg"}
assert xml.attrib["viewBox"] == "0 0 1200 480"
assert not xml.findall(".//s:script", ns)
ids = [e.attrib["id"] for e in xml.iter() if "id" in e.attrib]
assert len(ids) == len(set(ids)), "Duplicate SVG IDs"
for element in xml.iter():
    for key, value in element.attrib.items():
        if key.endswith("href"):
            assert value.startswith("#") and value[1:] in ids, value
        for target in re.findall(r"url\(#([^)]*)\)", value):
            assert target in ids, target
assert "assets/hatch-banner.svg" in (ROOT / "README.md").read_text(encoding="utf-8")
assert "prefers-reduced-motion" not in svg, "Profile banner must animate continuously"

def render(url, name, width, height, dump=False):
    args = [str(CHROME), "--headless=new", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--hide-scrollbars", "--force-device-scale-factor=1",
            f"--user-data-dir={QA / 'chrome-profile'}", f"--window-size={width},{height}",
            "--virtual-time-budget=1200", "--disable-background-networking"]
    args += ["--dump-dom"] if dump else [f"--screenshot={QA / name}"]
    result = subprocess.run(args + [url], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=40)
    if result.returncode:
        raise RuntimeError(result.stderr[-1500:])
    if not dump and not (QA / name).exists():
        raise RuntimeError("No screenshot produced: " + result.stderr[-1500:])
    return result.stdout

# Real <img> elements exercise secure-image SVG mode, as used in a README.
# Freeze CSS at sampled times; this is only applied to the QA copies.
def image_at(t):
    frozen = svg
    rule = f"*{{animation-delay:-{t}s!important;animation-play-state:paused!important}}"
    frozen = frozen.replace("</style>", rule + "</style>")
    return "data:image/svg+xml;base64," + base64.b64encode(frozen.encode()).decode()

samples = [(0, "01 / CERRADA"), (2.3, "02 / VOLANTE EN GIRO"), (3.9, "03 / CERROJOS RETRAÍDOS"),
           (4.8, "04 / APERTURA"), (10, "05 / PERFIL ABIERTO"), (18, "06 / CIERRE")]
cells = "".join(f'<section><p>{label} · {t:.1f} s</p><img alt="{html.escape(label)}" src="{image_at(t)}"></section>' for t, label in samples)
contact = '<!doctype html><meta charset="utf-8"><style>body{margin:0;padding:20px;background:#080d12;color:#aec0c8;font:12px Consolas,monospace}main{display:grid;grid-template-columns:1fr 1fr;gap:20px}p{margin:0 0 8px}img{width:100%;display:block}</style><main>' + cells + '</main>'
(QA / "contact.html").write_text(contact, encoding="utf-8")
render((QA / "contact.html").as_uri(), "contact.png", 1440, 985)

# Chromium clamps the headless viewport width on some Windows builds; use a
# fixed 375px image in a wider document to verify the actual mobile geometry.
mobile = '<!doctype html><style>body{margin:0;padding:16px;background:#f0f2ed}img{display:block;width:375px;height:150px;margin-bottom:16px}</style>'
mobile += ''.join(f'<img alt="Mobile frame" src="{image_at(t)}">' for t in (0, 4.8, 10))
(QA / "mobile.html").write_text(mobile, encoding="utf-8")
render((QA / "mobile.html").as_uri(), "mobile.png", 440, 540)
preview = (ROOT / "preview.html").as_uri()
render(preview + "?at=0", "preview-desktop.png", 1440, 990)
render(preview + "?capture=1&at=10", "open.png", 1200, 480)
render(preview + "?capture=1&at=0", "closed.png", 1200, 480)

# Review keyframe boundaries and accessibility from the actual preview DOM.
dom = render(preview + "?capture=1&at=4.8", "unused", 1200, 480, dump=True)
assert 'data-motion="full"' in dom
count = re.search(r'data-animations="(\d+)"', dom)
assert count and int(count.group(1)) >= 10, "CSS animations did not initialize"
reduced_dom = render(preview + "?capture=1", "unused", 1200, 480, dump=True)
assert 'data-motion="full"' in reduced_dom, "Default preview must autoplay"
# Local browser assertions for the mechanical sequence and preview controls.
checks = r'''<script>
try {
  const expect=(ok,msg)=>{if(!ok)throw Error(msg)};
  const matrix=sel=>new DOMMatrix(getComputedStyle(svg.querySelector(sel)).transform);
  const near=(a,b)=>Math.abs(a-b)<.1;
  expect(running&&animations.length>=10,'automatic playback');
  expect(animations.every(a=>a.playState==='running'&&a.effect.getTiming().iterations===Infinity),'continuous loop');
  seek(0);
  expect(near(matrix('#left-leaf').e,0)&&near(matrix('#right-leaf').e,0),'closed geometry');
  seek(3.2);
  expect(near(matrix('#handwheel').a,Math.cos(144*Math.PI/180)),'wheel turn');
  expect(near(matrix('#left-leaf').e,0),'door opens before unlock');
  seek(3.99);
  expect(matrix('.bolt').e < -43,'bolts did not retract');
  seek(6);
  expect(near(matrix('#left-leaf').e,-730)&&near(matrix('#right-leaf').e,650),'open geometry');
  seek(18.8);
  expect(near(matrix('#left-leaf').e,0)&&near(matrix('#right-leaf').e,0),'closing geometry');
  expect(near(matrix('.bolt').e,-44),'bolts advanced before doors closed');
  seek(20);
  expect(near(matrix('#left-leaf').e,0)&&near(matrix('#handwheel').a,1)&&near(matrix('.bolt').e,0),'loop continuity');
  document.querySelector('[data-time="10"]').click();
  expect(!running&&Number(slider.value)===10&&near(matrix('#left-leaf').e,-730),'phase button');
  slider.value=5;slider.dispatchEvent(new Event('input'));
  expect(!running&&animations.every(a=>a.currentTime===5000),'scrubber synchronization');
  play.click();expect(running,'play control');
  play.click();expect(!running,'pause control');
  document.querySelector('#restart').click();expect(running,'restart control');
  document.querySelector('[data-width="375"]').click();
  expect(document.querySelector('.frame').style.maxWidth==='375px','mobile control');
  document.querySelector('#theme').click();expect(document.body.classList.contains('light'),'light background');
  expect(animations.length>=10&&running,'animation remains active regardless of system motion preference');
  document.documentElement.dataset.selfTest='PASS';
} catch(error){document.documentElement.dataset.selfTest='FAIL: '+error.message;}
</script>'''
qa_html=(ROOT/'preview.html').read_text(encoding='utf-8').replace('</html>',checks+'</html>')
(QA/'controls.html').write_text(qa_html,encoding='utf-8')
tested=render((QA/'controls.html').as_uri(),'unused',1200,700,dump=True)
result=re.search(r'data-self-test="([^"]+)"',tested)
assert result and result.group(1)=='PASS', result.group(1) if result else 'Browser assertions did not run'
report = {"xml": "valid", "internal_references": "valid", "animated_elements": int(count.group(1)),
          "system_reduced_motion": 'data-system-motion="reduced"' in reduced_dom,
          "autoplay": "enabled", "loop": "infinite",
          "svg_bytes": len(svg.encode()), "rendered_times_seconds": [t for t, _ in samples],
          "image_mode": "rendered as img, no script inside SVG", "mechanics_and_controls": result.group(1),
          "note": "GitHub-hosted result not yet verified."}
(QA / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
print("Visual review: .preview-qa/contact.png, mobile.png and preview-desktop.png")
