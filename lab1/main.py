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

    def describe(self, arg):
        return f"f({arg}) = {self.func(arg)}"


class FunctionView(wx.Frame):
    def __init__(self, parent, functions):
        """
        @param parent: parent widget
        @param functions: function collection to show
        """
        wx.Frame.__init__(self, parent, -1, "Lab 1")
        # to create a panel and fill it with function descriptions
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(10, 10)
        sizer.SetRows(3)
        sizer.SetCols(3)
        # to create first row: function selector
        text = wx.StaticText(panel, -1, "Select a function:")
        sizer.Add(text, wx.GBPosition(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        f_choice = wx.Choice(panel, choices=[str(f) for f in functions])
        sizer.Add(f_choice, wx.GBPosition(0, 1), wx.GBSpan(1, 2), flag=wx.EXPAND)
        # to create second row: arg input
        text = wx.StaticText(panel, -1, "Arg value:")
        sizer.Add(text, wx.GBPosition(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        arg_input = wx.TextCtrl(panel, -1, size=wx.Size(192, 32))
        sizer.Add(arg_input, wx.GBPosition(1, 1), flag=wx.EXPAND)
        submit_button = wx.Button(panel, -1, "=", size=wx.Size(36, 32))
        submit_button.SetCanFocus(False)
        sizer.Add(submit_button, wx.GBPosition(1, 2), flag=wx.EXPAND)
        # to create third row: output
        output = wx.TextCtrl(panel, -1, style=(wx.TE_MULTILINE | wx.TE_READONLY))
        output.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(output, wx.GBPosition(2, 0), wx.GBSpan(1, 3), flag=wx.EXPAND)
        # to finish the panel
        sizer.AddGrowableCol(0, 6)
        sizer.AddGrowableCol(1, 3)
        sizer.AddGrowableCol(2, 1)
        sizer.AddGrowableRow(2, 1)
        panel.SetSizer(sizer)
        panel.Layout()
        # to make the panel fill main window
        sizer = wx.BoxSizer()
        sizer.Add(panel, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.Layout()
        preferred_size = self.GetSize()
        self.SetMinSize(wx.Size(preferred_size.width + 56, preferred_size.height + 100))
        self.SetMaxSize(wx.Size(preferred_size.width * 2, preferred_size.height * 2 + 100))
        # back up some variables
        self.counter = 0
        self.functions = functions
        self.f_choice = f_choice
        self.arg_input = arg_input
        self.submit_button = submit_button
        self.output = output
        # bind an event handler
        self.submit_button.Bind(wx.EVT_BUTTON, self.OnSubmitButtonClick)
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
        arg = 0
        try:
            arg = float(self.arg_input.GetValue())
        except ValueError:
            print("Can not convert argument to number")
            return
        # apply function to argument and describe it all in output field
        func = self.functions[f_choice_index]
        self.counter += 1
        self.output.AppendText(f"[{self.counter}]: {func}, {func.describe(arg)} \n")
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
