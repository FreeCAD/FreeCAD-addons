# WBO Workbench-Organizer widget for FreeCAD
# Copyright (C) 2015, 2016, 2017, 2018 by triplus @ FreeCAD who provided
# the wonderful TabBar widget on which this is based.
# Copyright (C) 2024 Oliver Rafelsberger
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""A workbench organizer for FreeCAD."""
"""Group and rename your workbenches as you like!"""

import FreeCADGui as Gui
import FreeCAD as App
from   PySide2 import QtGui, QtWidgets, QtCore
import os, json

__strAll__        = "WBO All"
__strDrop__       = "WBO In Groups Dropdown"
__strNew__        = "WBO New"
__strLost__       = "WBO Lost"
__strDisabled__   = "WBO Disabled"

__pathGroupFile__ = os.path.join(App.getUserAppDataDir(),"Mod\\WB_Organizer\\MyWorkbenches.txt")
__pathAliasFile__ = os.path.join(App.getUserAppDataDir(),"Mod\\WB_Organizer\\MyWorkbenchesRenaming.txt")
__pathInstruct__  = os.path.join(App.getUserAppDataDir(),"Mod\\WB_Organizer\\Resources\\Instructions.txt")
__pathIcons__     = os.path.dirname(__file__) + "\\Resources\\icons\\"
__pathToolbar__   = "User parameter:BaseApp/Workbench/Global/Toolbar"

__parameters__    = App.ParamGet("User parameter:BaseApp/WB_Organizer")
__groupedWB__     = {}
__aliasNames__    = {}

__actions__       = {}
__mainWindow__    = Gui.getMainWindow()
__tabActions__    = QtWidgets.QActionGroup(__mainWindow__)

__floatingWidgetWidth__ = 1330

#----------------------------------------------------------
class WBO(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

    def Deactivated(self):
        # is called whenever the Workbench is deactivated.
        return

class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(WBO(self))
        self.setTabPosition(QtWidgets.QTabWidget.West)
#--------------------------------------------------------------------

def saveMyWB():
        # Formatieren der Daten mit Einrückung
    
    formatted_data = json.dumps(__groupedWB__, indent=4)
    with open(__pathGroupFile__, 'w') as f:
        f.write(formatted_data)


def openMyWB():
    WB = Gui.listWorkbenches()
    justWB = list(WB)
    justWB.append("")
    newWB     = []
    global __groupedWB__
    global __aliasNames__, __strAll__, __strDrop__, __strNew__, __strLost__, __strDisabled__

    if not __parameters__.GetString("PrefButton"):
        __parameters__.SetString("floatingWidth", "1000")
        __parameters__.SetString("PrefButton", "Dropdown")
        __parameters__.SetString("Style", "IconText")

    # Schreiben der formatierten Daten in eine Datei
    if not os.path.exists(__pathGroupFile__):
        print("Config-file not found: generating new template.")
        __groupedWB__ = {__strDrop__: [""], __strAll__: justWB, __strNew__: justWB, __strLost__: [""], __strDisabled__: [""]}
        saveMyWB()
	
    else:	# a file already exists. Check for new and lost Workbenches
        with open(__pathGroupFile__, 'r') as f:
            try: 
                __groupedWB__ = json.load(f)
                loadedAll     = __groupedWB__.get(__strAll__)
                loadedAll.append("")    # ["a","","b","c",""]
                loadedAll.remove("")    # ["a","b","c",""]
                __groupedWB__.update({__strNew__: []})
                lostWB    = [wb for wb in loadedAll]
                for wb in WB:
                    if wb in loadedAll:
                        lostWB.remove(wb)
                    else:
                        newWB.append(wb)
                        loadedAll.append(wb)
        
                if lostWB:
                    lostWB.append("")
                    lostWB.remove("")
                    __groupedWB__.update({__strLost__: lostWB})
        
                if newWB:
                    newWB.append("")
                    newWB.remove("")
                    __groupedWB__.update({__strNew__: newWB})
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                __groupedWB__ = {__strDrop__: [""], __strAll__: justWB, __strNew__: justWB, __strLost__: [""], __strDisabled__: [""]}
            except Exception as e:
                print(f"Error: {e}")
                __groupedWB__ = {__strDrop__: [""], __strAll__: justWB, __strNew__: justWB, __strLost__: [""], __strDisabled__: [""]}
                # Add more specific exceptions if needed
                # Handle the error accordingly	
                print("ERROR on opening config-file.")

    if not os.path.exists(__pathAliasFile__):
        # generate a template file for renaming WB.
        print("Renaming-file not found: generating new Template.")
        aliasTemplate = {key: "" for key in justWB}
        aliasTemplate["ArchWorkbench"] = "Architecture"
        aliasTemplate[""] = ""
        formatted_data = json.dumps(aliasTemplate, indent=4)
        with open(__pathAliasFile__, 'w') as f:
            f.write(formatted_data)

    else:	# a file already exists. Check for new and lost Workbenches
        with open(__pathAliasFile__, 'r') as f:
            try: 
                __aliasNames__  = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error: {e}")
                # Add more specific exceptions if needed
                # Handle the error accordingly	

    global __selectedGroup__            
    __selectedGroup__ = __strAll__      # the currently selected Group
    return __groupedWB__

__groupedWB__  = openMyWB()


def testConfigFile(filePath):
    if os.path.exists(filePath):
	
        with open(filePath, 'r') as f:
            try: 
                json.load(f)
                return False 
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return str(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error: {e}")
                # Add more specific exceptions if needed
                # Handle the error accordingly	
                print("ERROR on opening file.")
                return str(f"Error: {e}")
    else:
        print("ERROR: file not found!")
        return False
    

def wbIcon(i):
    """Create workbench icon."""
    if str(i.find("XPM")) != "-1":
        icon = []
        for a in ((((i
                     .split('{', 1)[1])
                    .rsplit('}', 1)[0])
                   .strip())
                  .split("\n")):
            icon.append((a
                         .split('"', 1)[1])
                        .rsplit('"', 1)[0])
        icon = QtGui.QIcon(QtGui.QPixmap(icon))
    else:
        icon = QtGui.QIcon(QtGui.QPixmap(i))
    if icon.isNull():
        icon = QtGui.QIcon(":/icons/freecad")
    return icon


def wbActions():
    """Create workbench actions."""
    wbList = Gui.listWorkbenches()
    for i in wbList:
        if i not in __actions__:
            try:
                action = QtWidgets.QAction(__tabActions__)
                action.setCheckable(True)
                action.setText(wbList[i].MenuText)
                # replace original names by aliasNames
                if __aliasNames__ and i in __aliasNames__:
                    aliasName = __aliasNames__.get(i)
                    if aliasName:
                        action.setText(aliasName)
                action.setData(i)
                action.setIcon(wbIcon(wbList[i].Icon))
                __actions__[i] = action
            except:  # there is one 'none'-WB without an icon. We remove this here.
                action.setIcon(QtGui.QIcon(":/icons/freecad"))


def onOrientationChanged(w):
    """Set the tabs orientation."""
    btn = w[0]
    tab = w[1]
    orientation = __parameters__.GetString("Orientation", "Auto")
    prefbutton  = __parameters__.GetString("PrefButton", "Dropdown")
    #if prefbutton == "Tabs":

    def layout():
        """Support menu for West and East orientations."""
        wid = QtWidgets.QWidget()
        lo  = QtWidgets.QVBoxLayout()
        #spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        #lo.addItem(spacer)
        lo.addWidget(btn)
        lo.addWidget(tab)
        wid.setLayout(lo)
        tb.addWidget(wid)
        lo.setContentsMargins(0, 0, 0, 0)
        btn.setMaximumWidth(tab.height())

    if orientation == "Auto":
        if __mainWindow__.toolBarArea(tb) == QtCore.Qt.ToolBarArea.TopToolBarArea:
            orientation = "North"
        elif __mainWindow__.toolBarArea(tb) == QtCore.Qt.ToolBarArea.BottomToolBarArea:
            orientation = "South"
        elif __mainWindow__.toolBarArea(tb) == QtCore.Qt.ToolBarArea.LeftToolBarArea:
            orientation = "West"
        elif __mainWindow__.toolBarArea(tb) == QtCore.Qt.ToolBarArea.RightToolBarArea:
            orientation = "East"
        elif tb.orientation() == QtCore.Qt.Orientation.Horizontal:
            orientation = "North"
        elif tb.orientation() == QtCore.Qt.Orientation.Vertical:
            orientation = "West"
        else:
            pass

    if tb.isFloating():
        global __floatingWidgetWidth__
        __floatingWidgetWidth__ = int(__parameters__.GetString("floatingWidth", "1000"))
        tb.resize(__floatingWidgetWidth__, tb.height())
        orientation = "South"


    if orientation == "North":
        tb.addWidget(btn)
        tb.addWidget(tab)
        if prefbutton == "Tabs":
            tab.setTabPosition(QtWidgets.QTabWidget.North)
    elif orientation == "South":
        if prefbutton == "Tabs":
            tab.setTabPosition(QtWidgets.QTabWidget.South)
        tb.addWidget(btn)
        tb.addWidget(tab)
    elif orientation == "West":
        if prefbutton == "Tabs":
            tab.setLayoutDirection(QtCore.Qt.LeftToRight)
            tab.setTabPosition(QtWidgets.QTabWidget.West)
        layout()
    elif orientation == "East":
        if prefbutton == "Tabs":
            tab.setLayoutDirection(QtCore.Qt.LeftToRight)
            tab.setTabPosition(QtWidgets.QTabWidget.East)
        layout()
    else:
        pass

    btn.show()


def onGroupSelected(group):
    """Group selected"""
    global __selectedGroup__
    __selectedGroup__ = group

    btn.setText(group)

    for i in tb.findChildren(QtWidgets.QTabWidget, "TabBar"):
        i.deleteLater()
    for i in tb.findChildren(QtWidgets.QWidgetAction):
        i.deleteLater()

    ToolBarWidget = tabs(group)
    onOrientationChanged(ToolBarWidget)


def tabs(groupName = __strAll__):
    """Tabs widget."""
    # The user can decide in the Preferences if a WB shall be shown ...
    # ... in the TabBar as Tab (checked)
    # ... as Dropdown-Entry at the left Side of the TabBar (double not checked)
    # ... not (once not checked)

    def onGroupSelectedAction(group):
        return lambda checked=False, group=group: onGroupSelected(group)

    tb.clear()
    wbActions()
    
    w = QtWidgets.QTabWidget(tb)
    activeWB = Gui.activeWorkbench().__class__.__name__   # this is the currently active workbench

    # DropdownMenu for Groups ===========================================================
    global btn
    btn = QtWidgets.QPushButton(w)
    btn.setFlat(True)
    btn.setIcon(QtGui.QIcon(__pathIcons__ + "WBO_icon.svg"))
    btn.setStyleSheet("text-align: left;")
    if groupName == __strAll__:
        btn.setText("Select Group:")
    else:
        btn.setText(groupName)
    menu = QtWidgets.QMenu(btn)
    btn.setMenu(menu)

    # Add some WB from the __strDrop__ group directly to the Groups-DropDown
    inGroupsDD = __groupedWB__.get(__strDrop__)
    if not inGroupsDD: inGroupsDD = {}  # prevents error in case __strDrop__ has been changed
    """ remove the active WB from the ones in the Dropdownlist. I think, we don't need this.
        It might confuse users as the dropdown list always changes somehow magically.

    if inGroupsDD and (activeWB in inGroupsDD):     # remove existing inGroupsDD WB
        inGroupsDD.remove(activeWB)
    else:
        inGroupsDD = []
    """
    for i in inGroupsDD:                         # Add the inGroupsDD WB
        if i in __actions__:
            menu.addAction(__actions__[i])

    menu.addSeparator()

    # Add the groups to the dropdown-menu
    for group in __groupedWB__.keys():
        if group not in [__strDrop__, __strLost__, __strNew__, __strDisabled__]:
            gr = QtWidgets.QAction(menu)
            gr.setText(group)
            if group == __strAll__:
                gr.setText(__aliasNames__.get(__strAll__))
            gr.setData(group)
            gr.triggered.connect(onGroupSelectedAction(group))
            menu.addAction(gr)

    menu.addSeparator()

    pref = QtWidgets.QAction(menu)
    pref.setText("Preferences")
    pref.setIcon(QtGui.QIcon(__pathIcons__ + "WBO_Prefs.svg"))
    pref.triggered.connect(onPreferences)
    menu.addAction(pref)

    menu_width = menu.sizeHint().width()
    menu.setFixedWidth(menu_width + 20)


    prefbutton  = __parameters__.GetString("PrefButton", "Dropdown")
    if prefbutton == 'Dropdown':
        # Dropdown ======================================================================
        global btnWB
        btnWB = QtWidgets.QPushButton(w)
        btnWB.setFlat(True)
        btnWB.setIcon(__actions__.get(activeWB).icon())
        btnWB.setText(__actions__.get(activeWB).text())
        menu = QtWidgets.QMenu(btnWB)
        btnWB.setMenu(menu)

        # Add some WB from the __strDrop__ group directly to the Groups-DropDown
        group   = groupName
        groupWB = __groupedWB__.get(group)

        for i in groupWB:                         # Add the inGroupsDD WB
            if i in __actions__:
                menu.addAction(__actions__[i])

        menu2_width = menu.sizeHint().width()
        menu.setFixedWidth(menu2_width + 10)
        btnWB.setFixedWidth(menu2_width + 10)
        btnWB.setStyleSheet("text-align: left;")
        w = btnWB

    else:
        # Tabs ==========================================================================
        group   = groupName
        groupWB = __groupedWB__.get(group)

        w.setObjectName("TabBar")
        w.setDocumentMode(True)
        w.setUsesScrollButtons(True)
        w.tabBar().setDrawBase(True)

        # Add temporarily the active WB to the Tabs if it's not already there and remove it later again.
        tempAddedWB = ""                
        if activeWB not in groupWB:       
            groupWB.append(activeWB)      
            tempAddedWB = activeWB

        unchecked = __groupedWB__.get(__strDisabled__)
        if not unchecked: unchecked = {}  # prevents error in case __strDisabled__ has been changed
        for i in groupWB:
            if i in __actions__ and i not in unchecked:
                if __parameters__.GetString("Style") == "Icon":
                    r = w.tabBar().addTab(__actions__[i].icon(), None)
                elif __parameters__.GetString("Style") == "Text":
                    r = w.tabBar().addTab(__actions__[i].text())
                else:
                    r = w.tabBar().addTab(__actions__[i].icon(), __actions__[i].text())
                w.tabBar().setTabData(r, i)
                w.tabBar().setTabToolTip(r, __actions__[i].text())

        for i in range(w.count()):
            if w.tabBar().tabData(i) == activeWB:
                w.tabBar().setCurrentIndex(i)

        def onTab(d):
            """Activate workbench on tab."""
            data = w.tabBar().tabData(d)
            if data:
                for i in __actions__:
                    if __actions__[i].data() == data:
                        __actions__[i].trigger()
            w.currentChanged.disconnect(onTab)

        w.currentChanged.connect(onTab)

        # Remove the temporarily added Tab again
        if tempAddedWB:
            groupWB.remove(tempAddedWB)

    return [btn, w]

#==================================================================================================================================

def onWorkbenchActivated():
    """Populate the tabs toolbar."""
    for i in tb.findChildren(QtWidgets.QTabWidget, "TabBar"):
        i.deleteLater()
    for i in tb.findChildren(QtWidgets.QWidgetAction):
        i.deleteLater()
    global __selectedGroup__
    ToolBarWidget = tabs(__selectedGroup__)
    onOrientationChanged(ToolBarWidget)


def onWorkbenchSelected(a):     # When a WB-Tab has been pressed.
    """Activate workbench on action."""
    data = a.data()
    if data:
        try:
            #Gui.doCommand('Gui.activateWorkbench("' + data + '")')
            Gui.activateWorkbench(data)
        except KeyError:
            pass


import subprocess
import sys

def openFileInEditor(filePath):
    """A first, simple solution to edit the config-file that defines the groups"""
    try:
        if sys.platform.startswith('linux'):
            subprocess.Popen(['nano', filePath])
        elif sys.platform.startswith('win'):
            subprocess.Popen(['notepad', filePath])
        elif sys.platform.startswith('darwin'):  # MacOSX
            subprocess.Popen(['open', '-t', filePath])
        else:
            print("Operatingsystem not supported.")
    except Exception as e:
        print(f"Error on opening file: {e}")


def prefDialog():
    """Preferences dialog."""
    wbActions()
    dialog = QtWidgets.QDialog(__mainWindow__)
    dialog.setModal(True)
    dialog.resize(800, 450)
    dialog.setWindowTitle("WorkbenchOrganizer preferences")
    layout = QtWidgets.QVBoxLayout()
    dialog.setLayout(layout)
    #------------------------
    selector = QtWidgets.QListWidget(dialog)
    selector.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    btnClose = QtWidgets.QPushButton("Close", dialog)
    btnClose.setToolTip("Close the preferences dialog")
    btnClose.setDefault(True)

    btnUp = QtWidgets.QPushButton(dialog)
    btnUp.setToolTip("Move selected item up")
    btnUp.setIcon(QtGui.QIcon(__pathIcons__ + "WBO_MoveUp"))

    btnDown = QtWidgets.QPushButton(dialog)
    btnDown.setToolTip("Move selected item down")
    btnDown.setIcon(QtGui.QIcon(__pathIcons__ + "WBO_MoveDown"))

    btnInstructions = QtWidgets.QPushButton(dialog)
    btnInstructions.setToolTip("Show instructions how to define groups")
    btnInstructions.setText("Show instructions")

    btnFile = QtWidgets.QPushButton(dialog)
    btnFile.setToolTip("Open and Edit the config-file")
    btnFile.setText("Open config-file")

    btnTest = QtWidgets.QPushButton(dialog)
    btnTest.setToolTip("Test if the config-file is correct")
    btnTest.setText("Test config-file")

    btnResult = QtWidgets.QPushButton(dialog)
    btnResult.setToolTip("Push to hide for next test.")
    btnResult.setText("")
    btnResult.setVisible(False)

    txtResult = QtWidgets.QTextEdit(dialog)
    txtResult.setVisible(False)
    txtResult.setStyleSheet("color: #8B0000;")

    labelRename = QtWidgets.QLabel("Rename your WB here:")

    btnRename = QtWidgets.QPushButton(dialog)
    btnRename.setToolTip("Open and Edit the rename-file")
    btnRename.setText("Open rename-file")

    btnTestRename = QtWidgets.QPushButton(dialog)
    btnTestRename.setToolTip("Check the rename-file")
    btnTestRename.setText("Test rename-file")

    label = QtWidgets.QLabel("Length of Workbench Organizer when free floating:")
    explication = QtWidgets.QLabel("<i>Confirm your data entry with [Shift] + [Return]<br>to keep the dialog window open.</i>")
    explication.setStyleSheet("color: lightgrey")

    lineEdit = QtWidgets.QLineEdit(dialog)
    lineEdit.setGeometry(QtCore.QRect(30, 40, 211, 22))
    lineEdit.setObjectName("Length of tab")
    lineEdit.setFixedWidth(100)
    lineEdit.setToolTip("Use this to set the length of the tabbar\nif you want to place the Workbench Organizer\ni.e. on top of the header line of FreeCAD.")
    #lineEdit.setIconText("Length of freefloating tab")
    lineEdit.setText(str(__floatingWidgetWidth__))
    #----------------------- Center Area
    groupsPanel= QtWidgets.QGroupBox("Define your groups here:")
    groupsButtons = QtWidgets.QVBoxLayout()
    groupsButtons.addWidget(btnInstructions)
    groupsButtons.addWidget(btnFile)
    groupsButtons.addWidget(btnTest)
    groupsButtons.addWidget(labelRename)
    groupsButtons.addWidget(btnRename)
    groupsButtons.addWidget(btnTestRename)
    groupsButtons.addWidget(btnResult)
    groupsButtons.addWidget(txtResult)
    groupsButtons.addStretch()
    groupsPanel.setLayout(groupsButtons)
    #--------------------------------------------------------------
    l0 = QtWidgets.QHBoxLayout()
    stylePanel = QtWidgets.QGroupBox("Style:")
    stylePanel.setLayout(l0)
    r0 = QtWidgets.QRadioButton("Icon", stylePanel)
    r0.setObjectName("Icon")
    r0.setToolTip("Show just icon in tabbar.")
    r1 = QtWidgets.QRadioButton("Text", stylePanel)
    r1.setObjectName("Text")
    r1.setToolTip("Show just text in tabbar.")
    r2 = QtWidgets.QRadioButton("Icon and text", stylePanel)
    r2.setObjectName("IconText")
    r2.setToolTip("Show icon and text in tabbar")
    l0.addWidget(r0)
    l0.addWidget(r1)
    l0.addWidget(r2)
    #-----------------------
    """
    l1 = QtWidgets.QVBoxLayout()
    orientationPanel = QtWidgets.QGroupBox("Tab orientation:")
    orientationPanel.setLayout(l1)
    r3 = QtWidgets.QRadioButton("Auto", orientationPanel)
    r3.setObjectName("Auto")
    r3.setToolTip("Set based on the orientation")
    r4 = QtWidgets.QRadioButton("Top", orientationPanel)
    r4.setObjectName("North")
    r4.setToolTip("Tabs at top")
    r5 = QtWidgets.QRadioButton("Bottom", orientationPanel)
    r5.setObjectName("South")
    r5.setToolTip("Tabs at bottom")
    r6 = QtWidgets.QRadioButton("Left", orientationPanel)
    r6.setObjectName("West")
    r6.setToolTip("Tabs at left")
    r7 = QtWidgets.QRadioButton("Right", orientationPanel)
    r7.setObjectName("East")
    r7.setToolTip("Tabs at right")
    l1.addWidget(r3)
    l1.addWidget(r4)
    l1.addWidget(r5)
    l1.addWidget(r6)
    l1.addWidget(r7)
    """
    #-----------------------
    buttonsPanel = QtWidgets.QHBoxLayout()    # die untere Leiste mit den Up/down und Close-Buttons
    buttonsPanel.addWidget(btnUp)
    buttonsPanel.addWidget(btnDown)
    buttonsPanel.addStretch(1)
    buttonsPanel.addWidget(btnClose)
    #-----------------------
    l3 = QtWidgets.QHBoxLayout()
    l3.addStretch()
    l4 = QtWidgets.QVBoxLayout()
    l4.addWidget(stylePanel)
    #l4.addWidget(g1)
    #----------------------- Right Area
    showWBPanel = QtWidgets.QVBoxLayout()
    g6 = QtWidgets.QGroupBox("Show Workbenches as Tabs or as Dropdown:")
    g6.setLayout(showWBPanel)
    r8 = QtWidgets.QRadioButton("Tabs", g6)
    r8.setObjectName("Tabs")
    r8.setToolTip("Show the workbenches in a tabbar")
    r9 = QtWidgets.QRadioButton("Dropdown", g6)
    r9.setObjectName("Dropdown")
    r9.setToolTip("Show the workbenches in a dropdownlist")
    showWBPanel.addWidget(r9)
    showWBPanel.addWidget(r8)
    showWBPanel.addWidget(label)
    showWBPanel.addWidget(lineEdit)
    showWBPanel.addWidget(explication)
    l4.addWidget(g6)
    l4.addStretch()
    l4.insertLayout(0, l3)
    #--------------------------------------
    l5 = QtWidgets.QHBoxLayout()
    l5.addWidget(selector)      # All List
    l5.addWidget(groupsPanel)   # Groups
    l5.insertLayout(2, l4)      # Radio-Buttons

    #layout.insertLayout(0, l5)  # die beiden Bereiche Links Liste, Rechts Radio-Buttons
    #layout.insertLayout(1, buttonsPanel)  # die untere Lesite mit den Buttons

    # Create a top-level horizontal layout
    top_layout = QtWidgets.QHBoxLayout()

    # Add the left and right areas to the top-level layout
    top_layout.insertLayout(0, l5)  # die beiden Bereiche Links Liste, Rechts Radio-Buttons

    # Add the top-level layout to the main layout
    layout.addLayout(top_layout)
    layout.insertLayout(1, buttonsPanel)  # die untere Lesite mit den Buttons

    def onAccepted():
        """Close dialog on button close."""
        dialog.done(1)

    def onFinished():
        """Delete dialog on close."""
        dialog.deleteLater()

    def onItemChanged(item=None):
        """Save workbench list state."""
        if item:
            selector.blockSignals(True)
            if item.data(50) == "Unchecked":
                item.setCheckState(QtCore.Qt.CheckState(2))
                item.setData(50, "Checked")
            else:
                item.setCheckState(QtCore.Qt.CheckState(0))
                item.setData(50, "Unchecked")
            selector.blockSignals(False)
        disabled = []
        for index in range(selector.count()):
            if selector.item(index).checkState() != QtCore.Qt.Checked:
                disabled.append(selector.item(index).data(32))
        __groupedWB__.update({__strDisabled__: disabled})
        saveMyWB()

        onWorkbenchActivated()

    def onUp():
        """Save workbench position list."""
        currentIndex = selector.currentRow()
        if currentIndex != 0:
            selector.blockSignals(True)
            currentItem = selector.takeItem(currentIndex)
            selector.insertItem(currentIndex - 1, currentItem)
            selector.setCurrentRow(currentIndex - 1)
            selector.blockSignals(False)
            position = []
            for index in range(selector.count()):
                position.append(selector.item(index).data(32))
            __groupedWB__.update({__strAll__: position})
            saveMyWB()
            onItemChanged()

    def onDown():
        """Save workbench position list."""
        currentIndex = selector.currentRow()
        if currentIndex != selector.count() - 1 and currentIndex != -1:
            selector.blockSignals(True)
            currentItem = selector.takeItem(currentIndex)
            selector.insertItem(currentIndex + 1, currentItem)
            selector.setCurrentRow(currentIndex + 1)
            selector.blockSignals(False)
            position = []
            for index in range(selector.count()):
                position.append(selector.item(index).data(32))
            __groupedWB__.update({__strAll__: position})
            saveMyWB()
            onItemChanged()

    def onOpenFile():
        """Open the configuration file"""
        openFileInEditor(__pathGroupFile__)


    def onOpenRenameFile():
        """Open the configuration file"""
        openFileInEditor(__pathAliasFile__)


    def onTestFile():
        """Test the configuration file"""
        Error = testConfigFile(__pathGroupFile__)
        if not Error:
            openMyWB()
            btnResult.setText("Config-file OK")
            btnResult.setStyleSheet("background-color: green; color: white;")
            txtResult.setVisible(False)

        else:
            btnResult.setText("ERROR in config-file")
            btnResult.setStyleSheet("background-color: red; color: white;")
            txtResult.setText(Error)
            txtResult.setVisible(True)
        btnResult.setFlat(True)
        btnResult.setVisible(True)

    def onTestRenameFile():
        """Test the configuration file"""
        Error = testConfigFile(__pathAliasFile__)
        if not Error:
            openMyWB()
            btnResult.setText("Rename-file OK")
            btnResult.setStyleSheet("background-color: green; color: white;")
            txtResult.setVisible(False)

        else:
            btnResult.setText("ERROR in rename-file")
            btnResult.setStyleSheet("background-color: red; color: white;")
            txtResult.setText(Error)
            txtResult.setVisible(True)
        btnResult.setFlat(True)
        btnResult.setVisible(True)

    
    def onResult():
        """Hide the Result-Button again"""
        btnResult.setVisible(False)
        txtResult.setVisible(False)



    def onShowInstructions():
        """Open the configuration file"""
        openFileInEditor(__pathInstruct__)


    def on_lineEdit_clicked():
        global __floatingWidgetWidth__
        # if self.lineEdit.textChanged():
        __floatingWidgetWidth__ = int(lineEdit.displayText())
        __parameters__.SetString("floatingWidth", str(__floatingWidgetWidth__))
        onWorkbenchActivated()


    def onstylePanel(r):
        """Set TabBar style."""
        if r:
            for i in stylePanel.findChildren(QtWidgets.QRadioButton):
                if i.isChecked():
                    __parameters__.SetString("Style", i.objectName())
            onWorkbenchActivated()


    def onG6(r):
        """Set pref button."""
        if r:
            for i in g6.findChildren(QtWidgets.QRadioButton):
                if i.isChecked():
                    __parameters__.SetString("PrefButton", i.objectName())
            onWorkbenchActivated()

    """ 
    # This is a trial to prevent the 'Return' signal escaping the lineEdit-Widget and
    # propagating to the 'close' button. But doesn't work yet.
    def eventFilter(obj, event):
        if obj is line_edit and event.type() == QtCore.QEvent.KeyPress:
            # Check if the pressed key is 'Return'
            if event.key() == QtCore.Qt.Key_Return:
                # Prevent the 'Return' key event from being propagated to the line edit
                return True
        return False
    #lineEdit.installEventFilter(eventFilter)
    """

    unchecked = __groupedWB__.get(__strDisabled__)
    if not unchecked: unchecked = {}  # prevents error in case __strDisabled__ has been changed
    position  = __groupedWB__.get(__strAll__)
    if not position: position = {}    # prevents error in case __strAll__ has been changed


    # build up the list of WB and set the CheckState        
    for i in position:
        if i in __actions__:
            item = QtWidgets.QListWidgetItem(selector)
            item.setText(__actions__[i].text())
            item.setIcon(__actions__[i].icon())
            item.setData(32, __actions__[i].data())
            if __actions__[i].data() in position:
                item.setCheckState(QtCore.Qt.CheckState(2))
                item.setData(50, "Checked")
            if __actions__[i].data() in unchecked:
                item.setCheckState(QtCore.Qt.CheckState(0))
                item.setData(50, "Unchecked")

    # set the radio buttons to the stored values
    style = __parameters__.GetString("Style")
    if style == "Text":
        r1.setChecked(True)
    elif style == "IconText":
        r2.setChecked(True)
    else:
        r0.setChecked(True)

    """
    orientation = __parameters__.GetString("Orientation")
    if orientation == "North":
        r4.setChecked(True)
    elif orientation == "South":
        r5.setChecked(True)
    elif orientation == "West":
        r6.setChecked(True)
    elif orientation == "East":
        r7.setChecked(True)
    else:
        r3.setChecked(True)
    """    

    prefbutton = __parameters__.GetString("PrefButton", "Tabs")
    if prefbutton == "Tabs":
        r8.setChecked(True)
    else:
        r9.setChecked(True)
    r0.toggled.connect(onstylePanel)
    r1.toggled.connect(onstylePanel)
    r2.toggled.connect(onstylePanel)
    """
    #r3.toggled.connect(onOrientationPanel)
    #r4.toggled.connect(onOrientationPanel)
    #r5.toggled.connect(onOrientationPanel)
    #r6.toggled.connect(onOrientationPanel)
    #r7.toggled.connect(onOrientationPanel)
    """
    r8.toggled.connect(onG6)
    r9.toggled.connect(onG6)
    btnUp.clicked.connect(onUp)
    btnDown.clicked.connect(onDown)
    selector.itemChanged.connect(onItemChanged)
    dialog.finished.connect(onFinished)
    btnClose.clicked.connect(onAccepted)
    btnFile.clicked.connect(onOpenFile)
    btnTest.clicked.connect(onTestFile)
    btnResult.clicked.connect(onResult)
    btnRename.clicked.connect(onOpenRenameFile)
    btnTestRename.clicked.connect(onTestRenameFile)
    btnInstructions.clicked.connect(onShowInstructions)
    lineEdit.returnPressed.connect(on_lineEdit_clicked) #connection lineEdit

    return dialog


def onPreferences():
    """Open the preferences dialog."""
    dialog = prefDialog()
    dialog.show()

#==================================================================================================================================

def accessoriesMenu():
    """Add WorkbenchOrganizer preferences to accessories menu."""
    pref = QtWidgets.QAction(__mainWindow__)
    pref.setText("WorkbenchOrganizer")
    pref.setObjectName("WorkbenchOrganizer")
    pref.triggered.connect(onPreferences)
    try:
        import AccessoriesMenu
        AccessoriesMenu.addItem("WorkbenchOrganizer")
    except ImportError:
        a = __mainWindow__.findChild(QtWidgets.QAction, "AccessoriesMenu")
        if a:
            a.menu().addAction(pref)
        else:
            mb = __mainWindow__.menuBar()
            actionAccessories = QtWidgets.QAction(__mainWindow__)
            actionAccessories.setObjectName("AccessoriesMenu")
            actionAccessories.setIconText("Accessories")
            menu = QtWidgets.QMenu()
            actionAccessories.setMenu(menu)
            menu.addAction(pref)

            def addMenu():
                """Add accessories menu to the menu bar."""
                mb.addAction(actionAccessories)
                actionAccessories.setVisible(True)

            addMenu()
            __mainWindow__.workbenchActivated.connect(addMenu)


def onClose():
    """Remove tabs toolbar on FreeCAD close."""
    g = App.ParamGet("User parameter:BaseApp/Workbench/Global/Toolbar")
    g.RemGroup("Tabs")


def onStart():
    """Start TabBar."""
    start = False
    try:
        __mainWindow__.workbenchActivated
        __mainWindow__.mainWindowClosed
        global tb
        tb = __mainWindow__.findChild(QtWidgets.QToolBar, "Tabs")
        tb.orientation
        start = True
    except AttributeError:
        pass
    if start:
        t.stop()
        t.deleteLater()
        accessoriesMenu()
        onWorkbenchActivated()
        __tabActions__.triggered.connect(onWorkbenchSelected)
        __mainWindow__.mainWindowClosed.connect(onClose)
        __mainWindow__.workbenchActivated.connect(onWorkbenchActivated)
        tb.orientationChanged.connect(onWorkbenchActivated)
        tb.topLevelChanged.connect(onWorkbenchActivated)


def onPreStart():
    """Improve start reliability and maintain FreeCAD 0.16 support."""
    if App.Version()[1] < "17":
        onStart()
    else:
        if __mainWindow__.property("eventLoop"):
            onStart()


t = QtCore.QTimer()
t.timeout.connect(onPreStart)
t.start(500)