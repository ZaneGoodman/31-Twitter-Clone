"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 10
        self.testuser.id = self.testuser_id

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser2_id = 20
        self.testuser2.id = self.testuser2_id

        self.user3 = User.signup("zane", "zane@aol.com", "zane123", None)
        self.user3_id = 30
        self.user3.id = self.user3_id

        self.user4 = User.signup("nick", "nick@aol.com", "nick123", None)
        self.user4_id = 40
        self.user4.id = self.user4_id

        self.user5 = User.signup("andrew", "andrew@aol.com", "andrew123", None)
        self.user5_id = 50
        self.user5.id = self.user5_id

        self.test_msg = Message(id=11, text="Hello", user_id=self.user5_id)
        self.test_msg2 = Message(id=12, text="Goodbye", user_id=self.user5_id)
        self.like = Likes(user_id=self.user5_id, message_id=self.test_msg)
        self.like = Likes(user_id=self.user5_id, message_id=self.test_msg2)
       
        db.session.commit()
       

    def tearDown(self):
        db.session.rollback()

    def setup_followers(self):
        follow1 = Follows(user_being_followed_id=self.user3_id,user_following_id=self.testuser_id)
        follow2 = Follows(user_being_followed_id=self.user4_id,user_following_id=self.testuser_id)
        follow3 = Follows(user_being_followed_id=self.user5_id,user_following_id=self.testuser_id)
        follow4 = Follows(user_being_followed_id=self.testuser_id,user_following_id=self.user5_id)

        db.session.add_all([follow1, follow2, follow3, follow4])
        db.session.commit()


    def test_show_following(self):
        """When youre logged in, can you see the following pages for any user?"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        resp = c.get(f'/users/{self.testuser_id}/following')

        self.assertEqual(resp.status_code, 200)
        self.assertIn("zane", str(resp.data))
        self.assertIn("nick", str(resp.data))
        self.assertIn("andrew", str(resp.data))

    def test_show_followers(self):
        """When youre logged in, can you see the follower pages for any user?"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        resp = c.get(f'/users/{self.testuser_id}/followers')

        self.assertEqual(resp.status_code, 200)
        self.assertIn("andrew", str(resp.data))
        self.assertNotIn("nick", str(resp.data))


    def test_show_following_logged_out(self):
        """When youre logged in, can you see the following pages for any user?"""
        self.setup_followers()
        with self.client as c:
    
            resp = c.get(f'/users/{self.testuser_id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("nick", str(resp.data))
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)
           

    def test_show_followers_logged_out(self):
        """When youre logged in, can you see the follower pages for any user?"""
        self.setup_followers()
        with self.client as c:
        

            resp = c.get(f'/users/{self.testuser_id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("andrew", str(resp.data))
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)   

    def test_add_like(self):
        """Can a logged in user add a like?"""
       
        test_msg = Message(id=15, text="Hello", user_id=self.testuser_id)

        db.session.add(test_msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

        resp = c.post('/users/add_like/15', follow_redirects=True)
        likes = Likes.query.filter(Likes.message_id == 15).all()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_like(self):
        """Can a logged in user remove a like?"""
        test_msg = Message(id=11, text="Hello", user_id=self.user5_id)
        db.session.add(test_msg)
        db.session.commit()

        like = Likes(user_id=self.user5_id, message_id=test_msg)
        
        db.session.add(like)
        db.session.commit()

        check_like = Likes.query.filter(Likes.user_id==self.user5_id and Likes.message_id==test_msg).one()
        self.assertEqual(len(self.user5.likes), 1)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user5_id

        resp = c.post(f'/users/add_like/{self.test_msg.id}', follow_redirects=True)
   



