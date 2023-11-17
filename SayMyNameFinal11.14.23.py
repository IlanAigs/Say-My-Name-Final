import csv
import pandas as pd
from g2p_en import G2p
import os

# Transformation map.
phoneme_substitution = {
    'AA': 'a', 'AE': 'ae', 'AU': 'aow', 'AI': 'ayi', 'AO': 'aow', 'AY': 'ay', 'AH': 'ah',
    'EE': 'ey', 'EA': 'eya', 'EU': 'aow', 'EI': 'eyee', 'EO': 'eow', 'EY': 'ey', 'EH': 'e',
    'UU': 'oo', 'UA': 'owa', 'UE': 'owe', 'UI': 'yowi', 'UO': 'yoow', 'UY': 'yoy', 'UH': 'oo',
    'II': 'e', 'IA': 'aiy', 'IE': 'aiye', 'IU': 'iyoo', 'IO': 'iyo', 'IY': 'eay', 'IH': 'aiy',
    'OO': 'o', 'OA': 'owa', 'OU': 'owu', 'OI': 'oye', 'OE': 'owe', 'OY': 'oy', 'OH': 'oa',
    'YA': 'ya', 'YE': 'ye', 'YU': 'yoo', 'YI': 'yi', 'YO': 'yo', 'YY': 'y', 'YH': 'ya',
    'HA': 'ha', 'HE': 'he', 'HU': 'hoo', 'HI': 'hee', 'HO': 'ho', 'HY': 'hay', 'HH': 'ha'
}

# Get the name as written by the student.
def get_user_input():
    return input("Enter your name: ")

# Generate the phonetics
def generate_phonetic_spelling(user_input):
    g2p = G2p()
    phonetic_spelling = g2p(user_input)
    phonetic_spelling_without_stress = [phoneme.rstrip('012') for phoneme in phonetic_spelling]
    return ' '.join(phonetic_spelling_without_stress)

# Transform the phonetics using the transformation map.
def transform_phonetics(phonetics):
    transformed_phonetics = ''.join(phonetics).capitalize()

    for original, replacement in phoneme_substitution.items():
        transformed_phonetics = transformed_phonetics.replace(original.lower(), replacement)

    return transformed_phonetics.replace(" ", "")

# Get the user's approval
def get_user_approval(user_input):
    approval = input(f'Is "{user_input}" the way your name is pronounced? Yes/No: ')
    return approval.lower() == 'yes'

# Add the result to the xlsx file
def write_to_excel(data):
    filename = "ALL STUDENTS OCTOBER 17th.xlsx"
    columns = ["Original", "Phonetic", "Transformed"]

    if not os.path.isfile(filename):
        df = pd.DataFrame(columns=columns)
        df.to_excel(filename, index=False)

    df = pd.read_excel(filename)

    data_dict = dict(zip(columns, data))
    df = pd.concat([df, pd.DataFrame(data_dict, index=[0])], ignore_index=True)
    df.to_excel(filename, index=False)
    print("Data written to Excel.")

# The main execution of the program.
def main():
    user_name = get_user_input()
    phonetic_spelling_without_stress = generate_phonetic_spelling(user_name)
    transformed_phonetic = transform_phonetics(phonetic_spelling_without_stress)

    print(f'Original input as spelled by the student: {user_name}')
    print(f'Phonetic spelling: {phonetic_spelling_without_stress}')
    print(f'The name as pronounced: {transformed_phonetic}')

    if get_user_approval(transformed_phonetic):
        write_to_excel([user_name, phonetic_spelling_without_stress, transformed_phonetic])
    else:
        correct_phonetic = input("Please enter the correct phonetic spelling: ")
        transformed_phonetic = transform_phonetics(correct_phonetic)

        print(f'The corrected name as pronounced: {transformed_phonetic}')

        if get_user_approval(transformed_phonetic):
            write_to_excel([user_name, phonetic_spelling_without_stress, transformed_phonetic])
        else:
            print("User did not approve. Data not written.")

if __name__ == "__main__":
    main()
