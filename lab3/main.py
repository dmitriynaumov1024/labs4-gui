import math
import wx

class Function:
    def __init__(self, func, text):
        """
        @param func: delegate of type (double) -> double
        @param text: string
        """
        self.func = func
        self.text = "f(x) = " + text
        pass

    def __repr__(self):
        return self.text

    def apply(self, arg):
        return self.func(arg)

    def apply(self, start, end, slices):
        """
        Apply this function to several arg values on given interval
        and return list of arg-value pairs
        """
        a = min(start, end)
        b = max(start, end)
        step = (b - a) / slices
        result = []
        for i in range(slices):
            result.append((a, self.func(a)))
            a += step
        result.append((b, self.func(b)))
        return result

    def describe(self, arg):
        return f"f({arg}) = {self.func(arg)}"


class Plot(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, size=(600, 600))
        self.width = 600
        self.height = 600
        self.SetBackgroundColour(wx.Colour(0xffffff))
        self.series = []
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def SetData(self, series):
        self.series = series

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        if (len(self.series) < 2):
            return
        shifted = self.series[1::]
        shifted.append(shifted[-1])
        origin = (self.width // 2, self.height // 2)
        zoom = 10
        dc.SetPen(wx.Pen("#494949"))
        dc.DrawLine(origin[0], 0, origin[0], self.height)
        dc.DrawLine(0, origin[1], self.width, origin[1])
        dc.SetPen(wx.Pen("#e0e0e0"))
        for i in range(zoom, self.width // 2, zoom):
            dc.DrawLine(origin[0] + i, 0, origin[0] + i, self.height)
            dc.DrawLine(origin[0] - i, 0, origin[0] - i, self.height)
        for i in range(zoom, self.height // 2, zoom):
            dc.DrawLine(0, origin[1] + i, self.width, origin[1] + i)
            dc.DrawLine(0, origin[1] - i, self.width, origin[1] - i)
        val_max = self.height 
        arg_max = self.width
        dc.SetPen(wx.Pen("#991111"))
        for p1, p2 in zip(self.series, shifted):
            x1 = origin[0] + p1[0]*zoom
            y1 = origin[1] - p1[1]*zoom
            x2 = origin[0] + p2[0]*zoom
            y2 = origin[1] - p2[1]*zoom
            if x1 < arg_max and x1 > 0 and y1 < val_max and y1 > 0 \
                or x2 < arg_max and x2 > 0 and y2 < val_max and y2 > 0:
                dc.DrawLine(int(x1), int(y1), int(x2), int(y2))


class FunctionView(wx.Frame):
    def __init__(self, parent, functions):
        """
        @param parent: parent widget
        @param functions: function collection to show
        """
        wx.Frame.__init__(self, parent, -1, "Lab 3", 
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.RESIZE_BORDER)
        self.SetBackgroundColour(wx.Colour(0xf3f3f3))
        # to create a panel and fill it with function descriptions
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(4, 20)
        sizer.SetRows(6)
        sizer.SetCols(4)
        # to create first block: function selector
        text = wx.StaticText(panel, -1, "Оберіть функцію")
        sizer.Add(text, wx.GBPosition(0, 0), wx.GBSpan(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        f_choice = wx.Choice(panel, choices=[str(f) for f in functions])
        sizer.Add(f_choice, wx.GBPosition(1, 0), wx.GBSpan(1, 3), flag=wx.EXPAND | wx.BOTTOM, border=10)
        # to create second block: arg input
        text = wx.StaticText(panel, -1, "Початок")
        sizer.Add(text, wx.GBPosition(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        text = wx.StaticText(panel, -1, "Кінець")
        sizer.Add(text, wx.GBPosition(2, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        text = wx.StaticText(panel, -1, "К-ть відрізків")
        sizer.Add(text, wx.GBPosition(2, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        # inputs itself
        start_input = wx.TextCtrl(panel, -1, style=wx.TE_CENTER)
        sizer.Add(start_input, wx.GBPosition(3, 0), flag=wx.EXPAND | wx.BOTTOM, border=10)
        end_input = wx.TextCtrl(panel, -1, style=wx.TE_CENTER)
        sizer.Add(end_input, wx.GBPosition(3, 1), flag=wx.EXPAND | wx.BOTTOM, border=10)
        slices_input = wx.TextCtrl(panel, -1, style=wx.TE_CENTER)
        sizer.Add(slices_input, wx.GBPosition(3, 2), flag=wx.EXPAND | wx.BOTTOM, border=10)
        # Output header
        text = wx.StaticText(panel, -1, "Таблиця значень")
        sizer.Add(text, wx.GBPosition(4, 0), wx.GBSpan(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        submit_button = wx.Button(panel, -1, "⟳", size=wx.Size(40, 32))
        submit_button.SetCanFocus(False)
        sizer.Add(submit_button, wx.GBPosition(4, 2), flag=wx.ALIGN_RIGHT)
        # output table
        table_output = wx.TextCtrl(panel, -1, style=(wx.TE_MULTILINE | wx.TE_READONLY))
        table_output.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(table_output, wx.GBPosition(5, 0), wx.GBSpan(1, 3), flag=wx.EXPAND)
        # plot
        text = wx.StaticText(panel, -1, "Графік функції")
        sizer.Add(text, wx.GBPosition(0, 3), flag=wx.ALIGN_CENTER_VERTICAL)
        plot_output = Plot(panel)
        sizer.Add(plot_output, wx.GBPosition(1, 3), wx.GBSpan(5, 1))
        sizer.AddGrowableRow(5, 1)
        # to finish the panel
        # sizer.AddGrowableCol(3, 1)
        # sizer.AddGrowableRow(5, 1)
        panel.SetSizer(sizer)
        panel.Fit()
        # to make the panel fill main window
        sizer = wx.BoxSizer()
        sizer.Add(panel, 1, wx.ALL | wx.EXPAND, 4)
        self.SetSizer(sizer)
        self.Fit()
        prefer_size = self.GetSize()
        self.SetMinSize(wx.Size(prefer_size.width + 52, prefer_size.height + 156))
        self.SetMaxSize(wx.Size(prefer_size.width + 52, prefer_size.height + 156))
        # back up some variables
        self.functions = functions
        self.f_choice = f_choice
        self.start_input = start_input
        self.end_input = end_input
        self.slices_input = slices_input
        self.submit_button = submit_button
        self.table_output = table_output
        self.plot_output = plot_output
        # bind event handlers
        submit_button.Bind(wx.EVT_BUTTON, self.OnSubmitButtonClick)
        f_choice.Bind(wx.EVT_CHOICE, self.OnAnyInputChange)
        start_input.Bind(wx.EVT_TEXT, self.OnAnyInputChange)
        end_input.Bind(wx.EVT_TEXT, self.OnAnyInputChange)
        slices_input.Bind(wx.EVT_TEXT, self.OnAnyInputChange)
        pass

    def OnSubmitButtonClick(self, event):
        """
        Handler for submit button click event
        @param event: event to handle
        """
        # get choice index and do some safety checks
        f_choice_index = self.f_choice.GetSelection()
        if f_choice_index == wx.NOT_FOUND:
            self.Error("Для початку оберіть функцію з переліку.")
            return
        # get argument value and do some safety checks
        try:
            start = float(self.start_input.GetValue())
            end = float(self.end_input.GetValue())
            slices = int(self.slices_input.GetValue())
        except ValueError:
            self.Error("Не вдалося перетворити введені параметри в число. Спробуйте з іншими значеннями.")
            return
        # apply function to argument and describe it all in output field
        try:
            func = self.functions[f_choice_index]
            series = func.apply(start, end, slices)
        except:
            self.Error("При обчисленні значень функції виникла помилка. Спробуйте задати інші значення.")
            return
        self.FillTable(series)
        self.DrawPlot(series)
        self.submit_button.Disable()
        pass

    def OnAnyInputChange(self, event):
        """
        Responds to any input change
        @param event: event to handle
        """
        self.submit_button.Enable()
        pass

    def Error(self, message):
        self.table_output.SetValue(message)
        pass

    def FillTable(self, series):
        cnt = 0
        self.table_output.SetValue("  #  |           x    |           f(x)\n")
        for x, y in series:
            self.table_output.AppendText(f"{cnt:>4} | {x:>14.3f} | {y:>15.3g}\n")
            cnt += 1
        pass

    def DrawPlot(self, series):
        self.plot_output.SetData(series)
        self.plot_output.Refresh()
        pass


class FuctionViewerApp(wx.App):
    def OnInit(self):
        # Functions are created here
        self.functions = [
            Function (
                lambda x: math.pow(10, 1+x*x) - math.pow(10, 1-x*x), 
                "10^(1+x^2) - 10^(1-x^2)"
            ),
            Function (
                lambda x: math.tan(3*x-156) + math.tan(x) - 4*math.sin(x), 
                "tg(3x-156) + tg(x) - 4sin(x)"
            ),
            Function (
                lambda x: math.sin(x) + math.exp(x/9),
                "sin(x) + exp(x/9)"
            )
        ]
        # Create a view and show it
        self.view = FunctionView(None, self.functions)
        self.view.Show()
        return True


if __name__ == '__main__':
    app = FuctionViewerApp()
    app.MainLoop()
