"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()





class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        invalid_user = User(username="testuser3", password="HASHED_PASSWORD3")
        self.client = app.test_client()
        self.user1 = user1
        self.user2 = user2
        self.invalid_user = invalid_user

    def tearDown(self):
        db.session.rollback()
        
    def test_user_model(self):
        """Does basic model work?"""

        
        db.session.add(self.user1)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.user1.messages), 0)
        self.assertEqual(len(self.user1.followers), 0)

    def test_user_model_repr_method(self):
        """Does the _repr_ method work on user model?"""

        self.assertEqual(self.user1.__repr__(), f"<User #{self.user1.id}: {self.user1.username}, {self.user1.email}>" )

    def test_user_model_is_following_method(self):
        """Does is_following successfully detect when user1 is following user2?"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(self.user1.is_following(self.user2), True)

    def test_user_model_is_following_method_2(self):
        """Does is_following successfully detect when user1 is not following user2?"""

        self.assertEqual(self.user1.is_following(self.user2), False)

    def test_user_model_is_followed_by_method(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        self.user1.followers.append(self.user2)
        self.assertEqual(self.user1.is_followed_by(self.user2), True)

    def test_user_model_is_followed_by_method_2(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.assertEqual(self.user1.is_followed_by(self.user2), False)

    def test_successful_create_new_user(self):
        """Does User.create successfully create a new user given valid credentials?"""
        new_user = User(email="test3@test.com", username="testuser3", password="HASHED_PASSWORD3")
        db.session.add(new_user)
        db.session.commit()
        self.assertEqual(User.query.get(new_user.id), new_user)

    def test_unsuccessful_create_new_user(self):
        """Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        db.session.add(self.invalid_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_user_authenticate_successful(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        user = User.signup('bob', 'bob123@aol.com', "bob123", "/static/images/default-pic.png")
        db.session.commit()
        self.assertEqual(user.authenticate("bob", "bob123"), user)

    def test_user_authenticate_invalid_username(self):
        """Does User.authenticate successfully return False when the given username is invalid?"""
        user = User.signup('bob', 'bob123@aol.com', "bob123", "/static/images/default-pic.png")
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.authenticate("bob1", "bob123"), False)

    def test_user_authenticate_invalid_password(self):
        """Does User.authenticate successfully return False when the given password is invalid?"""
        user = User.signup('bob', 'bob123@aol.com', "bob123", "/static/images/default-pic.png")
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.authenticate("bob", "bob234"), False)

