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

# Simpole token (shown in class)

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
            cur.execute("DELETE FROM tokens WHERE timeout<current_timestamp")
            conn.commit()

            cur.execute("SELECT user_id FROM tokens WHERE token= ?", (token))

            if cur.rowcount==0:
                return flask.jsonify({'message': 
                   'invalid token'})
            else:
                current_user = cur.fetchone()[0]
        except (Exception) as error:
            logger.error(f'POST /users - error: {error}')
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
## Demo GET
##
## Obtain all users in JSON format
##
## To use it, access:
##
## http://localhost:8080/users/
##

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
## Demo GET
##
## Obtain user with username <username>
##
## To use it, access:
##
## http://localhost:8080/users/ssmith
##

@app.route('/users/<username>/', methods=['GET'])
def get_user(username):
    logger.info('GET /users/<username>')

    logger.debug('username: {username}')

    

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute('SELECT username, name, city FROM users where username = %s', (username,))
        rows = cur.fetchall()

        row = rows[0]

        logger.debug('GET /users/<username> - parse')
        logger.debug(row)
        content = {'username': row[0], 'name': row[1], 'city': row[2]}

        response = {'status': StatusCodes['success'], 'results': content}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /users/<username> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


##
## Demo GET
##
## Obtain all active auctions in JSON format
##
## To use it, access:
##
## http://localhost:8080/users/
##

@app.route('/auctions/', methods=['GET'])
def get_all_auctions():
    logger.info('GET /auctions')

    

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM auctions')
        rows = cur.fetchall()

        logger.debug('GET /users - parse')
        Results = []
        for row in rows:
            logger.debug(row)
            content = {'auction id': row[0], 'item_name': row[1], 'Date_and_time': row[2], 'Min_Price': row[3]}
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
## Demo POST
##
## Add a new user in a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X POST http://localhost:8080/users/ -H 'Content-Type: application/json' -d '{"city": "London", "username": "ppopov", "name": "Peter Popov"}'
##

@app.route('/users/', methods=['POST'])
def add_users():
    logger.info('POST /users')
    payload = flask.request.get_json()

    

    logger.debug(f'POST /users - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'username' not in payload or 'email' not in payload or 'password' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'values missing from payload'}
        return flask.jsonify(response)
    
    # parameterized queries, good for security and performance
    statement = 'INSERT INTO users (username, email, password) VALUES (?,?,?)'
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
## curl -X POST http://localhost:8080/users/ -H 'Content-Type: application/json' -d '{"city": "London", "username": "ppopov", "name": "Peter Popov"}'
##

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
    query = 'SELECT user_id FROM users WHERE username = ? AND password = ?)'
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
            
            query  = "INSERT INTO tokens (users_user_id, token, exp_datetime) \
                VALUES( ?, ? , current_timestamp + (24 * interval '1 hour'))"
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
## Demo PUT
##
## Update a user based on a JSON payload
##
## To use it, you need to use postman or curl:
##
## curl -X PUT http://localhost:8080/users/ssmith -H 'Content-Type: application/json' -d '{"city": "Raleigh"}'
##

@app.route('/users/<username>', methods=['PUT'])
def update_users(username):
    logger.info('PUT /users/<username>')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /users/<username> - payload: {payload}')

    # do not forget to validate every argument, e.g.,:
    if 'city' not in payload:
        response = {'status': StatusCodes['api_error'], 'results': 'city is required to update'}
        return flask.jsonify(response)

    # parameterized queries, good for security and performance
    statement = 'UPDATE users SET city = %s WHERE username = %s'
    values = (payload['city'], username)

    try:
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



