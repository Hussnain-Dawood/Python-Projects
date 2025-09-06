# Import SpellChecker class from the pyspellchecker library
from spellchecker import SpellChecker

# Define a class to handle spell checking
class SpellCheckerApp:
    # Constructor method that runs when an object of the class is created
    def __init__(self):
        # Create a SpellChecker object and assign it to self.spell
        # This will be used for all spell-checking operations
        self.spell = SpellChecker()

    # Method to correct spelling in a given text
    def correct_text(self, text):
        # Split the text into individual words (list of words)
        words = text.split()

        # Create an empty list to store corrected words
        corrected = []

        # Loop through each word in the sentence
        for word in words:
            # Check if the word is not recognized (misspelled)
            if word not in self.spell:
                # Get the most likely correct spelling suggestion
                correction = self.spell.correction(word)

                # Add the corrected word to the list
                corrected.append(correction)
            else:
                # If the word is correct, add it as it is
                corrected.append(word)

        # Join the corrected words back into a full sentence
        return " ".join(corrected)


# ----------------------- Example Usage -----------------------

# Create an object of SpellCheckerApp
app = SpellCheckerApp()

# Pass a sentence with spelling mistakes
content=input("Enter the Content :\n")
result = app.correct_text(content)

print(result)   
