import subprocess

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'Why was the math book sad? Because it had too many problems.'
# Use environment variables for sensitive information
SAP_IP_ADDRESS = 'SAP_IP_ADDRESS'#'142.250.200.142'
SAP_URL = 'SAP_URL' #'https://142.250.200.142'


@app.route('/')
@app.route("/index")
def index():
    latest_reviews = [
        {'date': '2024-02-17', 'action': 'Reviewed PCR request #123'},
        {'date': '2024-02-16', 'action': 'Reviewed DFC request #456'},
        {'date': '2024-02-15', 'action': 'Reviewed PCR request #789'},
    ]
    return render_template('index.html', latest_reviews=latest_reviews)

@app.route('/dictionnaire')
def dictionnaire():
    search_term = request.args.get("term")
    con = sql.connect("db_web.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    if search_term:
        search_words = search_term.lower().split()
        search_words = [word for word in search_words if len(word) > 2]
        term_conditions = " OR ".join(["LOWER(term) LIKE ?" for _ in search_words])
        definition_condition = "LOWER(definition) LIKE ?"
        query = f"SELECT * FROM Dictionnaire WHERE {term_conditions} OR {definition_condition}"

        # Create query parameters
        query_params = ['%' + word + '%' for word in search_words] + ['%' + search_term + '%']
        cur.execute(query, query_params)
    else:
        cur.execute("SELECT * FROM Dictionnaire")

    data = cur.fetchall()
    return render_template("dictionnaire/dictionnaire_index.html", datas=data)

@app.route("/dictionnaire/<string:id>", methods=['GET'])
def show_term(id):
    con = sql.connect("db_web.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from Dictionnaire where id=?", (id,))
    data = cur.fetchone()
    return render_template("dictionnaire/show_term.html", datas=data)

@app.route('/add_term', methods=['GET', 'POST'])
def add_term():
    if request.method == 'POST':
        term = request.form['term']
        definition = request.form['definition']

        # Check if term already exists in the database
        con = sql.connect("db_web.db")
        cur = con.cursor()
        cur.execute("SELECT term FROM Dictionnaire WHERE term=?", (term,))
        existing_term = cur.fetchone()

        if existing_term:
            # If term already exists, display a flash message and redirect back to the form
            flash('Term "' + term + '" already exists.', 'error')
            return redirect(url_for("dictionnaire"))
        else:
            # If term does not exist, insert it into the database
            cur.execute("INSERT INTO Dictionnaire(term, definition) VALUES (?, ?)", (term, definition))
            con.commit()
            flash('Term "' + term + '" added successfully.', 'success')
            return redirect(url_for("dictionnaire"))
    else:
        return render_template("dictionnaire/add_term.html")

@app.route("/edit_term/<string:id>", methods=['POST', 'GET'])
def edit_term(id):
    if request.method == 'POST':
        term = request.form['term']
        definition = request.form['definition']
        con = sql.connect("db_web.db")
        cur = con.cursor()
        cur.execute("update Dictionnaire set term=?,definition=? where id=?", (term, definition, id))
        con.commit()
        flash('Term '+term+' Updated', 'success')
        return redirect(url_for("dictionnaire"))
    con = sql.connect("db_web.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from Dictionnaire where id=?", (id,))
    data = cur.fetchone()
    return render_template("dictionnaire/edit_term.html", datas=data)

@app.route("/delete_term/<string:id>", methods=['POST'])
def delete_term(id):
    con = sql.connect("db_web.db")
    cur = con.cursor()

    # Fetch the term associated with the given ID
    cur.execute("SELECT term FROM Dictionnaire WHERE id=?", (id,))
    term_row = cur.fetchone()
    if term_row:
        term = term_row[0]
        # Delete the term
        cur.execute("DELETE FROM Dictionnaire WHERE id=?", (id,))
        con.commit()
        flash('Term "' + term + '" Deleted', 'warning')
    else:
        flash('Unknown Term', 'error')
    return redirect(url_for("dictionnaire"))

@app.route('/review_history')
def review_history():
    # Add logic here to fetch review history data from your database or any other source
    # For demonstration purposes, let's assume we have a list of review history items
    review_history_items = [
        {'date': '2024-02-17', 'action': 'Reviewed PCR request #123'},
        {'date': '2024-02-16', 'action': 'Reviewed DFC request #456'},
        {'date': '2024-02-15', 'action': 'Reviewed PCR request #789'},
    ]
    return render_template('review_history.html', review_history_items=review_history_items)

@app.route('/submit_pcr_request')
def submit_pcr_request():
    # Logic for submitting PCR request goes here
    return render_template('submit_pcr_request.html')

@app.route('/submit_dfc_request')
def submit_dfc_request():
    # Logic for submitting DFC request goes here
    return render_template('submit_dfc_request.html')

@app.route("/check_sap_availability", methods=['GET', 'POST'])
def check_sap_availability():
    if request.method == "GET":
        return render_template('sap_page.html')
    if request.method == "POST":
        try:
            # Check if SAP IP address is reachable
            result = subprocess.run(['ping', SAP_IP_ADDRESS], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:  # IP address reachable
                return jsonify({"status": "ok"})
            else:
                return jsonify({"status": "error", "message": "System unavailable"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": "Internal error"}), 500

@app.route("/sap_url")
def sap_url():
    return redirect(SAP_URL)

@app.route('/change_engineer_formation')
def change_engineer_formation():
    return render_template('formation.html')

if __name__ == '__main__':
    app.run(debug=True)

