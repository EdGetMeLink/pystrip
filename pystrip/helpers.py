"""
Utilities for 256 color support in terminals.

Adapted from:
http://stackoverflow.com/questions/1403353/256-color-terminal-library-for-ruby

The color palette is indexed as follows:

0-15: System colors
    0  black         8  dark gray
    1  red           9  bright red
    2  green         10 bright green
    3  yellow        11 bright yellow
    4  blue          12 bright blue
    5  magenta       13 bright magenta
    6  cyan          14 bright cyan
    7  light gray    15 white

16-231: 6x6x6 Color Cube
    All combinations of red, green, and blue from 0 to 5.

232-255: Grayscale Ramp
    24 shades of gray, not including black and white.
"""

# System color name constants.
(
    BLACK,
    RED,
    GREEN,
    YELLOW,
    BLUE,
    MAGENTA,
    CYAN,
    LIGHT_GRAY,
    DARK_GRAY,
    BRIGHT_RED,
    BRIGHT_GREEN,
    BRIGHT_YELLOW,
    BRIGHT_BLUE,
    BRIGHT_MAGENTA,
    BRIGHT_CYAN,
    WHITE,
) = range(16)

def rgb(red, green, blue):
    """
    Calculate the palette index of a color in the 6x6x6 color cube.

    The red, green and blue arguments may range from 0 to 5.
    """
    red = int(red / 42.5) - 1
    green  = int(green / 42.5) - 1
    blue  = int(blue / 42.5) - 1
    return 16 + (green * 36) + (red * 6) + blue

def rgb_hsv(args):
    r = args[0]
    g = args[1]
    b = args[2]

    _min = min(args)
    _max = max(args)

    delta = _max - _min
    h = None
    s = None
    v = None

    if _max == 0:
        s = 0
    else:
        s = (delta / _max * 1000) / 10

    if _max == _min:
        h = 0
    elif r == _max:
        h = (g - b) / delta
    elif g == _max:
        h = 2 + (b - r) / delta
    elif b == _max:
        h = 4 + (r - g) / delta

    h = min(h * 60, 360)
    if h < 0:
        h += 360

    v = ((_max / 255) * 1000) / 10
    return [h,s,v]

def rgb_ansi16(red, green, blue):
    args = [red, green, blue]
    r = args[0]
    g = args[1]
    b = args[2]
    # use rgb to hsv
    value = args[1] if 1 in args else rgb_hsv(args)[2]
    value = int(round(value / 50))

    if value == 0:
        return 30

    r = float(r)
    g = float(g)
    b = float(b)

    ansi = 30 + (int(round(b / 255)) << 2) | (int(round(g / 255)) << 1) | (int(round(r / 255)) << 2)
    if value == 2:
        ansi += 60

    return ansi



def gray(value):
    """
    Calculate the palette index of a color in the grayscale ramp.

    The value argument may range from 0 to 23.
    """
    return 232 + value

def set_color(fg=None, bg=None):
    """
    Print escape codes to set the terminal color.

    fg and bg are indices into the color palette for the foreground and
    background colors.
    """
    print(_set_color(fg, bg), end='')

def _set_color(fg=None, bg=None):
    result = ''
    if fg:
        result += '\x1b[38;5;%dm' % fg
    if bg:
        result += '\x1b[48;5;%dm' % bg
    return result

def reset_color():
    """
    Reset terminal color to default.
    """
    print(_reset_color(), end='')

def _reset_color():
    return '\x1b[0m'

def print_color(*args, **kwargs):
    """
    Print function, with extra arguments fg and bg to set colors.
    """
    fg = kwargs.pop('fg', None)
    bg = kwargs.pop('bg', None)
    set_color(fg, bg)
    print(*args, **kwargs)
    reset_color()

def format_color(string, fg=None, bg=None):
    return _set_color(fg, bg) + string + _reset_color()

def print_at_position(x, y, text):
    '''
    cursor positioning
    ESC [ y;x H     # position cursor at x across, y down
    ESC [ y;x f     # position cursor at x across, y down
    ESC [ n A       # move cursor n lines up
    ESC [ n B       # move cursor n lines down
    ESC [ n C       # move cursor n characters forward
    ESC [ n D       # move cursor n characters backward

    clear the screen
    ESC [ mode J    # clear the screen
    '''
    print(u'\033[{y};{x}H{text}'.format(x=x, y=y, text=text))
    return

def clear_screen():
    '''
    cursor positioning
    ESC [ y;x H     # position cursor at x across, y down
    ESC [ y;x f     # position cursor at x across, y down
    ESC [ n A       # move cursor n lines up
    ESC [ n B       # move cursor n lines down
    ESC [ n C       # move cursor n characters forward
    ESC [ n D       # move cursor n characters backward

    clear the screen
    ESC [ mode J    # clear the screen
    '''
    print(u'\033[2J')
    return


if __name__ == '__main__':
    # Print a test graphic showing all colors.

    print('System colors:')
    for c in range(8):
        print_color('  ', bg=c, end='')
    print()
    for c in range(8, 16):
        print_color('  ', bg=c, end='')
    print()
    print()

    print('RGB color cube, 6x6x6:')
    for green in range(6):
        for red in range(6):
            for blue in range(6):
                print_color('  ', bg=rgb(red, green, blue), end='')
            print(' ', end='')
        print()
    print()

    print('Grayscale ramp, with RGB grays:')
    for value in range(24):
        print_color('  ', bg=gray(value), end='')
    print()

    print_color('  ', bg=rgb(0, 0, 0), end='')
    print('  '*7, end='')
    print_color('    ', bg=rgb(1, 1, 1), end='')
    print('  '*2, end='')
    print_color('    ', bg=rgb(2, 2, 2), end='')
    print('  '*2, end='')
    print_color('    ', bg=rgb(3, 3, 3), end='')
    print('  '*2, end='')
    print_color('    ', bg=rgb(4, 4, 4), end='')
    print('  ', end='')
    print_color('  ', bg=rgb(5, 5, 5), end='')
    print()
