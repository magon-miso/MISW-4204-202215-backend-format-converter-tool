import json
from unittest import TestCase
from faker import Faker
from app import app
from tests import util
#from faker.generator import random

class TestTask(TestCase):

    def setUp(self):
        self.utilities = util.Util()
        self.data_factory = Faker()
        self.client = app.test_client()

        self.endpoint_signup = '/api/auth/signup'
        self.endpoint_login = '/api/auth/login'
        self.endpoint_tasks = '/api/tasks'

        signed = False
        while(not(signed)):
            new_user = self.utilities.getNewUser()
            req_new_user = self.client.post(self.endpoint_signup, data=json.dumps(new_user), headers={'Content-Type': 'application/json'})
            resp_new_user = json.loads(req_new_user.get_data())
            if(type(resp_new_user)==dict):
                signed=True
            else:
                print("not signed: ", new_user["username"], resp_new_user)
        
        self.new_user = new_user
        self.resp_new_user = resp_new_user

        req_login = self.client.post(self.endpoint_login, 
                    data=json.dumps({"username":self.new_user["username"], "password":self.new_user["password"]}),
                    headers={'Content-Type': 'application/json'})
        resp_login = json.loads(req_login.get_data())
        self.assertEqual(resp_login["mensaje"], "Inicio de sesión exitoso")
        self.token = resp_login["token"]
        self.headers = self.utilities.getHeaders(self.token)
        print(" ")


    def test_get_tasks_user(self):
        req_login = self.client.post(self.endpoint_login, 
                    data=json.dumps({"username":self.new_user["username"], "password":self.new_user["password"]}),
                    #data=json.dumps({"username":"Cory Cohen", "password":"group"}),
                    headers={'Content-Type': 'application/json'})
        resp_login = json.loads(req_login.get_data())
        self.assertEqual(resp_login["mensaje"], "Inicio de sesión exitoso")

        req_tasks = self.client.get(self.endpoint_tasks, headers=self.headers)
        #req_tasks = self.client.get(self.endpoint_tasks, headers=self.utilities.getHeaders(resp_login["token"]))
        resp_tasks = json.loads(req_tasks.get_data())
        #print(resp_tasks)
        self.assertEqual(req_tasks.status_code, 200)
        self.assertEqual(len(resp_tasks), 0)

    def test_create_task(self):
        req_tasks = self.client.get(self.endpoint_tasks, headers=self.headers)
        num_tasks_init = len(json.loads(req_tasks.get_data()))
        self.assertEqual(req_tasks.status_code, 200)
        self.assertEqual(num_tasks_init, 0)

        filename = "boys II men - end of the road.mp3"
        new_task = {"newFormat": "wav"}
        audiofile = open(filename, 'rb')
        new_task["file"] = (audiofile, filename)
        req_new_task = self.client.post(self.endpoint_tasks, data=new_task, headers=self.headers, content_type='multipart/form-data') 
        resp_new_task = json.loads(req_new_task.get_data())
        audiofile.close()
        #print("resp_new_task: ", resp_new_task)
        self.assertEqual(req_new_task.status_code, 200)
        self.assertEqual(resp_new_task["status"], "uploaded")

        filename = "boys II men - end of the road.mp3"
        new_task = {"newFormat": "ogg"}
        audiofile = open(filename, 'rb')
        new_task["file"] = (audiofile, filename)
        req_new_task = self.client.post(self.endpoint_tasks, data=new_task, headers=self.headers, content_type='multipart/form-data') 
        resp_new_task = json.loads(req_new_task.get_data())
        audiofile.close()
        #print("resp_new_task: ", resp_new_task)
        self.assertEqual(req_new_task.status_code, 200)
        self.assertEqual(resp_new_task["status"], "uploaded")

        filename = "blaze of glory.wav"
        new_task = {"newFormat": "mp3"}
        audiofile = open(filename, 'rb')
        new_task["file"] = (audiofile, filename)
        req_new_task = self.client.post(self.endpoint_tasks, data=new_task, headers=self.headers, content_type='multipart/form-data') 
        resp_new_task = json.loads(req_new_task.get_data())
        audiofile.close()
        #print("resp_new_task: ", resp_new_task)
        self.assertEqual(req_new_task.status_code, 200)
        self.assertEqual(resp_new_task["status"], "uploaded")

        filename = "blaze of glory.wav"
        new_task = {"newFormat": "ogg"}
        audiofile = open(filename, 'rb')
        new_task["file"] = (audiofile, filename)
        req_new_task = self.client.post(self.endpoint_tasks, data=new_task, headers=self.headers, content_type='multipart/form-data') 
        resp_new_task = json.loads(req_new_task.get_data())
        audiofile.close()
        #print("resp_new_task: ", resp_new_task)
        self.assertEqual(req_new_task.status_code, 200)
        self.assertEqual(resp_new_task["status"], "uploaded") 

        filename = "metallica - fade to black.ogg"
        new_task = {"newFormat": "mp3"}
        audiofile = open(filename, 'rb')
        new_task["file"] = (audiofile, filename)
        req_new_task = self.client.post(self.endpoint_tasks, data=new_task, headers=self.headers, content_type='multipart/form-data') 
        resp_new_task = json.loads(req_new_task.get_data())
        audiofile.close()
        #print("resp_new_task: ", resp_new_task)
        self.assertEqual(req_new_task.status_code, 200)
        self.assertEqual(resp_new_task["status"], "uploaded")

        filename = "metallica - fade to black.ogg"
        new_task = {"newFormat": "wav"}
        audiofile = open(filename, 'rb')
        new_task["file"] = (audiofile, filename)
        req_new_task = self.client.post(self.endpoint_tasks, data=new_task, headers=self.headers, content_type='multipart/form-data') 
        resp_new_task = json.loads(req_new_task.get_data())
        audiofile.close()
        #print("resp_new_task: ", resp_new_task)
        self.assertEqual(req_new_task.status_code, 200)
        self.assertEqual(resp_new_task["status"], "uploaded")

        req_tasks = self.client.get(self.endpoint_tasks, headers=self.headers)
        num_tasks_done = len(json.loads(req_tasks.get_data()))
        self.assertEqual(req_tasks.status_code, 200)        
        self.assertEqual(num_tasks_done, 6)

'''
    def test_login_usuario_contrasena_incorrecta(self):
        req_login = self.client.post(self.endpoint_login, 
                                data=json.dumps({"username":self.new_user["username"], "password":"wrong-password"}),
                                headers={'Content-Type': 'application/json'})
        respuesta_login = json.loads(req_login.get_data())
        self.assertEqual(req_login.status_code, 404)
        self.assertEqual(respuesta_login, "El usuario no existe")
'''