import math
import os
from PIL import Image
from colorsys import rgb_to_hsv, hsv_to_rgb
from pathlib import Path


# --------------------- Settings ----------------------------

tile_set_dir = "AbsoluteUnits/Images/TileSets/HexaRealm/Units"  # change to your directory here
outline_color = (0, 0, 0, 255)
shadow_color = (0, 0, 0, 83)  # can be set to (0, 0, 0, 0) to also blend shadow into the outline
outline_darkness = 1.5  # Must be != 0 | > 1 -> darker | < 1 -> lighter
darken_base_color_outline = True  # Determines if the outline_darkness is used to darken the base color outline
darken_nation_color_outlines = False  # Determines if the outline_darkness is used to also darken the nation color outline in the nation color files
alpha_reduction_strength = 8  # Must be != 0 | higher = less alpha -> less visible nation colors on outline
reduce_nation_color_alpha = True  # Determines if the nation color outline alpha should be reduced proportionally to the amount of nation color pixel adjacent to the outline pixel based on the alpha_reduction_strength

# --------------------- Settings ----------------------------


def add_to_list(pixels: list, pixel_value: tuple):
    """
    Adds the pixel_value to pixels if pixel_value is not transparent, outline_color or shadow_color

    :param pixels: the list to add
    :param pixel_value: the value to add
    """
    if pixel_value != (0, 0, 0, 0) and pixel_value != outline_color and pixel_value != shadow_color:
        pixels.append(pixel_value)


def blend_colors(colors: list, darken: bool = True) -> tuple:
    """
    Blends the given pixel colors and darkens the blend if darken is true

    :param colors: the colors to blend
    :param darken: should the color be darkened by a factor of outline_darkness?
    :returns: the blended and potentially darkened color
    """

    if len(colors) == 0:
        return 0, 0, 0, 0

    blend = [0, 0, 0, 0]
    for value in colors:
        blend[0] += value[0]
        blend[1] += value[1]
        blend[2] += value[2]
        blend[3] += value[3]
    blend[0] //= len(colors)
    blend[1] //= len(colors)
    blend[2] //= len(colors)
    blend[3] //= len(colors)
    if darken:
        hsv = rgb_to_hsv(blend[0], blend[1], blend[2])
        rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2] / outline_darkness)
        blend = (rgb[0], rgb[1], rgb[2], blend[3])
    return blend


def set_outline_pixel(pixelValues: list, index: int, img: Image, darkenColor: bool, reduceAlpha: bool = False):
    """
    Sets a pixel to a blend of its surrounding colors

    :param pixelValues: all pixel values of the image we want to modify
    :param index: the index of the pixel in the pixelValues list that should be set
    :param img: the image to modify itself
    :param darkenColor: should the blended color be darkened before being applied?
    :param reduceAlpha: should the alpha of the blended color be reduced based on how many adjacent colors where used for the blend?
    """

    colors = []
    # We can assume that if an outline pixel is at the edge of the image the next pixel is (0, 0, 0, 0)
    if index - width > 0:
        add_to_list(colors, pixelValues[index - width - 1])
        add_to_list(colors, pixelValues[index - width])
        add_to_list(colors, pixelValues[index - width + 1])

    add_to_list(colors, pixelValues[index - 1])
    add_to_list(colors, val)
    add_to_list(colors, pixelValues[index + 1])

    if index + width > 0:
        add_to_list(colors, pixelValues[index + width - 1])
        add_to_list(colors, pixelValues[index + width])
        add_to_list(colors, pixelValues[index + width + 1])

    y = index // width
    x = index - width * y

    if len(colors) > 0:
        blended_colors = blend_colors(colors, darkenColor)
        if reduceAlpha:
            alpha = int(blended_colors[3]) // math.ceil((alpha_reduction_strength / len(colors)))  # Reduce the alpha if not all surrounding colors are responsible for this blend
        else:
            alpha = int(blended_colors[3])

        img.putpixel(
            xy=(x, y),
            value=(int(blended_colors[0]), int(blended_colors[1]), int(blended_colors[2]), alpha)
        )


Path(f"{tile_set_dir}/ColoredOutline").mkdir(exist_ok=True)
for filename in os.listdir(tile_set_dir):
    if not filename.endswith(".png"):
        continue

    if filename.find('1') != -1 or filename.find('2') != -1:
        continue  # We don't have to look at nation color overlays directly

    has_nation_colors = Path(f"{tile_set_dir}/{filename.removesuffix('.png')}-1.png").is_file()
    outline_counter = 0

    baseImage = Image.open(f"{tile_set_dir}/{filename}", 'r')
    basePixelValues: list = list(baseImage.getdata())
    width, height = baseImage.size
    if has_nation_colors:
        fncOverlay = Image.open(f"{tile_set_dir}/{filename.removesuffix('.png')}-1.png", 'r')
        fncPixelValues = list(fncOverlay.getdata())
        sncOverlay = Image.open(f"{tile_set_dir}/{filename.removesuffix('.png')}-2.png", 'r')
        sncPixelValues = list(sncOverlay.getdata())

    for idx, val in enumerate(basePixelValues):
        if val == outline_color:
            outline_counter += 1

            set_outline_pixel(basePixelValues, idx, baseImage, darken_base_color_outline)
            if has_nation_colors:
                set_outline_pixel(fncPixelValues, idx, fncOverlay, darken_nation_color_outlines, reduce_nation_color_alpha)
                set_outline_pixel(sncPixelValues, idx, sncOverlay, darken_nation_color_outlines, reduce_nation_color_alpha)

    if outline_counter > 0:
        baseImage.save(f'{tile_set_dir}/ColoredOutline/{filename}')
        if has_nation_colors:
            fncOverlay.save(f"{tile_set_dir}/ColoredOutline/{filename.removesuffix('.png')}-1.png")
            sncOverlay.save(f"{tile_set_dir}/ColoredOutline/{filename.removesuffix('.png')}-2.png")
        print(f"Converted {filename}{' and its nation color overlays' if has_nation_colors else ''}")
