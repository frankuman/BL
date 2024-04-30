"""
Oliver Bölin
BTH, 2024
Flask frontend
"""
from flask import Flask, render_template, request, jsonify, redirect,url_for
import json
import library_db_func
import library_db
app = Flask(__name__)
session = library_db.db()

@app.route("/", methods=["POST", "GET"])
def start():
    result = session.sql("SELECT bookID, title, author FROM Books;").execute()
    all_result = result.fetch_all()
    amount_of_books = len(all_result)
    copies_list = []

    for i in range(1, amount_of_books+1):
        sum_result = session.sql(f"SELECT SUM(nrOfCopies) AS total_copies FROM LibBooks WHERE bookID = {i};").execute()
        row = sum_result.fetch_one()
        total_copies_decimal = row["total_copies"]
        total_copies_int = int(total_copies_decimal)
        copies_list.append(total_copies_int)
    
    list_with_copies = []
    for index, book in enumerate(all_result):
        book = list(book)  # Convert Row object to list
        book.append(copies_list[index])
        list_with_copies.append(book)

    return render_template('index.html', all_result=list_with_copies)

@app.route("/lend", methods=["POST", "GET"])
def lend_book():
    return render_template('lend.html')

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
    #print(str(result[0]))
    
    #print(res_lst)
    
    #last_str = str_lst[1]
    return render_template('lend-result.html', lend_result=lend_result,return_result=return_result)

@app.route("/return", methods=["POST", "GET"])
def return_book():
    return

@app.route("/evaluation", methods=['POST', 'GET'])
def evaluate():
    """
    Request site for dashboard
    Returns:
        template: 
    """
    # this is mostly just for show
    high_p = request.args.get('high_p', '')
    med_p = request.args.get('med_p', '')
    low_p = request.args.get('low_p', '')
    user_input = request.args.get('user_input', '')
    adress = request.args.get('adress', '')
    property_type = request.args.get('property_type', '')
    build_year = request.args.get('build_year', '')
    living_area = request.args.get('living_area', '')
    land_area = request.args.get('land_area', '')
    county = request.args.get('county', '')
    area = request.args.get('area', '')
    fee = request.args.get('fee', '')
    rooms = request.args.get('rooms', '')
    balcony = request.args.get('balcony', '')
    population_density = request.args.get('population_density', '')
    amount1 = int(low_p)
    amount2 = int(med_p)
    amount3 = int(high_p)
    low_p = "{:,.0f}".format(amount1).replace(",", " ")
    med_p = "{:,.0f}".format(amount2).replace(",", " ")
    high_p = "{:,.0f}".format(amount3).replace(",", " ")


    return render_template('results.html', high_p=high_p, med_p=med_p, low_p=low_p, user_input=user_input,adress=adress, property_type=property_type, build_year=build_year,
                           living_area=living_area, county=county, land_area=land_area, area=area, fee=fee, rooms=rooms,
                           balcony=balcony, population_density=population_density)