## ITCS 3160-0002, Spring 2024
## Marco Vieira, marco.vieira@charlotte.edu
## University of North Carolina at Charlotte
 
## IMPORTANT: this file includes the Python implementation of the REST API
## It is in this file that yiu should implement the functionalities/transactions   

import flask
import logging, psycopg2, time
import random
import datetime
from functools import wraps
from flask import request

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'unauthorized': 401, 
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user = "scott",
        password = "tiger",
        host = "db",
        port = "5432",
        database = "dbproj"
    )
    
    return db



##########################################################
## TOKEN VERIFICATION
##########################################################

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'access-token' in flask.request.headers:
            token = flask.request.headers['access-token']

        if not token:
            return flask.jsonify({'message': 'invalid token'})

        try:
            conn = db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM tokens WHERE exp_date < current_timestamp")
            conn.commit()

            cur.execute("SELECT users_user_id FROM tokens WHERE token= %s", (token,))

            if cur.rowcount==0:
                return flask.jsonify({'message': 
                   'invalid token'})
            else:
                current_user = cur.fetchone()[0]
        except (Exception) as error:
            logger.error(f'POST /users - error: {str(error)}')
            conn.rollback()

            return flask.jsonify({'message': 'invalid token'})

        return f(current_user, *args, **kwargs)

    return decorator

##########################################################
## ENDPOINTS
##########################################################


@app.route('/')
def landing_page():
    return """

    Hello World (Python)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    ITCS 3160-002, Spring 2024<br/>
    <br/>
    """

##
## List All Users
##
## Obtain all users in JSON format
##
## To use it, access:
##
## http://localhost:8080/users/
##
## Status: Complete

@app.route('/users/', methods=['GET'])
def get_all_users():
    logger.info('GET /users')

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute('SELECT username, email FROM users')
        rows = cur.fetchall()

        logger.debug('GET /users - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'username': row[0], 'email': row[1]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Get User
##
## Obtain user with username <username>
##
## To use it, access:
##
## http://localhost:8080/users/ssmith
##
## Status: Complete

@app.route('/users/<username>/', methods=['GET'])
def get_user(username):
    logger.info('GET /users/<username>')

    logger.debug('username: {username}')

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute('SELECT username, email FROM users where username = %s', (username,))
        row = cur.fetchone()

        logger.debug('GET /users/<username> - parse')
        logger.debug(row)
        content = {'username': row[0], 'email': row[1]}

        response = {'status': StatusCodes['success'], 'results': content}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users/<username> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##
## Demo PUT
##
## Update a user based on a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X PUT http://localhost:8080/users/ssmith -H 'Content-Type: application/json' -d '{"city": "Raleigh"}'
##
## Status: Complete

@app.route('/users/<username>', methods=['PUT'])
def update_users(username):
    logger.info('PUT /users/<username>')
    payload = flask.request.get_json()

    logger.debug(f'PUT /users/<username> - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'city' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'city is required to update'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'UPDATE users SET city = %s WHERE username = %s'
    values = (payload['city'], username)

    try:
        conn = db_connection()
        cur = conn.cursor()

        res = cur.execute(statement, values)
        response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

        # commit the transaction
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)



# ________________________________________________________________________________________________________________________________________________
# ________________________________________________________________________________________________________________________________________________
# ________________________________________________________________________________________________________________________________________________



##
## Add User
##
## Add a new user in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/users/ -H 'Content-Type: application/json' -d '{"username": "abc", "email": "abc@gmail.com", "password": "abc"}'
##
## Status: Complete

@app.route('/users/', methods=['POST'])
def add_users():
    logger.info('POST /users')
    payload = flask.request.get_json()

    

    logger.debug(f'POST /users - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if not payload or 'username' not in payload or 'email' not in payload or 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'values missing from payload'}
        return flask.jsonify(response)
    
    # parameterized queries, good for security and performance
    statement = 'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)'
    values = (payload['username'], payload['email'], payload['password'])

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted users {payload["username"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##
## User login
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/login/ -H 'Content-Type: application/json' -d '{"username": "abc", "password": "abc"}'
##
## Status: Complete

@app.route('/login/', methods=['POST'])
def user_login():
    logger.info('POST /login')
    payload = flask.request.get_json()

    logger.debug(f'POST /login - payload: {payload}')

    # Validate every argument
    if not payload \
        or 'username' not in payload \
        or 'password' not in payload :
        response = {'status': StatusCodes['unauthorized'], 'results': 'missing credentials from payload'}
        return flask.jsonify(response)
    
    # parameterized queries
    query = 'SELECT user_id FROM users WHERE username = %s AND password = %s'
    values = (payload['username'], payload['password'])
    

    try:
        # connecting to the database
        conn = db_connection()
        cur = conn.cursor()

        # excuting the query
        cur.execute(query, values)
        
        user_id = cur.fetchone()[0]

        if cur.rowcount == 0:
            response = ('could not verify', 401)
        else: 
            response = payload['username'] + \
                str(random.randrange(111111111, 999999999))
            
            query  = "INSERT INTO tokens (users_user_id, token, exp_date) \
                VALUES( %s, %s, current_timestamp + (24 * interval '1 hour'))"
            values = (user_id, response)

            cur.execute(query, values)

        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /login - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()
    
    return response




##
## Create Auction
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/auctions/ -H 'Content-Type: application/json' -H "access-token: corban543983361" -d '{"item_id": "1", "min_price" : "10.99", "end_date_time" : "2024-05-10 18:00:00","title" : "auction title", "item_desc" : "Blah blah"}'
##
## Status: Complete

@app.route('/auctions/', methods=['POST'])
@token_required
def create_auction(current_user):
    logger.info('POST /auctions')
    payload = flask.request.get_json()

    logger.debug(f'POST /auctions - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if not payload or 'end_date_time' not in payload \
        or 'item_id' not in payload or 'min_price' not in payload \
        or 'title' not in payload or 'item_desc' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'values missing from payload'}
        return flask.jsonify(response)
    
    # parameterized queries, good for security and performance
    statement = 'INSERT INTO auctions (item_id, min_price, title, item_desc, end_date_time, users_user_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING auction_id'
    values = (payload['item_id'], payload['min_price'], payload['title'], payload['item_desc'], payload['end_date_time'], current_user)

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute(statement, values)

        auction_id = cur.fetchone()[0]

        # commit the transaction
        conn.commit()
        response = {'auction_id': auction_id}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /auctions - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##
## Get All Auctions
##
## Obtain all active auctions in JSON format
##
## To use it, access:
##
## curl -X GET http://localhost:8080/auctions/  -H "Content-Type: application/json" -H "access-token: corban543983361"
##
## Status: Complete

@app.route('/auctions/', methods=['GET'])
@token_required
def get_all_auctions(current_user):
    logger.info('GET /auctions')    

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute('SELECT auction_id, item_des, end_date_time FROM auctions')
        rows = cur.fetchall()

        logger.debug('GET /users - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auction id': row[0], 'item_desc': row[1], 'End_Date_and_time': row[2]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auctions - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##
## Search Existing
##
## Search for auctions that have a matching Item_id or description 
##
## To use it, access:
##
## curl -X GET http://localhost:8080/items/<keyword>/  -H "Content-Type: application/json" -H "access-token: corban543983361"
##
## Status: Complete

@app.route('/items/<keyword>/', methods=['GET'])
@token_required
def search_existing(current_user, keyword):
    logger.info('GET /items')    

    logger.debug('keyword: {keyword}')

    try:
        conn = db_connection()
        cur = conn.cursor()

        if keyword.isdigit():
            query = 'SELECT auction_id, item_desc FROM auctions WHERE item_id = %s'
            values = (int(keyword),)
        else:
            query = 'SELECT auction_id, item_desc FROM auctions WHERE item_desc ILIKE %s'
            values = (f'%{keyword}%',)

        cur.execute(query, values)
        rows = cur.fetchall()

        logger.debug('GET /items - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auction id': row[0], 'item_desc': row[1]}
            Results.append(content)  # appending to the payload to be returned

        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /items/<keyword> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##
## Retrieve Auction
##
## Obtain all auction details in JSON format
##
## To use it, access:
##
## curl -X GET http://localhost:8080/auctions/<auction_id>/  -H "Content-Type: application/json" -H "access-token: corban543983361"
##
## Status: Complete

@app.route('/auctions/<auction_id>/', methods=['GET'])
@token_required
def retrieve_auction(current_user, auction_id):
    logger.info('GET auctions/<auction_id>')

    logger.debug('auction_id: {auction_id}')

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute('SELECT auction_id, item_id, title, min_price, end_date_time, item_desc FROM auctions WHERE auction_id = %s', (auction_id,))
        auction_info = cur.fetchone()

        cur.execute('SELECT amount FROM bids WHERE auctions_auction_id = %s', (auction_id,))
        all_bids = cur.fetchall()

        cur.execute('SELECT comm_content FROM comments WHERE auctions_auction_id = %s', (auction_id,))
        all_comments = cur.fetchall()

        logger.debug('GET auctions/<auction_id> - parse')
        logger.debug(auction_info)

        content = {
            'auction_id': auction_info[0], 
            'item_id': auction_info[1], 
            'title': auction_info[2], 
            'min_price': auction_info[3], 
            'end_date_time': auction_info[4], 
            'item_desc': auction_info[5],
            'bids': all_bids,
            'comments': all_comments
        }

        response = {'status': StatusCodes['success'], 'results': content}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /auctions/<auction_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




###########################################
## Edit properties of an auction
##
## curl -X PUT http://localhost:8080/auctions/<auction_id>/  -H "Content-Type: application/json" -H "access-token: corban543983361" -d '{"item_desc" : "words words words and some more words"}'
##
## Status: Complete
###########################################

@app.route('/auctions/<auction_id>/', methods=['PUT'])
@token_required
def edit_properties(current_user, auction_id):
    logger.info('PUT /auctions/<auction_id>/')
    payload = flask.request.get_json()

    logger.debug(f'PUT /auctions/<auction_id>/ - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if not payload or 'item_desc' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'item_description is required to update'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'UPDATE auctions SET item_desc = %s WHERE auction_id = %s'
    values = (payload['item_desc'], auction_id)

    try:
        conn = db_connection()
        cur = conn.cursor()

        res = cur.execute(statement, values)
        response = {'status': StatusCodes['success'], 'results': f'Updated: {cur.rowcount}'}

        # commit the transaction
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /auctions/<auction_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


############################################
## List All Auctions Where User Has Activity
##
## curl -X GET http://localhost:8080/user/activity/  -H "Content-Type: application/json" -H "access-token: corban543983361"
##
## Status: Complete
############################################

@app.route('/user/activity/', methods=['GET'])
@token_required
def list_user_auctions(current_user):
    logger.info(f'GET /user/activity/')

    try:
        conn = db_connection()
        cur = conn.cursor()

        # Fetch auctions the user created
        cur.execute("SELECT auction_id, item_id, end_date_time, title FROM auctions WHERE users_user_id = %s", (current_user,))
        auctions_started = cur.fetchall()

        # Prepare response
        auctions_summary = []
        for auction in auctions_started:
            content = {
                'auction_id': auction[0],
                'item_id': auction[1],
                'end_date_time': auction[2],
                'title': auction[3]
            }
            auctions_summary.append(content)

        
        # Fetch auctions the user is involved in
        cur.execute("SELECT auction_id, item_id, end_date_time, title FROM bids, auctions WHERE auctions_auction_id = auction_id AND bids.users_user_id = %s", (current_user,))
        bids_made = cur.fetchall()

        # Prepare response
        bids_summary = []
        for auction in bids_made:
            content = {
                'auction_id': auction[0],
                'item_id': auction[1],
                'end_date_time': auction[2],
                'title': auction[3]
            }
            bids_summary.append(content)

        
        
        response = {'status': StatusCodes['success'], 'auctions_summary': auctions_summary, 'bids_summary' : bids_summary}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET user/<username>/auctions - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)



###########################################
## Place a bid in an auction
##
## curl -X GET http://localhost:8080/user/activity/  -H "Content-Type: application/json" -H "access-token: corban543983361"
##
## Status: Incomplete
###########################################

@app.route('/dbproj/bid/<int:auction_id>/<float:bid_amount>', methods=['GET'])
@token_required
def place_bid(current_user, auction_id, bid_amount):
    logger.info(f'GET /dbproj/bid/{auction_id}/{bid_amount}')

    try:
        conn = db_connection()
        cur = conn.cursor()
        # Check if the auction exists
        cur.execute("SELECT * FROM auctions WHERE auction_id = %s", (auction_id,))
        auction = cur.fetchone()
        if auction is None:
            response = {'status': StatusCodes['not_found'], 'results': 'Auction not found'}
            return flask.jsonify(response)

        # Check if the auction has ended
        if auction[2]:  
            response = {'status': StatusCodes['bad_request'], 'results': 'Auction has already ended'}
            return flask.jsonify(response)

        # Check if the bid is higher than the current highest bid (if any)
        cur.execute("SELECT MAX(amount) FROM bids WHERE auction_id = %s", (auction_id))
        max_bid = cur.fetchone()[0]
        if max_bid is not None and bid_amount <= max_bid:
            response = {'status': StatusCodes['bad_request'], 'results': 'Bid must be higher than the current highest bid'}
            return flask.jsonify(response)

        # Check if the bid is higher than the minimum price
        if bid_amount < auction[3]:  # Assuming the 5th column indicates the minimum bid price
            response = {'status': StatusCodes['bad_request'], 'results': 'Bid must be higher than the minimum price'}
            return flask.jsonify(response)

        # Insert the bid into the database
        cur.execute("INSERT INTO bids (auction_id, users_user_id, amount) VALUES (%s, %s, %s)", (auction_id, users.user_id, bids.amount))
        conn.commit()

        response = {'status': StatusCodes['success'], 'results': 'Bid placed successfully'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/bid/<int:auction_id>/<float:bid_amount> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##########################################################
#Auction Board (Comments)
##########################################################

@app.route('/comments/', methods=['POST'])
@token_required
def auction_board(current_user):
    logger.info('POST /comments')
    payload = flask.request.get_json()

    logger.debug(f'POST /users - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'comm_content' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'username value not in payload'}
        return flask.jsonify(response)
    # parameterized queries, good for security and performance
    statement = 'INSERT INTO comments (comm_content) VALUES (%s)'
    values = (payload['comm_content'])

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute(statement, values)

        # commit the transaction
        conn.commit()
        response = {'status': StatusCodes['success'], 'results': f'Inserted comments {payload["comm_content"]}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /users - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##########################################################
#Cacnel an Auction
#########################################################

@app.route('/auctions/<int:auction_id>/close', methods=['POST'])
@token_required
def close_auction(current_user, auction_id):
    logger.info(f'POST /auctions/{auction_id}/close')

    

    try:
        conn = db_connection()
        cur = conn.cursor()

        # Check if the auction exists
        cur.execute("SELECT * FROM auctions WHERE auction_id = %s", (auction_id,))
        auction = cur.fetchone()
        if auction is None:
            response = {'status': StatusCodes['not_found'], 'results': 'Auction not found'}
            return flask.jsonify(response)

        # Check if the auction has already ended
        if auction[2]: 
            response = {'status': StatusCodes['bad_request'], 'results': 'Auction has already ended'}
            return flask.jsonify(response)

        # Check if the current date and time is past the specified end date of the auction
        end_date = auction[2]  
        if datetime.datetime.now() < end_date:
            response = {'status': StatusCodes['bad_request'], 'results': 'Auction has not yet ended'}
            return flask.jsonify(response)

        # Determine the winner (assuming the highest bidder)
        cur.execute("SELECT bidder_username, MAX(bid_amount) FROM bids WHERE auction_id = %s", (auction_id,))
        winner_data = cur.fetchone()
        if winner_data is None:
            response = {'status': StatusCodes['bad_request'], 'results': 'No bids found for this auction'}
            return flask.jsonify(response)
        
        winner_username, winning_bid_amount = winner_data

        # Update auction details with winner and winning bid amount
        cur.execute("UPDATE auctions SET winner_username = %s, winning_bid = %s, ended = TRUE WHERE auction_id = %s",
                    (winner_username, winning_bid_amount, auction_id))
        conn.commit()

        response = {'status': StatusCodes['success'], 'results': 'Auction closed successfully'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)




##########################################################
# Cancel Auction
##########################################################

@app.route('/auctions/<int:auction_id>/cancel', methods=['POST'])
@token_required
def cancel_auction(current_user, auction_id):
    logger.info(f'POST /auctions/{auction_id}/cancel')

    

    try:
        conn = db_connection()
        cur = conn.cursor()

        # Check if the auction exists
        cur.execute("SELECT * FROM auctions WHERE auction_id = %s", (auction_id,))
        auction = cur.fetchone()
        if auction is None:
            response = {'status': StatusCodes['not_found'], 'results': 'Auction not found'}
            return flask.jsonify(response)

        # Check if the auction has already ended
        if auction[2]:  
            response = {'status': StatusCodes['bad_request'], 'results': 'Auction has already ended'}
            return flask.jsonify(response)

        # Cancel the auction
        cur.execute("UPDATE auctions SET ended = TRUE WHERE auction_id = %s", (auction_id,))
        conn.commit()

        response = {'status': StatusCodes['success'], 'results': 'Auction canceled successfully'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)



##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    time.sleep(1) # just to let the DB start before this print :-)

    logger.info("\n---------------------------------------------------------------\n" + 
                  "API v1.1 online: http://localhost:8080/users/\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)



