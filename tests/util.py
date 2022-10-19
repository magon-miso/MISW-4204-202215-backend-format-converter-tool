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

    # def getNewCarrera(self, tipo_evento, nombre_competidores, numero_competidores=3):
    #     new_carrera = {
    #         "nombre": self.data_factory.sentence(),
    #         "tipo_evento":tipo_evento,
    #         "competidores": [
    #             {"probabilidad": round(random.uniform(0.1, 0.99), 2), "competidor": nombre_competidores[0] if len(nombre_competidores)>=1 else self.data_factory.name()},
    #             {"probabilidad": round(random.uniform(0.1, 0.99), 2), "competidor": nombre_competidores[1] if len(nombre_competidores)>=2 else self.data_factory.name()},
    #             {"probabilidad": round(random.uniform(0.1, 0.99), 2), "competidor": nombre_competidores[2] if len(nombre_competidores)>=3 else self.data_factory.name()} 
    #         ]
    #     }
    #     return new_carrera
    