import ast
import hashlib
import json
import os
import random
import logging
from datetime import date
import mysql.connector
from flask import Flask, jsonify, request

from solver import Solve_sudoku

# ---------- logger
logging.basicConfig(filename='./logs/'+str(date.today())+'.log',level=logging.DEBUG,
                    format=' %(levelname)s ---- %(asctime)s : %(message)s\n'+
'------------------------------------------------------------------------------------------------')

# ---------- set enviroment variable of sql password
mysqlpassword = os.environ["MYSQL_PASSWORD"]

# ---------- connect to mysql
mydb = mysql.connector.connect(
    host='mysql',
    user='root',
    password=mysqlpassword,
    database='sudoku_boards'
    )
mycursor = mydb.cursor()
logging.debug("\n\n\nconnected to MYSQL! starting to recive requests!\n\n")

# ---------- check if tables exist if not create.
mycursor.execute("SHOW TABLES")
tables = [x[0] for x in mycursor]
if 'bad_board' not in tables:
    mycursor.execute('CREATE TABLE bad_board (id VARCHAR(255), error VARCHAR(255))')
    logging.debug("created bad_board table")
if 'solved_board' not in tables:
    mycursor.execute('CREATE TABLE solved_board (id VARCHAR(255), solved_board VARCHAR(255), empty_places VARCHAR(255), multiple_answers VARCHAR(255))')
    logging.debug("created solved_board table")

def check_request(req, addr):
    logging.info("from " + addr + " starting to check request")
# ---------- check if request is json
    if req.is_json:
        req = req.get_json()
# ---------- check if request has 'data'
        if 'data' in req:
# ---------- check if request hs empty and board values
            if 'board' in req['data'] and 'empty' in req['data']:
# ---------- check if request's board is a list
                if type(req['data']['board']) == type([]):
# ---------- check if request's board is 81 items
                    if len(req['data']['board']) == 81:
# ---------- return True, the req, passed all the tests
                        logging.info("from " + addr + " done checking reqest everything was OK")
                        return True, req
# ---------- else return error json
                    else:
                        logging.warn("from " + addr + " bad json, bad board list value")
                        return jsonify({
                            "data_error":{"error":"invalid board value","fix":"board list should have 81 items"}}), 400
                else:
                    logging.warn("from " + addr + " bad json invalid format no list value for board")
                    return jsonify({
                        "data_error":{"error":"invalid key value","fix":"""board key should have a list value - {'data':{'board':[],'empty':X}}, make sure that the empty value is not true or false"""}}), 400
            else:
                logging.warn("from " + addr + " bad json invalid format no empty or board fields")
                return jsonify({
                    "data_error":{"error":"invalid json format","fix":"""use json format for request - {'data':{'board':[],'empty':X}}, make sure that the empty value is not true or false"""}}), 400
        else:
            logging.warn("from " + addr + " bad json no 'data' field")
            return jsonify({
                "data_error":{"error":"invalid json no 'data'","fix":"""use json format for request - {'data':{'board':[],'empty':X}}, make sure that the empty value is not true or false"""}}), 400
    else:
        logging.warn("from " + addr + " request was not a json!")
        return jsonify({
            "data_error":{"error":"request is not a json","fix":"""use json format for request - {'data':{'board':[],'empty':X}}"""}}), 400

def Solve(req, req_type, addr):
    logging.info("from " + addr + " starting to solve the board")
# ---------- hash the board and convert to hex - string
    hashed_board = hashlib.md5((str(req['data']['empty'])+str(req['data']['board'])).encode()).digest().hex()
# ---------- check if the id(hash) is already in the DB solved
    logging.info("from " + addr + " starting check the DB for solved/bad boards")
    mycursor.execute('SELECT * FROM solved_board WHERE id = %s',(hashed_board,))
    check_db = mycursor.fetchall()
    if len(check_db) > 0:
        if req_type == "solve":
            # create a list out of a string of a list
            board = ast.literal_eval(check_db[0][1])
            if check_db[0][3] == "True":
                # return json answer
                logging.info("to " + addr + " returning answer from DB " + req_type)
                return jsonify({"data":{"solved_board":board,"multiple_answers":True},"method":"db"}), 200
            else:
                # return json answer
                logging.info("to " + addr + " returning answer from DB " + req_type)
                return jsonify({"data":{"solved_board":board,"multiple_answers":False},"method":"db"}), 200
        else:
            random_place = random.choice(ast.literal_eval(check_db[0][2]))
            logging.info("to " + addr + " returning answer from DB " + req_type)
            return jsonify({"data":{"location":random_place,"value":ast.literal_eval(check_db[0][1])[random_place]},"method":"db"}), 200
# ---------- check if the id(hash) is already in DB error
    mycursor.execute('SELECT * FROM bad_board WHERE id = %s',(hashed_board,))
    check_db = mycursor.fetchall()
    if len(check_db) > 0:
        logging.warn("to " + addr + " returning bad board answer from DB")
        return jsonify(json.loads(check_db[0][1])), 400
    else:
# ---------- the board was not solved before create a board obj for the sudoku solver.
        logging.debug("from " + addr + " board was not in the DB tring to solve")
        board = Solve_sudoku(req['data']['board'],req['data']['empty'])
# ---------- check for errors
        board_error = board.error_check()
        logging.info("from " + addr + " checking for board errors")
        if board_error[0] == True:
            logging.warn("from " + addr + " bad board - " + board_error[1])
            mycursor.execute(f'INSERT INTO bad_board (id, error) VALUES (%s, %s)',(hashed_board, json.dumps({"data_error":{"error":board_error[1],"fix":board_error[2]},"method":"db"})))
            mydb.commit()
            logging.info("sent to DB")
            logging.info("to " + addr + " returning bad board answer")
            return jsonify({
                "data_error":{"error":board_error[1],"fix":board_error[2]},"method":"solver"}), 400
        else:
# ---------- solve the board and check if can be solved
            logging.info("from " + addr + " board has no error tring to solve")
            solve = board.solve()
            if solve == False:
                logging.warn("from " + addr + " bad board no valid solution")
                mycursor.execute(f'INSERT INTO bad_board (id, error) VALUES (%s, %s)',(hashed_board, json.dumps({"data_error":{"error":"bad board","fix":"bad sudoku board there is no valid solution"},"method":"db"})))
                mydb.commit()
                logging.info("sent to DB")
                logging.info("to " + addr + " returning bad board answer")
                return jsonify({
                        "data_error":{"error":"bad board","fix":"bad sudoku board there is no valid solution"},"method":"solver"}), 400
# ---------- add the board to DB
            logging.debug("from " + addr + " board is solved!")
            mycursor.execute(f'INSERT INTO solved_board (id, solved_board, empty_places, multiple_answers) VALUES (%s, %s, %s, %s)',(hashed_board, str(board.board), str(board.empty_places), str(board.multiple_answers)))
            mydb.commit()
            logging.info("sent to DB")
# ---------- return json answer solved board
            if req_type == "solve":
                logging.info("to " + addr + " returning answer " + req_type)
                return jsonify({"data":{"solved_board":board.board,"multiple_answers":board.multiple_answers},"method":"solver"}), 200
            else:
                hint = board.hint()
                logging.info("to " + addr + " returning answer " + req_type)
                return jsonify({"data":{"location":hint[0],"value":hint[1]},"method":"solver"}), 200

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    req_addr = request.remote_addr
    logging.debug("connection from " + req_addr + "to home")
    return '''
    welcome to sudoku API solver, using this API you can send http requests of an unsolved sudoku board
    and get back a solved one or a hint.
    there are 4 requests types:
    sudoku api:5000/solve GET - to get your sudoku solved:
    with a json in the body of the req in this foramt:
    {'data':{'board':[],'empty':X}}.

    sudoku api:5000/hint GET - to geta hint for youe sudoku:
    with a json in the body of the req in this foramt:
    {'data':{'board':[],'empty':X}}.

    sudoku api:5000/delete_db GET - if you want to delete all the contents of the Database:
    no body is required.

    and:
    sudoku api:5000/show_db GET - to get a list of all the data in the Database:
    no body is required.
    ''', 200

@app.route('/solve', methods=['GET'])
def solve_board():
    req_addr = request.remote_addr
    logging.debug(" ----- connection from " + req_addr + " to solve ----- ")
    req = check_request(request, req_addr)
# ---------- check that the json request was valid
    if not req[0] == True:
        return req
    else:
# ---------- solve and return json
        req = req[1]
        return Solve(req, "solve", req_addr)

@app.route('/hint', methods=['GET'])
def hint_answer():
    req_addr = request.remote_addr
    logging.debug(" ----- connection from " + req_addr + " to hint ----- ")
    req = check_request(request, req_addr)
# ---------- check that the json request was valid
    if not req[0] == True:
        return req
    else:
# ---------- solve and return json
        req = req[1]
        return Solve(req, "hint", req_addr)

@app.route('/delete_db', methods=['GET'])
def del_db():
    req_addr = request.remote_addr
    logging.debug(" ----- connection from " + req_addr + " to delete_db ----- ")
    mycursor.execute('DROP TABLE solved_board')
    mycursor.execute('DROP TABLE bad_board')
    mycursor.execute('CREATE TABLE solved_board (id VARCHAR(255), solved_board VARCHAR(255), empty_places VARCHAR(255), multiple_answers VARCHAR(255))')
    mycursor.execute('CREATE TABLE bad_board (id VARCHAR(255), error VARCHAR(255))')
    logging.info("deleted old DB tables")
    return jsonify({"data":{"delete":"deleted the contents of table's - solved_board & bad_board"}}), 200

@app.route('/show_db', methods=['GET'])
def show_db():
    req_addr = request.remote_addr
    logging.debug(" ----- connection from " + req_addr + " to show_db ----- ")
    mycursor.execute('SELECT * FROM solved_board')
    solved_list = mycursor.fetchall()
    mycursor.execute('SELECT * FROM bad_board')
    bad_list = mycursor.fetchall()
    logging.info("got all the data from the tables, sending to " + req_addr)
    return jsonify({"data":{"soloved":solved_list, "bad":bad_list}})

if __name__ == '__main__':
    app.run(debug=True)