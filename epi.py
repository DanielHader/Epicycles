from __future__ import division

from sys import argv

import colorsys
import wx

import numpy as np

import imageio
import os

from math import pi, sqrt
from cmath import exp

def zig_zag(n):
    for i in range(n // 2):
        yield i
        yield -i
    if n % 2 == 1:
        yield n//2

class CyclePanel(wx.Panel):
    def __init__(self, parent, points, precision):
        super(CyclePanel, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetBackgroundColour((0, 0, 0))

        self.precision = precision
        self.maxScale = 1.4
        self.scale = complex(self.maxScale, self.maxScale)
        self.size = complex(0, 0)
        self.window = (0, 0)

        self.points = points
        self.amplitudes = []
        self.path = []
        self.frequencies = []

        self.colors = []
        self.pens = []
        self.brushes = []
        self.pathPen = wx.Pen(wx.Colour('white'), 2)

        self.tick = 0
        self.time = 0

        self.InitializeAmplitudes()
        self.InitializePath()
        self.InitializeColors()

    def OnSize(self, event):
        size = event.GetSize()
        self.window = size
        self.size = complex(size[0], size[1])
        self.scale = complex(self.maxScale, self.maxScale * size[1] / size[0])
        self.InitializePath()
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        self.DrawCycles(dc, self.time)
        self.DrawPath(dc, self.tick)

    def InitializeAmplitudes(self):
        self.amplitudes = np.fft.fft(self.points)
        self.frequencies = np.fft.fftfreq(len(self.points))

    def InitializePath(self):
        self.path = []
        n = len(self.amplitudes)
        for t in range(self.precision + 1):
            time = t / self.precision * len(self.points)
            z = complex(0, 0)
            for i in zig_zag(len(self.points)):
                a = self.amplitudes[i]
                f = self.frequencies[i]
                z += a * exp(2j * pi * f * time) / n
            x, y = self.Coords(z)
            self.path.append(wx.Point(x, y))

    def InitializeColors(self):
        n = len(self.points)
        for i in range(n):
            r, g, b = colorsys.hls_to_rgb(sqrt(i / n), 0.5, 0.5)
            color = wx.Colour(int(r * 255), int(g * 255), int(b * 255))
            self.colors.append(color)

    def Coords(self, z):
        tz = (z + self.scale / 2) / (self.scale) * self.size
        return tz.real, tz.imag

    def DrawCircle(self, dc, z, r, color):
        x, y = self.Coords(z)
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawCircle(x, y, r / self.scale.real * self.size.real)

    def DrawDot(self, dc, z, color):
        x, y = self.Coords(z)
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.Brush(color))
        dc.DrawCircle(x, y, 2)

    def DrawCycles(self, dc, time):
        z = complex(0, 0)
        n = len(self.amplitudes)
        c = 0
        for i in zig_zag(len(self.points)):
            a = self.amplitudes[i]
            f = self.frequencies[i]
            color = self.colors[c]
            self.DrawCircle(dc, z, abs(a) / n, color)
            z += a * exp(2j * pi * f * time) / n
            self.DrawDot(dc, z, color)
            c += 1

    def DrawPath(self, dc, tick):
        dc.SetPen(self.pathPen)
        dc.DrawLines(self.path[:tick+1])

    def Scroll(self, tick, time):
        self.tick = tick
        self.time = time
        self.Refresh()

    def SaveGif(self):
        print "Saving Gif..."
        for i in range(self.precision + 2):
            time = i / self.precision * len(self.points)
            print "Creating frame " + str(i) + " out of " + str(self.precision + 1) + ", time=" + str(time)
            bmp = wx.Bitmap(self.window.width, self.window.height)
            dc = wx.MemoryDC()
            dc.SelectObject(bmp)
            dc.SetBackground(wx.Brush(wx.Colour('black')))
            dc.Clear()
            if i < self.precision + 1:
                self.DrawCycles(dc, time)
            self.DrawPath(dc, i)
            dc.SelectObject(wx.NullBitmap)
            img = bmp.ConvertToImage()
            img.SaveFile('saved/frame'+str(i)+'.png', wx.BITMAP_TYPE_PNG)
        images = []
        for i in range(self.precision + 2):
            filename = 'saved/frame' + str(i) + '.png'
            images.append(imageio.imread(filename))
        print "Making gif from " + str(len(images)) + " frames"
        images += [images[-1]] * 49
        imageio.mimwrite('saved/epicycle.gif', images, fps=30)
        print "Done"



class Frame(wx.Frame):
    def __init__(self, points):
        super(Frame, self).__init__(None)
        self.SetTitle('Epicycles')
        self.SetClientSize((1200, 1200))
        self.Center()

        self.precision = 1000
        self.points = points

        self.view = CyclePanel(self, points, self.precision)
        self.slider = wx.Slider(self, value=0, minValue=0, maxValue=self.precision)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view, -1, wx.EXPAND | wx.ALL, border = 10)
        sizer.Add(self.slider, 0, wx.EXPAND | wx.ALL, border = 10)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_SCROLL, self.OnScroll)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.view.Bind(wx.EVT_CHAR, self.OnChar)
        self.slider.Bind(wx.EVT_CHAR, self.OnChar)


        self.SetFocus()

    def OnChar(self, event):
        print event.GetKeyCode()
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE:
            self.view.SaveGif()

    def OnScroll(self, event):
        tick = event.GetPosition()
        self.view.Scroll(tick, tick / self.precision * len(self.points))

def main(points):
    app = wx.App(False)
    frame = Frame(points)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    points = []
    with open(argv[1]) as file:
        for line in file:
            z = eval(line.strip())
            points.append(z)
    main(points)
