from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog
import sys
import os
import pandas as pd
import csv
import re  # Import the regular expression module
import logging
import time
from tenacity import retry, stop_after_attempt, wait_fixed, after_log
from openai import OpenAI
from ui import CustomDialog  # Import the CustomDialog class from ui.py

# Create an OpenAI client instance
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")
else:
    client = OpenAI(api_key=api_key)
    print("API Key found and client instantiated")

def main():
    app = QApplication(sys.argv) #launch GUI
    dialog = CustomDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted: #get data from GUI
        filePath = dialog.filePath
        modelRole = dialog.modelRole
        modelUsed = dialog.modelUsed
        modelInstruction = dialog.modelInstruction + dialog.promptEnding + dialog.modelInstructionStyle
        outputFilePath = dialog.outputFilePath
        inputFilePromptColHeading = dialog.inputFilePromptColHeading
        dynamicHeaders = dialog.dynamicHeaders
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
        QMessageBox.critical(None, "File Type Error", str(e))

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def log_retry(retry_state):
        logger.info(f"Retrying... Attempt {retry_state.attempt_number}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), after=after_log(logger, log_level=logging.INFO))
    def get_chatgpt_response(text): #main chatGPT function
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
        return response.choices[0].message.content.strip()

    # Write an empty DataFrame with the same columns as df to the output file to create headers
    df.iloc[0:0].to_csv(outputFilePath, index=False)

    def parse_table(table_text):
        # Split the table_text into lines based on newline characters
        lines = table_text.strip().split('\n')
        # Remove the first line if it only consists of '-', '|', '+', ' ', or newline characters
        if lines[0].strip('-|+ \n') == '':
            lines = lines[1:]
        # Remove the last line if it only consists of '-', '|', '+', ' ', or newline characters
        if lines[-1].strip('-|+ \n') == '':
            lines = lines[:-1]

        # Initialize an empty list to hold the parsed table data
        table_data = []
        # Iterate over each line in the processed lines list
        for row in lines:
            # Skip the row if it only consists of '-', '|', '+', ' ', or newline characters
            if row.strip('-|+ \n') == '':
                continue
            # Split the row into columns based on the '|' character, excluding the first and last split parts
            columns = re.split(r'\|', row)[1:-1]
            # Strip whitespace from each column and add it to the list
            cleaned_columns = [col.strip() for col in columns]
            # Append the cleaned columns list to table_data
            table_data.append(cleaned_columns)
        # Return the parsed table data
        return table_data

    # Combine the original DataFrame columns with the dynamicHeaders for the output CSV
    headers = list(df.columns) + dynamicHeaders
    # Open the output file in write mode to write headers
    with open(outputFilePath, mode='w', newline='', encoding='utf-8') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the headers row
        writer.writerow(headers)

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Get the input text for the current row based on inputFilePromptColHeading
        input_text = row[inputFilePromptColHeading]
        #print(f"Now processing row {index+2}: {input_text}")  # Print current input text being processed
        print(f"Now processing row {index+2}")  # Print current row rather than input text being processed
        try:
            # Call the get_chatgpt_response function with the input text to get the table text
            table_text = get_chatgpt_response(input_text)
            # Parse the table text into a list of lists (rows and columns)
            table_data = parse_table(table_text)
            # Open the output file in append mode to write the processed rows
            with open(outputFilePath, mode='a', newline='', encoding='utf-8') as file:
                # Create a CSV writer object
                writer = csv.writer(file)
                # Iterate over each row in the parsed table data
                for table_row in table_data:
                    # Combine the original row data with the parsed table row data
                    output_row = list(row) + table_row
                    # Write the combined row to the output file
                    writer.writerow(output_row)
        except Exception as e:
            # Print and log the error if any occurs during processing
            print(f"Error at index {index}: {e}")
            logging.error(f'Error at index {index}: {e}')
            # Open the output file in append mode to write the error row
            with open(outputFilePath, mode='a', newline='', encoding='utf-8') as file:
                # Create a CSV writer object
                writer = csv.writer(file)
                # Write an error row indicating the error and the index at which it occurred
                error_row = list(row) + ['Error', f'Error at index {index}: {e}']
                writer.writerow(error_row)
                # Pause for 1 second after handling the error
                time.sleep(1)


if __name__ == "__main__":
    main()
