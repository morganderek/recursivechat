# README for ChatGPT Automation Python Application
## Overview
This Python application automates the process of prompting ChatGPT models. The application reads input data in the Excel file, appends it to a prompt and sends it to a specified ChatGPT model, and saves the structured outputs to the output file. It repeats thsi process this for each rows of data in the Excel file. 
User input is collected using PyQt6 to create a GUI application.

## Features
GUI Setup: Fully interactive GUI for easy operation.
Model Configuration: Allows users to select between different GPT models.
Dynamic Input/Output: Users can specify input and output files along with the columns to be processed and generated.
Customizable Prompts: Configure the role and instructions for ChatGPT dynamically.
Error Handling: Basic error handling and retry logic for API requests.

## Prerequisites
`pip install PyQt6 pandas openai tenacity`

The openai version is - 1.17.1 (https://pypi.org/project/openai/)

## Installation
Clone the repository:
`git clone https://github.com/morganderek/recursivechat`

Navigate to the project directory:
`cd <project_directory>`

Install dependencies:
`pip install -r requirements.txt`

## Configuration
An API key is required to authenticate requests sent to OpenAI's API.

Before running the application, you must set the OPENAI_API_KEY environment variable. See (https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)


## Usage
Set default GUI values in the defaultUIValues.txt file
To start the application, run the following command in the terminal:

`python main.py`

## How to Use the GUI
When GUI open, you can change the default values

Role: What is the role of the LLM. Something similar to your are an expert in XXX

Prompt: Provide specific instructions for the task.

Style: What tone of language do you want the results to be?

Select Model: Choose the GPT model you wish to use from the dropdown.

Configure Files and Columns: Use the "Browse" buttons to select input and output files and define the relevant column headings.

Run the Process: Click "Run" to start processing. The GUI will display progress and any errors encountered.

## Input

The input data should contain all the text you want to append to the standard prompt in one cell. The script will send the standard prompt, plus the text in the cell and return it to a new CSV. The script then repeats for the next cell until all the data in the input file is complete. 

## Output
The output will be saved in the format specified by the user in the chosen output file. The output includes dynamically specified columns along with the original data from the input file.

## Error Handling
The application will alert the user if mandatory fields are not filled.
Retries are implemented for handling API request failures.
Detailed error messages and logs will help in troubleshooting.

## Logging
Logs are generated to provide detailed operational traces, particularly useful for debugging and verifying the system processes.

## Limitations
The application currently supports only CSV and Excel file formats.
Error handling for file operations and API interactions is basic and might need enhancement for production use.

## Contributing
Contributions to the project are welcome.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
