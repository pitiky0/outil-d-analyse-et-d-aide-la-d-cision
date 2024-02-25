from database import Dictionnaire, db
from flask import request, render_template, url_for, flash, redirect


def dictionnaire():
    search_term = request.args.get("term")

    # Use SQLAlchemy for database interaction
    if search_term:
        # Perform safe, case-insensitive full-text search using SQLAlchemy filters
        search_words = search_term.lower().split()
        terms = Dictionnaire.query.filter(
            db.and_(  # Combine filter with "is_deleted" check
                db.or_(*[
                    Dictionnaire.term.ilike(f'%{word}%') for word in search_words
                ]),
                Dictionnaire.is_deleted == False  # Exclude deleted terms
            )
        ).all()

        definitions = Dictionnaire.query.filter(
            db.and_(  # Combine filter with "is_deleted" check
                Dictionnaire.definition.ilike(f'%{search_term}%'),
                Dictionnaire.is_deleted == False  # Exclude deleted terms
            )
        ).all()

        data = set(terms + definitions)  # Combine results and remove duplicates
    else:
        data = Dictionnaire.query.filter_by(is_deleted=False).all()  # Only fetch non-deleted terms
    return render_template("dictionnaire/dictionnaire_index.html", terms=data)

def show_term(id):
    term = Dictionnaire.query.filter_by(id=id).first()
    if term and not term.is_deleted:
        return render_template('dictionnaire/show_term.html', term=term)
    else:
        flash("Term not found!", "error")
        return redirect(url_for('dictionnaire'))

def add_term():
    if request.method == 'POST':
        term = request.form['term']
        definition = request.form['definition']

        errors = []  # Store validation errors

        if not term:
            errors.append("Please enter Term.")
        if not definition:
            errors.append("Please enter Definition.")

        if errors:
            return render_template('dictionnaire/add_term.html', errors=errors)

        # Use SQLAlchemy's query methods for efficient and secure database interactions
        existing_term = Dictionnaire.query.filter_by(term=term).first()

        if existing_term:
            if existing_term.is_deleted:
                existing_term.is_deleted = False
                existing_term.definition = definition
            else:
                flash('Term "' + term + '" already exists.', 'error')
                return redirect(url_for('dictionnaire'))
        else:
            # Create a new Dictionnaire object and add it to the database
            new_term = Dictionnaire(term=term, definition=definition)
            db.session.add(new_term)
        try:
            db.session.commit()
            flash('Term "' + term + '" added successfully.', 'success')
            return redirect(url_for('dictionnaire'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the term: ' + str(e), 'error')
            return redirect(url_for('add_term'))

    # Display the add term form on GET requests
    return render_template("dictionnaire/add_term.html")

def edit_term(id):
    term_to_edit = Dictionnaire.query.get(id)
    if request.method == 'POST':
        try:
            term = request.form['term']
            definition = request.form['definition']

            errors = []  # Store validation errors

            if not term:
                errors.append("Please enter Term.")
            if not definition:
                errors.append("Please enter Definition.")
            new_term = Dictionnaire(term=term, definition=definition)
            new_term.id = id
            if errors:
                return render_template('dictionnaire/edit_term.html', term=new_term, errors=errors)

            # Use SQLAlchemy's session for safe updates
            term_to_update = Dictionnaire.query.get(id)
            term_to_update.term = term
            term_to_update.definition = definition
            db.session.commit()

            flash('Term "' + term + '" Updated', 'success')
            return redirect(url_for("dictionnaire"))  # Use the correct route name
        except Exception as e:
            flash('An error occurred: ' + str(e), 'error')
            return redirect(url_for("edit_term", term=term_to_edit))  # Redirect to the same edit page

    if term_to_edit is None or term_to_edit.is_deleted:
        flash('Term not found', 'error')
        return redirect(url_for("dictionnaire"))  # Use the correct route name

    return render_template("dictionnaire/edit_term.html", term=term_to_edit)

def delete_term(id):
    term = Dictionnaire.query.get(id)  # Fetch the term using SQLAlchemy

    if term:
        term.is_deleted = True  # Set the 'is_deleted' flag to True
        db.session.commit()
        flash(f'Term "{term.term}" Deleted', 'warning')  # Use f-string for formatting
    else:
        flash('Unknown Term', 'error')

    return redirect(url_for("dictionnaire"))
