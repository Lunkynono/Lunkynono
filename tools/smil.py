"""Compile the hatch artwork into self-contained native SVG (SMIL) animation.

The original hatch-banner.svg remains the editable artwork. This compiler owns
the twenty-second mechanical timeline of the published SVG.
"""
import re
import xml.etree.ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)

def compile_svg(source):
    root = ET.fromstring(source)
    style = root.find(f'{{{NS}}}style')
    # Keep typography and colors; CSS transforms would override SMIL transforms.
    style.text = style.text.split('  .leaf-left')[0] + '\n.trace{stroke-dasharray:80 720}\n'
    root.find(f'{{{NS}}}desc').text = 'Antonio Navarro — Software Engineer. A rotating handwheel unlocks a two-leaf mechanical hatch. The doors reveal the profile, close and repeat in a continuous twenty-second native SVG animation.'

    def animate(parent, name, values, times, kind=None, easing=None, discrete=False):
        tag = 'animateTransform' if kind else 'animate'
        attrs = {'attributeName':name, 'dur':'20s', 'begin':'0s', 'repeatCount':'indefinite',
                 'values':values, 'keyTimes':times}
        if kind: attrs['type'] = kind
        if discrete: attrs['calcMode'] = 'discrete'
        elif easing:
            attrs['calcMode'] = 'spline'
            attrs['keySplines'] = ';'.join([easing]*(len(times.split(';'))-1))
        else: attrs['calcMode'] = 'linear'
        ET.SubElement(parent, f'{{{NS}}}{tag}', attrs)

    for element in list(root.iter()):
        classes = element.get('class','').split()
        if 'leaf-left' in classes or 'leaf-right' in classes:
            distance = '-730' if 'leaf-left' in classes else '650'
            animate(element,'transform',f'0 0;0 0;{distance} 0;{distance} 0;0 0;0 0',
                    '0;.2;.3;.83;.94;1','translate','.65 0 .22 1')
        if 'wheel-turn' in classes:
            animate(element,'transform','0 588 242;0 588 242;144 588 242;144 588 242;0 588 242',
                    '0;.06;.16;.96;1','rotate','.6 0 .2 1')
        if 'bolt' in classes:
            animate(element,'transform','0 0;0 0;-44 0;-44 0;0 0;0 0',
                    '0;.16;.2;.94;.96;1','translate','.6 0 .25 1')
        if 'orbit-turn' in classes:
            animate(element,'transform','0 944 239;360 944 239','0;1','rotate')
        if 'trace' in classes:
            animate(element,'stroke-dashoffset','0;-1600','0;1')
        if 'lock-light' in classes:
            element.set('fill','#F3E600')
            animate(element,'fill','#FF2A4F;#FF2A4F;#F3E600;#F3E600;#FF2A4F;#FF2A4F',
                    '0;.06;.16;.94;.96;1',easing='.25 .1 .25 1')
        if 'seam-light' in classes:
            element.set('opacity','0')
            animate(element,'opacity','0;0;.8;.8;0;0;.8;0;0',
                    '0;.15;.19;.22;.3;.83;.93;.96;1',easing='.25 .1 .25 1')
        for cls, values, times, base in [
            ('locked','1;0;1;1','0;.06;.96;1','0'),
            ('unlocking','0;1;0;0','0;.06;.2;1','0'),
            ('open-state','0;1;0;0','0;.2;.83;1','1'),
            ('closing','0;1;0;0','0;.83;.96;1','0')]:
            if cls in classes:
                element.set('opacity',base)
                animate(element,'opacity',values,times,discrete=True)
    return '\n'.join(line.rstrip() for line in ET.tostring(root,encoding='unicode').splitlines())+'\n'

def static_svg(source):
    root=ET.fromstring(source)
    for parent in root.iter():
        for child in list(parent):
            if child.tag in (f'{{{NS}}}animate',f'{{{NS}}}animateTransform'):
                parent.remove(child)
    return '\n'.join(line.rstrip() for line in ET.tostring(root,encoding='unicode').splitlines())+'\n'
