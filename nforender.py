#!/usr/bin/env python
"""
nforender.py

Author: Plux

Renders NFO-files to PNG.

Can be used both as a library and as a standalone tool.
"""
from __future__ import with_statement
from PIL import Image, ImageColor
from sys import argv, stdout
from getopt import getopt

def load_bitmap_font(filename, dimensions):
    cols, rows = dimensions
    im = Image.open(filename)
    width, height = im.size
    char_width = width / cols
    char_height = height / rows

    font = []
    for n in range(cols * rows):
        offsetx = (n%cols) * char_width
        offsety = (n/cols) * char_height
        crop = im.crop((offsetx,
                        offsety,
                        offsetx + char_width,
                        offsety + char_height))
        font.append(crop)

    return font


def load_nfo(filename):
    with open(filename) as f:
        nfo = f.readlines()
        width = 0
        for line in nfo:
            line = line.rstrip()
            width = max(len(line), width)

        height = len(nfo)
        return (nfo, width, height)

def render_nfo(filename, font):
    nfo, width, height = load_nfo(filename)

    char_width, char_height = font[0].size

    dimensions = (width*char_width + char_width*2,
                  height*char_height + char_height*2)

    image = Image.new("RGB", dimensions)
    y = 0
    for line in nfo:
        y += char_height
        x = 0
        for c in line.rstrip():
            x += char_width
            if c == '\t': # dont render anything is tab character
                continue
            char = font[ord(c)]
            image.paste(char, (x,y))            
    
    return image

BACKGROUND_COLOR = (0,0,0)
FOREGROUND_COLOR = (168 168,168)
def set_colors(im, fg, bg):
    buf = im.load()
    width, height = im.size
    for x in range(width):
        for y in range(height):
            c = buf[x,y]
            if c == BACKGROUND_COLOR:
                buf[x,y] = bg
            elif c == FOREGROUND_COLOR:
                buf[x,y] = fg

def usage():
    print """
Usage: nforender.py [OPTION] FILE

Renders a NFO-file to PNG. Default is to output to FILE.png

Options:

  -h, --help              Display help
  -o, --output=FILE       Output file (e.g., output.png), set to "-" to write to stdout
  -b, --background=COLOR  Set background color (e.g., #ff0000, red)
  -f, --foreground=COLOR  Set foreground color (e.g., #0000ff, blue)
  -s, --style=STYLE       Set font style, valid values: dos, courier
  -d                      Displays the image instead of writing to disk
"""
    exit()

def main(args):
    try:
        optlist, args = getopt(args, 'ho:b:f:s:d',
                               ["help", "output=", "background=",
                                "foreground=", "style=", "display"])
    except getopt.GetoptError, err:
        print "Error:", str(err)
        usage()
    try:
        nfo_filename = args[0]
    except:
        print "Error: You must give one file as argument."
        usage()

    font_styles = {"dos":     ("dos.png",     (32, 8)),
                   "courier": ("courier.png", (32, 8))}

    # Defaults
    output = nfo_filename + ".png"
    display = False
    fg = FOREGROUND_COLOR
    bg = BACKGROUND_COLOR
    font_style = font_styles["dos"]

    # Parse options
    for opt, arg in optlist:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-b", "--background"):
            try:
                bg = ImageColor.getrgb(arg.strip())
            except ValueError, err:
                print "Error:", err
                usage()
        elif opt in ("-f", "--foreground"):
            try:
                fg = ImageColor.getrgb(arg.strip())
            except ValueError, err:
                print "Error:", err
                usage()
        elif opt in ("-s", "--style"):
            try:
                font_style = font_styles[arg]
            except:
                print "Error: Not a valid style. Valid values:",
                print ", ".join(font_styles.keys())
                usage()
        elif opt in ("-d", "--display"):
            display = True
        else:
            assert False, "unhandled option"

    try:
        font = load_bitmap_font(*font_style)
        im = render_nfo(nfo_filename, font)
    except Exception, err:
        print err
        exit()

    # Only replace colors if necessary
    if not (fg == FOREGROUND_COLOR and bg == BACKGROUND_COLOR):
        set_colors(im, fg, bg)

    if display:
        im.show()
    else:
        if output == "-":
            im.save(stdout,"PNG")
        elif output == nfo_filename:
            print "Error: Output and input shouldn't be the same file"
            usage()
        else:
            im.save(output, "PNG")

if __name__ == "__main__":
    main(argv[1:])


