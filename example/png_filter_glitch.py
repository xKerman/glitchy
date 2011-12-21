# -*- coding: utf-8 -*-

import glitch


class PNGFilterGlitch(glitch.PNG):
    def glitch(self):
        lines = (self.FILTER_PEATH + line[1:] for line in self.readlines())
        self.raw = ''.join(lines)


if __name__ == '__main__':
    png = PNGFilterGlitch('lena.png')
    png.glitch()
    png.write('line_glitch_lena.png')
