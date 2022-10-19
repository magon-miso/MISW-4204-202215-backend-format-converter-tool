import json
from unittest import TestCase
from faker import Faker
from app import app
from tests import util
#from faker.generator import random

class TestUser(TestCase):

    def setUp(self):
        self.utilities = util.Util()
        self.data_factory = Faker()
        self.client = app.test_client()

        self.endpoint_signup = '/api/auth/signup'
        self.endpoint_login = '/api/auth/login'

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
        

    def test_crear_usuario(self):
        #print("..")
        #print(self.resp_new_user)
        self.assertEqual(self.resp_new_user["mensaje"], "usuario creado exitosamente")
        

    def test_crear_usuario_existente_error(self):
        user_exists = {
            "username": self.new_user["username"],
            "password": self.data_factory.word(),
            "email": self.data_factory.email()
        }

        req_user_exists = self.client.post(self.endpoint_signup, data=json.dumps(user_exists), headers={'Content-Type': 'application/json'})
        resp_user_exists = json.loads(req_user_exists.get_data())
        self.assertEqual(req_user_exists.status_code, 400)
        self.assertEqual(resp_user_exists, "Ya existe un usuario registrado con ese identificador")


    def test_crear_usuario_correo_existente_error(self):
        user_exists = {
            "username": self.data_factory.name(),
            "password": self.data_factory.word(),
            "email": self.new_user["email"],
        }        
        
        req_email_exists = self.client.post(self.endpoint_signup, data=json.dumps(user_exists), headers={'Content-Type': 'application/json'})
        resp_email_exists = json.loads(req_email_exists.get_data())
        self.assertEqual(req_email_exists.status_code, 400)
        self.assertEqual(resp_email_exists,  "Ya existe un usuario registrado con ese correo")


    def test_login_usuario(self):
        req_login = self.client.post(self.endpoint_login, 
                                data=json.dumps({"username":self.new_user["username"], "password":self.new_user["password"]}),
                                headers={'Content-Type': 'application/json'})
        resp_login = json.loads(req_login.get_data())
        self.assertEqual(resp_login["mensaje"], "Inicio de sesión exitoso")


    def test_login_usuario_contrasena_incorrecta(self):
        req_login = self.client.post(self.endpoint_login, 
                                data=json.dumps({"username":self.new_user["username"], "password":"wrong-password"}),
                                headers={'Content-Type': 'application/json'})
        respuesta_login = json.loads(req_login.get_data())
        self.assertEqual(req_login.status_code, 404)
        self.assertEqual(respuesta_login, "El usuario no existe")
    

    def test_login_usuario_inexsistente(self):
        req_login = self.client.post(self.endpoint_login, 
                                data=json.dumps({"username":"username-doesnt-exit", "password":self.new_user["password"]}),
                                headers={'Content-Type': 'application/json'})
        resp_login = json.loads(req_login.get_data())
        self.assertEqual(req_login.status_code, 404)
        self.assertEqual(resp_login, "El usuario no existe")
