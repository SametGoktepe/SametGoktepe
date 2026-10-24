"""Tiny pixel-art engine: integer canvas, proportional 8x8 bitmap text, run-length SVG output."""
from pixelfont import GLYPHS

SCALE = 2  # real px per virtual pixel
P = dict(
    night="#0b1024", dusk="#0f1430", glow="#141b3d", deep="#0a0e1f", horizon="#283058",
    silhouette="#1a2042", steel="#2e3657", steel_hi="#46507a", steel_lo="#232a4a",
    cream="#f2e9d8", mute="#8b93b8", teal="#35d0c0", amber="#ffb347", red="#ff5d5d",
    green="#8cff8c", green_dim="#3fae5a", screen="#061a12", scan="#07211a",
    wood="#7a4a2a", wood_hi="#a86a3d", wood_lo="#4e2e18",
)
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important}}"


def luminance(hex_color):
    r, g, b = (int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def glyph_span(ch):
    rows = GLYPHS.get(ch) or GLYPHS["?"]
    cols = [c for c in range(8) if any((row >> c) & 1 for row in rows)]
    return (min(cols), max(cols), rows) if cols else (0, 2, rows)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.fills = []          # big flat areas: (x, y, w, h, color)
        self.layers = {}         # layer -> {(x, y): color}
        self.styles = {}         # layer -> inline style

    def fill(self, x, y, w, h, color):
        self.fills.append((x, y, w, h, color))

    def px(self, x, y, color, layer="base"):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.layers.setdefault(layer, {})[(x, y)] = color

    def rect(self, x, y, w, h, color, layer="base"):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, color, layer)

    def bevel(self, x, y, w, h, hi, lo, t=1):
        self.fill(x, y, w, t, hi)
        self.fill(x, y, t, h, hi)
        self.fill(x, y + h - t, w, t, lo)
        self.fill(x + w - t, y, t, h, lo)

    def sprite(self, x, y, rows, color, layer="base"):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch == "#":
                    self.px(x + dx, y + dy, color, layer)

    def text_width(self, s, scale=1):
        w = 0
        for ch in s:
            if ch == " ":
                w += 3 * scale
                continue
            c0, c1, _ = glyph_span(ch)
            w += (c1 - c0 + 2) * scale
        return w - scale  # no trailing gap

    def text(self, x, y, s, color, scale=1, layer="base"):
        cx = x
        for ch in s:
            if ch == " ":
                cx += 3 * scale
                continue
            c0, c1, rows = glyph_span(ch)
            for r, row in enumerate(rows):
                for c in range(c0, c1 + 1):
                    if (row >> c) & 1:
                        self.rect(cx + (c - c0) * scale, y + r * scale, scale, scale, color, layer)
            cx += (c1 - c0 + 2) * scale
        return cx - scale

    def text_center(self, cx, y, s, color, scale=1, layer="base"):
        return self.text(cx - self.text_width(s, scale) // 2, y, s, color, scale, layer)

    def text_right(self, rx, y, s, color, scale=1, layer="base"):
        return self.text(rx - self.text_width(s, scale), y, s, color, scale, layer)

    def svg(self, css="", title=""):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w * SCALE}" height="{self.h * SCALE}" shape-rendering="crispEdges" role="img">']
        if title:
            out.append("<title>" + title.replace("&", "&amp;").replace("<", "&lt;") + "</title>")
        out.append(f"<style>{css}{REDUCED}</style>")
        for x, y, w, h, color in self.fills:
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
        for layer, pixels in self.layers.items():
            cls = "" if layer == "base" else f' class="{layer}"'
            style = f' style="{self.styles[layer]}"' if layer in self.styles else ""
            out.append(f"<g{cls}{style}>")
            out.extend(self._runs(pixels))
            out.append("</g>")
        out.append("</svg>")
        return "\n".join(out)

    @staticmethod
    def _runs(pixels):
        """One <path> per colour made of 1px-high runs: far smaller than a rect per pixel."""
        rows = {}
        for (x, y), color in pixels.items():
            rows.setdefault(y, []).append((x, color))
        paths = {}
        for y in sorted(rows):
            run_x, run_c, run_w = None, None, 0
            for x, color in sorted(rows[y]) + [(None, None)]:
                if run_x is not None and x == run_x + run_w and color == run_c:
                    run_w += 1
                    continue
                if run_x is not None:
                    paths.setdefault(run_c, []).append(f"M{run_x} {y}h{run_w}v1h-{run_w}z")
                run_x, run_c, run_w = x, color, 1
        for color, segs in paths.items():
            yield f'<path fill="{color}" d="{"".join(segs)}"/>'
