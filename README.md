# String Resource Generator

This is a Streamlit application designed to streamline the process of managing and converting string resources for mobile app development, supporting both Android and iOS platforms.

## Purpose

The main goal of this tool is to simplify the localization workflow by allowing developers to:

-   Generate platform-specific string resource files (XML for Android, .strings for iOS) from a standardized Excel sheet.
-   Convert existing XML or .strings files back into a CSV sheet for easier editing and management.

## Setup

To run this application locally, you'll need Python and `pip` installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/string-resource-generator.git
    cd string-resource-generator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

2.  **Generating String Resources:**
    -   Upload your Android string resource sheet (in `.xlsx` or `.xls` format). This file must contain `string_name` and `english_value` columns.
    -   Upload your translation sheet, where the second column is `english_value` and subsequent columns contain translations for different languages.
    -   Select the start and end rows you wish to process.
    -   Click "Generate Android XML" or "Generate iOS Strings" to create and download the respective files.

3.  **Converting Files to a Sheet:**
    -   Upload an existing `.xml` or `.strings` file.
    -   Click "Convert to Sheet" to generate a CSV file that you can download and edit.
