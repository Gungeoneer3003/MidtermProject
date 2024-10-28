from PIL import Image, ImageTk
from tkinter import Tk, Label, Entry, Button, StringVar, Frame
import os
import re
import time


class structure:
    def __init__(self):
        self.current = None
        self.count = 0
        self.running = False

        #Folder Check
        self.list = self.load_images_from_directory(self.folder_address_checker())

        #Create resulting structures
        self.dictionary, self.queue, self.stack = self.createStructures()
        #Set up GUI accordingly
        self.running = True

        self.root = Tk()
        self.createGUI()

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

    #Starting with the folder check functions
    def load_images_from_directory(self, directory):
        images = []
        configs = {}

        configAddress = os.path.join(directory, "config.txt")
        if os.path.isfile(configAddress):
            configs = self.parse_config_file(os.path.join(directory, "config.txt"))

        for filename in os.listdir(directory):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):  # Add more extensions as needed
                filepath = os.path.join(directory, filename)
                searchName = re.match(r"^(.*?)\s*\(", filename).group(1)
                name, _ = os.path.splitext(filename)

                # Attempt to open the config file
                card = self.determineCard(name, searchName, filepath, configs)
                images.append(card)

        return images

    def determineCard(self, name, searchName, filepath, configs):
        if searchName in configs.keys():
            file = configs[searchName]
            if file["Type"] == "creature":
                return CreatureCard(name, searchName, Image.open(filepath), file["Damage"], file["Health"],
                                    file["Cost"], file["Flavor Text"], file["Description"])
            elif file["Type"] == "spell":
                return SpellCard(name, searchName, Image.open(filepath), file["Cost"], file["Description"],
                                 file["Flavor Text"])
        else:
            return card(name, searchName, Image.open(filepath))

    def parse_config_line(self, line, dictionary):
        # Split line by delimiter " // "
        parts = line.strip().split(" \\\\ ")

        # Ensure correct number of fields
        if len(parts) != 7:
            print(f"Invalid line format: {line}")
            return None

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
            print(f"File '{filename}' not found.")
            return []

        entries = {}
        # Open and read file line by line
        with open(filename, "r") as file:
            for line in file:
                if line.strip():  # Ignore empty lines
                    entry = self.parse_config_line(line, entries)

        return entries

    def createStructures(self):
        #Create dictionary, which will act as a check if a card is in the stack
        dictionary = {}
        for item in self.list:
            dictionary[item.name] = False
        q = queue(self.list)
        return dictionary, q, Stack()

    def createGUI(self):
        self.root.title("Multiple Image Viewer")

        img = Image.open("0.png")
        img = img.resize((img.width * 2, img.height * 2))
        img.verify()
        print("Image loaded successfully")

        self.tk_img1 = ImageTk.PhotoImage(img)
        self.tk_img2 = ImageTk.PhotoImage(img)
        self.tk_img3 = ImageTk.PhotoImage(img)

        # Create a frame for the search bar
        search_frame = Frame(self.root)
        search_frame.grid(row=0, column=0, columnspan=3, padx=(0, 35))  # Place the search frame in the first row

        # Add the respective label and entry box for the search bar
        search_label = Label(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(0, 5))  # Padding to the right of the label
        search_entry = Entry(search_frame, width=30)  # Adjust width as needed
        search_entry.grid(row=0, column=1)

        # Create a frame for the buttons
        buttonframe = Frame(self.root)
        buttonframe.grid(row=1, column=0, columnspan=4, pady=(0, 10))  # Spans across all columns

        # Add buttons to control the image viewer
        shuffle_button = Button(buttonframe, text="Previous", command=self.Previous)
        shuffle_button.grid(row=1, column=0, padx=0)  # Spans across all columns
        shuffle_button = Button(buttonframe, text="Shuffle", command=self.shuffle)
        shuffle_button.grid(row=1, column=1, padx=0)  # Spans across all columns
        sort_button = Button(buttonframe, text="Sort", command=self.sort)
        sort_button.grid(row=1, column=2, padx=0)  # Spans across all columns
        draw_button = Button(buttonframe, text="Draw", command=self.draw)
        draw_button.grid(row=1, column=3, padx=0)  # Spans across all columns

        # Create a frame for the images
        imageframe = Frame(self.root)
        imageframe.grid(row=2, column=0, columnspan=3, pady=5)  # Spans across all columns

        # Display the images in a horizontal row
        label1 = Label(imageframe, image = self.tk_img1)
        label1.grid(row=2, column=0, padx=(0, 75))  # Padding: space between and around images

        label2 = Label(imageframe, image = self.tk_img2)
        label2.grid(row=2, column=1)

        label3 = Label(imageframe, image=self.tk_img3)
        label3.grid(row=2, column=2, padx=(75, 0))  # Padding on the right

        # Add a close button below the images
        str = "Ace of Hearts"
        current_card = Label(self.root, text="Current Card: " + str, font=("Times New Roman", 15))
        current_card.grid(row=3, column=0, columnspan=3, pady=(10, 0))  # Spans across all columns

        # Add a description
        # Note: the description takes up multiple lines, so some pady might be needed
        desc = "Creature: 5 HP, 10 Damage, 2 Mana \n Each player chooses a nonland permanent they control. \nReturn all nonland permanents not chosen this way to their owners\' hands. \nThen you draw a card for each opponent who has more cards in their hand than you. \nIvold gasped in surprise. Either a very strange insect had crawled onto one of \nthe lenses or he was seeing geists at last!"
        x = desc
        description = Label(self.root, text=x)
        description.grid(row=4, column=0, columnspan=3, pady=15 if x == "" else 0)  # Spans across all columns

        # Change Deck
        NewDeckButton = Button(self.root, text="New Deck", command=self.SetDeck)
        NewDeckButton.grid(row=5, column=0, columnspan=3)  # Spans across all columns

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

    def draw(self):
        pass

    def shuffle(self):
        pass

    def sort(self):
        pass

    def Previous(self):
        pass

    def search(self):
        pass

    def SetDeck(self):
        pass

    def run(self):
        self.root.mainloop()

class card:
    def __init__(self, name, searchName, image):
        self.name = name
        self.searchName = searchName
        self.image = image

#Creature and Spell Card implementations, might change if flavor text doesn't work out
class CreatureCard:
    def __init__(self, name, searchName, image, attack, health, energy, flavor, description):
        super().__init__(name, searchName, image)
        self.attack = attack
        self.health = health
        self.energy = energy
        self.flavor = flavor
        self.description = description

    def __str__(self):
        return f"Creature: ({self.attack},{self.health}) for {self.energy} \n {self.description} \n {self.flavor}"

class SpellCard:
    def __init__(self, name, searchName, image, cost, effect, flavor):
        super().__init__(name, searchName, image)
        self.cost = cost
        self.effect = effect
        self.flavor = flavor

    def __str__(self):
        return f"Spell: {self.cost} \n {self.effect} \n {self.flavor}"

class node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    # def __init__(self, list):
    #     self.head = None
    #     self.size = len(list)
    #     for item in list:
    #         self.add(item)

    def add(self, data):
        new_node = node(data, self.head)
        self.head = new_node
        self.size += 1

    def remove(self, data):
        if self.head is None:
            return
        if self.head.data == data:
            temp = self.head
            self.head = self.head.next
            self.size -= 1
            return temp
        current = self.head
        while current.next is not None and current.next.data!= data:
            current = current.next
        if current.next is None:
            return
        temp = current.next
        current.next = current.next.next
        self.size -= 1

    def remove_head(self):
        if self.head is None:
            return None
        temp = self.head
        self.head = self.head.next
        self.size -= 1
        return temp

    def search(self, data):
        current = self.head
        while current is not None:
            if current.data == data:
                return current
            current = current.next
        return None

    def rear(self):
        current = self.head
        while current is not None:
            current = current.next
        return current

    def sort(self):
        current = self.head
        if current is None or current.next is None:
            return
        while current.next is not None:
            next_node = current.next
            while next_node is not None:
                if current.data > next_node.data:
                    current.data, next_node.data = next_node.data, current.data
                next_node = next_node.next
            current = current.next

class queue:
    def __init__(self, list):
        self.front = LinkedList()  # Initialize LinkedList for queue
        for item in list:
            self.enqueue(item)
        self.rear = self.front.rear()  # Set rear to the LinkedList's rear

    def enqueue(self, data):
        rear_node = self.front.rear()
        new_node = node(data)  # New node to be added at the rear
        if rear_node is None:  # Queue is empty
            self.front.head = new_node
        else:
            rear_node.next = new_node
        self.front.size += 1
        self.rear = new_node  # Update rear

    def dequeue(self):
        if self.front.head is None:
            raise IndexError("Queue is empty")
        removed_node = self.front.remove_head()
        self.rear = self.front.rear()  # Update rear if necessary
        return removed_node.data if removed_node else None

class Stack:
    def __init__(self):
        self.top = LinkedList()
        self.size = 0

    def push(self, data):
        self.top.add(data)
        self.size += 1

    def pop(self):
        if self.top is None:
            return None
        temp = self.top.remove_head()
        self.size -= 1
        return temp.data

    def is_empty(self):
        return self.top is None

if __name__ == "__main__":
    window = structure()
    window.run()
