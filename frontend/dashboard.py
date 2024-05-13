"""
Oliver Bölin
BTH, 2024
Flask frontend
"""
from flask import Flask, render_template, request, jsonify, redirect,url_for
import json
import library_db_func
import library_db
import Levenshtein
import datetime
app = Flask(__name__)
session = library_db.reset_all()

@app.route("/", methods=["POST", "GET"])
def start():
    result = session.sql("SELECT bookID, title, author FROM Books;").execute()
    all_result = result.fetch_all()
    amount_of_books = len(all_result)
    copies_list = []

    for i in range(1, amount_of_books+1):
        sum_result = session.sql(f"SELECT SUM(nrOfCopies) AS total_copies FROM LibBooks WHERE bookID = {str(i)};").execute()
        row = sum_result.fetch_one()
        total_copies_decimal = row["total_copies"]
        total_copies_int = int(total_copies_decimal)
        copies_list.append(total_copies_int)
    
    list_with_copies = []
    for index, book in enumerate(all_result):
        book = list(book)  # Convert Row object to list
        book.append(copies_list[index])
        list_with_copies.append(book)
    print(list_with_copies)
    sort_by = request.args.get('search')

    if sort_by != None:
        try:
            sort_by = int(sort_by)
            sorting_version = 'bookID'
        except:
            sorting_version = 'title'

        if sorting_version == 'title':
            list_with_copies.sort(key=lambda x: Levenshtein.distance(x[1], sort_by))  
        elif sorting_version == 'bookID':
            list_with_copies.sort(key=lambda x: abs(x[0] - sort_by))  

    return render_template('index.html', all_result=list_with_copies)

@app.route("/lend", methods=["POST", "GET"])
def lend_book():
    return render_template('lend.html')

@app.route("/return", methods=["POST", "GET"])
def return_book():
    return render_template('return.html')

@app.route("/lend-result", methods=["POST", "GET"])
def catch_lend_form():
    search_values = request.args.getlist('search')
    lib_tick_value = request.args.get('lib_tick')
    Book_id = search_values[0]
    Member_id = search_values[1]
    try:
        session.sql(f"CALL lendBook({Member_id}, {Book_id}, {lib_tick_value}, @res);").execute()
        result = session.sql("SELECT @res;").execute()
        if result:
        # Extract the value from the result
            lend_result = result.fetch_all()
            print(lend_result)
            lend_result = str(lend_result[0][0])
            lend_result_lst = lend_result.split(".")
            lend_result = lend_result_lst[0]
            return_result = lend_result_lst[1]
            
        else:
            lend_result = "No result"

    except library_db_func.mysqlx.errors.OperationalError as db_err:
        lend_result = "BibLoaner error 1: DB error or you failed... Try again"
        return_result = ""
        print(db_err)
    return render_template('lend-result.html', lend_result=lend_result,return_result=return_result)

@app.route("/return-result", methods=["POST", "GET"])
def catch_return_form():
    search_values = request.args.getlist('search')
    lib_tick_value = request.args.get('lib_tick')
    Book_id = search_values[0]
    Member_id = search_values[1]
    try:
        session.sql(f"CALL returnBook({Member_id}, {Book_id}, {lib_tick_value}, @res);").execute()
        result = session.sql("SELECT @res;").execute()
        if result:
        # Extract the value from the result
            lend_result = result.fetch_all()
            print(lend_result)
            lend_result = str(lend_result[0][0])
            lend_result_lst = lend_result.split(".")
            lend_result = lend_result_lst[0]
            try:
                return_result = lend_result_lst[1]
            except IndexError:
                return_result = " "
        else:
            lend_result = "No result"

    except library_db_func.mysqlx.errors.OperationalError as db_err:
        lend_result = "BibLoaner error 1: DB error or you failed... Try again"
        return_result = ""
        print(db_err)
    #print(str(result[0]))
    
    #print(res_lst)
    
    #last_str = str_lst[1]
    return render_template('return-result.html', lend_result=lend_result,return_result=return_result)

@app.route("/members", methods=["POST", "GET"])
def view_members():
    
    result = session.sql(f"SELECT M.memberID, M.firstName, M.lastName, COUNT(L.loanID), M.debt FROM Members M LEFT JOIN Loans L ON M.memberID = L.memberID WHERE L.returnedDate IS NULL GROUP BY M.memberID, M.firstName, M.lastName, M.debt;").execute()
    all_result = result.fetch_all()
    members_list = []
    for member in all_result:
        members_list.append(list(member))
    print(members_list)

    sort_by = request.args.get('search')

    if sort_by != None:
        try:
            sort_by = int(sort_by)
            sorting_version = 'bookID'
        except:
            sorting_version = 'title'

        if sorting_version == 'title':
            members_list.sort(key=lambda x: Levenshtein.distance(x[1], sort_by))  
        elif sorting_version == 'bookID':
            members_list.sort(key=lambda x: abs(x[0] - sort_by))  

    return render_template('members.html', members_list=members_list)

@app.route("/memberinfo/<int:member_id>", methods=["POST", "GET"])
def member_info(member_id):
    loans_result = session.sql(f"SELECT  L.loanID, B.bookID, B.title, L.dueDate FROM Members M INNER JOIN Loans L ON m.memberID = L.memberID INNER JOIN Books B ON B.bookID = L.bookID WHERE M.memberID = {member_id} AND L.returnedDate IS NULL;").execute()
    member_result = session.sql(f"SELECT M.memberID, M.firstName, M.lastName, COUNT(L.loanID), M.debt FROM Members M LEFT JOIN Loans L ON M.memberID = L.memberID WHERE M.memberID = {member_id} AND L.returnedDate IS NULL GROUP BY M.memberID, M.firstName, M.lastName, M.debt;").execute()
    member_fetch = member_result.fetch_all()
    loan_fetch = loans_result.fetch_all()
    
    members_list = []
    for member in member_fetch:
        members_list.append(list(member))
    print(members_list)
    loan_list = []
    for loan in loan_fetch:
        loan_list.append(list(loan))
    for loan in loan_list:
        loan[3] = loan[3].strftime("%d/%m/%y")
    print(loan_list)

    sort_by = request.args.get('search')

    if sort_by != None:
        try:
            sort_by = int(sort_by)
            sorting_version = 'bookID'
        except:
            sorting_version = 'title'

        if sorting_version == 'title':
            loan_list.sort(key=lambda x: Levenshtein.distance(x[2], sort_by))  
        elif sorting_version == 'bookID':
            loan_list.sort(key=lambda x: abs(x[0] - sort_by))  

    return render_template('memberinfo.html', members_list=members_list, loan_list=loan_list)

@app.route("/debt/<int:member_id>", methods=["POST", "GET"])
def set_debt(member_id):
    # Retrieve form data
    debt = request.form.get('debt')

    # Update member's debt in the database
    session.sql(f"UPDATE Members SET debt = {debt} WHERE memberID = {member_id}").execute()
    print(f"Debt for {member_id} set to {debt}")
    # Redirect to the member info page
    return redirect(url_for('member_info', member_id=member_id))


@app.route("/addmember", methods=["POST", "GET"])
def add_member():
    return render_template("addmember.html")
@app.route("/add-mem", methods=["POST", "GET"])
def submit_member():
    fname = request.args.get('fname')
    lname = request.args.get('lname')
    print(fname, lname)
    session.sql(f'INSERT INTO Members (firstName, lastName) VALUES ("{fname}", "{lname}");').execute()
    
    return redirect(f"/members?search={fname}")

@app.route("/logout", methods=['POST', 'GET'])
def logout():
    import os
    print("! Quitting !")
    os._exit(os.EX_OK)
