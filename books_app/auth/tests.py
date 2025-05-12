import os
from unittest import TestCase

from datetime import date
 
from books_app.extensions import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################

def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        # test for the signup route. 
        # - Make a POST request to /signup, sending a username & password
        # Make a POST request to /signup, sending a username & password
        post_data = {
            'username': 'new_user',
            'password': 'new_password'
        }
        response = self.app.post('/signup', data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # - Check that the user now exists in the database
        user = User.query.filter_by(username='new_user').one()
        self.assertIsNotNone(user) 

    def test_signup_existing_user(self):
        # test for the signup route
        # creates a user with username 'me1'
        create_user()
        # - Make a POST request to /signup, sending the same username & password
        post_data = {
        'username': 'me1',
            'password': 'passwor d'
        }
        response = self.app.post('/signup', data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # - Check that the form is displayed again with an error message
        response_text = response.get_data(as_text=True)
        self.assertIn('That username is taken', response_text)

    def test_login_correct_password(self):
        # test for the login route
        # Creates user with username 'me1' and password 'password'
        create_user()
        # - Make a POST request to /login, sending the created username & password
        post_data = {
            'username': 'me1',
            'password': 'password'
        }
        response = self.app.post('/login', data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # - Check that the "login" button is not displayed on the homepage
        response_text = response.get_data(as_text=True)
        self.assertNotIn('Log In', response_text)
        # Should see logout instead
        self.assertIn('Log Out', response_text)  

    def test_login_nonexistent_user(self):
        # Test login with a nonexistent user
        # Make a POST request to /login, sending a non existent username & password
        post_data = {
            'username': 'nonexistent_user',
            'password': 'password'
        }
        response = self.app.post('/login', data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        response_text = response.get_data(as_text=True)
        self.assertIn('No user with that username', response_text)
        # Login form should still be visible
        self.assertIn('Log In', response_text)  

    def test_login_incorrect_password(self):        
        # Test login with incorrect password
         # Create user with username 'me1' and password 'password'
        create_user() 
        
        # Make a POST request to /login, sending the created username & an incorrect password
        post_data = {
            'username': 'me1',
            'password': 'wrong_password'
        }
        response = self.app.post('/login', data=post_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the login form is displayed again, with an appropriate error message
        response_text = response.get_data(as_text=True)
        self.assertIn('Password doesn\'t match', response_text)
        self.assertIn('Log In', response_text)  # Login form should still be visible
        

    def test_logout(self):
        # test for the logout route
        # - Create a user
        create_user()
        # - Log the user in (make a POST request to /login)
        post_data = {
            'username': 'me1',
            'password': 'password'
        }
        response = self.app.post('/login', data=post_data, follow_redirects=True)

        # - Make a GET request to /logout
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # - Check that the "login" button appears on the homepage
        response_text = response.get_data(as_text=True)
        self.assertIn('Log In', response_text)
        self.assertNotIn('Log Out', response_text)
