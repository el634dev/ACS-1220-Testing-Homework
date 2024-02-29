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
    """Create a user and password"""
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
        """Unit test for signup"""
        # Write a test for the signup route. It should:
        # - Make a POST request to /signup, sending a username & password
        result = app.test_client().post('/signup',
                    data={'username': 'username', 'password': 'password'})
        # - Check that the user now exists in the database
        self.assertEqual(result.status_code, 200)

    # -----------------------------------
    def test_signup_existing_user(self):
        """Unit test for existing user trying to signup"""
        # Write a test for the signup route. It should:
        # - Create a user
        user = {
            'username': 'username',
            'password': 'password'
        }
        # - Make a POST request to /signup, sending the same username & password
        result = app.test_client().post('/signup', user=user)
        # - Check that the form is displayed again with an error message
        self.assertIn(b'That user already exists.', result.data)

    # -----------------------------------
    def test_login_correct_password(self):
        """Unit testing for logging in with the correct password"""
        # Write a test for the login route. It should:
        # - Create a user
        user = {
            'username': 'username',
            'password': 'password'
        }
        # - Make a POST request to /login, sending the created username & password
        result = app.test_client().post('/login', user=user)
        # - Check that the "login" button is not displayed on the homepage
        assert b'login' not in result.data

    # ------------------------------------
    def test_login_nonexistent_user(self):
        """Test for noexistent user loggging in"""
        # Write a test for the login route. It should:
        # - Make a POST request to /login, sending a username & password
        result = app.test_client().post('/login', 
                    data={'username': 'some_user', 'password': 'password'})
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        self.assertIn(b'User does not exist. Please try again.', result.data)

    def test_login_incorrect_password(self):
        """Test for incorrect password"""
        # Write a test for the login route. It should:
        # - Create a user
        user = {
            'username': 'username',
            'password': 'no_valid'
        }
        # - Make a POST request to /login, sending the created username &
        #   an incorrect password
        result = app.test_client().post('login', user=user)
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        self.assertIn(b'That password is incorrect. Please try again.', result.data)

    def test_logout(self):
        """Test Logout function"""
        # Write a test for the logout route. It should:
        # - Create a user
        user = {
            'username': 'username',
            'password': 'password'
        }
        # - Log the user in (make a POST request to /login)
        response = app.test_client().post('/logout', data=user)
        self.assertEqual(response.status_code, 200)
        # - Make a GET request to /logout
        request = app.test_client().get('/logout', follow_redirects=True)
        # - Check that the "login" button appears on the homepage
        self.assertIn(b'Logout', request.data)
