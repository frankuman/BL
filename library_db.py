import mysqlx
import library_db_func as lf
import configparser
import random

titles = ["The Great Gatsby", "To Kill a Mockingbird", "1984", "Pride and Prejudice", "The Catcher in the Rye",
          "Harry Potter and the Philosophers Stone", "The Hobbit", "The Lord of the Rings", "The Hunger Games",
          "The Da Vinci Code", "The Alchemist", "The Girl with the Dragon Tattoo", "The Shining", "The Chronicles of Narnia",
          "Gone with the Wind", "Moby-Dick", "Frankenstein", "Jane Eyre", "Brave New World", "The Grapes of Wrath",
          "The Picture of Dorian Gray", "The Road", "The Adventures of Huckleberry Finn", "Alices Adventures in Wonderland",
          "Dracula", "Wuthering Heights", "The Count of Monte Cristo", "The Little Prince", "The Odyssey",
          "The Adventures of Sherlock Holmes", "Les Misérables", "War and Peace", "Anna Karenina", "Crime and Punishment",
          "One Hundred Years of Solitude", "The Brothers Karamazov", "Don Quixote", "The Iliad", "The Odyssey",
          "A Tale of Two Cities", "The Divine Comedy", "The Canterbury Tales", "Paradise Lost", "Ulysses",
          "Heart of Darkness", "Slaughterhouse-Five", "The Old Man and the Sea", "Catch-22", "The Sun Also Rises"]

authors = ["F. Scott Fitzgerald", "Harper Lee", "George Orwell", "Jane Austen", "J.D. Salinger",
           "J.K. Rowling", "J.R.R. Tolkien", "J.R.R. Tolkien", "Suzanne Collins", "Dan Brown",
           "Paulo Coelho", "Stieg Larsson", "Stephen King", "C.S. Lewis", "Margaret Mitchell",
           "Herman Melville", "Mary Shelley", "Charlotte Brontë", "Aldous Huxley", "John Steinbeck",
           "Oscar Wilde", "Cormac McCarthy", "Mark Twain", "Lewis Carroll", "Bram Stoker",
           "Emily Brontë", "Alexandre Dumas", "Antoine de Saint-Exupéry", "Homer",
           "Arthur Conan Doyle", "Victor Hugo", "Leo Tolstoy", "Leo Tolstoy", "Fyodor Dostoevsky",
           "Gabriel García Márquez", "Fyodor Dostoevsky", "Miguel de Cervantes", "Homer", "Homer",
           "Charles Dickens", "Dante Alighieri", "Geoffrey Chaucer", "John Milton", "James Joyce",
           "Joseph Conrad", "Kurt Vonnegut", "Ernest Hemingway", "Joseph Heller", "Ernest Hemingway"]

publishers = ["Scribner", "J.B. Lippincott & Co.", "Secker & Warburg", "T. Egerton", "Little, Brown and Company",
              "Bloomsbury Publishing", "George Allen & Unwin", "George Allen & Unwin", "Scholastic Corporation", "Doubleday",
              "HarperCollins", "Norstedts förlag", "Doubleday", "Geoffrey Bles", "Macmillan Publishers", "Harper & Brothers",
              "Richard Bentley", "Smith, Elder & Co.", "Chatto & Windus", "Chatto & Windus", "The Viking Press",
              "Ward, Lock & Co.", "Bantam Books", "Macmillan Publishers", "Macmillan Publishers", "Archibald Constable & Co.",
              "Thomas Cautley Newby", "Smith, Elder & Co.", "The Cresset Press", "Didot", "George Allen & Unwin",
              "A. Lacroix, Verboeckhoven & Cie", "Publisher not identified", "The Russian Messenger", "The Russian Messenger",
              "Columbia Pictures", "F. Tennyson Neely", "Librairie générale française", "The Russian Messenger", "Henry Colburn",
              "Henry Colburn", "Chapman & Hall", "Folio", "Richard Brinsley Sheridan", "Samuel Simmons", "Sylvia Beach",
              "Random House", "Charles Scribners Sons", "Jonathan Cape"]

genres = ["Fiction", "Fiction", "Science Fiction", "Romance", "Fiction",
          "Fantasy", "Fantasy", "Fantasy", "Young Adult", "Mystery",
          "Fantasy", "Mystery", "Horror", "Fantasy", "Historical Fiction",
          "Adventure", "Horror", "Romance", "Dystopian", "Historical Fiction",
          "Gothic", "Post-Apocalyptic", "Adventure", "Fantasy", "Gothic",
          "Gothic", "Historical Fiction", "Fantasy", "Epic", "Mystery",
          "Historical Fiction", "Historical Fiction", "Literary Fiction", "Literary Fiction",
          "Literary Fiction", "Magical Realism", "Literary Fiction", "Literary Fiction", "Epic",
          "Epic", "Historical Fiction", "Epic", "Poetry", "Epic", "Modernist",
          "Literary Fiction", "Science Fiction", "Literary Fiction", "Satire", "Literary Fiction"]

def db():
    """
    Main function for library database program
    """
    # Read settings from the settings file
    config = configparser.ConfigParser()
    config.read('settings.ini')

    # Get database connection parameters from the settings
    db_settings = config['database']

    # Establish a session with the database
    session = mysqlx.get_session({
        "host": db_settings['host'],
        "port": int(db_settings['port']),
        "user": db_settings['user'],
        "password": db_settings['password']
    })
    addbooks = db_settings['addrandombooks']
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
                if addbooks == "True":
                    for i in range(50):
                        session.sql(f"INSERT INTO `Books` (title, author, publisher, genre) VALUES ('{titles[i]}', '{authors[i]}', '{publishers[i]}', '{genres[i]}');").execute()
                    
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
    config = configparser.ConfigParser()
    config.read('settings.ini')

    # Get database connection parameters from the settings
    db_settings = config['database']

    # Establish a session with the database
    session = mysqlx.get_session({
        "host": db_settings['host'],
        "port": int(db_settings['port']),
        "user": db_settings['user'],
        "password": db_settings['password']
    })
    addbooks = db_settings['addrandombooks']
    db_name = "myLibrary"
    
    try:
        db_name = "myLibrary"
        lf.create_all(session, db_name)
        print(f"Database '{db_name}' created successfully.")
        session.sql(f"USE {db_name}").execute()  # Switch to the newly created database
        if addbooks == "True":
            for i in range(50):
                session.sql(f"INSERT INTO `Books` (title, author, publisher, genre) VALUES ('{titles[i]}', '{authors[i]}', '{publishers[i]}', '{genres[i]}');").execute()
                
    except Exception as create_err:
        print(f"Error creating database '{db_name}': {create_err}")
    
    for i in range(1,157):
        for y in range(3):
            x = random.randint(1,9)
            session.sql(f"UPDATE LibBooks SET nrOfCopies = {x} WHERE libraryID = {y} AND bookID = {i};").execute()
    return session
