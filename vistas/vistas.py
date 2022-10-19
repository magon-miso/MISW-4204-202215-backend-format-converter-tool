from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
#from sqlalchemy.exc import IntegrityError
#from sqlalchemy import or_, desc
from datetime import datetime

from modelos import db, Task, TaskSchema, User, UserSchema

task_schema = TaskSchema()
user_schema = UserSchema()


class VistaSignup(Resource):

    def post(self):        
        validacion = self.validateUser(request)
        if validacion is not None:
            return "Ya existe un usuario registrado con ese " + validacion, 400
        
        new_user = User(username=request.json["username"], 
                                password=request.json["password"], 
                                email=request.json["email"],
                                role="USER")
        db.session.add(new_user)
        user_created = db.session.query(User).filter(User.username.like(request.json["username"]), User.password.like(request.json["password"])).first()
        db.session.commit()
        token = create_access_token(identity=new_user.id,additional_claims={"role": new_user.role, "user": new_user.username})
        return {"mensaje": "usuario creado exitosamente", "token": token, "id": user_created.id}
    

    def validateUser(self, request):
        user_name = db.session.query(User).filter(User.username.like(request.json["username"])).first()
        if user_name is not None:
            return "identificador"
    
        user_email = db.session.query(User).filter(User.email.like(request.json["email"])).first()
        if user_email is not None:
            return "correo"


class VistaLogin(Resource):

    def post(self):
        user = User.query.filter(User.username == request.json["username"], User.password == request.json["password"]).first()
        db.session.commit()
        if user is None:
            return "El usuario no existe", 404
        else:
            token = create_access_token(identity=user.id, additional_claims={"role": user.role, "user": user.username})
            return {"mensaje": "Inicio de sesión exitoso", "token": token}


class VistaTasks(Resource):

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        new_task = Task(filename=request.json["fileName"], 
                        newformat=request.json["newFormat"],
                        user=user_id,
                        status="uploaded", 
                        upload_time=datetime.now())

        db.session.add(new_task)
        db.session.commit()
        return task_schema.dump(new_task)


class VistaTask(Resource):

    @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))        

    @jwt_required()
    def delete(self, id_task):
        task = Task.query.get_or_404(id_task)
        db.session.delete(task)
        db.session.commit()
        return '', 204
