import wx
import wx.adv
import datetime as dt

class SinglePanelWindow(wx.Frame):
    def __init__(self, parent, title=""):
        wx.Frame.__init__(self, parent)
        self.SetTitle(title)

    def SetContent(self, content):
        sizer = wx.BoxSizer()
        sizer.Add(content, 1, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(sizer)
        self.SetMinClientSize(content.GetMinSize())
        self.Layout()


TIMEOUT = False
FIXEDTIME = True
MODE_INDICATOR_TEXT = { 
    TIMEOUT: "Timeout (hh:mm:ss)", 
    FIXEDTIME: "Fixed time (hh:mm:ss)" 
}

class NotificationsView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.pending = []
        self.ready = []
        self.mode = TIMEOUT
        sizer = wx.GridBagSizer(8, 2)
        rows, cols = 5, 5
        sizer.SetRows(rows)
        sizer.SetCols(cols)
        sizer.AddGrowableRow(rows-1, 1)
        for j in range(cols): sizer.AddGrowableCol(j, 0)
        # mode indicator and switcher
        mode_indicator = wx.Button(self, -1, MODE_INDICATOR_TEXT[self.mode])
        mode_indicator.Bind(wx.EVT_BUTTON, lambda _: self.on_mode_indicator())
        sizer.Add(mode_indicator, wx.GBPosition(0, 0), wx.GBSpan(1, 3), flag=wx.EXPAND)
        # Time picker
        time_input = wx.adv.TimePickerCtrl(self, -1)
        time_input.SetTime(0, 0, 10) 
        sizer.Add(time_input, wx.GBPosition(0, 3), wx.GBSpan(1, 2), flag=wx.EXPAND)
        # Text input
        text = wx.StaticText(self, -1, "Message")
        sizer.Add(text, wx.GBPosition(1, 0), wx.GBSpan(1, 3), flag=wx.TOP | wx.LEFT | wx.EXPAND, border=6)
        text_input = wx.TextCtrl(self, -1)
        text_input.SetMinSize((314,-1))
        sizer.Add(text_input, wx.GBPosition(2, 0), wx.GBSpan(1, 4), flag=wx.EXPAND)
        # submit button
        submit_button = wx.Button(self, -1, "✓")
        submit_button.Bind(wx.EVT_BUTTON, lambda _: self.add_notification())
        sizer.Add(submit_button, wx.GBPosition(2, 4), flag=wx.EXPAND)
        # Output
        text = wx.StaticText(self, -1, "Notifications")
        sizer.Add(text, wx.GBPosition(3, 0), wx.GBSpan(1, 3), flag=wx.TOP | wx.LEFT | wx.EXPAND, border=6)
        output = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        output.SetFont(wx.Font(11, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(output, wx.GBPosition(4, 0), wx.GBSpan(1, 5), flag=wx.EXPAND)
        # Remember widgets
        self.mode_indicator = mode_indicator
        self.time_input = time_input
        self.text_input = text_input
        self.submit_button = submit_button
        self.output = output
        # Timer
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, lambda _: self.every_second())
        self.timer.Start(500)
        # Layout
        self.SetSizer(sizer)
        self.SetMinSize((480, 560))
        self.Layout()
        self.Fit()

    def on_mode_indicator(self):
        self.mode = not self.mode 
        self.mode_indicator.SetLabel(MODE_INDICATOR_TEXT[self.mode])
        if self.mode == FIXEDTIME:
            now = dt.datetime.now()
            self.time_input.SetTime(now.hour, now.minute, now.second)
        else:
            self.time_input.SetTime(0, 0, 10)
        pass

    def add_notification(self):
        time_input_val = self.time_input.GetTime() 
        if self.mode == TIMEOUT:
            time = dt.datetime.now() + dt.timedelta(hours=time_input_val[0], 
                minutes=time_input_val[1], seconds=time_input_val[2]) - dt.timedelta(seconds=1)
        else:
            time = dt.datetime.combine(dt.datetime.now(), 
                dt.time(time_input_val[0], time_input_val[1], time_input_val[2]))
        message = self.text_input.GetValue()
        self.text_input.SetValue("")
        self.pending.append((time, message))
        pass

    def every_second(self):
        now = dt.datetime.now()
        def is_ready(item):
            time, message = item
            return now >= time
        for time, message in filter(is_ready, self.pending):
            # self.output.AppendText(f"─ [{time.hour:02}:{time.minute:02}:{time.second:02}] ────────────────────────────────\n{message}\n\n")
            self.output.AppendText(f"[{time.hour:02}:{time.minute:02}:{time.second:02}] {message}\n\n")
        self.pending = [item for item in filter(lambda i: not is_ready(i), self.pending)]


def main():
    def on_exit(event, nv):
        nv.timer.Stop()
        event.Skip()

    app = wx.App()
    frame = SinglePanelWindow(None, "Timed notifications")
    nv = NotificationsView(frame)
    frame.SetContent(nv)
    frame.Bind(wx.EVT_CLOSE, lambda event: on_exit(event, nv))
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
