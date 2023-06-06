import obbinstall, re, datetime
from Toolkit.Misc import stringOperations
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Button
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Python import common, configFile
from os.path import *
from distutils.version import LooseVersion

class AppConfig(configFile.Config):
    def __init__(self, filePath):
        configFile.Config.__init__(self)
        self.history = []
        self.load(filePath)

    def SetAndSave(self, varName, value):
        self.__dict__[varName] = value
        self.save()

def getConfigFilePath():
    _, fileName, _ = common.getFileParts(__file__)
    return abspath(fileName + ".user")

def createGroups(lines, patternSeparator):
    regex = re.compile(patternSeparator)
    res = []
    currentGroup = None
    for line in lines:
        if regex.match(line):
            if currentGroup is not None:
                res.append(currentGroup)
            currentGroup = []
        if currentGroup is not None:
            currentGroup.append(line)
    if currentGroup is not None:
        res.append(currentGroup)
    return res


class VersionContent:
    def __init__(self, lines, *highlighters):
        self.name = lines[0]
        contentIdx = 1
        try:
            self.date = datetime.datetime.strptime(lines[contentIdx], "%b %d, %Y")
            self.isRealDate = True
            contentIdx += 1
        except:
            self.date = None
            self.isRealDate = False
            pass
        self.content = lines[contentIdx:]
        self.highlights = []
        for highlighter in highlighters:
            self.highlights.append(highlighter(self))
    def __str__(self):
        return "{} - {}".format(self.date, self.name)
    def __repr__(self):
        return "{} - {}".format(self.date, self.name)

def process():
    config = AppConfig(getConfigFilePath())

    # ==================================================================================================================
    # Setup Tkinter + Matplot
    root = tk.Tk()
    root.wm_title("Patch notes analyzer")
    def onClose():
        config.save(getConfigFilePath())
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", onClose)

    statsFrame = tk.Frame(root)
    statsFrame.pack(side=tk.LEFT, fill=tk.Y, expand=1)

    fig = plt.Figure(figsize=(10, 4), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    # ==================================================================================================================
    # Full figure update
    def processFile(filePath):
        _, currentFileName, _ = common.getFileParts(filePath)
        currentFileName = currentFileName.replace("Data-", "")
        root.wm_title("Patch notes analyzer - " + currentFileName)

        lines = stringOperations.textToLines(filePath)
        lines = stringOperations.removeEmptyLines(lines)

        # Parse highlighters
        categories = ["Update"]
        highlighters = []
        highlightersEndIdx = -1
        for i in range(len(lines)):
            if "===" in lines[i]:
                highlightersEndIdx = i
                break
        if highlightersEndIdx >= 0:
            highlightLines = lines[:highlightersEndIdx]
            idx = 0
            while idx < len(highlightLines):
                if not highlightLines[idx].startswith("\t"):
                    categoryTitle = highlightLines[idx]
                    categories.append(categoryTitle)
                    tested = []
                    idx += 1
                    while idx < len(highlightLines) \
                    and (highlightLines[idx].startswith("\t") or highlightLines[idx].startswith(" ")):
                        tested.append(highlightLines[idx].strip().lower())
                        idx += 1
                    tested = [re.compile(x, re.IGNORECASE) for x in tested]
                    def testHighlighter(version, _tested):
                        for line in version.content:
                            for tested in _tested:
                                if tested.search(line) is not None:
                                    return line
                    highlighters.append(lambda version, _tested=tested: testHighlighter(version, _tested))
            lines = lines[highlightersEndIdx + 1:]

        # Clean lines to match AppleStore format: version, date, content line
        lines = stringOperations.strip(lines)
        if lines[0].startswith("Version History"): # AppStore log
            lines = stringOperations.removeLineWithPattern(lines, "Version History")
        elif lines[0].startswith("What's New"): # AppAnnie log
            lines = stringOperations.removeLineWithPattern(lines, "What's New")
            lines = stringOperations.removeLineWithPattern(lines, "Collapse notes")
            lines = stringOperations.removeLineWithPattern(lines, "Expand notes")
            lines = stringOperations.removeLineWithPattern(lines, "Show less")
            i = 0
            while i < len(lines):
                if lines[i].startswith("Version "):
                    line = lines[i].replace("Version ", "")
                    if "(" in line:
                        separator = line.index("(")
                        versionName, date = line[:separator-1], line[separator+1:-1]
                        lines[i] = versionName
                        lines.insert(i+1, date)
                i += 1
        # Split long lines
        i = 0
        while i < len(lines):
            line = lines[i]
            if len(line) > 100:
                separator = line.find(" ", 100)
                if separator >= 0:
                    line1, line2 = line[:separator], line[separator + 1:]
                    lines[i] = line1
                    lines.insert(i + 1, line2)
            i += 1

        # Parse versions content
        versions = createGroups(lines, "\d+(\.\d+)+")
        versions.sort(key=lambda x: LooseVersion(x[0]))
        versions = [VersionContent(x, *highlighters) for x in versions]

        # # Remove duplicates
        # # i = 0
        # while i < len(versions):
        #     j = i + 1
        #     while j < len(versions):
        #         if versions[i].content == versions[j].content:
        #             versions.remove(versions[j])
        #         else:
        #             j += 1
        #     i += 1

        # Fix possible bug with dates
        for i in range(len(versions)):
            if versions[i].date: continue
            end = i + 1
            while end < len(versions):
                if versions[end].date:
                    break
                end += 1
            unassignedCount = end - i
            if i > 0 and end < len(versions):
                startDate, endDate = versions[i-1].date, versions[end].date
            elif i == 0:
                endDate = versions[end].date
                startDate = endDate - datetime.timedelta(days=unassignedCount+1)
            elif end == len(versions):
                startDate = versions[i - 1].date
                endDate = startDate + datetime.timedelta(days=unassignedCount+1)
            else:
                raise Exception("All dates are missing")
            offset = (endDate - startDate) / (unassignedCount + 1)
            for j in range(unassignedCount):
                versions[i + j].date = startDate + (j + 1) * offset

        # Create plotting data
        xData, yData, textData, colors, versionIndex = [], [], [], [], []
        def append(version, category, text):
            xData.append(version.date)
            yData.append(category)
            textData.append("{} - {}\n{}".format(version.name, version.date.strftime("%d/%b/%Y"), text))
            colors.append("blue" if version.isRealDate else "red")
            versionIndex.append(versions.index(version))
        for x in versions:
            append(x, 0, "\n".join(x.content))
            for i, y in enumerate(x.highlights):
                if y is not None:
                    append(x, i + 1, y)

        # Plot
        fig.clear()
        ax = fig.add_subplot(111, autoscalex_on=True)
        ax.grid(True, linestyle="--", zorder=1)
        ax.set_ylim(-1, len(categories))
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels(categories)
        scattered = ax.scatter(xData, yData, color=colors, s=10, zorder=2)

        # Hover
        annot = ax.annotate("", xy=(0, 0), xycoords="data",
                            xytext=(20, 20), textcoords="offset pixels",
                            bbox=dict(boxstyle="round", fc="w",
                            alpha=0.8),
                            # arrowprops=dict(arrowstyle="->")
        )
        annot.set_visible(False)
        lastPosition = [None]
        startDate, endDate = min(xData), max(xData)
        def hover(event):
            vis = annot.get_visible()
            cont, ind = scattered.contains(event)
            if cont:
                index = ind["ind"][0]
                date = xData[index]
                pos = (date, yData[index])
                if pos == lastPosition[0]:
                    return
                annot.xy = pos
                lastPosition[0] = pos

                # Adjust offset to ensure annotation is always located in the screen zone
                annot.set_text("{}".format(textData[index]))
                annot.update_bbox_position_size(annot._renderer)
                bbox = annot.get_bbox_patch()
                annot.set_visible(True)
                annot.xyann = (-bbox.get_width() * (1 - (endDate - date) / (endDate - startDate)), 20)

                fig.canvas.draw_idle()
            elif vis:
                if lastPosition[0] == None:
                    return
                lastPosition[0] = None
                annot.set_visible(False)
                fig.canvas.draw_idle()
        canvas.mpl_connect("motion_notify_event", hover)
        canvas.draw_idle()

        # Update stats
        for child in statsFrame.winfo_children():
            child.destroy()
        texts = [
            "* " + currentFileName,
            "",
            "Updates count: {}".format(len(versions)),
            "Avg update delay: {:.2f}".format(((endDate - startDate) / (len(versions) - 1)).total_seconds() / (60*60*24))
        ]
        tk.Label(statsFrame, text="\n".join(texts), anchor=tk.W, justify=tk.LEFT).pack()


    # ==================================================================================================================
    # Menu
    menu = tk.Menu(root, tearoff=0)
    recentMenu = tk.Menu(menu, tearoff=0)

    def loadFile(filePath):
        if not filePath:
            return

        # Backup in history
        if filePath in config.history:
            config.history.remove(filePath)
        config.history.append(filePath)

        # Refresh recent menu
        recentMenu.delete(0, recentMenu.index('end'))
        for filePath in reversed(config.history):
            _, fileName, _ = common.getFileParts(filePath)
            fileName = fileName.replace("Data-", "")
            if config.history.index(filePath) == len(config.history) - 1:
                fileName = "> " + fileName
            recentMenu.add_command(label=fileName, command=lambda x=filePath: loadFile(x))

        processFile(config.history[-1])

    def load():
        currentLocation, _, _ = common.getFileParts(__file__)
        filePath = tk.filedialog.askopenfilename(initialdir=currentLocation, title="Select file", filetypes=(("Data file","*.txt"),("all files","*.*")))
        loadFile(filePath)

    # Add refresh button
    def refresh():
        if len(config.history) > 0:
            loadFile(config.history[-1])

    menu.add_command(label="Load...", command=load)
    menu.add_command(label="Refresh", command=refresh)
    menu.add_cascade(label="Recent files", menu=recentMenu)

    # ==================================================================================================================
    # Start app
    root.winfo_toplevel().configure(menu=menu)
    refresh()
    tk.mainloop()

process()
