from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QComboBox, QFileDialog, QMessageBox, QSpacerItem, QSizePolicy,QFrame
from PyQt6.QtCore import pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont
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

api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
else:
    print("API Key found")

class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Automation")
        self.setGeometry(100, 100, 800, 500)
        self.modelRole = None
        self.modelUsed = None
        self.modelInstruction = None
        self.promptEnding = None
        self.openaiApikey = None
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
        self.modelInstructionEntry = QTextEdit("I am writing a report for the Coventry city council in the UK on their future climate change risks. I am using the summary document CCRA-Evidence-Report-England-Summary to introduce each risk. I need you to draft a summary for a specific risk or opportunity. The summary should broadly explain what the risk or opportunity is. Please use this structure. Explain what the risk or opportunity is Explain why its important in the context of cities like Coventry in England Explain why its important to begin adapting to it. ")
        generalInfoLayout.addWidget(self.modelInstructionEntry)

        endingLabel = QLabel("How should the retured data be structured (Prompt Ending?)")
        endingLabel.setFont(bold_font)
        generalInfoLayout.addWidget(endingLabel)
        self.promptEndingEntry = QTextEdit("Return the response in a table with 3 columns, 1) What, 2) Why Important and 3) Why adapt. Return only a table in the completion. I don't want any other comments. Don't say -here is your summary- or similar remarks. Please use plain language in the summary. This is the text I want you to summarise: ")
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

        openaiApiLabel = QLabel("What is your OpenAI API Key?")
        openaiApiLabel.setFont(bold_font)
        generalInfoLayout.addWidget(openaiApiLabel)
        self.openaiApiEntry = QLineEdit(api_key)
        generalInfoLayout.addWidget(self.openaiApiEntry)

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
        default_dir = r"C:\Users\morga\OneDrive - CAG Consultants\04 Tech\Python Scripts\ChatGPT"  # Change this to the desired path
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
        self.openaiApikey = self.openaiApiEntry.text()
        self.filePath = self.filePathLabel.text()  # Assuming filePathLabel displays the selected file path
        self.outputFilePath = self.outputFilePathLabel.text()  # Assuming outputFilePathLabel displays the selected output file path
        self.inputFilePromptColHeading = self.inputFilePromptColHeadingEntry.text()
        self.outputColumnNames = self.outputColumnNamesEntry.text()
        self.dynamicHeaders = [x.strip() for x in self.outputColumnNames.split(',') if x.strip()]
        self.accept()  # Use QDialog's accept method to close the dialog properly

def main():
    app = QApplication(sys.argv)
    dialog = CustomDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Extract the file path once and use it locally
        filePath = dialog.filePath
        modelRole = dialog.modelRole
        modelUsed = dialog.modelUsed
        modelInstruction = dialog.modelInstruction +dialog.promptEnding
        outputFilePath = dialog.outputFilePath
        inputFilePromptColHeading = dialog.inputFilePromptColHeading
        dynamicHeaders = dialog.dynamicHeaders

    #Set the API key
        openai.api_key = dialog.openaiApikey

        print(f"Model Role: {modelRole}")
        print(f"Model Used: {modelUsed}")
        print(f"OpenAIAPI: {dialog.openaiApikey}")
        print(f"File Path: {filePath}")
        print(f"Output File Path: {outputFilePath}")
        print(f"Input Column Heading: {inputFilePromptColHeading}")
        print(f"Output Column Names: {dynamicHeaders}")
        print(f"Instruction: {modelInstruction}")

    # Determine the file extension
    try:
        file_extension = filePath.split('.')[-1]

        # Load the file accordingly
        if file_extension.lower() == 'csv':
            df = pd.read_csv(filePath)
        elif file_extension.lower() in ['xls', 'xlsx']:
            df = pd.read_excel(filePath)
        else:
            raise ValueError(f'Only upload EXCEL or CSV files. Unsupported file extension: {file_extension}')
    except ValueError as e:
        messagebox.showerror("File Type Error", str(e))

    # Configure logging (writes to the terminal when there is a retry on the get_chatgpt_response function)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # a function that logs a message whenever a retry is about to happen
    def log_retry(attempt):
        logger.info(f"Retrying... Attempt {attempt.retry_state.attempt_number}")

    # Updated function to get a response from gpt
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1)) # Retry the prompt 3 times if there is a problem with a 1 second wait

    # ChatGPT Call function, passing in text
    def get_chatgpt_response(text):
        response = openai.ChatCompletion.create(
            model=modelUsed,
            messages=[
                {"role": "system", "content": modelRole},
                {"role": "user", "content": modelInstruction},
                {"role": "user", "content": text}
            ],
        temperature=0.1, #A higher temperature (e.g., 0.7) results in more diverse and creative output, while a lower temperature (e.g., 0.2) makes the output more deterministic and focused.
        #stop=["\n"],
        timeout=10  # sets a 10-second timeout for the request
        )

    # extract the usage part of the loggin info
        usage_info = response.get('usage', {})
        logging.info(f"ChatGPT usage: {usage_info}")
        # alternative here for all data is logging.info(f'ChatGPT response: {response}')
        return response['choices'][0]['message']['content'].strip() 

    # Write the header to the output CSV file
    df.iloc[0:0].to_csv(outputFilePath, index=False)  # Write an empty DataFrame with the same columns to create the CSV with headers

    # Function to split resulting table into rows and columns
    def parse_table(table_text):
        # Split the text into lines
        lines = table_text.strip().split('\n')

        # Check if the first and last lines are borders (optional based on your data structure)
        if lines[0].strip('-|+ \n') == '':
            lines = lines[1:]  # Remove the first line if it's a border
        if lines[-1].strip('-|+ \n') == '':
            lines = lines[:-1]  # Remove the last line if it's a border

        # Initialize an empty list to hold the cleaned table data
        table_data = []
        for row in lines:
            # Check if the row is a dash separator line
            if row.strip('-|+ \n') == '':
                continue  # Skip this row if it's a separator line

            # Split the row into columns and strip whitespace
            columns = re.split(r'\|', row)[1:-1]
            cleaned_columns = [col.strip() for col in columns]
            table_data.append(cleaned_columns)

        return table_data

    #write headers to columns in output file
    headers = list(df.columns) + dynamicHeaders
    with open(outputFilePath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

    # Process each row, update the data columns, and append to the CSV file
    for index, row in df.iterrows():
        print(f"Now processing row {index+2}")  # Prints the current row being processed
        try:
            table_text = get_chatgpt_response(row[inputFilePromptColHeading])
            table_data = parse_table(table_text)
            # Append the parsed rows to the CSV file
            with open(outputFilePath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for table_row in table_data:
                    # Include the input data for the first row
                    output_row = list(row) + table_row
                    writer.writerow(output_row)
        except Exception as e:
            print(f"Error at index {index}: {e}")
            logging.error(f'Error at index {index}: {e}')  # Logging the error
            # Append an error row to the CSV file
            with open(outputFilePath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                error_row = list(row) + ['Error', f'Error at index {index}: {e}']
                writer.writerow(error_row)
                time.sleep(1)

if __name__ == "__main__":
    main()
