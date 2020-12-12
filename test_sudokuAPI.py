import unittest
import json
import requests

url = 'http://localhost:5000'

test = [
    {"data":{"empty":0,"board":[0,0,0,0,7,0,0,0,0,6,0,0,1,9,5,0,0,0,0,9,8,0,0,0,0,6,0,8,0,0,0,6,0,0,0,3,4,0,0,8,0,3,0,0,1,7,0,0,0,2,0,0,0,6,0,6,0,0,0,0,2,8,0,0,0,0,4,1,9,0,0,5,0,0,0,0,8,0,0,7,9]}},
    {"empty":0,"board":[0,0,0,0,7,0,0,0,0,6,0,0,1,9,5,0,0,0,0,9,8,0,0,0,0,6,0,8,0,0,0,6,0,0,0,3,4,0,0,8,0,3,0,0,1,7,0,0,0,2,0,0,0,6,0,6,0,0,0,0,2,8,0,0,0,0,4,1,9,0,0,5,0,0,0,0,8,0,0,7,9]},
    {"data":{"ampty":0,"board":[0,0,0,0,7,0,0,0,0,6,0,0,1,9,5,0,0,0,0,9,8,0,0,0,0,6,0,8,0,0,0,6,0,0,0,3,4,0,0,8,0,3,0,0,1,7,0,0,0,2,0,0,0,6,0,6,0,0,0,0,2,8,0,0,0,0,4,1,9,0,0,5,0,0,0,0,8,0,0,7,9]}},
    {"data":{"empty":0,"bord":[0,0,0,0,7,0,0,0,0,6,0,0,1,9,5,0,0,0,0,9,8,0,0,0,0,6,0,8,0,0,0,6,0,0,0,3,4,0,0,8,0,3,0,0,1,7,0,0,0,2,0,0,0,6,0,6,0,0,0,0,2,8,0,0,0,0,4,1,9,0,0,5,0,0,0,0,8,0,0,7,9]}},
    {"data":{"non":0,"sudoku":[0,0,0,0,7,0,0,0,0,6,0,0,1,9,5,0,0,0,0,9,8,0,0,0,0,6,0,8,0,0,0,6,0,0,0,3,4,0,0,8,0,3,0,0,1,7,0,0,0,2,0,0,0,6,0,6,0,0,0,0,2,8,0,0,0,0,4,1,9,0,0,5,0,0,0,0,8,0,0,7,9]}},
    {"data":{"empty":0,"board":"0,0,0,0,7,0,0,0,0,6,0,0,1,9,5,0,0,0,0,9,8,0,0,0,0,6,0,8,0,0,0,6,0,0,0,3,4,0,0,8,0,3,0,0,1,7,0,0,0,2,0,0,0,6,0,6,0,0,0,0,2,8,0,0,0,0,4,1,9,0,0,5,0,0,0,0,8,0,0,7,9"}},
    {"data":{"empty":0,"board":[1,0,0,0,0,7,0,0,0,0,6,0,0,1,9,5,0,0,0,0,9,8,0,0,0,0,6,0,8,0,0,0,6,0,0,0,3,4,0,0,8,0,3,0,0,1,7,0,0,0,2,0,0,0,6,0,6,0,0,0,0,2,8,0,0,0,0,4,1,9,0,0,5,0,0,0,0,8,0,0,7,9]}}
]
res  = [
    {"data":{"delete":"deleted the contents of table's - solved_board & bad_board"}},
    {"data": {"bad": [],"soloved": []}},
    {"data_error":{"error":"request is not a json","fix":"use json format for request - {'data':{'board':[],'empty':X}}"}},
    {"data_error":{"error":"invalid json no 'data'","fix":"""use json format for request - {'data':{'board':[],'empty':X}}, make sure that the empty value is not true or false"""}},
    {"data_error":{"error":"invalid json format","fix":"use json format for request - {'data':{'board':[],'empty':X}}, make sure that the empty value is not true or false"}},
    {"data_error":{"error":"invalid key value","fix":"board key should have a list value - {'data':{'board':[],'empty':X}}, make sure that the empty value is not true or false"}},
    {"data_error":{"error":"invalid board value","fix":"board list should have 81 items"}}
]

def send_req(**data):
    if 'not_json' in data:
        r = requests.get(url+"/"+data['type'], data=data['test'])
        return r.json()
    if 'test' in data:
        r = requests.get(url+"/"+data['type'], json=data['test'])
        return r.json()
    else:
        r = requests.get(url+"/"+data['type'])
        return r.json()


class Testapi(unittest.TestCase):
    
    def test_table_del(self):
        self.assertEqual(send_req(type="delete_db"),res[0])
        self.assertEqual(send_req(type="show_db"),res[1])

    def test_bad_req(self):
        req_type = "solve"
        for _ in range(2):
            self.assertEqual(send_req(type=req_type,test=test[0],not_json=True),res[2])
            self.assertEqual(send_req(type=req_type,test=test[1]),res[3])
            self.assertEqual(send_req(type=req_type,test=test[2]),res[4])
            self.assertEqual(send_req(type=req_type,test=test[3]),res[4])
            self.assertEqual(send_req(type=req_type,test=test[4]),res[4])
            self.assertEqual(send_req(type=req_type,test=test[5]),res[5])
            self.assertEqual(send_req(type=req_type,test=test[6]),res[6])
            req_type = "hint"

    def test_board(self):
        pass

if __name__ == "__main__":
    unittest.main()