from collections import defaultdict
from datetime import datetime, timedelta
import json
import re
import os


class PersonalAssistant:
    def __init__(self):
        self.notes = {}
        self.contacts = {}
        self.modified = False


    def input_error(func):
        def inner(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            
            except ValueError:
                return "Invalid input format. Please check your input and try again."
            except KeyError:
                return "Contact not found or invalid operation. Please ensure you are providing correct input."
            except IndexError:
                return "Incomplete input. Please provide all necessary details."
            except TypeError:
                return "Invalid input type. Please ensure you are providing the correct data type."
            except Exception:
                return "An unexpected error occurred. Please try again later or contact support for assistance."
   
        return inner


    @input_error
    def parse_input(self, user_input):
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, args
    


    def add_contact(self, args):                                                         
        if len(args) != 2:
            return "Please provide both a name and a phone number!"
        
        name, phone = args
        if len(phone) != 10 or not phone.isdigit():
            return "Phone number must consist of 10 digits!"
        
        if name in self.contacts:
            return f'Contact "{name}", already exists!'
        else:
            self.contacts[name] = {"phone": phone, "birthday": None}
            self.sort_contacts()
            self.modified = True
            return f'Contact "{name}", added successfully!'
        

    def add_email(self, args):                                         ###########################
        if len(args) != 2:
            return "Please provide both a name and an email address!"
        
        name, email = args

        if name not in self.contacts:
            return f"Contact '{name}' does not exist!"
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email address format!"

        self.contacts[name]["email"] = email
        self.modified = True
        return f'Email address "{email}" added for contact "{name}" successfully!'
    

    def add_address(self, args):
        if len(args) < 5:
            return "Please provide name, house number, street, city, and country for the address!"

        name = args[0]
        address_info = {
            "house_number": args[1],
            "street": args[2],
            "city": args[3],
            "country": args[4]
        }

        if name not in self.contacts:
            return f"Contact '{name}' does not exist!"

        if "address" not in self.contacts[name]:
            self.contacts[name]["address"] = []

        self.contacts[name]["address"].append(address_info)
        self.modified = True
        return f'Address added successfully for contact "{name}"!'
    

    def update_address(self, args):
        if len(args) < 5:
            return "Please provide name, house number, street, city, and country for the new address!"

        name = args[0]
        new_address_info = {
            "house_number": args[1],
            "street": args[2],
            "city": args[3],
            "country": args[4]
        }

        if name not in self.contacts:
            return f"Contact '{name}' does not exist!"

        if "address" not in self.contacts[name]:
            return f"No address found for contact '{name}'."

        self.contacts[name]["address"] = [new_address_info]
        self.modified = True
        return f'Address updated successfully for contact "{name}"!'
    

                                                               
    def add_note(self, note_id, content):                                  
        if note_id in self.notes:
            return f'Note with ID "{note_id}" already exists!'
        else:
            self.notes[note_id] = content
            self.modified = True
            self.save_to_file("personal_assistant_notes.json")
            return f'Note with ID "{note_id}" added successfully!'


    def show_all_notes(self):
        if not self.notes:
            return "No notes found."

        all_notes = []
        for note_id, content in self.notes.items():
            all_notes.append(f"Note ID: {note_id}\nContent: {content}")

        return '\n\n'.join(all_notes)


    def edit_note(self, note_id, new_content):
        if note_id not in self.notes:
            return f'Note with ID "{note_id}" not found!'
        else:
            self.notes[note_id] = new_content
            self.modified = True
            self.save_to_file("personal_assistant_notes.json")
            return f'Note with ID "{note_id}" edited successfully!'
        

    def delete_note(self, note_id):
        if note_id not in self.notes:
            return f'Note with ID "{note_id}" not found!'
        else:
            del self.notes[note_id]
            self.modified = True
            self.save_to_file("personal_assistant_notes.json")
            return f'Note with ID "{note_id}" deleted successfully!'
        

    def search_notes_by_keyword(self, keyword):
        found_notes = []
        for note_id, content in self.notes.items():
            if keyword.lower() in content.lower():
                found_notes.append((note_id, content))
        if found_notes:
            return found_notes
        else:
            return f'No notes found containing the keyword "{keyword}".'
    

                                                                       
    def update_contact(self, args):                       ####################################
        if len(args) != 2:
            return "Please provide both a name and a phone number!"
        name, phone = args
        if len(phone) != 10 or not phone.isdigit():
            return "Phone number must consist of 10 digits!"
        
        if name not in self.contacts:
            return "Contact not found or not existing!"
        else:
            self.contacts[name]["phone"] = phone
            self.modified = True
            return f'Contact "{name}", successfully updated!'
        
        
    def update_contact_name(self, args):
        if len(args) != 2:
            return "Please provide both the old and new names!"
        
        old_name, new_name = args
        if old_name not in self.contacts:
            return "Contact not found, or not existing!"
        
        self.contacts[new_name] = self.contacts.pop(old_name)
        self.sort_contacts()
        self.modified = True
        return f'Contact name updated from "{old_name}" to "{new_name}" successfully!'


    def show_phone(self, args): 
        name = args[0]
        if name not in self.contacts:
            return"Contact not found or not existing!"
        contact_info = self.contacts[name]
        phone = contact_info.get("phone", "Phone number not available")
        email = contact_info.get("email", "Email address not available")
        birthday = contact_info.get("birthday", "Birthday not available")
        address_info = ""
        if "address" in contact_info:
            address_info = "\nAddress: "
            for address in contact_info["address"]:
                address_info += f'{address["house_number"]}, {address["street"]}, {address["city"]}, {address["country"]}\n'
        return f'Contact details for "{name}":\nPhone: {phone}\nEmail: {email}\nBirthday: {birthday}{address_info}'
        
    

    def show_all(self):
        if not self.contacts:
            return "No contacts found."

        contact_details = []
        for name, info in self.contacts.items():
            contact_info = f'Contact details for "{name}":\n'
            if "phone" in info:
                contact_info += f'Phone: {info["phone"]}\n'
            if "email" in info:
                contact_info += f'Email: {info["email"]}\n'
            if "birthday" in info:
                contact_info += f'Birthday: {info["birthday"]}\n'
            if "address" in info:
                contact_info += "Addresses:\n"
                for address in info["address"]:
                    contact_info += f'House Number: {address["house_number"]}, Street: {address["street"]}, City: {address["city"]}, Country: {address["country"]}\n'
            contact_details.append(contact_info)

        return '\n\n'.join(contact_details)                             
    

    def delete_contact(self, args):
        name = args[0]
        if name in self.contacts:
            del self.contacts[name]
            self.sort_contacts()
            self.modified = True
            return f'Contact "{name}" deleted successfully!'
        else:
            return f'Contact "{name}" does not exist!'
        

    def clear_all_contacts(self):
        confirmation = input("Are you sure you want to delete all contacts? (yes/no): ")
        if confirmation.lower() == "yes":
            self.contacts.clear()
            self.modified = True
            return 'All contacts deleted successfully!'
        else:
            return 'No contacts were deleted.'
    

    def add_birthday(self, name, birth_day):
        if name in self.contacts:
            self.contacts[name]["birthday"] = birth_day
            self.modified = True
            return f'Birthday successfully added for contact "{name}"!'
        else:
            return f'Contact "{name}", does not exist!'


    def show_birthday(self, name):
        if name in self.contacts and self.contacts[name]["birthday"]:
            return f'Birthday for contact "{name}": {self.contacts[name]["birthday"]}'
        elif name not in self.contacts:
            return f'Contact "{name}", does not exists!'
        else:
            f'No birthday found for contact "{name}"!'


    def get_birthdays_per_week(self):                                             
        birthdays_per_week = defaultdict(list)
        today = datetime.today().date()
        next_week = today + timedelta(days=7)

        for name, info in self.contacts.items():
            if info["birthday"]:
                birth_day = datetime.strptime(info["birthday"], '%d/%m/%Y').date() 
                birthday_current_year = birth_day.replace(year=today.year)

                if birthday_current_year < today:
                    birthday_current_year = birthday_current_year.replace(year=today.year + 1)

                delta_days = (birthday_current_year - today).days

                if 0 <= delta_days < 7:
                    birthday_week = birthday_current_year.strftime("%A")
                    if birthday_week in ["Saturday", "Sunday"]:
                        birthday_week = "Monday"
                    birthdays_per_week[birthday_week].append(name)

        return birthdays_per_week
    

    @staticmethod
    def validate_birthday(birthday_str):
        try:
            datetime.strptime(birthday_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False
    

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.contacts, file)

    def save_notes_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.notes, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.contacts = json.load(file)
        except FileNotFoundError:
            print("No previous data found. Starting with an empty address book.")
        
    def load_notes_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.notes = json.load(file)
        except FileNotFoundError:
            print("No previous notes found. Starting with an empty notes list.")


    def sort_contacts(self):
        self.contacts = dict(sorted(self.contacts.items()))

    



def main():
    personal_assistant = PersonalAssistant()
    filename = "personal_assistant.json"
    filename_notes = "personal_assistant_notes.json"
    personal_assistant.load_from_file(filename)
    personal_assistant.load_notes_from_file(filename_notes)


    print('\nWelcome to your assistant bot!\nIf you need help with the commands, please type "help".')

    save_choice = None

    while True:
        user_input = input("\nEnter a command: ")
        parts = user_input.split()
        command = parts[0].strip().lower()
        args = parts[1:]

        if command in ["close", "exit"]:
            if personal_assistant.modified:
                save_choice = input("Do you want to save changes to the address book, before exiting? (yes/no): ")
                if save_choice.lower() == "yes":
                    personal_assistant.save_to_file(filename)
                    personal_assistant.save_notes_to_file(filename_notes)
                    print("Saved")
            print("Goodbye!")
            break

        elif command == "hello":
            print("Hi, how can I help you today?")

        elif command == "help":
            print('\nPlease use one of the commands bellow:')
            print('"add ___"             - To add a new contact, (name and number)\n"edit ___"            - To edit an existing contact\'s number, (name + new number)\n"edit-name ___"       - To edit the name of an existing contact, (old name + new name)')
            print('"add-address ___"     - To add an address for an existing contact, (contact name  + house number, street, city, country)\n"edit-address ___"    - To edit the address of a contact, (contact name + new address)')
            print('"show ___"            - To display a specific contact,\n"contacts"            - To display all contacts,\n"add-email ___"       - To add an email address to an existing contact, (this command can also change the current email),')
            print('"add-birthday ___"    - To add birthday to an existing contact, (DD/MM/YYYY)\n"delete ___"          - To delete a contact,\n"clear_all"           - To delete all contacts,')
            print('"show-birthday ___"   - To display the birthday of a contact,\n"birthdays"           - To display the birthdays of contacts occurring in the next week,')
            print('"add-note ___"        - To start writing your note, (note ID + your text)\n"edit-note ___"       - To edit an existing note, (note ID + new text)\n"notes"               - To display all notes,')
            print('"delete-note ___"     - To delete an existing note, (note ID),\n"search-note___"      - To find a specific note by a keyword, (keyword)\n"notes"               - To see all notes,')
            print('And "exit" or "close"')

        elif command == "add-note":                                 
            if len(args) < 2:
                print("Please provide a note ID and content.")
            else:
                note_id, content = args[0], ' '.join(args[1:])
                print(personal_assistant.add_note(note_id, content))

        elif command == "edit-note":
            if len(args) < 2:
                print("Please provide a note ID and new content.")
            else:
                note_id, new_content = args[0], ' '.join(args[1:])
                print(personal_assistant.edit_note(note_id, new_content))

        elif command == "delete-note":
            if len(args) != 1:
                print("Please provide the note ID to delete.")
            else:
                note_id = args[0]
                print(personal_assistant.delete_note(note_id))

        elif command == "notes":
            print(personal_assistant.show_all_notes())

        elif command == "search-note":
            if len(args) != 1:
                print("Please provide a keyword to search.")
            else:
                keyword = args[0]
                results = personal_assistant.search_notes_by_keyword(keyword)
                if isinstance(results, str):
                    print(results)
                else:
                    print("Notes containing the keyword:")
                    for note_id, content in results:
                        print(f"ID: {note_id}, Content: {content}")         

        
        
        elif command == "add":
            print(personal_assistant.add_contact(args))

        elif command == "add-address":
            print(personal_assistant.add_address(args))

        elif command == "edit-address":
            print(personal_assistant.update_address(args))

        elif command == "add-email":
            print(personal_assistant.add_email(args))

        elif command == "edit":
            print(personal_assistant.update_contact(args))

        elif command == "edit-name":
            print(personal_assistant.update_contact_name(args))

        elif command == "show":
            print(personal_assistant.show_phone(args))

        elif command == "contacts":
            print(personal_assistant.show_all())

        elif command == "delete":
            print(personal_assistant.delete_contact(args))

        elif command == "clear_all":
            print(personal_assistant.clear_all_contacts())       #        ******  This command shall be used carefully :)) ******* 

        elif command == "add-birthday":
            if len(args) != 2:
                print("Please provide both name and birthday in DD/MM/YYYY format!")
            else:
                name, birth_date = args
                print(personal_assistant.add_birthday(name, birth_date))

        elif command == "show-birthday":
            if len(args) != 1:
                print("Please provide the name of the contact.")
            else:
                name = args[0]
                print(personal_assistant.show_birthday(name))

        elif command == "birthdays":
            birthdays = personal_assistant.get_birthdays_per_week()
            if birthdays:
                for day, contacts in birthdays.items():
                    print(f"{day}: {', '.join(contacts)}")
            else:
                print("No birthdays in the next week.")

        else:
            print("\nInvalid command.\nPlease try again!\n")


if __name__ == "__main__":
    main()