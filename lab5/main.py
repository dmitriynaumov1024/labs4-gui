import math
import re
import json 
from weasyprint import HTML
import wx
import wx.lib.dialogs as dialog

DEFAULT_COLOR = "#fe0101"
MIN_PLOT_SIZE = 10
MULTIPLE_MAIN_WINDOWS = True

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
            result.append([a, self.func(a)])
            a += step
        result.append([b, self.func(b)])
        return result

    def describe(self, arg):
        return f"f({arg}) = {self.func(arg)}"


class SinglePanelWindow(wx.Frame):
    def __init__(self, parent, title=""):
        wx.Frame.__init__(self, parent)
        self.SetTitle(title)

    def SetContent(self, content):
        sizer = wx.BoxSizer()
        sizer.Add(content, 1, wx.EXPAND | wx.ALL, 4)
        self.SetSizer(sizer)
        self.SetMinClientSize(content.GetMinSize())
        self.Layout()


class FPlot(wx.Panel):
    def __init__(self, parent): 
        wx.Panel.__init__(self, parent, -1)
        self.counter = 0
        self.zoom = 20
        self.series = []
        self.description = ""
        self.color = DEFAULT_COLOR
        self.plot = wx.Panel(self, -1)
        sizer = wx.GridBagSizer()
        sizer.SetRows(3)
        sizer.SetCols(3)
        sizer.AddGrowableRow(0, 1)
        sizer.AddGrowableRow(2, 1)
        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableCol(2, 1)
        sizer.Add(self.plot, wx.GBPosition(1, 1))
        self.text = wx.StaticText(self, -1, "")
        sizer.Add(self.text, wx.GBPosition(0, 1), flag = wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.Panel(self, -1, size=(1,1)), wx.GBPosition(2, 2), 
                  flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self.SetSizer(sizer)
        self.SetMinSize((600, 600))
        self.Layout()
        self.plot.SetBackgroundColour(wx.Colour(0xfbf8f5))
        self.plot.Bind(wx.EVT_PAINT, self.OnPaint)

    def SetData(self, series, description=""):
        self.series = series
        self.text.SetLabel(description)
        width = max(abs(int(series[-1][0]-series[0][0])), MIN_PLOT_SIZE) * self.zoom
        self.plot.SetInitialSize(wx.Size(width, width))
        self.plot.Refresh()

    def SetLineColor(self, color):
        if re.match(r"^#[0-9a-fA-F]{6}$", color):
            self.color = color
            self.plot.Refresh()

    def OnPaint(self, event):
        zoom = self.zoom
        self.counter += 1
        dc = wx.PaintDC(self.plot)

        if (len(self.series) < 2):
            return

        shifted = self.series[1::]
        shifted.append(shifted[-1])

        x_start = int(self.series[0][0]-MIN_PLOT_SIZE)

        width, height = self.plot.GetSize()
        origin = (width // 2 - int(self.series[0][0]+self.series[-1][0]) // 2 * zoom, height // 2)

        # draw grid
        dc.SetPen(wx.Pen("#e8e9ef"))
        for i in range(origin[0]+x_start*zoom, width, zoom):
            dc.DrawLine(i, 0, i, height)
        for i in range(zoom, height // 2, zoom):
            dc.DrawLine(0, origin[1] + i, width, origin[1] + i)
            dc.DrawLine(0, origin[1] - i, width, origin[1] - i)

        # draw coordinate axes
        dc.SetPen(wx.Pen("#494949"))
        dc.DrawLine(origin[0], 0, origin[0], height)
        dc.DrawLine(0, origin[1], width, origin[1])
        dc.DrawLine(origin[0]+zoom, origin[1]-zoom//5, origin[0]+zoom, origin[1]+zoom//5)
        dc.DrawText("0", origin[0]-10, origin[1]+zoom//6)
        dc.DrawText("1", origin[0]+zoom-4, origin[1]+zoom//5)
        dc.DrawText("x", width-12, origin[1]+zoom//5)
        dc.DrawText("y", origin[0]-10, 1)

        val_max = height 
        arg_max = width
        # draw function graph
        dc.SetPen(wx.Pen(self.color))
        for p1, p2 in zip(self.series, shifted):
            x1 = origin[0] + p1[0]*zoom
            y1 = origin[1] - p1[1]*zoom
            x2 = origin[0] + p2[0]*zoom
            y2 = origin[1] - p2[1]*zoom
            if x1 < arg_max and x1 > 0 and y1 < val_max and y1 > 0 \
                or x2 < arg_max and x2 > 0 and y2 < val_max and y2 > 0:
                dc.DrawLine(int(x1), int(y1), int(x2), int(y2))


class FTable(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, -1, style=(wx.TE_MULTILINE | wx.TE_READONLY))
        self.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.SetCanFocus(False)
        self.SetMinSize((250, 400))
        self.Layout()

    def SetData(self, series):
        cnt = 0
        self.SetValue("  #             x               f(x)\n")
        for x, y in series:
            self.AppendText(f"{cnt:>4}  {x:>14.3f}  {y:>15.3g}\n")
            cnt += 1


class FunctionView(wx.Panel):
    def __init__(self, parent, functions, onTableButton, onPlotButton):
        """
        @param parent: parent widget
        @param functions: function collection to show
        """
        wx.Panel.__init__(self, parent, -1)
        # to create a panel and fill it with function descriptions
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(4, 12)
        rows, cols = 7, 3
        sizer.SetRows(rows)
        sizer.SetCols(cols)
        for i in range(rows): sizer.AddGrowableRow(i, 1)
        for j in range(cols): sizer.AddGrowableCol(j, 1)
        # to create first block: function selector
        text = wx.StaticText(panel, -1, "Оберіть функцію")
        sizer.Add(text, wx.GBPosition(0, 0), wx.GBSpan(1, 2), flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP, border=30)
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
        # color of plot
        text = wx.StaticText(panel, -1, "Колір лінії графіка")
        sizer.Add(text, wx.GBPosition(4, 0), wx.GBSpan(1, 2), flag=wx.ALIGN_CENTER_VERTICAL)
        color_hex_input = wx.TextCtrl(panel, -1, style=wx.TE_CENTER)
        color_hex_input.SetValue(DEFAULT_COLOR)
        sizer.Add(color_hex_input, wx.GBPosition(4, 2), flag= wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        # submit buttons
        plot_button = wx.Button(panel, -1, "Графік")
        plot_button.SetCanFocus(False)
        sizer.Add(plot_button, wx.GBPosition(6, 0), flag=wx.EXPAND)
        table_button = wx.Button(panel, -1, "Таблиця")
        table_button.SetCanFocus(False)
        sizer.Add(table_button, wx.GBPosition(6, 1), flag=wx.EXPAND)
        pdf_button = wx.Button(panel, -1, ">> PDF")
        pdf_button.SetCanFocus(False)
        sizer.Add(pdf_button, wx.GBPosition(6, 2), flag=wx.EXPAND)
        # finish panel layout
        panel.SetSizer(sizer)
        panel.Layout()
        # to make the panel fill main window
        sizer = wx.BoxSizer()
        sizer.AddStretchSpacer()
        sizer.Add(panel, 1)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)
        self.SetMinSize(wx.Size(480, 480))
        self.Layout()
        # back up some variables
        self.functions = functions
        self.f_choice = f_choice
        self.start_input = start_input
        self.end_input = end_input
        self.slices_input = slices_input
        self.table_button = table_button
        self.plot_button = plot_button
        self.color_hex_input = color_hex_input
        # bind event handlers
        table_button.Bind(wx.EVT_BUTTON, lambda event: onTableButton(self.OnSubmit()))
        plot_button.Bind(wx.EVT_BUTTON, lambda event: onPlotButton(self.OnSubmit()))
        pdf_button.Bind(wx.EVT_BUTTON, lambda event: self.ToPdf())
        pass

    def OnSubmit(self):
        # get choice index and do some safety checks
        f_choice_index = self.f_choice.GetSelection()
        color = self.color_hex_input.GetValue()
        if f_choice_index == wx.NOT_FOUND:
            self.Error("Для початку оберіть функцію з переліку.")
            return ([], "", color)
        # get argument value and do some safety checks
        try:
            start = float(self.start_input.GetValue())
            end = float(self.end_input.GetValue())
            slices = int(self.slices_input.GetValue())
        except ValueError:
            self.Error("Не вдалося перетворити введені параметри в число. Спробуйте з іншими значеннями.")
            return ([], "", color)
        # apply function to argument and describe it all in output field
        try:
            func = self.functions[f_choice_index]
            series = func.apply(start, end, slices)
        except:
            self.Error("При обчисленні значень функції виникла помилка. Спробуйте задати інші значення.")
            return ([], "", color)
        return (series, str(func), color)

    def Error(self, message):
        print(message)
        pass

    def FromFile(self):
        try:
            filePath = dialog.openFileDialog().paths[0]
            f = open(filePath, "r")
            data = json.loads(f.read())
            f.close()
            self.f_choice.SetSelection(data["choice_index"])
            self.start_input.SetValue(data["start"])
            self.end_input.SetValue(data["end"])
            self.slices_input.SetValue(data["slices"])
            self.color_hex_input.SetValue(data["color"])
        except:
            print("[FunctionView.FromFile]: unknown error occured")

    def ToFile(self):
        try:
            filePath = dialog.saveFileDialog(wildcard="JSON format (*.json)|*.json").paths[0]
            f = open(filePath, "w+")
            data = ({
                "choice_index": self.f_choice.GetSelection(),
                "start": self.start_input.GetValue(),
                "end": self.end_input.GetValue(),
                "slices": self.slices_input.GetValue(),
                "color": self.color_hex_input.GetValue()
            })
            f.write(json.dumps(data)+"\n")
            f.close()
        except:
            print("[FunctionView.ToFile]: unknown error occured")

    def ToPdf(self):
        dialogResult = dialog.saveFileDialog(wildcard="Portable document (*.pdf)|*.pdf")
        if dialogResult.paths is None: return
        filePath = dialogResult.paths[0]

        series, description, color = self.OnSubmit()

        def oneTableRow(_tuple): 
            row, data = _tuple
            return f"<tr><td>{row}</td><td>{data[0]:.3f}</td><td>{data[1]:.3f}</td></tr>"

        htmlString = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Таблиця значень функції</title>
        <style>
        @page { size: a4; margin: 1.5cm; }
        body { font-family: sans-serif; font-size: 11pt; }
        table { border-collapse: collapse; }
        th, td { padding: 2pt 10pt; border: 0.5pt solid #454349; }
        tr:nth-child(2n+1) { background-color: #f8f5fb; }
        tr:first-child { background-color: #f2f1f7; }
        th { text-align: center; }
        td { text-align: right; }
        </style>
        </head>
        <body>
        <p>""" + description + """</p>
        <table>
        <tr><th></th><th>x</th><th>y</th></tr>
        """ + str.join("\n", map(oneTableRow, enumerate(series)))  + """
        </table>
        </body>
        </html>
        """
        HTML(string=htmlString, base_url="").write_pdf(filePath)


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
        self.plotCount = 0
        self.tableCount = 0
        self.mainWindowCount = 0
        self.AddFunctionView()
        return True

    def AddFunctionView(self):
        frame0 = SinglePanelWindow(None)
        frame0.SetTitle("Функція")
        frame0.Bind(wx.EVT_CLOSE, self.OnFunctionViewClosed)
        fselect = FunctionView(frame0, self.functions, self.AddTable, self.AddPlot)
        frame0.SetContent(fselect)
        frame0.Show()
        menubar = wx.MenuBar()
        windowMenu = wx.Menu(0)
        if MULTIPLE_MAIN_WINDOWS:
            newItem = windowMenu.Append(wx.ID_NEW, "Нове вікно", "Нове вікно")
            menubar.Bind(wx.EVT_MENU, lambda _: self.AddFunctionView(), newItem)
        openItem = windowMenu.Append(wx.ID_OPEN, "Відкрити", "Завантажити з існуючого файлу")
        menubar.Bind(wx.EVT_MENU, lambda _: fselect.FromFile(), openItem)
        saveItem = windowMenu.Append(wx.ID_SAVE, "Зберегти", "Зберегти параметри в файл")
        menubar.Bind(wx.EVT_MENU, lambda _: fselect.ToFile(), saveItem)
        menubar.Append(windowMenu, "Меню")
        frame0.SetMenuBar(menubar)
        self.mainWindowCount += 1

    def AddTable(self, data):
        self.tableCount += 1
        series, description, color = data
        frame1 = SinglePanelWindow(None)
        frame1.SetTitle(f"Таблиця {self.tableCount}")
        ftable = FTable(frame1)
        ftable.SetData(series)
        frame1.SetContent(ftable)
        frame1.Show()

    def AddPlot(self, data):
        self.plotCount += 1
        series, description, color = data
        frame2 = SinglePanelWindow(None)
        frame2.SetTitle(f"Графік {self.plotCount}")
        fplot = FPlot(frame2)
        fplot.SetData(series, description)
        fplot.SetLineColor(color)
        frame2.SetContent(fplot)
        frame2.Show()

    def OnFunctionViewClosed(self, event):
        self.mainWindowCount -= 1
        if self.mainWindowCount == 0:
            self.ExitMainLoop()
        event.Skip()


if __name__ == '__main__':
    app = FuctionViewerApp()
    app.MainLoop()
