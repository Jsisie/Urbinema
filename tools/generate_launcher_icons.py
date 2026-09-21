from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "app" / "src" / "main" / "res" / "drawable-nodpi" / "logo_urbinema.png"
RES = ROOT / "app" / "src" / "main" / "res"
CREAM = (250, 246, 240, 255)
FG_SIZE = 432
SAFE = int(FG_SIZE * 0.48)

DENSITIES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}


def fit(image: Image.Image, box: int) -> Image.Image:
    fitted = image.copy()
    fitted.thumbnail((box, box), Image.Resampling.LANCZOS)
    return fitted


def on_canvas(image: Image.Image, size: int, background: tuple[int, int, int, int] | None) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), background or (0, 0, 0, 0))
    x = (size - image.width) // 2
    y = (size - image.height) // 2
    canvas.paste(image, (x, y), image)
    return canvas


def rounded(image: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *image.size), radius=radius, fill=255)
    out = image.copy()
    out.putalpha(mask)
    return out


def main() -> None:
    logo = Image.open(SRC).convert("RGBA")
    drawable = RES / "drawable-nodpi"
    drawable.mkdir(parents=True, exist_ok=True)
    logo.save(drawable / "logo_urbinema.png", optimize=True)

    foreground = on_canvas(fit(logo, SAFE), FG_SIZE, None)
    foreground.save(drawable / "ic_launcher_foreground.png", optimize=True)

    for folder, size in DENSITIES.items():
        dest = RES / folder
        dest.mkdir(parents=True, exist_ok=True)
        square = on_canvas(fit(logo, int(size * 0.82)), size, CREAM)
        square.save(dest / "ic_launcher.png", optimize=True)
        rounded(square, radius=size // 2).save(dest / "ic_launcher_round.png", optimize=True)
        for leftover in dest.glob("*.webp"):
            leftover.unlink()


if __name__ == "__main__":
    main()
