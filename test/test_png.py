#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import unittest
import sys

sys.path.append('src')
import png


class TestPNG(unittest.TestCase):
    def setUp(self):
        thisdir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(thisdir, 'lena.png')
        self.png = png.PNG(filename)

    def test_header(self):
        self.assertEqual(self.png.header['width'], 512)
        self.assertEqual(self.png.header['height'], 512)
        self.assertEqual(self.png.header['bitdepth'], 8)
        self.assertEqual(self.png.header['colortype'], 2)
        self.assertEqual(self.png.header['compress'], 0)
        self.assertEqual(self.png.header['filter'], 0)
        self.assertEqual(self.png.header['interlace'], 0)

    def test_raw(self):
        expected_width, expected_height = 512, 512
        expected_raw_length = (1 + expected_width * 3) * expected_height
        self.assertEqual(len(self.png.raw), expected_raw_length)

    def test_readlines(self):
        expected_width = 512
        expected_height = 512
        expected_line_length = 1 + expected_width * 3
        filter_types = (png.PNG.FILTER_NONE,
                        png.PNG.FILTER_SUB,
                        png.PNG.FILTER_UP,
                        png.PNG.FILTER_AVERAGE,
                        png.PNG.FILTER_PEATH)
        num_line = 0
        for line in self.png.readlines():
            self.assertEqual(len(line), expected_line_length)
            self.assertTrue(line[0] in filter_types)
            num_line += 1
        self.assertEqual(num_line, expected_height)

    def test_glitch(self):
        self.assertRaises(NotImplementedError, self.png.glitch)

if __name__ == '__main__':
    unittest.main()
