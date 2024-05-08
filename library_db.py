import mysqlx
import library_db_func as lf
import randomname
import random
def db():
    """
    Main function for library database program
    """
    session = mysqlx.get_session({
        "host": "localhost",
        "port": 33060,
        "user": "bibloaner", # enter your username here
        "password": "dv1663" # enter your password here
    })

    db_name = "myLibrary"
    try:
        session.sql(f"USE {db_name}").execute()
    except mysqlx.errors.OperationalError as db_err:
        if db_err.errno == 1049:
            print(f"The database '{db_name}' doesn't exist. Creating new db...")
            try:
                lf.create_all(session, db_name)
                print(f"Database '{db_name}' created successfully.")
                session.sql(f"USE {db_name}").execute()  # Switch to the newly created database
                for i in range(50):
                    name1, name2, name3 = randomname.get_name(),randomname.get_name(),randomname.get_name()
                    session.sql(f"INSERT INTO `Books` (title, author, publisher, genre) VALUES ('{name1}', '{name2}', '{name3}', 'Sci-Fi');").execute()
                    
            except Exception as create_err:
                print(f"Error creating database '{db_name}': {create_err}")
        else:
            print(f"Error: {db_err}")
    for i in range(1,157):
        for y in range(3):
            x = random.randint(1,9)
            session.sql(f"UPDATE LibBooks SET nrOfCopies = {x} WHERE libraryID = {y} AND bookID = {i};").execute()
    
    return session
def reset_all():
    
    session = mysqlx.get_session({
        "host": "localhost",
        "port": 33060,
        "user": "bibloaner", # enter your username here
        "password": "dv1663" # enter your password here
    })
    try:
        db_name = "myLibrary"
        lf.create_all(session, db_name)
        print(f"Database '{db_name}' created successfully.")
        session.sql(f"USE {db_name}").execute()  # Switch to the newly created database
        for i in range(50):
            name1, name2, name3 = randomname.get_name(),randomname.get_name(),randomname.get_name()
            session.sql(f"INSERT INTO `Books` (title, author, publisher, genre) VALUES ('{name1}', '{name2}', '{name3}', 'Sci-Fi');").execute()
                
    except Exception as create_err:
        print(f"Error creating database '{db_name}': {create_err}")
      
    for i in range(1,157):
        for y in range(3):
            x = random.randint(1,9)
            session.sql(f"UPDATE LibBooks SET nrOfCopies = {x} WHERE libraryID = {y} AND bookID = {i};").execute()
    return session
def functions():
    while True:
        print("\n\nWhat would you like to do [0-11]?\n")
        print(" 1. Lend a book to a member\n" \
              " 2. Return a book to a library\n" \
              " 3. Add a new member\n" \
              " 4. Add a new book\n" \
              " 5. Add copies of a book to a library\n" \
              " 6. Add a new library (Feature coming soon)\n" \
              " 7. See an overview of a member\n" \
              " 8. See all books current loans by a member\n" \
              " 9. See all books in a library\n" \
              " 10. See all members\n" \
              " 11. See all books\n" \
              " 0. Exit"
            )
        user_action = input(">>")

        if user_action not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"):
            print("Invalid input")
            continue

        elif user_action == "1":
            member = input("ID of member borrowing the book: ")
            book = input("ID of book being borrowed: ")
            library = input("ID of library being borrowed from: ")
            try:
                session.sql(f"CALL lendBook({member}, {book}, {library}, @res);").execute()
                result = session.sql("SELECT @res;").execute()
            except lf.DatabaseError as db_err:
                print("Error: Loan failed")
                print(db_err.msg)
            else:
                for row in result.fetch_all():
                    print(row)
            continue

        elif user_action == "2":
            loan = input("ID of loan being finished: ")
            library = input("ID of library the book is returned to: ")
            try:
                session.sql(f"CALL returnBook({loan}, {library}, @res);")
                result = session.sql("SELECT @res;").execute()
            except lf.DatabaseError as db_err:
                print("Error: Book return failed")
                print(db_err.msg)
            else:
                for row in result.fetch_all():
                    print(row)
            continue

        elif user_action == "3":
            first_name = input("First name: ")
            last_name = input("Last name: ")
            email = input("Email address: ")
            address = input("Address: ")
            city = input("City: ")
            try:
                query = f"INSERT INTO `Members` (firstName, lastName, emailAddress, address, city) VALUES ({first_name}, {last_name}, {email}, {address}, {city});"
                session.sql(query).execute()
            except lf.DatabaseError as db_err:
                print("Error: Member creation failed")
                print(db_err.msg)
            else:
                print("Member successfully added")
            continue

        elif user_action == "4":
            title = input("Title: ")
            author = input("Author: ")
            publisher = input("Publisher: ")
            genre = input("Genre: ")
            try:
                session.sql(f"INSERT INTO `Books` (title, author, publisher, genre) VALUES ({title}, {author}, {publisher}, {genre});").execute()
            except lf.DatabaseError as db_err:
                print("Error: Book creation failed")
                print(db_err.msg)
            else:
                print("Book successfully added")
            continue

        elif user_action == "5":
            library = input("ID of library being added to: ")
            book = input("ID of book being added: ")
            nr = input("Number of copies being added: ")
            try:
                session.sql(f"UPDATE LibBooks SET nrOfCopies = nrOfCopies + {int(nr)} WHERE libraryID = {library} AND bookID = {book};").execute()
            except lf.DatabaseError as db_err:
                print("Error: Adding books failed")
                print(db_err.msg)
            else:
                print("Book(s) successfully added")
            continue

        elif user_action == "6":
            print("Feature not yet implemented")
            continue

        elif user_action == "7":
            member = input("Member ID: ")
            try:
                query = f"SELECT M.firstName, M.lastName, COUNT(L.loanID), M.debt FROM Members M INNER JOIN Loans L ON M.memberID = L.memberID WHERE M.memberID = {member} AND L.returnedDate IS NULL GROUP BY M.firstName, M.lastName, M.debt;"
                result = session.sql(query).execute()
            except lf.DatabaseError as db_err:
                print("Error: Member overview failed")
                print(db_err.msg)
            else:
                print("| {:<15} | {:<15} | {:<15} | {}".format("First name", "Last name", "Active loans", "Debt"))
                print("-"*68)
                for (firstName, lastName, loans, debt) in result.fetch_all():
                    print("| {:<15} | {:<15} | {:<15} | {}".format(firstName, lastName, loans, debt))
            continue

        elif user_action == "8":
            member = input("Member ID: ")
            try:
                query = f"SELECT  L.loanID, B.bookID, B.title, L.dueDate FROM Members M INNER JOIN Loans L ON m.memberID = L.memberID INNER JOIN Books B ON B.bookID = L.bookID WHERE M.memberID = {member} AND L.returnedDate IS NULL;"
                result = session.sql(query).execute()
            except lf.DatabaseError as db_err:
                print("Error: Member loans overview failed")
                print(db_err.msg)
            else:
                print("| {:<15} | {:<15} | {}".format("BookID", "Title", "Due date"))
                print("-"*68)
                for (bookID, title, dueDate) in result.fetch_all():
                    print("| {:<15} | {:<15} | {}".format(bookID, title, dueDate))
            continue

        elif user_action == "9":
            library = input("Library ID: ")
            try:
                query = f"SELECT B.bookID, B.title, L.nrOfCopies FROM Libraries INNER JOIN LibBooks L ON Libraries.libraryID = L.libraryID INNER JOIN Books B ON B.bookID = L.bookID WHERE Libraries.libraryID = {library} AND L.nrOfCopies > 0;"
                result = session.sql(query).execute()
            except lf.DatabaseError as db_err:
                print("Error: Library overview failed")
                print(db_err.msg)
            else:
                print("| {:<15} | {:<15} | {}".format("BookID", "Title", "Copies"))
                print("-"*68)
                for (bookID, title, copies) in result.fetch_all():
                    print("| {:<15} | {:<15} | {}".format(bookID, title, copies))
            continue

        elif user_action == "10":
            try:
                result = session.sql("SELECT memberID, firstname, lastName FROM Members;").execute()
            except lf.DatabaseError as db_err:
                print("Error: Viewing members failed")
                print(db_err.msg)
            else:
                print("| {:<15} | {:<15} | {}".format("ID", "First name", "Last name"))
                print("-"*68)
                for (memberID, firstName, lastName) in result.fetch_all():
                    print("| {:<15} | {:<15} | {}".format(memberID, firstName, lastName))
            continue

        elif user_action == "11":
            try:
                result = session.sql("SELECT bookID, title, author FROM Books;").execute()
            except lf.DatabaseError as db_err:
                print("Error: Viewing books failed")
                print(db_err.msg)
            else:
                print("| {:<15} | {:<15} | {}".format("ID", "Title", "Author"))
                print("-"*68)
                for (bookID, title, author) in result.fetch_all():
                    print("| {:<15} | {:<15} | {}".format(bookID, title, author))
            continue

        elif user_action == "0":
            break




