from collections import UserDict
import re
import pickle
from datetime import datetime, timedelta
from notes import Notebook  # Added import statement
from Levenshtein import distance as levenshtein_distance
from abc import ABC, abstractmethod

# Provided classes
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_name(self):
        return self.name

    def get_age(self):
        return self.age


class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id

    def get_student_id(self):
        return self.student_id


class Teacher(Person):
    def __init__(self, name, age, employee_id):
        super().__init__(name, age)
        self.employee_id = employee_id

    def get_employee_id(self):
        return self.employee_id


class Course:
    def __init__(self, course_name, course_code):
        self.course_name = course_name
        self.course_code = course_code

    def get_course_name(self):
        return self.course_name

    def get_course_code(self):
        return self.course_code


class Enrollment:
    def __init__(self, student, course):
        self.student = student
        self.course = course

    def get_student(self):
        return self.student

    def get_course(self):
        return self.course

# UML diagram
'''
+---------------------+     +---------------------+     +-----------------------+
|       Person        |     |       Student       |     |        Teacher        |
+---------------------+     +---------------------+     +-----------------------+
| - name: str         |     | - student_id: int   |     | - employee_id: int    |
| - age: int          |     +---------------------+     +-----------------------+
+---------------------+              |                              |
| + get_name(): str   |              |                              |
| + get_age(): int    |              |                              |
+---------------------+              |                              |
                                     |                              |
                                     |                              |
                                     |                              |
                          +----------+-----------+                  |
                          |                      |                  |
                          |     Enrollment       |                  |
                          |                      |                  |
                          +----------------------+                  |
                          | - student: Student   |                  |
                          | - course: Course     |                  |
                          +----------------------+                  |
                          | + get_student(): Student                |
                          | + get_course(): Course                  |
                          +-----------------------------------------+
'''

# Original code...

class UserInterface(ABC):
    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_notes(self, notes):
        pass

    @abstractmethod
    def display_commands(self, commands):
        pass

class ConsoleUI(UserInterface):
    def display_contacts(self, contacts):
        print("=== Contacts ===")
        for contact in contacts:
            print(f"{contact.name.value} - {contact.email.value} - {contact.phone.value}")

    def display_notes(self, notes):
        print("=== Notes ===")
        for note in notes:
            print(note)

    def display_commands(self, commands):
        print("=== Commands ===")
        for command in commands:
            print(command)

    def get_user_input(self):
        return input("Enter your command: ")

class Field:
    """Base class for entry fields."""
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number")
        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        pattern = re.compile(r"^\d{9}$")
        return pattern.match(value) is not None

class Email(Field):
    def __init__(self, value):
        if not self.validate_email(value):
            raise ValueError("Invalid email address")
        super().__init__(value)

    @staticmethod
    def validate_email(value):
        pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        return pattern.match(value) is not None

class Birthday(Field):
    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Invalid birthday date")
        super().__init__(value)

    @staticmethod
    def validate_birthday(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

class Address(Field):
    def __init__(self, street, city, postal_code, country):
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
        super().__init__(value=f"{street}, {city}, {postal_code}, {country}")

class Tag:
    """Class representing a tag for categorizing notes."""
    def __init__(self, name):
        self.name = name

class Note:
    """Class representing a note with content and tags."""
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.tag = []
        
    def add_tag(self, tag):
        """Add a tag to the note."""
        self.tags.append(tag)

    def remove_tag(self, tag):
        """Remove a tag from the note."""
        self.tags.remove(tag)

class Notebook(UserDict):
    def __init__(self):
        super().__init__()
        self.next_id = 1
        self.free_ids = set()

    def create_note(self):
        """Creates a note with user input, including tags."""
        title = input("Enter the note title: ")
        content = input("Enter the note content: ")
        note = Note(title, content)

        #Adding tags
        while True:
            tag_input = input("Enter a tag (or press Enter to finish adding tags): ").strip()
            if not tag_input:
                break
            tag = Tag(tag_input)
            note.add_tag(tag)

        self.data[self.next_id] = note
        self.next_id += 1
        print("Note created.")

    def remove_note_by_id(self):
        """Remove a note based on ID."""
        user_input = input("Enter the ID of the note you want to remove: ").strip()
        
        try:
            note_id = int(user_input)
            if note_id in self.data:
                del self.data[note_id]
                print(f"Note with ID {note_id} removed.")
            else:
                print("No note found with the provider Id.")
        except ValueError:
            print("Invalid ID. Please enter a number.")

    def show_notes_with_tags(self):
        """Display all notes with their tags."""
        if not self.data:
            print("No notes available.")
        else:
            for note_id, note in self.data.items():
                print(f"ID: {note_id}, Title: {note.title}\n Content: {note.content}")
                if note.tags:
                    print("  Tags:", ', '.join(tag.name for tag in note.tags))
                    print()

    def add_tag_to_note(self):
        """Adds a tag to a note based on id."""
        user_input = input("Enter the ID of the note you want to tag: ").strip()

        try:
            note_id = int(user_input)
            if note_id in self.data:
                note = self.data[note_id]
                tag_input = input("Enter a tag to add: ").strip()
                tag = Tag(tag_input)
                note.add_tag(tag)
                print(f"Tag '{tag.name}' added to note with ID {note_id}.")
            else:
                print("No note found with the provider ID.")
        except ValueError:
            print("Invalid ID. Please enter a number.")

    def remove_tag_from_note(self):
        """Remove a tag from a note based on ID."""
        user_input = input("Enter the ID of the note you want to untag: ").strip()

        try:
            note_id = int(user_input)
            if note_id in self.data:
                note = self.data[note_id]
                tag_input = input("Enter a tag to remove: ").strip()
                tag = Tag(tag_input)
                if tag in note.tags:
                    note.remove_tag(tag)
                    print(f"Tag '{tag.name}' removed from note with ID {note_id}.")
                else:
                    print("No note found with the provided ID.")
        except ValueError:
                print("Invalid ID. Please enter a number.")

class Record:
    def __init__(self, name: Name, birthday: Birthday = None):
        self.id = None  # The ID will be assigned by AddressBook
        self.name = name
        self.phones = []
        self.emails = []
        self.birthday = birthday
        self.address = None  # Add a new property to store the address

    def add_address(self, address: Address):
        """Adds an address."""
        self.address = address

    def add_phone(self, phone: Phone):
        """Adds a phone number."""
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        """Removes a phone number."""
        self.phones.remove(phone)

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        """Changes a phone number."""
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_email(self, email: Email):
        """Adds an email address."""
        self.emails.append(email)

    def remove_email(self, email: Email):
        """Removes an email address."""
        self.emails.remove(email)

    def edit_email(self, old_email: Email, new_email: Email):
        """Changes an email address."""
        self.remove_email(old_email)
        self.add_email(new_email)

    def edit_name(self, new_name: Name):
        """Changes the first and last name."""
        self.name = new_name

    def days_to_birthday(self):
        """Returns the number of days to the next birthday."""
        if not self.birthday or not self.birthday.value:
            return "No birth date provided"
        today = datetime.now()
        bday = datetime.strptime(self.birthday.value, "%Y-%m-%d")
        next_birthday = bday.replace(year=today.year)
        if today > next_birthday:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        """Returns a string representation of the entry, including the ID."""
        phones = ', '.join(phone.value for phone in self.phones)
        emails = ', '.join(email.value for email in self.emails)
        birthday_str = f", Birthday: {self.birthday.value}" if self.birthday else ""
        days_to_bday_str = f", Days until birthday: {self.days_to_birthday()}" if self.birthday else ""
        address_str = f"\nAddress: {self.address.value}" if self.address else ""
        return f"ID: {self.id}, Name: {self.name.value}, " \
               f"Phones: {phones}, Email: {emails}{birthday_str}{days_to_bday_str}{address_str}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        """Adds a new record to the address book."""
        record.id = len(self.data) + 1
        self.data[record.id] = record

    def remove_record(self, record: Record):
        """Removes a record from the address book."""
        del self.data[record.id]

    def edit_record(self, record: Record):
        """Edits a record in the address book."""
        self.data[record.id] = record

def load_address_book():
    """Loads the address book from a file (if available)."""
    try:
        with open("address_book.pkl", "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, pickle.PickleError):
        return AddressBook()

def save_address_book(address_book):
    """Saves the address book to a file."""
    with open("address_book.pkl", "wb") as file:
        pickle.dump(address_book, file)

def main():
    address_book = load_address_book()
    ui = ConsoleUI()

    available_commands = ['add', 'search', 'delete', 'edit', 'show', 'exit']

    while True:
        ui.display_commands(available_commands)
        command = ui.get_user_input()

        if command == 'exit':
            save_address_book(address_book)
            print("Exiting the program.")
            break
        elif command == 'add':
            name = Name(input("Enter name: "))
            birthday_str = input("Enter birthday (YYYY-MM-DD): ")
            birthday = Birthday(birthday_str) if birthday_str else None
            record = Record(name, birthday)
            address_book.add_record(record)
        elif command == 'search':
            # Implement search functionality
            pass
        elif command == 'delete':
            # Implement delete functionality
            pass
        elif command == 'edit':
            # Implement edit functionality
            pass
        elif command == 'show':
            ui.display_contacts(address_book.values())
        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    main()
