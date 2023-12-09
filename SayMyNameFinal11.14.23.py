import csv
from gtts import gTTS
import os
import pronouncing
import streamlit as st
import snowflake.connector


class TextToSpeechConverter:
    def __init__(self):
        self.accent_options: dict[str, str] = {
            "American English": "en",
            "British English": "en-uk",
            "Australian English": "en-au",
            "Indian English": "en-in",
            "Spanish": "es",
            "Mexican Spanish": "es-mx",
            "French": "fr",
            "Canadian French": "fr-ca",
            "German": "de",
            "Italian": "it",
            "Japanese": "ja",
            "Portuguese": "pt",
            "Brazilian Portuguese": "pt-br",
            "Russian": "ru",
            "Chinese (Simplified)": "zh",
            "Chinese (Traditional)": "zh-tw",
            "Korean": "ko",
            "Arabic": "ar",
            # Add more accent options as needed
        }

    st.session_state.first_name = ""
    st.session_state.last_name = ""
    st.session_state.student_id = ""
    st.session_state.id_found = False 
    student_id = ""
    first_name = ""
    last_name = ""
    first_name_spelling = ""
    
    @staticmethod
    def prompt_user_for_name() -> None:
        name = st.text_input(
            label="Student ID / Name",
            placeholder="What is your name?",
            key="name",
            help="Type your Student ID or Name to confirm the phonetic",
            disabled=st.session_state.disabled,
        )
        #if not name:
            #st.warning("Please enter your name to proceed.")

    # end def

    @staticmethod
    def get_phonetic_spelling() -> None:
        if st.session_state.name:
            name_id = st.session_state.name
            st.session_state.first_name = ""
            st.session_state.last_name = ""
            st.session_state.student_id = ""  
            st.session_state.id_found = False
            if(name_id.isnumeric()):
                conn = st.connection("snowflake")
                try:                                    
                    df = conn.query(f"SELECT * from students where student_id={st.session_state.name};")
                    st.session_state.first_name = df['FIRST_NAME'][0]
                    st.session_state.last_name = df['LAST_NAME'][0]
                    st.session_state.student_id = df['STUDENT_ID'][0]
                    st.session_state.id_found = True
                except:  
                    st.session_state.first_name = st.session_state.name
                    st.session_state.last_name = ""
                    st.session_state.student_id = ""  
                    st.session_state.id_found = False

                st.session_state.phonetic_spelling = pronouncing.phones_for_word(st.session_state.first_name)                    
                                      
            else:
                st.session_state.first_name = st.session_state.name
                st.session_state.phonetic_spelling = pronouncing.phones_for_word(st.session_state.first_name)

            if st.session_state.phonetic_spelling and st.session_state.approval:
                st.session_state.phonetic_spelling = "".join(
                    char
                    for char in st.session_state.phonetic_spelling[0]
                    if char.isalpha()
                )
                st.session_state.satisfies_phonetic_spelling = True

            if not st.session_state.phonetic_spelling:  
                if not (st.session_state.id_found):
                    st.warning("Student ID not found, correct and try again!.")
                else:                                   
                    st.warning("Hold on we are working on it.")
                

            if not st.session_state.phonetic_spelling or not st.session_state.approval:
                user_input = st.text_input(
                    label="Phonetic Spelling",
                    placeholder="Please enter the phonetic spelling ",
                    help="Please provide the phonetic spelling for your name",
                    disabled=st.session_state.disabled,
                )

                if not user_input:
                    st.warning("Please enter the phonetic spelling manually.")
                else:
                    st.session_state.phonetic_spelling = user_input

                # end if

            # end if

        # end if

    # end def

    @staticmethod
    def display_phonetic_spelling() -> None:
        if st.session_state.name and st.session_state.phonetic_spelling:
            if (
                    st.session_state.satisfies_phonetic_spelling
                    and st.session_state.approval
            ):
                st.info(
                    f"Phonetic spelling: {st.session_state.phonetic_spelling}"
                )

            st.radio(
                label="Are you happy with the phonetic spelling?",
                key="approval",
                options=[True, False],
                format_func=lambda x: "Yes 😄" if x else "No ☹",
            )

            # end if

        # end if

    # end def

    def prompt_user_for_accent(self):
        if st.session_state.name and st.session_state.phonetic_spelling:
            accent_key = st.selectbox(
                label="Desire Accent",
                options=list(self.accent_options.keys()),
                key="accent_key",
                index=None,
                placeholder="Select an accent",
                help="Select an accent",
            )

            if not accent_key:
                st.warning("Please select an accent.")
            else:
                st.session_state.selected_accent = self.accent_options[accent_key]

            # end if

        # end if

    # end def

    @staticmethod
    def convert_to_speech():
        tts = gTTS(
            text=st.session_state.first_name,
            lang=st.session_state.selected_accent,
        )
        filename = f"{st.session_state.name}.mp3"
        tts.save(filename)


    @staticmethod
    def save_to_csv():
        data = [
            (
                st.session_state.name,
                st.session_state.first_name,
                st.session_state.last_name,
                st.session_state.phonetic_spelling,
                st.session_state.selected_accent,
            )
        ]
        
        try:            
            conn = st.connection("snowflake",autocommit=True)        
            cur = conn.cursor()      
            sqlstr = f"UPDATE students SET first_name_spell='{st.session_state.phonetic_spelling}' " 
            sqlstr += f"WHERE student_id={st.session_state.student_id};"
            #st.warning(sqlstr)
            cur.execute(sqlstr)
            cur.close()
        except:
            st.warning(sqlstr)
            #st.warning("Internet issue-refresh and try again")
            

        filename = f"{st.session_state.name}_data.csv"

        with open(filename, mode="w", newline="") as file:
            # comment: create the csv writer
            writer = csv.writer(file)
            writer.writerow(["Student ID / Name", "First Name", "Last Name", "Phonetic Spelling", "Selected Accent"])
            writer.writerows(data)

        # end with

    # end def
