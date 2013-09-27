"""Views to handle logging in and out of hactar"""
from flask import current_app, request, redirect, session, flash, url_for

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle logins."""
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            flash('Invalid username')
        elif request.form['password'] != current_app.config['PASSWORD']:
            flash('Invalid password')
        else:
            session['logged_in'] = True
            flash('You were logged in')
    return redirect(url_for('home'))


@current_app.route('/logout')
def logout():
    """Handle logging out."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))
