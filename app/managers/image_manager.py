from functools import lru_cache



# https://en.wikipedia.org/wiki/Web_colors
WEB_COLORS = {
    # pink colors
    "medium_violet_red": (199, 21, 133),
    "deep_pink": (255, 20, 147),
    "pale_violet_red": (219, 112, 147),
    "hot_pink": (255, 105, 180),
    "light_pink": (255, 182, 193),
    "pink": (255, 192, 203),
}


class ImageManager:

    @lru_cache
    @staticmethod
    def get_colors_list():
        web_colors = tuple(WEB_COLORS[x] for x in WEB_COLORS)
        colors = []
        for x in web_colors:
            colors.extend(x)
        return colors

    @staticmethod
    def get_colormap(im):
        colors = ImageManager.get_colors_list()

        im = im.convert("P")
        im.putpalette(colors)
        im.save("/hide/data/mediafiles/cga.png")
