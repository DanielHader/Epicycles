from __future__ import division

from sys import argv
from PIL import Image

import colorsys
import wx
class TracePanel(wx.Panel):
    def __init__(self, parent, image):
        super(TracePanel, self).__init__(parent, size=(image.width * 2, image.height * 2))
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

        self.points = []

        self.image = wx.Image(image.width, image.height)
        self.image.SetData(image.convert('RGB').tobytes())
        self.bitmap = wx.Bitmap(self.image.Scale(image.width * 2, image.height * 2, wx.IMAGE_QUALITY_HIGH))

        self.coords = complex(image.width, image.height)
        self.scale = image.height * 2

    def OnSize(self, event):
        self.Refresh()

    def OnPaint(self, event):
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.bitmap, 0, 0)

        dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))
        dc.DrawLines(self.points)

        dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), width=1))
        dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
        for p in self.points:
            dc.DrawCircle(p, 2)


    def OnLeftClick(self, event):
        self.points.append(event.GetPosition())
        self.Refresh()

    def OnRightClick(self, event):
        if len(self.points) > 0:
            self.points.pop()
            self.Refresh()

    def OnClose(self):
        print 'Saving points to points.txt'
        with open('points.txt', 'w') as file:
            for p in self.points:
                z = complex(p.x, p.y)
                z = (z - self.coords) / self.scale
                file.write(str(z) + '\n')

class Frame(wx.Frame):
    def __init__(self, filename):
        super(Frame, self).__init__(None)
        self.SetTitle('Epicycles')
        self.SetClientSize((1000, 1270))
        self.Center()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        image = Image.open(filename)

        self.view = TracePanel(self, image)

    def OnClose(self, event):
        self.view.OnClose()
        self.Destroy()

def main():
    app = wx.App(False)
    frame = Frame(argv[1])
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
