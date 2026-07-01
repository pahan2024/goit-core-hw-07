from collections import UserDict
from datetime import datetime, timedelta


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter user name and/or accurate data."
        except KeyError:
            return "Contact not found."

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        # Валідація: рядок, що складається рівно з 10 цифр
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            # Валідація та перетворення рядка на об'єкт datetime.date
            valid_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(valid_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        # Повертаємо у звичному текстовому форматі при виведенні через print
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  # Нове поле для дня народження

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_number, new_number):
        phone_to_edit = self.find_phone(old_number)
        if not phone_to_edit:
            raise ValueError(f"Phone number {old_number} not found.")
        new_phone = Phone(new_number)
        phone_to_edit.value = new_phone.value

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday_str):
        # Додає дату народження до контакту
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        # Адаптоване виведення рядка, якщо додано день народження
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        # Поточна дата
        today = datetime.now().date()

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday_date = record.birthday.value
            # Переносимо день народження на поточний рік
            birthday_this_year = birthday_date.replace(year=today.year)

            # Якщо день народження вже пройшов цього року, перевіряємо наступний
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Перевіряємо інтервал у 7 днів включно з сьогоднішнім
            if today <= birthday_this_year <= today + timedelta(days=7):
                congratulation_date = birthday_this_year

                # Перенесення привітання на понеділок, якщо день народження у вихідні
                # 5 — субота, 6 — неділя
                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime("%d.%m.%Y"),
                    }
                )

        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())


def parse_input(user_input):
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise KeyError


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s phones: " + ", ".join(p.value for p in record.phones)
    else:
        raise KeyError


@input_error
def show_all(book: AddressBook):
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        raise KeyError


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"{name}'s birthday is {record.birthday}"
        return f"{name} doesn't have birthday info yet."
    else:
        raise KeyError


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next 7 days."

    result = "Upcoming birthdays:\n"
    for user in upcoming:
        result += f"{user['name']}: congratulate on {user['birthday']}\n"
    return result.strip()


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "":
            continue

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
