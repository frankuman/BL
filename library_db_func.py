import mysqlx
from mysql.connector import DatabaseError, OperationalError

def create_database(session, db_name):
    """
    Create a database with the name 'db_name' in the session 'session'
    """
    session.sql(f"DROP DATABASE IF EXISTS `{db_name}`;").execute()
    try:
        print(f"Creating database {db_name}")
        session.sql(f"CREATE DATABASE {db_name} CHARACTER SET 'utf8mb4'").execute()
    except DatabaseError as db_err:
        print(f"Failed to create database, error: {db_err}")
        return 1
    else:
        return 0

def create_tables(session):
    """
    Create all tables needed for the library database
    """
    tables = {
    "Books": # CREATE Books
     "CREATE TABLE `Books` (" \
     "  `bookID` INT UNSIGNED AUTO_INCREMENT," \
     "  `title` varchar(128) NOT NULL," \
     "  `author` varchar(64) NOT NULL," \
     "  `publisher` varchar(64) NOT NULL," \
     "  `genre` varchar(16) NOT NULL," \
     "  PRIMARY KEY (`bookID`)" \
     ") ENGINE=InnoDB",   
    "Members": # CREATE Members
     "CREATE TABLE `Members` (" \
     "  `memberID` INT UNSIGNED AUTO_INCREMENT," \
     "  `firstName` varchar(64) NOT NULL," \
     "  `lastName` varchar(64) NOT NULL," \
     "  `emailAddress` varchar(64) NOT NULL," \
     "  `address` varchar(64) NOT NULL," \
     "  `city` varchar(64) NOT NULL," \
     "  `debt` INT DEFAULT 0," \
     "  PRIMARY KEY (`memberID`)" \
     ") ENGINE=InnoDB",   
    "Libraries": # CREATE Libraries
     "CREATE TABLE `Libraries` (" \
     "  `libraryID` INT UNSIGNED AUTO_INCREMENT," \
     "  `address` varchar(64) NOT NULL," \
     "  `city` varchar(64) NOT NULL," \
     "  PRIMARY KEY (`libraryID`)" \
     ") ENGINE=InnoDB",    
    "Loans": # CREATE Loans
     "CREATE TABLE `Loans` (" \
     "  `loanID` INT UNSIGNED AUTO_INCREMENT," \
     "  `bookID` INT UNSIGNED," \
     "  `memberID` INT UNSIGNED," \
     "  `loanLib` INT UNSIGNED," \
     "  `retLib` INT UNSIGNED," \
     "  `startDate` DATE," \
     "  `dueDate` DATE," \
     "  `returnedDate` DATE," \
     "  PRIMARY KEY (`loanID`)," \
     "  FOREIGN KEY (`bookID`) REFERENCES `Books`(`bookID`)," \
     "  FOREIGN KEY (`memberID`) REFERENCES `Members`(`memberID`)," \
     "  FOREIGN KEY (`loanLib`) REFERENCES `Libraries`(`libraryID`)," \
     "  FOREIGN KEY (`retLib`) REFERENCES `Libraries`(`libraryID`)" \
     ") ENGINE=InnoDB",
    "LibBooks": # CREATE LibBooks
     "CREATE TABLE `LibBooks` (" \
     "  `libraryID` INT UNSIGNED," \
     "  `bookID` INT UNSIGNED," \
     "  `nrOfCopies` INT," \
     "  PRIMARY KEY (`libraryID`, `bookID`)," \
     "  FOREIGN KEY (`libraryID`) REFERENCES `Libraries`(`libraryID`)," \
     "  FOREIGN KEY (`bookID`) REFERENCES `Books`(`bookID`)" \
     ") ENGINE=InnoDB"
    }

    for i in tables.items():
        try:
            print(f"Creating table {i[0]}:")
            session.sql(i[1]).execute()
        except DatabaseError as db_err:
            if db_err.errno == 1050:
                print("already exists.")
            else:
                print(db_err.msg)
            return 1
        else:
            print(f"{i[0]} created succesfully.")
    return 0

def create_procedures(session):
    """
    Create stored procedures for library database
    """
    lend_book = [
        #"DELIMITER &&",
        " CREATE PROCEDURE `lendBook` (IN mID INT UNSIGNED, IN bID INT UNSIGNED, IN lID INT UNSIGNED, OUT msg TEXT)" \
        " BEGIN" \
    	" DECLARE x INT;" \
        " DECLARE datevar DATE;" \
	    " DECLARE flag INT;" \
        " DECLARE now DATE;" \
        " SET now = CURRENT_DATE();" \
        " SET x = 0;" \
        " SET flag = 1;" \
        " SET msg = '';" \
        " START TRANSACTION;" \
        " SELECT nrOfCopies INTO x FROM LibBooks WHERE libraryID = lID AND bookID = bID;"\
        " IF x = 0 THEN" \
		" SET flag = 0;" \
        " SET msg = CONCAT(msg, 'Book not available from this library.');" \
	    " END IF;" \
	    " SELECT EXISTS(SELECT * FROM Loans WHERE memberID = mID AND bookID = bID AND returnedDate IS NULL) INTO x;" \
	    " IF x = 1 THEN" \
        " SELECT loanID INTO x FROM Loans WHERE memberID = mID AND bookID = bID AND returnedDate IS NULL;" \
		" UPDATE Loans SET retLib = lID, returnedDate = now WHERE loanID = x;" \
        " SET msg = CONCAT(msg, 'Loan updated\n');" \
	    " END IF;" \
        " SELECT dueDate INTO datevar FROM Loans WHERE loanID = x;" \
        " IF now > datevar THEN" \
		" SET flag = 0;" \
		" UPDATE Members SET debt = debt + 10 WHERE memberID = (SELECT memberID FROM Loans WHERE loanID = x);" \
		" SET msg = CONCAT(msg, 'Loan due date expired. Book returned and 10 added to debt.');" \
        " END IF;" \
        " SELECT debt INTO x FROM Members WHERE memberID = mID;" \
        " IF x > 0 THEN" \
		" SET flag = 0;" \
        " SET msg = CONCAT(msg, 'You may not borrow any books before paying current debt. Current Debt: ');" \
        " SET msg = CONCAT(msg, CONVERT(x, CHAR));" \
	    " END IF;" \
        " IF flag = 1 THEN" \
		" INSERT INTO Loans (bookID, memberID, loanLib, startDate, dueDate)" \
        " VALUES (bID, mID, lID, now, ADDDATE(now, 30));" \
        " SET msg = CONCAT(msg, 'Book succesfully borrowed.\n Book to be returned by: ');" \
        " SET msg = CONCAT(msg, CONVERT(ADDDATE(now, 30), CHAR));" \
        " UPDATE LibBooks SET nrOfCopies = nrOfCopies - 1 WHERE bookID = bID AND libraryID = lID;" \
        " END IF;" \
        " COMMIT;" \
        " END;"#,
        #"DELIMITER ;"
    ]

    return_book = [
        #"DELIMITER &&",
        " CREATE PROCEDURE returnBook (IN mID INT UNSIGNED, bID INT UNSIGNED, IN lib INT UNSIGNED, OUT msg TEXT)" \
        " BEGIN" \
        " DECLARE loan INT;" \
	    " DECLARE now DATE;" \
        " DECLARE due DATE;" \
        " SET now = CURRENT_DATE();" \
	    " SET msg = '';" \
        " SELECT EXISTS(SELECT * FROM Loans WHERE memberID = mID AND bookID = bID AND returnedDate IS NULL) INTO loan;" \
        " IF loan = 0 THEN" \
        " SET msg = CONCAT(msg, 'Loan does not exist');" \
        " ELSEIF loan = 1 THEN" \
        " SELECT loanID INTO loan FROM Loans WHERE memberID = mID AND bookID = bID AND returnedDate IS NULL;" \
        " UPDATE Loans SET returnedDate = now, retLib = lib WHERE loanID = loan;" \
        " SET msg = CONCAT(msg, 'The book has been returned.');" \
        " SELECT dueDate INTO due FROM Loans WHERE loanID = loan;" \
        " IF now > due THEN" \
		" UPDATE Members SET debt = debt + 10 WHERE memberID = (SELECT memberID FROM Loans WHERE loanID = loan);" \
        " SET msg = CONCAT(msg, ' 10 added to debt for late return.');" \
        " END IF;" \
        " END IF;" \
        " END;"#,
        #"DELIMITER ;"
    ]

    for query in lend_book:
        try:
            session.sql(query).execute()
        except DatabaseError as db_err:
            print("Error: Could not create procedure 'lendBook'")
            print(db_err.msg)
            return 1
    
    for query in return_book:
        try:
            session.sql(query).execute()
        except DatabaseError as db_err:
            print("Error: Could not create procedure returnBook")
            print(db_err.msg)
            return 1
    return 0

def create_triggers(session):
    """
    Create triggers for library database
    """
    book_returned = [
        #"DELIMITER &&",
        "CREATE TRIGGER bookReturned" \
        " AFTER UPDATE ON Loans" \
        " FOR EACH ROW" \
        " BEGIN" \
	    " IF OLD.returnedDate IS NULL AND NEW.returnedDate IS NOT NULL THEN" \
		" UPDATE LibBooks SET nrOfCopies = nrOfCopies + 1" \
        " WHERE LibBooks.libraryID = NEW.retLib AND LibBooks.BookID = NEW.bookID;" \
	    " END IF;" \
        "END;"#,
        #"DELIMITER ;"
    ]

    book_added = [
        #"DELIMITER &&",
        "CREATE TRIGGER bookAdded" \
        " AFTER INSERT ON Books" \
        " FOR EACH ROW" \
        " BEGIN" \
	    " DECLARE libNum INT;" \
        " SELECT COUNT(LibraryID) INTO libNum FROM Libraries;" \
        " insert_loop: LOOP" \
		" INSERT INTO LibBooks VALUES (libNum, NEW.bookID, 0);" \
        " SET libNum = libNum - 1;" \
        " IF libNum = 0 THEN" \
		" LEAVE insert_loop;" \
		" END IF;" \
	    " END LOOP;" \
        "END;",
        #"DELIMITER ;"
    ]

    for query in book_returned:
        try:
            session.sql(query).execute()
        except DatabaseError as db_err:
            print("Error: Could not create trigger 'bookReturned'")
            print(db_err.msg)
            return 1
    
    for query in book_added:
        try:
            session.sql(query).execute()
        except DatabaseError as db_err:
            print("Error: Could not create trigger bookAdded")
            print(db_err.msg)
            return 1
    return 0

def insert_test_data(session):
    """
    Inserts test data into library system tables
    """
    test_data = {
        "Libraries": # INSERT INTO Libraries
        "INSERT INTO `Libraries` VALUES" \
        " (1, 'St Nicholas Coppice 54', 'Ckenveyhedge')," \
        " (2, 'Lucerne Boulevard 12', 'West Glosrdeau')," \
        " (3, 'Shire Orchards 25', 'Niemau');",
        "Books": # INSERT INTO Books
        "INSERT INTO `Books` (title, author, publisher, genre) VALUES" \
        " ('The Fellowship of the Ring', 'J.R.R. Tolkien', 'Harper Collins', 'Fantasy')," \
        " ('The Two Towers', 'J.R.R. Tolkien', 'Harper Collins', 'Fantasy')," \
        " ('The Return of the King', 'J.R.R. Tolkien', 'Harper Collins', 'Fantasy')," \
        " ('The Hobbit', 'J.R.R. Tolkien', 'Harper Collins', 'Fantasy')," \
        " ('So Long and Thanks for All the Fish', 'Douglas Adams', 'Pan Books', 'Sci-Fi')," \
        " ('Database Systems A Practical Approach to Design, Implementation, and Management', 'Thomas M. Connolly', 'Pearson Education Limited', 'Computer Science');",
        "Members": # INSERT INTO Members
        "INSERT INTO `Members` (firstName, lastName, emailAddress, address, city) VALUES" \
        " ('Theudoricus', 'Hendrickx','th@abc.com', 'Vernon End 6', 'Niemau')," \
        " ('Majda', 'Braxton', 'mb@abc.com', 'Warwick Fields 15', 'Niemau')," \
        " ('Emmalyn', 'Ó Proinntigh', 'ep@abc.com', 'Brambling Birches 11', 'East Skerna')," \
        " ('Ampelio', 'Traylor', 'at@abc.com', 'Powell Cross 1', 'Ckenveyhedge')," \
        " ('Wulfhram', 'Blanco', 'wb@abc.com', ' Kenyon Newydd 4', 'Ckenveyhedge');",
        "LibBooks1": # UPDATE LibBook copies
        "UPDATE `LibBooks` SET nrOfCopies = 5 WHERE libraryID = 1 AND bookID = 1;",
        "LibBooks2":
        "UPDATE `LibBooks` SET nrOfCopies = 3 WHERE libraryID = 1 AND bookID = 2;",
        "LibBooks3":
        "UPDATE `LibBooks` SET nrOfCopies = 3 WHERE libraryID = 2 AND bookID = 2;",
        "LibBooks4":
        "UPDATE `LibBooks` SET nrOfCopies = 2 WHERE libraryID = 2 AND bookID = 5;",
        "LibBooks5":
        "UPDATE `LibBooks` SET nrOfCopies = 2 WHERE libraryID = 3 AND bookID = 5;",
        "LibBooks6":
        "UPDATE `LibBooks` SET nrOfCopies = 2 WHERE libraryID = 3 AND bookID = 4;",
        "LibBooks7":
        "UPDATE `LibBooks` SET nrOfCopies = 2 WHERE libraryID = 3 AND bookID = 3;",
        "LibBooks8":
        "UPDATE `LibBooks` SET nrOfCopies = 2 WHERE libraryID = 3 AND bookID = 1;",
    }

    for i in test_data.items():
        try:
            print(f"Inserting test data in table {i[0]}: ")
            session.sql(i[1]).execute()
        except DatabaseError as db_err:
            print("Error: Could not insert test data")
            print(db_err.msg)
            return 1
    return 0

def create_all(session, db_name):
    """
    Creates database, tables, procedures and triggers, allows to insert test data
    """
    res = 0
    res += create_database(session, db_name)
    session.sql(f"USE {db_name}").execute()
    res += create_tables(session)
    res += create_procedures(session)
    res += create_triggers(session)
    res += insert_test_data(session)
    return res
