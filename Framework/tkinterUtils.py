#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, collections, threading, obbinstall
from os.path import *
from tkinter import *
from tkinter import ttk
from tkinter.font import *

import Framework.common as common, uuid
from Framework.ext.tablelist.tablelist import *

def getPrettyValue(val):
    if isinstance(val, float):
        if int(val) == val:
            return int(val)
    return val

def displayDefaultLabel(obj, field, frame, row, col):
    val = field.getValue(obj)
    widget = Label(frame, text=val)
    return widget

def setEnabledState(widget, state):
    if isinstance(state, bool):
        state = DISABLED if not state else NORMAL
    try:
        widget.configure(state=state)
    except:
        pass
    for childName in widget.children:
        child = widget.children[childName]
        try:
            setEnabledState(child, state)
        except:
            pass

def setWindowSize(window, w=-1, h=-1):
    window.update()
    if w <= 0: w = window.winfo_width()
    if h <= 0: h = window.winfo_height()
    window.geometry("%dx%d+%d+%d" % (w, h, window.winfo_x(), window.winfo_y()))

def centerWindow(window):
    window.update()
    w = window.winfo_width()
    h = window.winfo_height()
    x = int((window.winfo_screenwidth() - w) / 2 + window.winfo_rootx())
    y = int((window.winfo_screenheight() - h) / 2 + window.winfo_rooty())
    window.geometry("%dx%d+%d+%d" % (w, h, x, y))

def setFullScreen(window, state):
    # self.master.attributes('-zoomed', True)
    if window.master:
        window = window.master
    w, h = window.winfo_width(), window.winfo_height()
    fullWidth, fullHeight = window.winfo_screenwidth(), window.winfo_screenheight()
    if state and (w != fullWidth or h != fullHeight):
        window.width = w
        window.height = h
        # self.master.overrideredirect(True)
        # self.master.geometry("%dx%d" % (fullWidth, fullHeight))
        # self.master.bind('<Escape>', lambda event: self.fullScreen(False))
        window.state("zoomed")
    elif not state and w == fullWidth and h == fullHeight:
        window.overrideredirect(False)
        window.geometry("%dx%d+0+0" % (window.width, window.height))
        
def dropDownButton(button, menuDetails):
    
    def showDropDown():
        dropDownMenu = Menu(button.master, tearoff=0)
        for nameAndCb in menuDetails:
            dropDownMenu.add_command(label=nameAndCb[0], command=nameAndCb[1])
        dropDownMenu.post(button.winfo_rootx() + int(button.winfo_width() / 2), button.winfo_rooty() + button.winfo_height())
    button.configure(command=showDropDown)
    return button

def dropDownButtonOrDefault(button, menuDetails, defaultChoice, dropDownEnabled=True):
    if dropDownEnabled:
        button = dropDownButton(button, menuDetails)
    else:
        for d in menuDetails:
            if d[0] == defaultChoice:
                button.configure(command=d[1])
    return button

class FieldDisplay():
    def __init__(self, fieldName, propertyName=None, viewFn=getPrettyValue, displayFn=displayDefaultLabel, displayed=True):
        self.fieldName = fieldName
        self.propertyName = propertyName
        self.viewFn = viewFn
        self.displayFn = displayFn
        self.displayed = displayed

    def display(self, obj, frame, row, col):
        widget = self.displayFn(obj, self, frame, row, col)
        return widget
            
    def getValue(self, obj):
        if self.propertyName:
            val = obj.__dict__[self.propertyName]
        else:
            val = obj
        if self.viewFn:
            return self.viewFn(val)
        return val

class Table(Frame):
    def __init__(self, frame, fields=[], scrollable=True):
        Frame.__init__(self, frame)
        if scrollable:
            self.canvas = Canvas(frame, borderwidth=0)
            self.frame = Frame(self.canvas)
            self.vsb = Scrollbar(frame, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vsb.set)

            self.vsb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)
            self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")

            # Reset the scroll region to encompass the inner frame
            def onFrameConfigure(event):
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.frame.bind("<Configure>", onFrameConfigure)

            # Bind mouse wheel
            def mouse_wheel(event):
                count = 0
                if event.num == 5 or event.delta == -120:
                    count -= 1
                if event.num == 4 or event.delta == 120:
                    count += 1
                self.canvas.yview_scroll(-count, "units")
            if common.isWindowsOS():
                self.frame.bind("<MouseWheel>", mouse_wheel)
            else:
                self.frame.bind("<Button-4>", mouse_wheel)
                self.frame.bind("<Button-5>", mouse_wheel)
        else:
            self.frame = frame

        self.fields = fields
        self.data = None
        self.filterFn = None
        self.filteredData = None

    def bind(self, data):
        self.data = data
        self.refreshAll()

    def refreshColumnsView(self, fields=None):
        if not fields:  fields = self.getFilteredColumns()
        for j, val in enumerate(fields):
            w = Label(self.frame, text=val.fieldName)
            w.grid(row=0, column=j)
            setFontProperty(w, "weight", "bold")

    def refreshAll(self):
        fields = self.getFilteredColumns()
        self.refreshColumnsView()
        data = self.getDisplayedData()
        for i, obj in enumerate(data):
            self.refreshLine(i, fields)

    def refresh(self, obj):
        line = self.getObjectLine(obj)
        if line >= 0:
            refreshLine(self, line)

    def refreshLine(self, lineIdx, fields=None):
        if not fields:  fields = self.getFilteredColumns()
        data = self.getDisplayedData()
        if lineIdx >= 0 and lineIdx < len(data):
            obj = data[lineIdx]
            for j, field in enumerate(fields):
                widget = field.display(obj, self.frame, lineIdx+1, j)
                widget.grid(row=lineIdx+1, column=j, sticky=W)


    def getObjectLine(self, obj):
        if isinstance(self.filteredData, list) and obj in self.filteredData:
            return self.filteredData.index(obj)
        elif isinstance(self.data, list) and obj in self.data:
            return self.data.index(obj)
        return -1

    def getDisplayedData(self):
        return self.data if not self.filteredData else self.filteredData

    def getFilteredColumns(self):
        return [x for x in self.fields if x.displayed]

def displayLink(obj, field, frame, row, col):
    widget = displayDefaultLabel(obj, field, frame, row, col)
    url = widget.cget("text")
    setLink(widget, url, "Link")
    return widget

def setLink(label, url, text=None):
    label.config(foreground='blue')
    if text:
        label.config(text=text)
    setFontProperty(label, "underline", 1)
    def openHLink(event):
        webbrowser.open_new_tab(url)
    label.bind("<Button-1>", openHLink)

def setFontProperty(widget, propertyName, val):
    font = Font(widget, widget.cget("font"))
    font[propertyName] = val
    widget.config(font=font)

def removeWidgetContent(widget):
    for child in widget.winfo_children():
        child.destroy()
    # widget.pack_forget()
    # widget.grid_forget()

def getRightClickEvent():
    if common.isMacOS():    return "<Button-2>"
    else:                   return "<Button-3>"

def getDoubleClickEvent():
    return "<Double-Button-1>"

class ColumnDef():
    def __init__(self, name="", getValueFn=None, getStyleFn=None, id=None, width=0, anchor=W):
        """
        :param name: Name of the column
        :param getValueFn: Function with one argument being the displayed entry. Return custom the value to be displayed
        :param getStyleFn: Function with one argument being the displayed entry. Return None or a config dict. Ex: {"bg": "#FFAAAA"}
        :param id:
        :param width:
        :param anchor:
        """
        self.name = name
        self.id = id
        self.anchor = anchor
        self.width = width
        if getValueFn == None:              self.getValueFn = lambda entry: entry               # Same value, usefull for dict keys
        elif isinstance(getValueFn, str):   self.getValueFn = lambda entry: entry[getValueFn]   # Dict
        elif isinstance(getValueFn, int):   self.getValueFn = lambda entry: entry[getValueFn]   # List
        else:                               self.getValueFn = getValueFn
        self.getStyleFn = getStyleFn

def displayTableList(frame, entries, columnDefs, itemClickedFn=None, selectmode="multiple", selecttype="row", **kargs):
    """
    :param frame:
    :param entries: Some iterable content
    :param columnDefs:
    :param itemClickedFn:
    :param multipleSelection:
    :return:
    For further documentation:
    http://docs.activestate.com/activetcl/8.6/tablelist/tablelistWidget.html
    """
    displayedColumns = []
    for col in columnDefs:
        displayedColumns.append(col.width)
        displayedColumns.append(col.name)
    displayedColumns = tuple(displayedColumns)

    kargs["columns"] = displayedColumns
    kargs["stretch"] = "all"
    kargs["width"] = 50
    kargs["setfocus"] = 1
    kargs["activestyle"] = "none"
    kargs["takefocus"] = 0
    kargs["selectmode"] = selectmode
    kargs["selecttype"] = selecttype
    tl = ScrolledTableList(frame, **kargs)
    tl.pack(fill=BOTH, expand=1)
    tl.entries = entries

    if len(entries) == 0:
        return tl

    def sortbycolumn(table, col):
        """alternate increasing and decreasing order sorts """
        order = "-increasing"
        if tl.sortcolumn() == int(col) and tl.sortorder() == "increasing":
            order = "-decreasing"
        tl.sortbycolumn(col, order)
    tl.configure(labelcommand=sortbycolumn)

    # Ensure column with numbers will be sorted by number instead of string
    for i, col in enumerate(columnDefs):
        # Test only first row
        for key in entries:
            sampleRes = col.getValueFn(key)
            if isinstance(sampleRes, int):
                tl.columnconfigure(i, sortmode="real")
            elif isinstance(sampleRes, str):
                tl.columnconfigure(i, sortmode="asciinocase")
            alignDict = {"w": "left", "center": "center", "e": "right"}
            anchor = col.anchor.lower()
            if anchor in alignDict: tl.columnconfigure(i, align=alignDict[anchor])
            else:                   tl.columnconfigure(i, align=anchor)
            break

    for e in entries:
        values = [col.getValueFn(e) for col in columnDefs]
        tl.insert("end", tuple(values))

    if itemClickedFn:
        tl.tablelist.bind('<<ListboxSelect>>', itemClickedFn)

    for i, col in enumerate(columnDefs):
        if not col.getStyleFn:
            continue
        for j, key in enumerate(entries):
            style = col.getStyleFn(key)
            if style:
                cellIndex = tl.cellindex("%s,%s" % (j, i))
                tl.cellconfigure(cellIndex, style)

    return tl

def getTableListColumns(tl):
    return [tl.columncget(i, "title") for i in range(tl.columncount())]

def getTreeListSelection(tl):
    selecttype =tl.cget("-selecttype")
    if str(selecttype) == "row":
        clickedRows = tl.curselection()
        if not clickedRows or clickedRows == "":
            return []
        res = []
        for x in clickedRows:
            ID = int(tl.getkeys(x))
            res.append(ID)
        if isinstance(tl.entries, dict):
            keys = list(tl.entries.keys())
            res = [keys[x] for x in res]
        return res
    else:
        clickedCells = tl.curcellselection()
        if not clickedCells or clickedCells == "":
            return []
        return clickedCells

def JSONTree(Tree, Parent, item):
    if isinstance(item, dict):
        for key in item :
            uid = uuid.uuid4()
            if isinstance(item[key], dict):
                Tree.insert(Parent, 'end', uid, text=key)
                JSONTree(Tree, uid, item[key])
            elif isinstance(item[key], list):
                Tree.insert(Parent, 'end', uid, text=key + '[]')
                JSONTree(Tree,
                         uid,
                         dict([(i, x) for i, x in enumerate(item[key])]))
            else:
                value = item[key]
                if isinstance(value, str):
                    value = value.replace(' ', '_')
                if value != None:
                    Tree.insert(Parent, 'end', uid, text=key, values=value)
                else:
                    Tree.insert(Parent, 'end', uid, text=key)
    elif isinstance(item, list):
        itemsDict = collections.OrderedDict()
        for i, x in enumerate(item):
            itemsDict[i] = x
        JSONTree(Tree, Parent, itemsDict)
    else:
        JSONTree(Tree, Parent, {item, item})


def displayObjectTree(frame, obj):
    tree = ttk.Treeview(frame, columns=('Values'))
    tree.column('Values', width=100, anchor='w')
    tree.heading('Values', text='Values')
    JSONTree(tree, '', obj)
    return tree

def updateTableListCell(tl, rowIdx, columnName, text):
    columns = getTableListColumns(tl)
    if columnName not in columns:
        return
    cellindex = tl.cellindex("{},{}".format(rowIdx, columns.index(columnName)))
    tl.cellconfigure(cellindex, text=text)

def updateTableListCellStyle(tl, rowIdx, column, style):
    if isinstance(column, str):
        columns = getTableListColumns(tl)
        if column not in columns:
            return
        column = columns.index(column)
    cellindex = tl.cellindex("{},{}".format(rowIdx, column))
    tl.cellconfigure(cellindex, cnf=style)
    
def useCheckboxEditor(tl, column, getStatusFn, setStatusFn):
    dataDir = join(dirname(__file__), "ext", "tablelist", "demos")
    # Very important: checkbox images cannot be kept only as local variables, else they will be deleted
    if not hasattr(tl, "imgChecked"):
        tl.imgChecked = PhotoImage(file=join(dataDir, "checked.gif"))
    if not hasattr(tl, "imgUnchecked"):
        tl.imgUnchecked = PhotoImage(file=join(dataDir, "unchecked.gif"))

    tl.columnconfigure(column, editable=YES)

    def getCheckboxState(isChecked):
        if isChecked:   return {"image": tl.imgChecked}
        else:           return {"image": tl.imgUnchecked}

    def onEditStarted(table, row, col, text):
        row, col = int(row), int(col)
        if col == 0:
            isChecked = getStatusFn(tl.entries[row])
            isChecked = not isChecked
            setStatusFn(tl.entries[row], isChecked)

            style = getCheckboxState(isChecked)
            updateTableListCellStyle(tl, row, col, style)

            t = threading.Timer(0.0001, lambda: tl.finishediting())
            t.start()
            return ""

    tl.configure(editstartcommand=onEditStarted)

    for row in range(len(tl.entries)):
        isChecked = getStatusFn(tl.entries[row])
        style = getCheckboxState(isChecked)
        updateTableListCellStyle(tl, row, column, style)

# def displayObjectTree(frame, obj):
#     selectMode = "extended" if multipleSelection else "single"
#     tl = ScrolledTableList(frame,
#         columns = (0, "Path", 0, "Value"),
#         stretch = "all",
#         width = 50,
#         setfocus = 1,
#         activestyle = "none",
#         takefocus = 0,
#         selectmode = selectMode,
#     )
#     tl.pack(fill=BOTH, expand=1)
#
#     def sortbycolumn(table, col):
#         """alternate increasing and decreasing order sorts """
#         order = "-increasing"
#         if tl.sortcolumn() == int(col) and tl.sortorder() == "increasing":
#             order = "-decreasing"
#         tl.sortbycolumn(col, order)
#     tl.configure(labelcommand=sortbycolumn)
#
#     # Ensure column with numbers will be sorted by number instead of string
#     for col in range(len(columnDefs)):
#         # Test only first row
#         for key in entries:
#             sampleRes = columnDefs[col].getValueFn(key)
#             if isinstance(sampleRes, int):
#                 tl.columnconfigure(col, sortmode="real")
#             elif isinstance(sampleRes, str):
#                 tl.columnconfigure(col, sortmode="asciinocase")
#             break
#
#     for e in entries:
#         values = [col.getValueFn(e) for col in columnDefs]
#         tl.insert("end", tuple(values))
#
#     if itemClickedFn:
#         tl.tablelist.bind('<<ListboxSelect>>', itemClickedFn)
#
#     return tl

class LoopTimer:
    def __init__(self, duration, function=None, *args):
        self.duration = duration
        self.function = function
        self.args = args
        self.timer = None
        if function:
            self.onTimer()

    def onTimer(self):
        self.function(*self.args)
        self.timer = threading.Timer(self.duration, self.onTimer)
        self.timer.start()

    def start(self):
        if self.function:
            self.onTimer()

    def cancel(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

def bindWaitingText(label, text):
    labelTimer = LoopTimer(0.3)

    def printLoading(count, text=text):
        for i in range(count):
            text += "."
        label.config(text = text)
        count = count + 1 if count < 3 else 0
        labelTimer.args[0] = count

    labelTimer.function = printLoading
    labelTimer.args = [0]
    labelTimer.start()
    return labelTimer

def getGridItem(gridRoot, row, column):
    for children in gridRoot.children.values():
        info = children.grid_info()
        if "row" in info and "column" in info and info["row"] == row and info["column"] == column:
            return children

########################################################################################################################
# Tooltip

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
