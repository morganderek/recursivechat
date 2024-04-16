from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QComboBox, QFileDialog, QMessageBox, QSpacerItem, QSizePolicy,QFrame
from PyQt6.QtCore import pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont
from openai import OpenAI
import pandas as pd
import os
import openai
import csv
import sys
import re  # Import the regular expression module
import logging
import time
import textwrap
from tenacity import retry, stop_after_attempt, wait_fixed

with open('prompt.txt', 'r') as file:
    # Read the content of the file
    promptText = file.read()

with open('promptEnding.txt', 'r') as file:
    # Read the content of the file
    promptEndingText = file.read()    

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Automation")
        self.setGeometry(100, 100, 800, 500)
        self.modelRole = None
        self.modelUsed = None
        self.modelInstruction = None
        self.promptEnding = None
    #    self.openaiApikey = None
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
        self.modelRoleEntry = QLineEdit("You are a helpful expert climate change expert.")
        generalInfoLayout.addWidget(self.modelRoleEntry)

        promptLabel = QLabel("What do you want ChatGpt to do (Prompt)?")
        promptLabel.setFont(bold_font)
        generalInfoLayout.addWidget(promptLabel)
        self.modelInstructionEntry = QTextEdit(promptText)
        generalInfoLayout.addWidget(self.modelInstructionEntry)

        endingLabel = QLabel("How should the retured data be structured (Prompt Ending?)")
        endingLabel.setFont(bold_font)
        generalInfoLayout.addWidget(endingLabel)
        self.promptEndingEntry = QTextEdit(promptEndingText)
        generalInfoLayout.addWidget(self.promptEndingEntry)

        # Model selection
        modelSelectionLayout = QVBoxLayout()
        masterLayout.addLayout(modelSelectionLayout)

        modelLabel = QLabel("Which model should be used?")
        modelLabel.setFont(bold_font)
        modelSelectionLayout.addWidget(modelLabel)
        self.modelUsedCombo = QComboBox()
        self.modelUsedCombo.addItems(['gpt-4','gpt-4-turbo','gpt-3.5-turbo', ])
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
        #self.setLayout(inputLayout)

        inputColumnLabel = QLabel("What is the column heading with your input data:")
        inputColumnLabel.setFont(bold_font)
        inputLayout.addWidget(inputColumnLabel)

        self.inputFilePromptColHeadingEntry = QLineEdit("Data")
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

        self.outputColumnNamesEntry = QLineEdit("1) What, 2) Why Important,3) Why adapt")
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
        self.okButton.clicked.connect(self.on_ok)
        buttonLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        buttonLayout.addWidget(self.cancelButton)

        masterLayout.addLayout(buttonLayout)

    def browse_file(self):
        default_dir = r"C:\Temp"  # Change this to the desired path
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
        self.promptEnding = self.promptEndingEntry.toPlainText()
    #    self.openaiApikey = self.openaiApiEntry.text()
        self.filePath = self.filePathLabel.text()  # Assuming filePathLabel displays the selected file path
        self.outputFilePath = self.outputFilePathLabel.text()  # Assuming outputFilePathLabel displays the selected output file path
        self.inputFilePromptColHeading = self.inputFilePromptColHeadingEntry.text()
        self.outputColumnNames = self.outputColumnNamesEntry.text()
        self.dynamicHeaders = [x.strip() for x in self.outputColumnNames.split(',') if x.strip()]
        self.accept()  # Use QDialog's accept method to close the dialog properly

# Create an OpenAI client instance
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")
else:
    client = OpenAI(api_key=api_key)
    print("API Key found and client instantiated")

""" client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
) """

def main():
    app = QApplication(sys.argv)
    dialog = CustomDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        filePath = dialog.filePath
        modelRole = dialog.modelRole
        modelUsed = dialog.modelUsed
        modelInstruction = dialog.modelInstruction + dialog.promptEnding
        outputFilePath = dialog.outputFilePath
        inputFilePromptColHeading = dialog.inputFilePromptColHeading
        dynamicHeaders = dialog.dynamicHeaders

        print(f"Model Role: {modelRole}")
        print(f"Model Used: {modelUsed}")
        print(f"File Path: {filePath}")
        print(f"Output File Path: {outputFilePath}")
        print(f"Input Column Heading: {inputFilePromptColHeading}")
        print(f"Output Column Names: {dynamicHeaders}")
        print(f"Instruction: {modelInstruction}")

    try:
        file_extension = filePath.split('.')[-1]
        if file_extension.lower() == 'csv':
            df = pd.read_csv(filePath)
        elif file_extension.lower() in ['xls', 'xlsx']:
            df = pd.read_excel(filePath)
        else:
            raise ValueError(f'Unsupported file extension: {file_extension}')
    except ValueError as e:
        messagebox.showerror("File Type Error", str(e))

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def log_retry(attempt):
        logger.info(f"Retrying... Attempt {attempt.retry_state.attempt_number}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def get_chatgpt_response(text):
        response = client.chat.completions.create(
            model=modelUsed,
            messages=[
                {"role": "system", "content": modelRole},
                {"role": "user", "content": modelInstruction},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            timeout=10
        )
        
     #   usage_info = response.get('usage', {})
     #   logging.info(f"ChatGPT usage: {usage_info}")
        return response.choices[0].message.content.strip()

    df.iloc[0:0].to_csv(outputFilePath, index=False)

    def parse_table(table_text):
        lines = table_text.strip().split('\n')
        if lines[0].strip('-|+ \n') == '':
            lines = lines[1:]
        if lines[-1].strip('-|+ \n') == '':
            lines = lines[:-1]

        table_data = []
        for row in lines:
            if row.strip('-|+ \n') == '':
                continue
            columns = re.split(r'\|', row)[1:-1]
            cleaned_columns = [col.strip() for col in columns]
            table_data.append(cleaned_columns)
        return table_data

    headers = list(df.columns) + dynamicHeaders
    with open(outputFilePath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

    for index, row in df.iterrows():
        print(f"Now processing row {index+2}")
        try:
            table_text = get_chatgpt_response(row[inputFilePromptColHeading])
            table_data = parse_table(table_text)
            with open(outputFilePath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for table_row in table_data:
                    output_row = list(row) + table_row
                    writer.writerow(output_row)
        except Exception as e:
            print(f"Error at index {index}: {e}")
            logging.error(f'Error at index {index}: {e}')
            with open(outputFilePath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                error_row = list(row) + ['Error', f'Error at index {index}: {e}']
                writer.writerow(error_row)
                time.sleep(1) 

if __name__ == "__main__":
    main()
