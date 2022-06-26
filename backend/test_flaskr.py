import os
import unittest
import json
from urllib import response
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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'question': 'What is the capital city of Ethiopia',
            'answer': 'Addis Ababa',
            'difficulty': 2,
            'category': 2
            }

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
    # test questions pagination success
    def test_get_questions(self):
        response =self.client().get('/questions')
        data = json.loads(response.data)
        
        #status code and message returned
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
        # test questions returned
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    def test_delete_question(self):
        #question to be deleted
        question = Question(question=self.new_question['question'], 
                            answer=self.new_question['answer'],
                            category=self.new_question['category'],
                            difficulty=self.new_question['category'])
        question.insert()
        q_id= question.id
        question_before_delete = Question.query.all()
        
        #delete question and store response
        response = self.client().delete(f'/questions/{q_id}')
        data =json.loads(response.data)
        
        #get questions after delete
        question_after_delete = Question.query.all()
        
        question = question.query.filter(Question.id ==question.id).one_or_none()
        
        # check status code if delete succeded
        self.assertEqual(response.status_code,200) # if true, deleted
        self.assertEqual(data['success'],True)
        
        #deleted.check if id matches
        self.assertEqual(data['deleted'], str(q_id))
        
        # check if number of questions reduced by one after delete
        self.assertTrue(len(question_before_delete) - len(question_after_delete) == 1)
        
        # check if question is None after delete
        self.assertEqual(question, None)
        
    def test_create_new_question(self):
        # no questions before post
        questions_before_post = Question.query.all()
        
        # create new question and laod response data
        response = self.client().post('/questions', json = self.new_question)
        data =json.laods(response.data)
        
        #questions after post
        questions_after_post = Question.query.all()
        
        # check if created
        question = Question.query.filter(id = data['created']).one_or_none()
        
        #check statud code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success', True])
        
        #check if one question is added
        self.assertTrue(len(questions_after_post)- len(questions_before_post)==1)
        
        # check the question is not None
        self.assertIsNone(question)
    
    def test_422_question_creation_fail(self):
        questions_before_post = Question.query.all()
        response = self.client().post('/questions',json = {})
        data = json.loads(response.data)
        
        questions_after_post = Question.query.all()
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success', False])
        self.assertTrue(len(questions_after_post) == len(questions_before_post))
        
    
    def test_search_questions_searchTerm(self):
        #send post request with searchTerm
        search_term = {'searchTerm':'b'}
        response = self.client().post('/questions/search', 
                                    json = {'searchTerm': search_term})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success', True])
        
        # check the response result is one
        self.assertEqual(len(data['questions'], 1))
        
        # check question id in the respons is correct
        self.assertEqual(data['questions'][0]['id'], 10)
    
    def test_404_search_questions_fail(self):
        #send post request with search term that fails
        response = self.client().post('/questions', 
                                    json = {'searchTerm': '1258962'})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'resource not found')
        
    def test_get_questions_by_category(self):
        # send request with category id 1, science
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')
        
    def test_404_questions_by_category_fails(self):
        # send request with category id 3000
        response = self.client().get('/categories/3000/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
        
    def test_play_quiz_game(self):
        # send request with category and previous question
        response = self.client().post('/quizzes', 
                                    json = {'previous_questions':[20,21],
                                            'quiz_category':{'type': 'Science', 'id':1}})
        data  = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'], True)
        
        self.assertTrue(data['questions'])
        self.assertNotEqual(data['questions']['id'], 20)
        self.assertNotEqual(data['questions']['id'], 21)
        
    
    def test_play_quiz_fails(self):
        response=self.client().post('/quizzes',json={})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


    def test_404_request_beyond_valid_page(self):
        response = self.client().get('/questions?page=100')
        data =json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()