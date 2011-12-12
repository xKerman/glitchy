# -*- coding: utf-8 -*-

import itertools
import struct
import zlib


class PNGError(Exception):
    pass


class PNG(object):
    SIGNATURE = '\x89PNG\r\n\x1a\n'
    FILTER_NONE = '\x00'
    FILTER_SUB = '\x01'
    FILTER_UP = '\x02'
    FILTER_AVERAGE = '\x03'
    FILTER_PEATH = '\x04'

    def __init__(self, filename):
        with open(filename, 'rb') as f:
            data = f.read()
        self.header, self._chunks = self.parse(data)
        self.raw = self.create_raw_data()

    def parse(self, data):
        if data[:8] != self.SIGNATURE:
            raise PNGError('signature mismatch')
        index = 8
        ihdr, index = self.parse_chunk(data, index)
        if ihdr['type'] != 'IHDR':
            raise PNGError
        header = self.parse_header(ihdr['data'])
        chunks = []
        while index < len(data):
            chunk, index = self.parse_chunk(data, index)
            chunks.append(chunk)
        return header, chunks

    def parse_chunk(self, data, start):
        index = start
        chunk_len = struct.unpack('!I', data[index:index+4])[0]
        index += 4
        if chunk_len > 2 ** 31 - 1:
            raise PNGError
        chunk_type = data[index:index+4]
        if not chunk_type.isalpha():
            raise PNGError
        index += 4
        chunk_data = data[index:index+chunk_len]
        index += chunk_len
        crc = data[index:index+4]
        index += 4
        chunk = {'type': chunk_type, 'data': chunk_data}
        return chunk, index

    def parse_header(self, ihdr_data):
        (width,
         height,
         bitdepth,
         colortype,
         compress,
         filter_,
         interlace) = struct.unpack('!IIBBBBB', ihdr_data)
        header = {'width': width,
                  'height': height,
                  'bitdepth': bitdepth,
                  'colortype': colortype,
                  'compress': compress,
                  'filter': filter_,
                  'interlace': interlace}
        return header

    def create_raw_data(self):
        raw = ''.join(zlib.decompress(chunk['data']) for chunk in self._chunks
                      if chunk['type'] == 'IDAT')
        return raw

    @property
    def bps(self):
        colors = (1, 3, 3, 2, 4)[self.header['colortype']]
        sample_depth = 8 if self.header['colortype'] == 3 else self.header['bitdepth']
        bit_per_sample = sample_depth * colors
        return bit_per_sample

    def readlines(self):
        line_len = 1 + (self.header['width'] * self.bps / 8)
        for i in xrange(self.header['height']):
            start = i * line_len
            end = (i + 1) * line_len
            yield self.raw[start:end]

    def write(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.SIGNATURE)
            header = struct.pack('!IIBBBBB',
                                 self.header['width'],
                                 self.header['height'],
                                 self.header['bitdepth'],
                                 self.header['colortype'],
                                 self.header['compress'],
                                 self.header['filter'],
                                 self.header['interlace'])
            self.write_chunk(f, 'IHDR', header)
            is_not_idat = lambda chunk: chunk['type'] != 'IDAT'
            for chunk in itertools.takewhile(is_not_idat, self._chunks):
                self.write_chunk(f, chunk['type'], chunk['data'])
            self.write_chunk(f, 'IDAT', zlib.compress(self.raw))
            remainder = itertools.dropwhile(is_not_idat, self._chunks)
            for chunk in (chunk for chunk in remainder if is_not_idat(chunk)):
                self.write_chunk(f, chunk['type'], chunk['data'])

    def write_chunk(self, fileobj, type_, data):
        chunk_len = len(data)
        chunk_max_len = 2 ** 31 - 1
        multiple_chunk_type = ('IDAT', 'sPLT', 'iTXt', 'tEXt', 'zTXt')
        if chunk_len > chunk_max_len:
            if type_ in multiple_chunk_type:
                for i in xrange(0, chunk_len, chunk_max_len):
                    self.write_chunk(fileobj, type_, data[i:i+chunk_max_len])
                return
            else:
                raise PNGError
        chunk_len = struct.pack('!I', chunk_len)
        crc = zlib.crc32(data, zlib.crc32(type_))
        crc = struct.pack('!i', crc)
        chunk = ''.join((chunk_len, type_, data, crc))
        fileobj.write(chunk)

    def glitch(self):
        raise NotImplementedError


if __name__ == '__main__':
    import random
    import re
    import types
    def monkey_glitch(self):
        self.raw = re.sub(r'\w', '{0}'.format(random.randint(0, 15)), self.raw)
    png = PNG('lena.png')
    png.glitch = types.MethodType(monkey_glitch, png, PNG)
    png.glitch()
    png.write('glitch_lena.png')
