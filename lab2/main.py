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


class FunctionView(wx.Frame):
    def __init__(self, parent, functions):
        """
        @param parent: parent widget
        @param functions: function collection to show
        """
        wx.Frame.__init__(self, parent, -1, "Lab 2", 
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.RESIZE_BORDER)
        # to create a panel and fill it with function descriptions
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(4, 20)
        sizer.SetRows(6)
        sizer.SetCols(3)
        # to create first block: function selector
        text = wx.StaticText(panel, -1, "Function")
        sizer.Add(text, wx.GBPosition(0, 0), wx.GBSpan(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        f_choice = wx.Choice(panel, choices=[str(f) for f in functions])
        sizer.Add(f_choice, wx.GBPosition(1, 0), wx.GBSpan(1, 3), flag=wx.EXPAND | wx.BOTTOM, border=10)
        # to create second block: arg input
        text = wx.StaticText(panel, -1, "Start")
        sizer.Add(text, wx.GBPosition(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        text = wx.StaticText(panel, -1, "End")
        sizer.Add(text, wx.GBPosition(2, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        text = wx.StaticText(panel, -1, "N. of Slices")
        sizer.Add(text, wx.GBPosition(2, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        # inputs itself
        start_input = wx.TextCtrl(panel, -1, style=wx.TE_CENTER)
        sizer.Add(start_input, wx.GBPosition(3, 0), flag=wx.EXPAND | wx.BOTTOM, border=10)
        end_input = wx.TextCtrl(panel, -1, style=wx.TE_CENTER)
        sizer.Add(end_input, wx.GBPosition(3, 1), flag=wx.EXPAND | wx.BOTTOM, border=10)
        slices_input = wx.TextCtrl(panel, -1, style=wx.TE_CENTER)
        sizer.Add(slices_input, wx.GBPosition(3, 2), flag=wx.EXPAND | wx.BOTTOM, border=10)
        # Output header
        text = wx.StaticText(panel, -1, "Output")
        sizer.Add(text, wx.GBPosition(4, 0), wx.GBSpan(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        submit_button = wx.Button(panel, -1, "⟳", size=wx.Size(40, 32))
        submit_button.SetCanFocus(False)
        sizer.Add(submit_button, wx.GBPosition(4, 2), flag=wx.ALIGN_RIGHT)
        # output body
        output = wx.TextCtrl(panel, -1, style=(wx.TE_MULTILINE | wx.TE_READONLY))
        output.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(output, wx.GBPosition(5, 0), wx.GBSpan(1, 3), flag=wx.EXPAND)
        # to finish the panel
        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableCol(2, 1)
        sizer.AddGrowableRow(5, 1)
        panel.SetSizer(sizer)
        panel.Layout()
        # to make the panel fill main window
        sizer = wx.BoxSizer()
        sizer.Add(panel, 1, wx.ALL | wx.EXPAND, 4)
        self.SetSizer(sizer)
        self.Layout()
        prefer_size = self.GetSize()
        self.SetMinSize(wx.Size(prefer_size.width + 56, prefer_size.height + 200))
        self.SetMaxSize(wx.Size(prefer_size.width * 7 // 5 + 56, prefer_size.height * 3 // 2 + 200))
        # back up some variables
        self.functions = functions
        self.f_choice = f_choice
        self.start_input = start_input
        self.end_input = end_input
        self.slices_input = slices_input
        self.submit_button = submit_button
        self.output = output
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
            print("Nothing was selected")
            return
        # get argument value and do some safety checks
        try:
            start = float(self.start_input.GetValue())
            end = float(self.end_input.GetValue())
            slices = int(self.slices_input.GetValue())
        except ValueError:
            print("Can not convert arguments to numbers")
            return
        # apply function to argument and describe it all in output field
        func = self.functions[f_choice_index]
        self.output.SetValue("  #  |           x    |           f(x)\n")
        cnt = 0
        for x, y in func.apply(start, end, slices):
            self.output.AppendText(f"{cnt:>4} | {x:>14.3f} | {y:>14.3f}\n")
            cnt += 1
        self.submit_button.Disable()
        pass

    def OnAnyInputChange(self, event):
        """
        Responds to any input change
        @param event: event to handle
        """
        self.submit_button.Enable()
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
            )
        ]
        # Create a view and show it
        self.view = FunctionView(None, self.functions)
        self.view.Show()
        return True


if __name__ == '__main__':
    app = FuctionViewerApp()
    app.MainLoop()
