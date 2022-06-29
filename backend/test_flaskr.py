import os
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
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

    def create_sample_question(self):
        question = Question(question="What is the capital city of Ethiopia?",
                            answer="Addis Ababa", difficulty=2, category=2)

    # test questions pagination success
    def test_get_questions(self):
        response = self.client().get('/questions')
        json_data = json.loads(response.data)

        # status code and data content returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data['success'], True)
        self.assertTrue(json_data['categories'])
        self.assertTrue(json_data['questions'])
        self.assertEqual(len(json_data['questions']))
        self.assertTrue(json_data['total_questions'])

    def test_no_category(self):
        # test with non existing id, 5000
        response = self.client().get('categories/5000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_create_questions(self):

        questions_before_post = Question.query.all()
        response = self.client().post('/questions', json=self.create_sample_question())
        data = json.laods(response.data)
        questions_after_post = Question.query.all()
        question = Question.query.filter(id=data['created']).one_or_none()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success', True])
        self.assertNotEqual(question, None)

    def test_create_question_fail(self):
        questions_before_post = Question.query.all()
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        questions_after_post = Question.query.all()
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success', False])
        self.assertTrue(len(questions_after_post) ==
                        len(questions_before_post))

    def test_search_questions_searchTerm(self):
        # send post request with searchTerm
        search_term = {'searchTerm': 'b'}
        response = self.client().post('/questions/search',
                                      json={'searchTerm': search_term})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success', True])

    def test_empty_searchTerm(self):
        requested_term = {'searchTerm': ''}
        response = self.client().post('/questions/search', json=requested_term)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_search_questions_fail(self):
        # send post request with inexisting searchTerm
        response = self.client().post(
            '/questions', json={'searchTerm': '1258962'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category(self):
        # send request with category id 1, science
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_questions_by_category_fails(self):
        # send request with category id 3000
        response = self.client().get('/categories/3000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_delete_question(self):
        # question to be deleted
        new_question_id = self.create_sample_question()

        question_before_delete = Question.query.all()

        # delete question and store response
        response = self.client().delete(f'/questions/{new_question_id}')
        data = json.loads(response.data)

        # get questions after delete
        question_after_delete = Question.query.all()

        question = question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(response.status_code, 200)  # if true, deleted
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(new_question_id))
        self.assertEqual(question, None)

    def test_play_quiz(self):
        # send request with category(id =1) and previous questions(3,6)
        requested = {'previous_questions': [
            3, 6], 'quiz_category': {'type': 'Science', 'id': 1}}
        response = self.client().post('/quizzes', json=requested)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertNotEqual(data['questions']['id'], 3)
        self.assertNotEqual(data['questions']['id'], 6)
        self.assertEqual(data['questions']['category'], 1)

    def test_if_no_data_to_play_quiz(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_request_None_page(self):
        response = self.client().get('/questions?page=30000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
