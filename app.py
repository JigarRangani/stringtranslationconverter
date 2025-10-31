import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

def main():
    """Initializes and runs the Streamlit application.

    This function sets up the user interface for the String Resource Generator,
    including file uploaders for Android and translation sheets, input fields for
    row selection, and buttons to trigger the generation of Android XML and iOS
    .strings files. It also provides functionality to convert XML and .strings
    files back into a sheet format.
    """
    st.title("String Resource Generator")

    # File upload
    android_file = st.file_uploader("Upload Android string resource sheet (must have columns: string_name, english_value)", type=["xlsx", "xls"])
    translation_file = st.file_uploader("Upload translation sheet (second column name must be english_value)", type=["xlsx", "xls"])

    if android_file and translation_file:
        try:
            android_df = pd.read_excel(android_file)
            translation_df = pd.read_excel(translation_file)
        except Exception as e:
            st.error(f"Error reading Excel files: {e}")
            return

        # --- File validation ---
        required_android_cols = ['string_name', 'english_value']
        if not all(col in android_df.columns for col in required_android_cols):
            st.error("The Android string resource sheet must contain 'string_name' and 'english_value' columns.")
            return

        if 'english_value' not in translation_df.columns:
            st.error("The translation sheet must contain an 'english_value' column to map translations.")
            return

        # Display DataFrames
        st.subheader("String Resource Sheet")
        st.dataframe(android_df)

        st.subheader("Translation Sheet")
        st.dataframe(translation_df)

        # Row selection
        start_row = st.number_input("Start row", min_value=0, max_value=len(android_df) - 1, value=0)
        end_row = st.number_input("End row", min_value=start_row, max_value=len(android_df) - 1, value=len(android_df) - 1)

        if st.button("Generate Android XML"):
            xml_outputs = generate_android_xml(android_df, translation_df, start_row, end_row)
            for lang, xml_string in xml_outputs.items():
                st.download_button(f"Download Android {lang} XML", xml_string, file_name=f"strings_{lang}.xml")
        
        if st.button("Generate iOS Strings"):
            strings_outputs = generate_ios_strings(android_df, translation_df, start_row, end_row)
            for lang, strings_string in strings_outputs.items():
                st.download_button(f"Download iOS {lang} Strings", strings_string, file_name=f"{lang}.strings")

    # XML/Strings to sheet conversion
    uploaded_file = st.file_uploader("Upload XML/Strings file to convert to sheet", type=["xml", "strings"])
    if uploaded_file:
        if st.button("Convert to Sheet"):
            try:
                if uploaded_file.name.endswith(".xml"):
                    sheet_data = xml_to_sheet(uploaded_file)
                else:  # Assuming .strings file
                    sheet_data = strings_to_sheet(uploaded_file)

                if not sheet_data.empty:
                    st.download_button("Download Sheet", sheet_data.to_csv(index=False), file_name="strings.csv")
                else:
                    st.warning("The uploaded file appears to be empty or incorrectly formatted.")
            except Exception as e:
                st.error(f"An error occurred during file conversion: {e}")

def generate_android_xml(android_df, translation_df, start_row, end_row):
    """Generates separate XML files for each language for Android.

    Args:
        android_df (pd.DataFrame): DataFrame containing the string resources,
                                   with columns 'string_name' and 'english_value'.
        translation_df (pd.DataFrame): DataFrame containing translations, where the
                                       first column is 'english_value' and subsequent
                                       columns are language codes.
        start_row (int): The starting row index for processing strings.
        end_row (int): The ending row index for processing strings.

    Returns:
        dict: A dictionary where keys are language codes and values are the
              corresponding XML content as strings.
    """
    return generate_string_files(android_df, translation_df, start_row, end_row, "android")


def generate_ios_strings(android_df, translation_df, start_row, end_row):
    """Generates separate .strings files for each language for iOS.

    Args:
        android_df (pd.DataFrame): DataFrame with columns 'string_name' and
                                   'english_value'.
        translation_df (pd.DataFrame): DataFrame where the first column is
                                       'english_value' and subsequent columns
                                       are language codes with translations.
        start_row (int): The starting row index for processing.
        end_row (int): The ending row index for processing.

    Returns:
        dict: A dictionary where keys are language codes and values are the
              corresponding .strings content.
    """
    return generate_string_files(android_df, translation_df, start_row, end_row, "ios")


def generate_string_files(android_df, translation_df, start_row, end_row, platform):
    """Generates XML or .strings files based on the specified platform.

    This function iterates through the provided DataFrames to generate
    platform-specific string resource files for each language.

    Args:
        android_df (pd.DataFrame): DataFrame containing the base strings with
                                   'string_name' and 'english_value'.
        translation_df (pd.DataFrame): DataFrame with translations, where the
                                       first column is 'english_value' and the
                                       rest are language codes.
        start_row (int): The starting row index from which to process strings.
        end_row (int): The ending row index for processing.
        platform (str): The target platform, either 'android' or 'ios'.

    Returns:
        dict: A dictionary where keys are language codes and values are the
              generated file content as strings.
    """
    languages = translation_df.columns[1:]
    outputs = {}

    warnings = []

    for lang in languages:
        output_lines = []
        if platform == "android":
            output_lines.append('<resources>')

        for i in range(start_row, end_row + 1):
            row = android_df.iloc[i]
            string_name = row['string_name']
            english_value = row['english_value']

            # Get translation for the current language
            try:
                translation_val = translation_df.loc[
                    translation_df['english_value'] == english_value, lang
                ].values[0]
                if pd.notna(translation_val) and str(translation_val).strip():
                    value = translation_val
                else:
                    value = english_value  # Fallback to English
                    warnings.append(f"Empty translation for '{english_value}' in '{lang}'. Using English value.")
            except (KeyError, IndexError):
                value = english_value  # Fallback to English
                warnings.append(f"No translation found for '{english_value}' in '{lang}'. Using English value.")

            if platform == "android":
                output_lines.append(f'    <string name="{string_name}">{value}</string>')
            elif platform == "ios":
                output_lines.append(f'"{english_value}" = "{value}";')

        if platform == "android":
            output_lines.append('</resources>')

        outputs[lang] = "\n".join(output_lines)

    if warnings:
        st.warning("Translation warnings:\n\n" + "\n".join(warnings))

    return outputs


def xml_to_sheet(xml_file):
    """Converts an XML string resource file to a Pandas DataFrame.

    Args:
        xml_file (UploadedFile): The uploaded XML file object from Streamlit.

    Returns:
        pd.DataFrame: A DataFrame with 'string_name' and 'value' columns.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    data = []
    for string_element in root.findall('string'):
        data.append({'string_name': string_element.get('name'), 'value': string_element.text})
    return pd.DataFrame(data)

def strings_to_sheet(strings_file):
    """Converts an iOS .strings file to a Pandas DataFrame.

    Args:
        strings_file (UploadedFile): The uploaded .strings file object from
                                     Streamlit.

    Returns:
        pd.DataFrame: A DataFrame with 'string_name' and 'value' columns.
    """
    data = []
    for line in strings_file:
        line = line.decode("utf-8").strip()  # Decode from bytes and remove whitespace
        if line and not line.startswith("//"):  # Ignore empty and comment lines
            string_name, value = line.split(" = ")
            string_name = string_name.strip('"')  # Remove quotes
            value = value.strip('";')  # Remove quotes and semicolon
            data.append({'string_name': string_name, 'value': value})
    return pd.DataFrame(data)

if __name__ == "__main__":
    main()
