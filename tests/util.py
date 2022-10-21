from faker import Faker
#from faker.generator import random

class Util():
    
    def __init__(self):
        self.data_factory = Faker()
        
    def getNewUser(self):
        new_user = {
            "username": self.data_factory.name(),
            "password": self.data_factory.word(),
            "email": self.data_factory.email()
        }
        return new_user
        
    def getNewTask(self, filename, newformat):
        new_task = {
            "filename": filename,
            "newformat": newformat
        }
        return new_task

    def getHeaders(self, token):
        return {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(token)}