from functools import lru_cache, reduce
from PIL import Image, ImageOps
from app.config import get_cfg

cfg = get_cfg()

PRIMARY_COLORS = {
    "maroon": (128, 0, 0),
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "olive": (128, 128, 0),
    "green": (0, 128, 0),
    "lime": (0, 255, 0),
    "teal": (0, 128, 128),
    "aqua": (0, 255, 255),
    "blue": (0, 0, 255),
    "navy": (0, 0, 128),
    "fuchsia": (255, 0, 255),
    "purple": (128, 0, 128),
    "black": (0, 0, 0),
    "gray": (128, 128, 128),
    "silver": (192, 192, 192),
    "white": (255, 255, 255),
}


class ImageManager:

    @staticmethod
    def open_image(image_path: str) -> Image:
        """Open image."""
        return Image.open(image_path)

    @staticmethod
    def create_thumbnail(image_path: str) -> Image:
        """Create thumbnail."""
        im = Image.open(image_path)
        im.thumbnail(tuple([cfg.THUMBNAIL_WIDTH, cfg.THUMBNAIL_HEIGHT]))
        im.save(image_path, image_quality=cfg.THUMBNAIL_QUALITY)
        return im

    @lru_cache
    @staticmethod
    def get_colors_list():
        web_colors = tuple(PRIMARY_COLORS[x] for x in PRIMARY_COLORS)
        colors = []
        for x in web_colors:
            colors.extend(x)
        return colors
    
    @lru_cache
    @staticmethod
    def get_colors_keys():
        return [x for x in PRIMARY_COLORS.keys()]

    @staticmethod
    def get_colors_dict(im):
        w, h = im.size
        colors = im.getcolors(w * h)
        colordict = {x[1]:x[0] for x in colors}
        return colordict

    @staticmethod
    def get_colors(im):
        colors = ImageManager.get_colors_list()
        palette = Image.new("P", (1, 1))
        palette.putpalette(colors)
        out = im.quantize(colors=len(colors), palette=palette, dither=Image.Dither.NONE)

        colordict = ImageManager.get_colors_dict(out)
        color_names = ImageManager.get_colors_keys()
        pixels_number = reduce(lambda x, value: x + value, colordict.values(), 0)
        tmp = {color_names[x]:colordict[x] for x in colordict}
        tmp = {x:tmp[x] / (pixels_number / 100) for x in tmp}
        return tmp
