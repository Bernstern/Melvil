from typing import Optional
import os
import typer
from datetime import date
import json
import helper as h



TODAY = date.today()
app = typer.Typer()

VERSION = "0.3.0"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
STATES = ["To Read", "Reading", "Read", "Reviewed"]
FILE_NAME = "mortimer.json"

"""
Initialize JSON in location specified by user or, if none, the working directory.
"""
@app.command()
def init(location: Optional[str] = "./mortimer.json"):
    global TODAY
    try:
        assert(location.endswith("json"))
    except:
        print("Incorrect file format. Please use a different file name and location.")
        quit()
    TODAY = str(TODAY)
    initDict = {}
    initDict['lastEdited'] = TODAY
    initDict['book_list'] = [] # An empty list indicates that no books have been added yet.
    json_string = json.dumps(initDict, indent=4)
    with open(location, "w+") as file:
        print(f"New JSON file initialized at {location}")
        file.write(json_string)
        print("Wrote lastEdited data.")

@app.command()
def add():
    # Capture info about the new book
    path = os.getcwd()
    title = input("What is the title? ")
    book_author = input("What is the author? ")
    tag_num = h.check_user_input("How many tags to add? ", 1)
    tags = []
    for i in range(tag_num):
        tags.append(input(f"Tag #{i + 1}? "))
    state_response = h.request_status()

    state = state_response
    priority_response = -1
    priority_response = h.check_user_input("Please input a priority between 0 and 100. ", 1)
    while priority_response not in range(0, 101):
        # TODO: Use inquirer for this.
        priority_response = h.check_user_input("Please input a priority between 0 and 100. ", 1)
    priority = priority_response

    # Create dictionary of book with all this information, convert it to JSON load the JSON
    # of the file holding the books, append this JSON to the other JSON, and dump it all back into the file.
    book = {}
    book["title"] = title
    book["author"] = book_author
    book["tags"] = tags
    book["state"] = state
    book["priority"] = priority

    # Read mortimer.json to get what's already there.
    old_data = h.read_file()

    # Add new_book to the booklist
    old_book_list = old_data["book_list"]
    old_book_list.append(book)

    # Update old_data
    old_data["book_list"] = old_book_list

    # Write old_data to file
    h.write_file(old_data)

"""
Searches the database for a book with this title. Deletes the book with that title or, if there
are no such books, lets the user know this.
"""
@app.command()
def remove():
    input_title = input("Input the title of the book to remove. ")
    raw_json = h.read_file()

    # raw_json is a dictionary, raw_json["book_list"] is a list of dictionaries
    new_book_list = raw_json["book_list"]
    for bookNum, book in enumerate(raw_json["book_list"]):
        if book["title"] == input_title:
            new_book_list.pop(bookNum)
            break # We only remove the FIRST book matching that title

            # TODO: Provision unique IDs to books so they can have the same titles.
            # If we are at the end of the list, notify the user that there is no book with such a title
        elif ((bookNum + 1) == len(raw_json["book_list"])):
            print("There is no book with such a title in your list.")
            return
    raw_json["book_list"] = new_book_list
    h.write_file(raw_json)

"""
Prints the contents of the list in order of greatest-to-least priority.
"""
@app.command()
def flip():
    raw_json = h.read_file()

    book_list = raw_json["book_list"]
    new_list = sorted(book_list, key=lambda d: d['priority'])
    for book in new_list:
        print(book["title"])

"""
Changes the status of target book to target status.
"""
@app.command()
def advance():

    # Get the index of the target book
    target_book = input("Which book would you like to change? ")
    raw_json = h.read_file()
    try:
        book_index = h.search_booklist(target_book, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    # Get the target state
    target_state_index = h.request_state()

    # Change the state of the target title to the target state
    book = raw_json["book_list"][book_index]
    book["state"] = STATES[target_state_index]
    raw_json["book_list"][book_index] = book
    assert(type(raw_json) == dict) # Typecheck


    h.write_file(raw_json)
    print(f"Changed the status of {target_book} to {STATES[target_state_index]}")
    return

"""
Lists all the attributes of the single input book.
"""
@app.command()
def skim():
    target_book = input("Which book would you like to skim? ")
    raw_json = h.read_file()

    try:
        book_index = h.search_booklist(target_book, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    book = raw_json["book_list"][book_index]
    book_keys = book.keys()
    book_values = book.values()
    keys_to_values = zip(book.keys(), book.values())
    for pair in keys_to_values:
        print(f"{pair[0]}: {pair[1]}")


"""
Changes the status of target book to target status.
"""
@app.command()
def prioritize():

    # Get the index of the target book
    target_book = input("Which book would you like to change? ")
    raw_json = h.read_file()
    try:
        book_index = h.search_booklist(target_book, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    # Get the target priority
    target_priority = h.check_user_input("What priority to switch to? ", 1)

    # Change the state of the target title to the target state
    book = raw_json["book_list"][book_index]
    book["priority"] = target_priority

    h.write_file(raw_json)
    print(f"Changed the priority of {target_book} to {target_priority}")
    return

"""
Adds the target tag to the target book.
"""
@app.command()
def tag():
    target_book = input("Which book would you like to tag? ")
    raw_json = h.read_file()
    try:
        book_index = h.search_booklist(target_book, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    # Get the target tag
    tag = input(f"What tag would you like to add to {target_book}? ")
    # Change the state of the target title to the target state
    book = raw_json["book_list"][book_index]
    book["tags"].append(tag)
    h.write_file(raw_json)
    print(f"Added the tag {tag} to target book {book}.")

"""
Removes the target tag from the target book.
"""
@app.command()
def untag():
    target_book_input = input("Which book would you like to remove a tag from? ")
    raw_json = h.read_file()
    try:
        book_index = h.search_booklist(target_book_input, raw_json["book_list"])
    except h.TitleNotFoundException:
        print("There are no books with that title in your list.")
        return

    # Get the target tag
    target_book = raw_json["book_list"][book_index]
    target_tag = input(f"What tag would you like to remove from {target_book_input}? ").strip()
    # Search list of tags for target tag
    for tag in target_book["tags"]:
        if tag.strip() == target_tag:
            print(target_book["tags"])
            target_book["tags"].remove(target_tag)
            new_taglist = target_book["tags"]
            raw_json["book_list"][book_index]["tags"] = new_taglist
            h.write_file(raw_json)
            print(f"Removed tag {target_tag} from {target_book_input}")
            return
    print(f"{target_tag} isn't a tag of {target_book['title']}")



if __name__ == "__main__":
      app()
