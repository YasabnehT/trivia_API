from crypt import methods
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# set questions number of questions per page

def questions_number_page(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1)* QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection]
    currunt_question = questions[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

   # set CORS to homepage and origins to everywhere
    CORS(app, resources= {'/':{'origins': '*'}})


    #set Access-Control-Allow-Headers and -Methods
    @app.after_request
    def after_request(response):
        response.haders.add('Access-Control-Allow-Headers',
                            'Content-Type, Autherization,true')
        response.headers.add('Access-Control-Allow-Methods',
                            'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    #Categories endpoint, GET
    
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_dictionary = {}
        for category in categories:
            categories_dictionary[category.id] = category.type
        
        # if no categories found: 404
        if(len(categories_dictionary) == 0):
            abort(404)
        
        # view data
        return jsonify({'success':True, 'categories' : categories_dictionary})
    
    # questions endpoint, GET
    @app.route('/questions')
    def get_questions():
        # get all questions and paginate them
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = questions_number_page(request, selection)
        
        # get all categories
        categories = Category.query.all()
        categories_dictionary = {}
        for category in categories:
            categories_dictionary[category.id] = category.type
        
        # if no questions found: 404
        if(len(current_questions)==0):
            abort(404)
        
        # view data
        return jsonify({'success':True, 'questions': current_questions, 
                    'total_questions': total_questions, 'categories': categories_dictionary})
    
    


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods = ['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.filter(id = id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({'success': True, 'deleted': id})
        except:
            abort(404)
        

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods = ['POST'])
    def post_question():
        body = request.get_json()
        
        # sesrch fro db using searchTerm
        if(body.get('searchTerm')):
            search_term = body.get('searchTerm')
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            
            # if no result matching the searchTerm
            if(len(selection)==0):
                abort(404)
            
            # paginate the results
            paginated = questions_number_page(request,selection)
            return jsonify({'succes': True, 'questions':paginated,
                            'total_questions':len(Question.query.all())})
            
        # if no searchTerm found, add new question
        else:
            #load data from body
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')
            
            # ensure not nullable
            if(new_question is None or new_answer is None or 
                new_difficulty is None or new_category is None):
                abort(404)
            try:
                question = Question(question = new_question,answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                question.insert()
                
                # get all questions added and pagenate them
                selection = Question.query.order_by(Question.id).all()
                current_questions = questions_number_page(request,selection)
                
                # veiw data
                return jsonify({'success': True, 'created':question.id,
                                'questions': current_questions, 
                                'total_question':len(Question.query.all())})
            except:
                abort(404)
            
            

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        category = Category.query.filter(id=id).one_or_none()
        if(category is None):
            abort(404)
        selection = Question.query.filter(category = category.id)
        paginated = questions_number_page(request, selection)
        return jsonify({'success':True, 'questions': paginated,
                        'total_questions':len(Question.query.all()), 
                        'current_category':category.type})
        

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods = ['POST'])
    def get_random_quiz_question():
        body = request.get_json()
        previous = body.get('previous_questions')
        category = body.get('quiz_category')
        
        if(category is None or previous is None):
            abort(404)
        
        # load all questions if selected
        if(category['id'] == 0):
            questions = Question.query.all()
        
        #load specific questions of given category
        else:
            questions = Question.query.filter(category = category.id)
        total = len(questions) # total questions in the category
        
        #random selection from results
        def get_random_question():
            return questions[random.randrange(0,len(questions),1)]
        
        # check if questions are used previously
        def check_if_used(question):
            used =False
            for q in previous:
                if(q == question.id):
                    used = True
            return used
        question = get_random_question()
        
        # iterate until unused is found
        while(check_if_used(question)):
            question = get_random_question
            if(len(previous)==total):
                return jsonify({'success':True})
        
        return jsonify({'success': True, 'question':question.format()})


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error':404, 
                        'message': 'resource not found'}),404
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'error':400,
                        'message':"bad request"}), 400
    @app.errorhandler(422)
    def unprocessable(erro):
        return jsonify({'success':False, 'error':422,
                        'message':"unprocessable"}), 422
    
        

    return app

