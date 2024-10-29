import streamlit as st
import pandas as pd

def main():
    st.title("Android String Resource Generator")

    # File upload
    android_file = st.file_uploader("Upload Android string resource sheet", type=["xlsx", "xls"])
    translation_file = st.file_uploader("Upload translation sheet", type=["xlsx", "xls"])

    if android_file and translation_file:
        android_df = pd.read_excel(android_file)
        translation_df = pd.read_excel(translation_file)

        # Display DataFrames
        st.subheader("Android String Resource Sheet")
        st.dataframe(android_df)

        st.subheader("Translation Sheet")
        st.dataframe(translation_df)

        # Row selection
        start_row = st.number_input("Start row", min_value=0, max_value=len(android_df) - 1, value=0)
        end_row = st.number_input("End row", min_value=start_row, max_value=len(android_df) - 1, value=len(android_df) - 1)

        if st.button("Generate XML"):
            xml_outputs = generate_xml(android_df, translation_df, start_row, end_row)

            # Download buttons for each language
            for lang, xml_string in xml_outputs.items():
                st.download_button(f"Download {lang} XML", xml_string, file_name=f"strings_{lang}.xml")

def generate_xml(android_df, translation_df, start_row, end_row):
    """Generates separate XML files for each language."""

    languages = translation_df.columns[1:]  # Get language columns

    xml_outputs = {}  # Dictionary to store XML outputs for each language

    for lang in languages:
        xml_string = '<resources>\n'
        for i in range(start_row, end_row + 1):
            row = android_df.iloc[i]
            string_name = row['string_name']
            english_value = row['english_value']

            xml_string += f'    <string name="{string_name}">'

            # Get translation for the current language
            translation = translation_df.loc[
                translation_df['english_value'] == english_value, lang
            ].values[0]

            if pd.notna(translation):
                xml_string += f'{translation}'
            else:
                xml_string += f'{english_value}'  # Fallback to English

            xml_string += '</string>\n'

        xml_string += '</resources>'
        xml_outputs[lang] = xml_string  # Store XML for the language

    return xml_outputs

if __name__ == "__main__":
    main()