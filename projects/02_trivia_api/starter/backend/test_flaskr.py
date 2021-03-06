import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:dimulstR@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_405_for_POST_categories(self):
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_invalid_page(self):
        res = self.client().get('/questions?page=-200')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_new_question(self):
        res = self.client().post('/questions', json={'question': 'Neverwhere?',
                                                     'answer': 'Neil Gaiman',
                                                     'difficulty': 5,
                                                     'category': 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_new_question_no_answer_and_difficulty(self):
        res = self.client().post('/questions', json={'question': 'Neverwhere?',
                                                     'category': 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    '''def test_delete_question(self):
        res = self.client().delete('/questions/33')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 33).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)'''

    def test_404_deleting_invalid_question_id(self):
        res = self.client().delete('/questions/-33')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_search_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 2)

    def test_422_when_searching_empty_string(self):
        res = self.client().post('/questions', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)

    def test_list_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 4)

    def test_404_when_listing_questions_for_invalid_cat(self):
        res = self.client().get('/categories/2000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_get_questions_for_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [],
                                                   'quiz_category': {'type': "Sports", 'id': "6"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_null_wrong_category_for_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [],
                                                   'quiz_category': {'type': "Sports", 'id': "6000"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], None)

    def test_422_no_category_for_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions': []})

        self.assertEqual(res.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()