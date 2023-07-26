"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


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





class MessageModelTestCase(TestCase):
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
        invalid_message = Message(user_id=1)
        message1 = Message(text="Hello World")

        

        self.client = app.test_client()
        self.user1 = user1
        self.user2 = user2
        self.invalid_message = invalid_message
        
        self.message1 = message1
    

        

    def tearDown(self):
        db.session.rollback()
        
    def test_user_model(self):
        """Does basic model work?"""

        
        db.session.add(self.message1)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.user1.messages), 0)
        self.assertEqual(self.message1.text, "Hello World")

    def test_message_model_user_relationship_successful(self):
        """Does Message.user return the user who created the message?"""
        self.user1.messages.append(self.message1)
        db.session.add(self.user1)
        db.session.commit()
        self.assertEqual(self.message1.user, self.user1)

    def test_message_model_user_relationship_unsuccessful(self):
        """Does Message.user return the user who created the message?"""
        self.user1.messages.append(self.message1)
        db.session.add(self.user1)
        db.session.commit()
        self.assertNotEqual(self.message1.user, self.user2)

    def test_message_model_user_id_set_none(self):
        """Is Message.user_id set to None when the user is deleted?"""
        self.user1.messages.append(self.message1)
        db.session.add(self.user1)
        db.session.commit()
        db.session.delete(self.user1)
        db.session.commit()
        
        self.assertEqual(self.message1.user_id, None)

    def test_successful_create_new_message(self):
        """Does Message.create successfully create a new message given valid credentials?"""
        new_message = Message(text="Goodbye Everyone")
        db.session.add(new_message)
        db.session.commit()
        self.assertEqual(Message.query.get(new_message.id), new_message)

    def test_unsuccessful_create_new_user(self):
        """Does Message.create throw IntegrityError when given invalid credentials?"""
        db.session.add(self.invalid_message)
        self.assertRaises(IntegrityError, db.session.commit)

    