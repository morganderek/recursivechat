README for ChatGPT Automation Python Application
Overview
This Python application leverages the PyQt6 framework to create a GUI application that automates the process of using ChatGPT models to process Excel and CSV files recursively. The application reads input data, sends it to a specified ChatGPT model, and saves the structured outputs to a user-defined file.

Features
GUI Setup: Fully interactive GUI for easy operation.
Model Configuration: Allows users to select between different GPT models.
Dynamic Input/Output: Users can specify input and output files along with the columns to be processed and generated.
Customizable Prompts: Configure the role and instructions for ChatGPT dynamically.
Error Handling: Basic error handling and retry logic for API requests.
Prerequisites
Python 3.x
PyQt6
pandas
OpenAI's Python client library
tenacity
Ensure you have the latest versions of these libraries. You can install any missing libraries using pip:

bash
Copy code
pip install PyQt6 pandas openai tenacity
Installation
Clone the repository:

bash
Copy code
git clone <repository_url>
Navigate to the project directory:

bash
Copy code
cd <project_directory>
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configuration
Before running the application, you must set the OPENAI_API_KEY environment variable:

bash
Copy code
export OPENAI_API_KEY='your-api-key-here'
This API key is required to authenticate requests sent to OpenAI's API.

Usage
To start the application, run the following command in the terminal:

bash
Copy code
python <script_name.py>
How to Use the GUI
Set Role and Instructions: Define what role ChatGPT should play and provide specific instructions for the task.
Select Model: Choose the GPT model you wish to use from the dropdown.
Configure Files and Columns: Use the "Browse" buttons to select input and output files and define the relevant column headings.
Run the Process: Click "Run" to start processing. The GUI will display progress and any errors encountered.
Output
The output will be saved in the format specified by the user in the chosen output file. The output includes dynamically specified columns along with the original data from the input file.

Error Handling
The application will alert the user if mandatory fields are not filled.
Retries are implemented for handling API request failures.
Detailed error messages and logs will help in troubleshooting.
Logging
Logs are generated to provide detailed operational traces, particularly useful for debugging and verifying the system processes.

Limitations
The application currently supports only CSV and Excel file formats.
Error handling for file operations and API interactions is basic and might need enhancement for production use.
Contributing
Contributions to the project are welcome. You can contribute by:

Reporting bugs
Suggesting enhancements
Creating pull requests to propose improvements
Ensure you follow the existing code structure and quality standards.

License
This project is licensed under the MIT License - see the LICENSE file for details.
