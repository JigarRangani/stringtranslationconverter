import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

def main():
    st.title("String Resource Generator")

    # File upload
    android_file = st.file_uploader("Upload Android string resource sheet (must have columns: string_name, english_value)", type=["xlsx", "xls"])
    translation_file = st.file_uploader("Upload translation sheet (second column name must be english_value)", type=["xlsx", "xls"])

    if android_file and translation_file:
        android_df = pd.read_excel(android_file)
        translation_df = pd.read_excel(translation_file)

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
            if uploaded_file.name.endswith(".xml"):
                sheet_data = xml_to_sheet(uploaded_file)
            else:  # Assuming .strings file
                sheet_data = strings_to_sheet(uploaded_file)
            st.download_button("Download Sheet", sheet_data.to_csv(index=False), file_name="strings.csv")

def generate_android_xml(android_df, translation_df, start_row, end_row):
    """Generates separate XML files for each language (Android)."""
    return generate_xml(android_df, translation_df, start_row, end_row, "android")


def generate_ios_strings(android_df, translation_df, start_row, end_row):
    """Generates separate .strings files for each language (iOS)."""

    languages = translation_df.columns[1:]
    outputs = {}

    for lang in languages:
        output_string = ""
        for i in range(start_row, end_row + 1):
            row = android_df.iloc[i]
            string_name = row['string_name']
            english_value = row['english_value']

            # Get translation for the current language
            try:
                translation = translation_df.loc[
                    translation_df['english_value'] == english_value, lang
                ].values[0]
            except (KeyError, IndexError) as e:
                translation = english_value  # Fallback to English
                print(f"Warning: No translation found for '{english_value}' in '{lang}'")
                
            if pd.notna(translation):
                value = translation
            else:
                value = english_value  # Fallback to English

            output_string += f'"{english_value}" = "{value}";\n'  # iOS format

        outputs[lang] = output_string
    return outputs

def generate_xml(android_df, translation_df, start_row, end_row, platform):
    """Generates XML or .strings files based on the platform."""

    languages = translation_df.columns[1:]
    outputs = {}

    for lang in languages:
        if platform == "android":
            output_string = '<resources>\n'
            string_tag = "string"
        elif platform == "ios":
            output_string = ""
            string_tag = '"{string_name}"'

        for i in range(start_row, end_row + 1):
            row = android_df.iloc[i]
            string_name = row['string_name']
            english_value = row['english_value']

            # Get translation for the current language
            try:
                translation = translation_df.loc[
                    translation_df['english_value'] == english_value, lang
                ].values[0]
            except (KeyError, IndexError) as e:
                translation = english_value  # Fallback to English
                print(f"Warning: No translation found for '{english_value}' in '{lang}'")

            if pd.notna(translation):
                value = translation
            else:
                value = english_value  # Fallback to English

            if platform == "android":
                output_string += f'    <{string_tag} name="{string_name}">{value}</{string_tag}>\n'
            elif platform == "ios":
                output_string += f'    {string_tag.format(string_name=string_name)} = "{value}";\n'

        if platform == "android":
            output_string += '</resources>'

        outputs[lang] = output_string
    return outputs


def xml_to_sheet(xml_file):
    """Converts an XML string resource file to a Pandas DataFrame."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    data = []
    for string_element in root.findall('string'):
        data.append({'string_name': string_element.get('name'), 'value': string_element.text})
    return pd.DataFrame(data)

def strings_to_sheet(strings_file):
    """Converts an iOS .strings file to a Pandas DataFrame."""
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
