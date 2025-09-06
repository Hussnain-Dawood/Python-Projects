from difflib import SequenceMatcher #This is library for comparing sequences
with open('demo1.txt') as file1, open('demo2.txt') as file2:
    file1_data = file1.read()
    file2_data = file2.read()
    matches=SequenceMatcher(None,file1_data,file2_data).ratio()
    print(f"The Plagiarism ratio is {matches*100}%")