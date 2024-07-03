from PyQt6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QTextEdit, QComboBox, QFileDialog,
                             QMessageBox, QFrame)
from PyQt6.QtGui import QFont
import os

def read_defaultUIValues_file(filename):
    defaults = {"Role": "You are a helpful expert climate change expert.",  # Default values
                "Prompt": "Insert your detailed prompt here.",
                "PromptStyle": "This is the text: ",
                "InputColHeading": "Data",
                "ColumnHeadings": "1,2,3",
                "FilePath": "C:\Temp"}
    if not os.path.exists(filename):
        return defaults["Role"], defaults["Prompt"],defaults["PromptStyle"], defaults["InputColHeading"], defaults["ColumnHeadings"], defaults["FilePath"]
    
    with open(filename, 'r') as file:
        for line in file:
            if '|' in line:
                key, value = line.split('|', 1)  # Split on the first colon
                key = key.strip()
                value = value.strip()
                if key in defaults:
                    defaults[key] = value
    
    return defaults["Role"], defaults["Prompt"], defaults["PromptStyle"], defaults["InputColHeading"], defaults["ColumnHeadings"], defaults["FilePath"]

# Read from defaultUIValues.txt
default_role, default_instruction, default_PromptStyle, default_InputColHeading, default_ColumnHeadings, default_Filepath = read_defaultUIValues_file('defaultUIValues.txt')

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Automation")
        self.setGeometry(100, 100, 800, 500)
        self.modelRole = None
        self.modelUsed = None
        self.modelInstruction = None
        self.modelInstructionStyle = None
        self.filePath = None
        self.outputFilePath = None
        self.inputFilePromptColHeading = None
        self.outputColumnNames = None
        self.dynamicHeaders = None
        self.initUI()

    def initUI(self):
        # Master layout
        masterLayout = QVBoxLayout()
        masterLayout.setSpacing(10)  # Adjust the amount of space as needed
        self.setLayout(masterLayout)
        
        # Create QFont object for bold labels
        bold_font = QFont("Helvetica", 10)
        bold_font.setBold(True)
        subheading_font = QFont("Helvetica", 13)
        subheading_font.setBold(True)

        # ChatGPT Role and Instructions
        generalInfoLayout = QVBoxLayout()
        masterLayout.addLayout(generalInfoLayout)
        
        formHeader = QLabel("ChatGPT Excel Recursive Processor")
        formHeader.setFont(subheading_font)
        generalInfoLayout.addWidget(formHeader)

        roleLabel = QLabel("What role should ChatGpt play (Role)?")
        roleLabel.setFont(bold_font)
        generalInfoLayout.addWidget(roleLabel)
        self.modelRoleEntry = QLineEdit(default_role)
        generalInfoLayout.addWidget(self.modelRoleEntry)

        promptLabel = QLabel("What do you want ChatGpt to do (Prompt)?")
        promptLabel.setFont(bold_font)
        generalInfoLayout.addWidget(promptLabel)
        self.modelInstructionEntry = QTextEdit(default_instruction)
        generalInfoLayout.addWidget(self.modelInstructionEntry)

        # Prompt Ending
        promptStyleLabel = QLabel("What style do want ChatGpt to communicate in?")
        promptStyleLabel.setFont(bold_font)
        generalInfoLayout.addWidget(promptStyleLabel)
        self.modelInstructionStyleEntry = QTextEdit(default_PromptStyle)
        generalInfoLayout.addWidget(self.modelInstructionStyleEntry)

        # Model selection
        modelSelectionLayout = QVBoxLayout()
        masterLayout.addLayout(modelSelectionLayout)

        modelLabel = QLabel("Which model should be used?")
        modelLabel.setFont(bold_font)
        modelSelectionLayout.addWidget(modelLabel)
        self.modelUsedCombo = QComboBox()
        self.modelUsedCombo.addItems(['gpt-4o','gpt-4','gpt-4-turbo','gpt-3.5-turbo', ])
        modelSelectionLayout.addWidget(self.modelUsedCombo)

        # Insert horizontal line separator before input configuration
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        masterLayout.addWidget(line)  # Ensure this is added to the correct layout

        # Input and Output Configuration
        configLayout = QHBoxLayout()
        masterLayout.addLayout(configLayout)

        # Column 1: Input File Configuration
        inputLayout = QVBoxLayout()
        inputHeader = QLabel("Input Data")
        inputHeader.setFont(subheading_font)
        inputLayout.addWidget(inputHeader)

        inputLabel = QLabel("Select file where your input data is stored:")
        inputLabel.setFont(bold_font)
        inputLayout.addWidget(inputLabel)

        self.fileButton = QPushButton("Browse")
        self.fileButton.clicked.connect(self.browse_file)
        inputLayout.addWidget(self.fileButton)

        self.filePathLabel = QLabel("No input file selected")
        inputLayout.addWidget(self.filePathLabel)
        
        inputColumnLabel = QLabel("What is the column heading with your input data:")
        inputColumnLabel.setFont(bold_font)
        inputLayout.addWidget(inputColumnLabel)

        self.inputFilePromptColHeadingEntry = QLineEdit(default_InputColHeading)
        inputLayout.addWidget(self.inputFilePromptColHeadingEntry)
        configLayout.addLayout(inputLayout)

        # Vertical Divider
        vertical_line = QFrame()
        vertical_line.setFrameShape(QFrame.Shape.VLine)
        vertical_line.setFrameShadow(QFrame.Shadow.Sunken)
        vertical_line.setStyleSheet("color: #b1b1b1;")  # Set color to light grey (optional)
        configLayout.addWidget(vertical_line)

        # Column 2: Output File Configuration
        outputLayout = QVBoxLayout()
        outputHeader = QLabel("Output Data")
        outputHeader.setFont(subheading_font)
        outputLayout.addWidget(outputHeader)

        outputLabel = QLabel("Select file where your output data will be saved:")
        outputLabel.setFont(bold_font)
        outputLayout.addWidget(outputLabel)

        self.outputFileButton = QPushButton("Browse")
        self.outputFileButton.clicked.connect(self.browse_output_file)
        outputLayout.addWidget(self.outputFileButton)

        self.outputFilePathLabel = QLabel("No output file selected")
        outputLayout.addWidget(self.outputFilePathLabel)

        outputColumnLabel = QLabel("What are the output column names (comma-separated):")
        outputColumnLabel.setFont(bold_font)
        outputLayout.addWidget(outputColumnLabel)

        self.outputColumnNamesEntry = QLineEdit(default_ColumnHeadings)
        outputLayout.addWidget(self.outputColumnNamesEntry)
        configLayout.addLayout(outputLayout)

        # Insert horizontal line separator before input configuration
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        masterLayout.addWidget(line)  # Ensure this is added to the correct layout

        # Bottom buttons
        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton("Run")
        self.okButton.setDefault(True)  # Make this the default button
        self.okButton.setStyleSheet("background-color: #4682B4; color: white; font-weight: bold;")  # Steel blue color
        self.okButton.clicked.connect(self.on_ok)
        buttonLayout.addWidget(self.okButton)


        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        buttonLayout.addWidget(self.cancelButton)
        masterLayout.addLayout(buttonLayout)

    def browse_file(self):
        default_dir = (default_Filepath)
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", default_dir, "CSV files (*.csv);;Excel files (*.xlsx)")
        if filePath:
            self.filePath = filePath
            self.filePathLabel.setText(self.filePath)
            self.lastDir = os.path.dirname(filePath)  # Update lastDir to the folder of the opened file
        else:
            self.filePathLabel.setText("No file selected. Please select a file.")
    
    def browse_output_file(self):
        outputFilePath, _ = QFileDialog.getOpenFileName(self, "Save File", "", "CSV files (*.csv);;Excel files (*.xlsx)")
        if outputFilePath:
            self.outputFilePath = outputFilePath
            self.outputFilePathLabel.setText(self.outputFilePath)
            self.lastDir = os.path.dirname(outputFilePath)  # Update lastDir to the folder of the opened file
        else:
            self.outputFilePathLabel.setText("No file selected. Please select a file.")

    def on_ok(self):
        if not self.filePath or not self.outputFilePath:
            QMessageBox.warning(self, "Warning", "You must select both input and output data files before proceeding.")
            return

        self.modelRole = self.modelRoleEntry.text()
        self.modelUsed = self.modelUsedCombo.currentText()
        self.modelInstruction = self.modelInstructionEntry.toPlainText()
        self.modelInstructionStyle = self.modelInstructionStyleEntry.toPlainText()
        self.filePath = self.filePathLabel.text()  # Assuming filePathLabel displays the selected file path
        self.outputFilePath = self.outputFilePathLabel.text()  # Assuming outputFilePathLabel displays the selected output file path
        self.inputFilePromptColHeading = self.inputFilePromptColHeadingEntry.text()
        self.outputColumnNames = self.outputColumnNamesEntry.text()
        self.dynamicHeaders = [x.strip() for x in self.outputColumnNames.split(',') if x.strip()]
                # Call format_prompt to generate and print the promptEnding
        self.format_prompt()
        super(CustomDialog, self).accept()

    def format_prompt(self):
            headers_string = ', '.join(self.dynamicHeaders)
            self.promptEnding = f" Return only a table in the completion. Return the response in a table with the columns {headers_string}.  I don't want any other comments. Don't say 'here is your summary' or similar remarks."
            #print(self.promptEnding)
