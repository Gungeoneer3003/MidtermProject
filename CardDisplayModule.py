'''
CIST 005B Fall 2024
Midterm Project
Description: A card display module to look at a deck of cards
Input: A folder address
Output: A GUI showing the cards (images) in the directory
Student: Chris Amey
Known bugs: None
Date: 11/3/2024
'''

#Libaries used
from PIL import Image, ImageTk
from tkinter import Tk, Label, Entry, Button, StringVar, Frame, messagebox
import os
import re
import random
import sys

#################################################################
# This program was made with the help of Tabnine AI and ChatGPT #
#################################################################

# Main structure class for setting up the card system and GUI
class Structure:
    def __init__(self):
        self.current = None
        self.count = 0

        #Create the background image
        image = Image.open("0.png")
        self.img = image.resize((image.width * 2, image.height * 2))

        # Folder Check
        self.path = self.folder_address_checker()
        if not self.outerfolderAddressValidation(self.path):
            sys.exit()
        self.list = self.load_images_from_directory(self.path)

        # Clean the given data
        self.list, self.count = self.cleanData(self.list)

        # Create resulting structures
        self.dictionary, self.draw, self.discard = self.createStructures()

        # Set up GUI accordingly
        self.root = Tk()
        self.createGUI()


    # A repeat of the folder check, so that the folder is still valid even if the window is manually closed
    def outerfolderAddressValidation(self, path):
        if not os.path.isdir(path):
            return False
        image_extensions = {".jpg", ".jpeg", ".png"}
        image_files = [f for f in os.listdir(path) if os.path.splitext(f)[1].lower() in image_extensions]

        if not image_files:
            return False
        return True

    # Take input for the folder address in the form of a GUI
# GUI function to check and validate folder address containing images
    def folder_address_checker(self):
        path = ""

        """
        Sets up a GUI to check a folder path.
        Validates if the path is a directory, not an executable, and contains image files.
        """

        def validate_path(event=None):
            # Get the path from the input field
            nonlocal path
            path = path_entry.get()

            # Check if the path is a directory
            if not os.path.isdir(path):
                feedback.set("Invalid directory address.")
                feedback_label.config(fg="red")
                return

            # Check for executable files
            if any(path.endswith(ext) for ext in [".exe", ".bat", ".sh"]):
                feedback.set("Error: Executable file detected.")
                feedback_label.config(fg="red")
                return

            # Check for image files
            image_extensions = {".jpg", ".jpeg", ".png", ".gif"}
            image_files = [f for f in os.listdir(path) if os.path.splitext(f)[1].lower() in image_extensions]

            if not image_files:
                feedback.set("No image files found in the directory.")
                feedback_label.config(fg="red")
            else:
                feedback.set("Images found!")
                feedback_label.config(fg="green")
                filesearch.destroy()

        # Set up the GUI
        filesearch = Tk()
        filesearch.title("Image Directory Checker")

        # Define UI elements
        path_label = Label(filesearch, text="Enter folder path:")
        path_label.pack()

        # Input field
        path_entry = Entry(filesearch, width=75)
        path_entry.pack(padx=20)
        path_entry.bind("<Return>", validate_path)

        # Feedback label in red by default
        feedback = StringVar()
        feedback_label = Label(filesearch, textvariable=feedback, fg="red")
        feedback_label.pack()

        # Submit button
        check_button = Button(filesearch, text="Check Folder", command=validate_path)
        check_button.pack()

        # Run the GUI loop
        filesearch.mainloop()

        return path

    # Access the images and config file and create the list of card objects
# Loads images and creates card objects from the specified directory
    def load_images_from_directory(self, directory):
        images = []
        configs = {}
        flag = False

        configAddress = os.path.join(directory, "config.txt")
        configExists = os.path.isfile(configAddress)
        if configExists:
            configs = self.parse_config_file(os.path.join(directory, "config.txt"))

        for filename in os.listdir(directory):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):  # Add more extensions as needed
                filepath = os.path.join(directory, filename)
                try:
                    searchName = re.match(r"^(.*?)\s*\(", filename).group(1)
                    name, _ = os.path.splitext(filename)
                except AttributeError as e:
                    name, _ = os.path.splitext(filename)
                    searchName = name

                if len(name) > 45:
                    flag = True
                    name = name[:45] + "..."
                if len(searchName) > 45:
                    flag = True
                    searchName = searchName[:45]

                # Attempt to open the config file
                card = self.determineCard(name, searchName, filepath, configs)
                images.append(card)

        # If the name of any card exceeds 25 characters, print a warning
        if flag:
            messagebox.showerror("Note", "Some of the names of your cards exceed 45 characters. \nAs a result, those cards have a name reduced down. \nPlease take this into consideration when searching for a card.")

        return images

    # This function creates a card object from the info in the config file
    # If there's an existing card name in the config file, it will create either a spell or creature
# Determine if a card is a Creature or Spell based on config
    def determineCard(self, name, searchName, filepath, configs):
        if searchName in configs.keys():
            file = configs[searchName]

            # Clean up the config file for the flavor text and description
            if file["Flavor Text"] == "N/A":
                file["Flavor Text"] = ""
            if file["Description"] == "N/A":
                file["Description"] = ""

            description = file["Flavor Text"]
            chunked_lines = [description[j:j + 75] for j in range(0, len(description), 75)]
            output1 = "\n".join(chunked_lines[:3]) + ("..." if len(chunked_lines) > 3 else "")

            # Split the description into 100-character chunks
            description = file["Description"]
            chunked_lines = [description[j:j + 75] for j in range(0, len(description), 75)]
            output2 = "-\n-".join(chunked_lines[:3]) + ("..." if len(chunked_lines) > 3 else "")

            # Clean up the cost, damage, and health strings
            if len(file["Cost"]) > 40:
                file["Cost"] = file["Cost"][:40] + "..."
            if len(file["Damage"]) > 16:
                file["Damage"] = file["Damage"][:16]
            if len(file["Health"]) > 20:
                file["Health"] = file["Health"][:20]

            # Create the appropriate card object based on the card type in the config file
            if file["Type"] == "creature":
                return CreatureCard(name, searchName, Image.open(filepath), file["Damage"], file["Health"],
                                    file["Cost"], output1, output2)
            elif file["Type"] == "spell":
                return SpellCard(name, searchName, Image.open(filepath), file["Cost"], output2,
                                 output1)
            else:  # If the card isn't a creature or spell
                return Card(name, searchName, Image.open(filepath))
        else:  # If the card doesn't appear in the config file
            return Card(name, searchName, Image.open(filepath))

    # Go line by line through the config file
    def parse_config_line(self, line, dictionary):
        # Split line by delimiter " // "
        parts = line.strip().split(" \\\\ ")

        #Ensure correct number of fields
        #The program will take a bad config file as a sign to close the program
        #This is to allow the user to repair the config file
        #The other solution is to skip this line, which could cause issues if it was expected to work
        if len(parts) != 7:
            messagebox.showerror("Error", f"Corrupted or bad config file detected!\nPlease check the config file and try again\nPlace of Error: \n{line}")
            sys.exit()

        # Assign each part to a variable
        name, type_, cost, health, damage, description, flavor_text = parts

        # Store data in a dictionary
        dictionary[name] = {
            "Type": type_,
            "Cost": cost,
            "Health": health,
            "Damage": damage,
            "Description": description,
            "Flavor Text": flavor_text
        }

        return

    def parse_config_file(self, filename="config.txt"):
        # Check if file exists
        if not os.path.exists(filename):
            #print(f"File '{filename}' not found.")
            return []

        entries = {}
        # Open and read file line by line
        with open(filename, "r") as file:
            for line in file:
                if line.strip():  # Ignore empty lines
                    entry = self.parse_config_line(line, entries)

        return entries

    def cleanData(self, list):
        x = 0
        for item in list:
            x += 1
            item.image = item.image.resize((self.img.width, self.img.height))

        return list, x

    def createStructures(self):
        # Create dictionary, which will act as a check if a card is in the stack
        dictionary = {}
        for item in self.list:
            if item.searchName not in dictionary.keys():
                dictionary[item.searchName] = {"Max": 1, "Count": 0}
            else:
                dictionary[item.searchName]["Max"] += 1
        Draw = Stack(self.list)
        return dictionary, Draw, Stack([])

# Set up the main GUI components
    def createGUI(self):
        self.root.title("Card Viewer")

        #Create variables that will be accessible to the setGUI function

        self.background = ImageTk.PhotoImage(self.img)
        blank_image = Image.new("RGBA", (self.background.width(), self.background.height()),
                                (210, 180, 140, 100))  # Create a transparent image
        self.blank_image_tk = ImageTk.PhotoImage(blank_image)


        # Create a frame for the search bar
        search_frame = Frame(self.root)
        search_frame.grid(row=0, column=0, columnspan=3, padx=(0, 35))  # Place the search frame in the first row

        # Add the respective label and entry box for the search bar
        # The search bar will be accessible to the search function
        search_label = Label(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(0, 5))  # Padding to the right of the label
        self.search_entry = Entry(search_frame, width=30)  # Adjust width as needed
        self.search_entry.grid(row=0, column=1)
        self.search_entry.bind("<Return>", self.search)

        # Create a frame for the buttons
        buttonframe = Frame(self.root)
        buttonframe.grid(row=1, column=0, columnspan=4, pady=(0, 10))  # Spans across all columns

        # Add buttons to control the image viewer
        shuffle_button = Button(buttonframe, text="Previous", command=self.Previous)
        shuffle_button.grid(row=1, column=0, padx=0)  # Spans across all columns
        shuffle_button = Button(buttonframe, text="Shuffle", command=self.shuffle)
        shuffle_button.grid(row=1, column=1, padx=0)  # Spans across all columns
        sort_button = Button(buttonframe, text="Sort/Replenish", command=self.mergeSortHelper)
        sort_button.grid(row=1, column=2, padx=0)  # Spans across all columns
        draw_button = Button(buttonframe, text="Draw", command=self.pull)
        draw_button.grid(row=1, column=3, padx=0)  # Spans across all columns

        # Create a frame for the images
        imageframe = Frame(self.root)
        imageframe.grid(row=2, column=0, columnspan=3, pady=5)  # Spans across all columns

        #Create the discard pile label
        self.label1 = Label(imageframe, image=self.blank_image_tk)
        self.label1.grid(row=2, column=0, padx=(0, 75))  # Padding: space between and around images
        self.discard_label = Label(self.label1, text="Discard", font=("Times New Roman", 12))
        self.discard_label.place(relx=0.5, rely=1.0, anchor="s")  # Position at the bottom center

        #Create the current card label
        self.label2 = Label(imageframe, image=self.blank_image_tk)
        self.label2.grid(row=2, column=1)

        #Create the draw pile label
        self.label3 = Label(imageframe, image=self.background)
        self.label3.grid(row=2, column=2, padx=(75, 0))  # Padding on the right
        self.draw_label = Label(self.label3, text=f"Draw\n{self.draw.size} Cards", font=("Times New Roman", 12))
        self.draw_label.place(relx=0.5, rely=1.0, anchor="s")  # Position at the bottom center

        #Add a label for the name of the card below
        self.currentCard = Label(self.root, text="Current Card: ", font=("Times New Roman", 15))
        self.currentCard.grid(row=3, column=0, columnspan=3, pady=(10, 0))  # Spans across all columns
        self.currentCard.configure(text="Current Card: (Blank)", font=("Times New Roman", 15))

        # Add a description
        # Note: the description takes up multiple lines, so some pady might be needed
        self.description = Label(self.root, text="")
        self.description.grid(row=4, column=0, columnspan=3, pady=15)  # Spans across all columns

        # Change Deck
        NewDeckButton = Button(self.root, text="New Deck", command=self.SetDeck)
        NewDeckButton.grid(row=5, column=0, columnspan=3)  # Spans across all columns

        #As a last step, create the empty label without placing it
        self.emptyLabel = Label(self.label3, text="Empty", font=("Times New Roman", 12))

    # This function changes the GUI to match the cards in the draw pile, current card pile, and discard pile, respectively
    def setGUI(self):
        # Set the discard pile image
        if not self.discard.isEmpty():
            image = self.discard.peek().image
            self.discardImage = ImageTk.PhotoImage(image)
            self.label1.config(image=self.discardImage)
        else:
            self.label1.config(image=self.blank_image_tk)

        #Replace the discard label
        self.discard_label.place_forget()
        self.discard_label.place(relx=0.5, rely=1.0, anchor="s")  # Position at the bottom center

        # Set the current
        if self.current is not None:
            image = self.current.image
            self.currentImage = ImageTk.PhotoImage(image)
            self.label2.config(image=self.currentImage)
            self.currentCard.configure(text="Current Card: " + self.current.name, font=("Times New Roman", 15))
            self.description.configure(text=str(self.current))
        else:
            self.label2.config(image=self.blank_image_tk)
            self.currentCard.configure(text="Current Card: (Blank)", font=("Times New Roman", 15))
            self.description.configure(text="")

        #Set the draw pile image
        if self.draw.isEmpty():
            self.label3.config(image=self.blank_image_tk)
            self.emptyLabel.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.label3.config(image=self.background)
            self.emptyLabel.place_forget()

        #Replace the draw_label
        self.draw_label.place_forget()
        self.draw_label.configure(text=f"Draw\n{self.draw.size} Cards")
        self.draw_label.place(relx=0.5, rely=1.0, anchor="s")  # Position at the bottom center


    #This function pulls from the draw pile and places it into the current card slot
    def pull(self):
        # Do a try and catch for if the queue is empty
        try:
            card = self.draw.pop()
            # Take the card from the queue

            # If there's a card in current, move it to the discard
            if self.current is not None:
                self.discard.push(self.current)
                self.dictionary[self.current.searchName]["Count"] += 1

            self.current = card

            # Change the GUI accordingly (discard, then current, then queue [if empty])
            self.setGUI()

        except AttributeError as e:
            pass

# Shuffle the cards in the draw pile
    def shuffle(self):
        random.shuffle(self.list)

        self.dictionary, self.draw, self.discard = self.createStructures()
        self.current = None
        self.setGUI()

    def mergeSortHelper(self):
        self.list = self.mergeSort(self.list)

        self.dictionary, self.draw, self.discard = self.createStructures()
        self.current = None
        self.setGUI()

    #The recursive sort function
    def mergeSort(self, lst):
        if len(lst) <= 1:
            return lst

        mid = len(lst) // 2
        left = self.mergeSort(lst[:mid])
        right = self.mergeSort(lst[mid:])

        return self.merge(left, right)

    def merge(self, left, right):
        sorted = [None] * (len(left) + len(right))
        c = i = j = 0

        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                sorted[c] = left[i]
                i += 1
                c += 1
            else:
                sorted[c] = right[j]
                j += 1
                c += 1

        while i < len(left):
            sorted[c] = left[i]
            i += 1
            c += 1

            # Place any remaining elements from the right half
        while j < len(right):
            sorted[c] = right[j]
            j += 1
            c += 1

        return sorted

    '''
    Search = King of Hearts
    In discard pile is King of Spades
    Draw pile is King of Hearts, Clubs, and Diamonds
    if Dictionary["Count"] != Dictionary["Max"]:
    While current.searchName != search:
    draw()
    else:
    (move all of stack over using enqueue to draw pile)

    While current.searchName != search:
    draw()
    '''

    #This function pulls through either the discard pile or the search pile to look for a card
    #An important part of this is no exception checking is done because the card is known to already be there
    #Another part is the setGUI function is saved for the end of the function, leading to similar code as
    #the previous function and the draw function, but draw and previous aren't used to save setting the GUI
    #multiple times when it's unnecessary
    def search(self, event=None):
        #Geting the data input
        search = self.search_entry.get()
        if self.current is not None:
            if search == self.current.searchName:
                messagebox.showerror("Error", "looking at the searched card!")
                return
        if search not in self.dictionary.keys():
            messagebox.showerror("Error", "Name not found, please enter the proper name of the card")
            return

        # Check if the search card is only in discard pile, if it is, then go pull through the discard pile
        if (self.dictionary[search]["Max"] == self.dictionary[search]["Count"]):
            while True:
                card = self.discard.pop()
                # Take the card from the queue

                # If there's a card in current, move it back to the draw
                if self.current is not None:
                    self.draw.push(self.current)

                self.current = card
                self.dictionary[self.current.searchName]["Count"] -= 1

                if self.current.searchName == search:
                    break
        else:
            #Keep drawing cards until the search is found
            while True:
                card = self.draw.pop()

                if self.current is not None:
                    self.discard.push(self.current)
                    self.dictionary[self.current.searchName]["Count"] += 1

                self.current = card

                if self.current.searchName == search:
                    break

        #Conclude by setting the GUI
        self.setGUI()
        return

    #Draw the previous card from the discard
    def Previous(self):
        # Do a try and catch for if the queue is empty
        try:
            card = self.discard.pop()
            # Take the card from the queue

            # If there's a card in current, move it back to the queue
            if self.current is not None:
                self.draw.push(self.current)

            self.current = card
            self.dictionary[self.current.searchName]["Count"] -= 1

            # Change the GUI accordingly (discard, then current, then queue [if empty])
            self.setGUI()

        except AttributeError as e:
            pass

    #This in effect creates a whole new deck and window
    #The program closes if the folder search is closed with an invalid folder address
    #The program essentially starts from the beginning and recreates itself with this function
    def SetDeck(self):
        self.root.destroy()  # Hide the root window
        self.path = self.folder_address_checker()
        if not self.outerfolderAddressValidation(self.path):
            sys.exit()
        self.list = self.load_images_from_directory(self.path)

        self.list, self.count = self.cleanData(self.list)

        self.dictionary, self.draw, self.discard = self.createStructures()
        self.current = None
        self.root = Tk()
        self.createGUI()    #This part right here is necessary as the original is destroyed, otherwise setGUI is used

    def run(self):
        self.root.mainloop()


# Parent class Card which handles anything that isn't in the config file
# Base Card class for representing generic cards
class Card:
    def __init__(self, name, searchName, image):
        self.name = name
        self.searchName = searchName
        self.image = image

    def __lt__(self, other):
        return self.searchName < other.searchName

    def __str__(self):
        return ""


# Creature and Spell Card implementations
# Creature Card subclass with additional attributes
class CreatureCard(Card):
    def __init__(self, name, searchName, image, attack, health, energy, flavor, description):
        super().__init__(name, searchName, image)
        self.attack = attack
        self.health = health
        self.energy = energy
        self.flavor = flavor
        self.description = description

    def __str__(self):
        flavorText = ""
        if self.flavor != "":
            flavorText = f"\"{self.flavor}\""
        return f"Creature: ({self.attack},{self.health}) for {self.energy} \n {self.description} \n\n {flavorText}"


# Spell Card subclass with additional attributes
class SpellCard(Card):
    def __init__(self, name, searchName, image, cost, effect, flavor):
        super().__init__(name, searchName, image)
        self.cost = cost
        self.effect = effect
        self.flavor = flavor

    def __str__(self):
        flavorText = ""
        if self.flavor != "":
            flavorText = f"\"{self.flavor}\""
        return f"Spell: {self.cost} \n {self.effect} \n\n {flavorText}"


# Node for a singly linked list
# Used for linked list structure in stack
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


# A stack, which uses both the LIFO and FIFO behaviors
class Stack:
    def __init__(self, list):
        self.front = None
        self.rear = None
        self.size = 0
        for i in list[::-1]:
            self.push(i)

    # Put an item at the top of the linked list
    def push(self, data):
        new_node = Node(data)
        new_node.next = self.front
        self.front = new_node
        self.size += 1

    # Remove an item from the front of the list
    def pop(self):
        removed_node = self.front
        self.front = self.front.next
        self.size -= 1
        return removed_node.data

    # Check if the stack is empty
    def isEmpty(self):
        return self.size == 0

    # A function for looking at the front of the stack
    def peek(self):
        if self.isEmpty():
            return None
        return self.front.data


if __name__ == "__main__":
    window = Structure()
    window.run()