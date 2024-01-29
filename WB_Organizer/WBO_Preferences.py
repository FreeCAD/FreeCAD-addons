def onWorkbenchActivated():
    """Populate the tabs toolbar."""
    for i in tb.findChildren(QtGui.QTabWidget, "TabBar"):
        i.deleteLater()
    for i in tb.findChildren(QtGui.QWidgetAction):
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
    dialog = QtGui.QDialog(__mainWindow__)
    dialog.setModal(True)
    dialog.resize(800, 450)
    dialog.setWindowTitle("WorkbenchOrganizer preferences")
    layout = QtGui.QVBoxLayout()
    dialog.setLayout(layout)
    #------------------------
    selector = QtGui.QListWidget(dialog)
    selector.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    btnClose = QtGui.QPushButton("Close", dialog)
    btnClose.setToolTip("Close the preferences dialog")
    btnClose.setDefault(True)

    btnUp = QtGui.QPushButton(dialog)
    btnUp.setToolTip("Move selected item up")
    btnUp.setIcon(QtGui.QIcon(__pathIcons__ + "WBO_MoveUp"))

    btnDown = QtGui.QPushButton(dialog)
    btnDown.setToolTip("Move selected item down")
    btnDown.setIcon(QtGui.QIcon(__pathIcons__ + "WBO_MoveDown"))

    btnInstructions = QtGui.QPushButton(dialog)
    btnInstructions.setToolTip("Show instructions how to define groups")
    btnInstructions.setText("Show instructions")

    btnFile = QtGui.QPushButton(dialog)
    btnFile.setToolTip("Open and Edit the config-file")
    btnFile.setText("Open config-file")

    btnTest = QtGui.QPushButton(dialog)
    btnTest.setToolTip("Test if the config-file is correct")
    btnTest.setText("Test config-file")

    btnResult = QtGui.QPushButton(dialog)
    btnResult.setToolTip("Push to hide for next test.")
    btnResult.setText("")
    btnResult.setVisible(False)

    txtResult = QtGui.QTextEdit(dialog)
    txtResult.setVisible(False)
    txtResult.setStyleSheet("color: #8B0000;")

    labelRename = QtWidgets.QLabel("Rename your WB here:")

    btnRename = QtGui.QPushButton(dialog)
    btnRename.setToolTip("Open and Edit the rename-file")
    btnRename.setText("Open rename-file")

    btnTestRename = QtGui.QPushButton(dialog)
    btnTestRename.setToolTip("Check the rename-file")
    btnTestRename.setText("Test rename-file")

    label = QtWidgets.QLabel("Length of Workbench Organizer when free floating:")
    explication = QtWidgets.QLabel("<i>Confirm your data entry with [Shift] + [Return]<br>to keep the dialog window open.</i>")
    explication.setStyleSheet("color: lightgrey")

    lineEdit = QtGui.QLineEdit(dialog)
    lineEdit.setGeometry(QtCore.QRect(30, 40, 211, 22))
    lineEdit.setObjectName("Length of tab")
    lineEdit.setFixedWidth(100)
    lineEdit.setToolTip("Use this to set the length of the tabbar\nif you want to place the Workbench Organizer\ni.e. on top of the header line of FreeCAD.")
    #lineEdit.setIconText("Length of freefloating tab")
    lineEdit.setText(str(__floatingWidgetWidth__))
    #----------------------- Center Area
    groupsPanel= QtGui.QGroupBox("Define your groups here:")
    groupsButtons = QtGui.QVBoxLayout()
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
    l0 = QtGui.QHBoxLayout()
    stylePanel = QtGui.QGroupBox("Style:")
    stylePanel.setLayout(l0)
    r0 = QtGui.QRadioButton("Icon", stylePanel)
    r0.setObjectName("Icon")
    r0.setToolTip("Show just icon in tabbar.")
    r1 = QtGui.QRadioButton("Text", stylePanel)
    r1.setObjectName("Text")
    r1.setToolTip("Show just text in tabbar.")
    r2 = QtGui.QRadioButton("Icon and text", stylePanel)
    r2.setObjectName("IconText")
    r2.setToolTip("Show icon and text in tabbar")
    l0.addWidget(r0)
    l0.addWidget(r1)
    l0.addWidget(r2)
    #-----------------------
    """
    l1 = QtGui.QVBoxLayout()
    orientationPanel = QtGui.QGroupBox("Tab orientation:")
    orientationPanel.setLayout(l1)
    r3 = QtGui.QRadioButton("Auto", orientationPanel)
    r3.setObjectName("Auto")
    r3.setToolTip("Set based on the orientation")
    r4 = QtGui.QRadioButton("Top", orientationPanel)
    r4.setObjectName("North")
    r4.setToolTip("Tabs at top")
    r5 = QtGui.QRadioButton("Bottom", orientationPanel)
    r5.setObjectName("South")
    r5.setToolTip("Tabs at bottom")
    r6 = QtGui.QRadioButton("Left", orientationPanel)
    r6.setObjectName("West")
    r6.setToolTip("Tabs at left")
    r7 = QtGui.QRadioButton("Right", orientationPanel)
    r7.setObjectName("East")
    r7.setToolTip("Tabs at right")
    l1.addWidget(r3)
    l1.addWidget(r4)
    l1.addWidget(r5)
    l1.addWidget(r6)
    l1.addWidget(r7)
    """
    #-----------------------
    buttonsPanel = QtGui.QHBoxLayout()    # die untere Leiste mit den Up/down und Close-Buttons
    buttonsPanel.addWidget(btnUp)
    buttonsPanel.addWidget(btnDown)
    buttonsPanel.addStretch(1)
    buttonsPanel.addWidget(btnClose)
    #-----------------------
    l3 = QtGui.QHBoxLayout()
    l3.addStretch()
    l4 = QtGui.QVBoxLayout()
    l4.addWidget(stylePanel)
    #l4.addWidget(g1)
    #----------------------- Right Area
    showWBPanel = QtGui.QVBoxLayout()
    g6 = QtGui.QGroupBox("Show Workbenches as Tabs or as Dropdown:")
    g6.setLayout(showWBPanel)
    r8 = QtGui.QRadioButton("Tabs", g6)
    r8.setObjectName("Tabs")
    r8.setToolTip("Show the workbenches in a tabbar")
    r9 = QtGui.QRadioButton("Dropdown", g6)
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
    l5 = QtGui.QHBoxLayout()
    l5.addWidget(selector)      # All List
    l5.addWidget(groupsPanel)   # Groups
    l5.insertLayout(2, l4)      # Radio-Buttons

    #layout.insertLayout(0, l5)  # die beiden Bereiche Links Liste, Rechts Radio-Buttons
    #layout.insertLayout(1, buttonsPanel)  # die untere Lesite mit den Buttons

    # Create a top-level horizontal layout
    top_layout = QtGui.QHBoxLayout()

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
        #__parameters__.SetString("Unchecked", ",".join(disabled))
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
            #__parameters__.SetString("Position", ",".join(position))
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
            #__parameters__.SetString("Position", ",".join(position))
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
        openFileInEditor(__pathInstructions__)


    def on_lineEdit_clicked():
        global __floatingWidgetWidth__
        # if self.lineEdit.textChanged():
        __floatingWidgetWidth__ = int(lineEdit.displayText())
        __parameters__.SetString("floatingWidth", str(__floatingWidgetWidth__))
        onWorkbenchActivated()


    def onstylePanel(r):
        """Set TabBar style."""
        if r:
            for i in stylePanel.findChildren(QtGui.QRadioButton):
                if i.isChecked():
                    __parameters__.SetString("Style", i.objectName())
            onWorkbenchActivated()

    """
    def onOrientationPanel(r):
        #Set TabBar orientation.
        if r:
            for i in orientationPanel.findChildren(QtGui.QRadioButton):
                if i.isChecked():
                    __parameters__.SetString("Orientation", i.objectName())
            onWorkbenchActivated()
    """

    def onG6(r):
        """Set pref button."""
        if r:
            for i in g6.findChildren(QtGui.QRadioButton):
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
    if not position: position = {}  # prevents error in case __strAll__ has been changed


    # build up the list of WB and set the CheckState        
    for i in position:
        if i in __actions__:
            item = QtGui.QListWidgetItem(selector)
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
