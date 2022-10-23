import os
import json
import redis
from os import remove
from flask import request, current_app, send_from_directory
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from werkzeug.utils import secure_filename
#from hashlib import algorithms_available
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
        
        resultado, mensaje = self.validatePassword(request)
        if not (resultado):
            return mensaje, 401
        
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

    def validatePassword(self, request):
        resultado = False
        mensaje = ""
        if request.json["password"] == request.json["password2"]:
            password = request.json["password"]
            if len(request.json["password"])<8:
                mensaje = "password no cumple longitud"
            else:
                minuscula = 0
                for minus in password:
                    if minus.islower()==True:
                        minuscula = 1
                        break
                mayuscula = 0
                for mayus in password:
                    if mayus.isupper()==True:
                        mayuscula = 1
                        break
                digito = 0
                for dig in password:
                    if dig.isdigit()==True:
                        digito = 1
                        break
                blanco = 0
                if password.count(" ")>0:
                    blanco = 1
                caracter = 0
                if password.count(".")>0 or password.count("$")>0 or password.count("&")>0:
                    caracter = 1
                if caracter == 1 and blanco == 0 and digito == 1 and minuscula == 1 and mayuscula == 1:
                    resultado = True
                else:
                    mensaje = "password no cumple condiciones de seguridad"
        else:
            mensaje = "password no coincide"
        return resultado, mensaje


class VistaLogin(Resource):

    def post(self):
        user = User.query.filter(User.username == request.json["username"], User.password == request.json["password"]).first()
        db.session.commit()
        if user is None:
            return "El usuario no existe", 404
        else:
            token = create_access_token(identity=user.id, additional_claims={"role": user.role, "user": user.username})
            return {"mensaje": "Inicio de sesion exitoso", "token": token}


class VistaTasks(Resource):

    def __init__(self) -> None:
        # self.admin_email = 'ag.castiblanco1207@uniandes.edu.co'
        # self.redis_cli = redis.Redis(host="localhost", password="redispw", port=6379, decode_responses=True, encoding="utf-8", )
        self.admin_email = 'c.solanor@uniandes.edu.co'
        self.redis_cli = redis.Redis(host="redis-converter", port=6379, decode_responses=True, encoding="utf-8", )
        super().__init__()

    # listar todas las tareas de conversion de un usuario 
    # usuario debe proveer el token
    # servicio devuelve id tarea, nombre y extension archivo, extension a convertir, estado 
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        #print("vista-tasks-get user_id: ", user_id)
        tasks = db.session.query(Task).select_from(Task).filter(Task.user==user_id).all()
        return [task_schema.dump(t) for t in tasks]


    @jwt_required()
    def post(self):
        filename = None
        print("")
        # if 'fileName' in request.files:
        if 'file' in request.files:
            #file = request.files['fileName']
            file = request.files['file']

            # print("file.filename: ", file.filename)
            if file.filename:                
                #print("vista-tasks-post file.filename: ", file.filename)
                filename = secure_filename(file.filename)

                format = file.filename[len(file.filename)-3:]
                newformat = request.form["newFormat"]

                supported = False
                if format=="mp3" and (newformat=="ogg" or newformat=="wav"):
                    supported = True
                elif format=="wav" and (newformat=="ogg" or newformat=="mp3"):
                    supported = True
                elif format=="ogg" and (newformat=="wav" or newformat=="mp3"):
                    supported = True

                if(not supported):
                    return "Task was not created - formats not supported", 400

                #print("vista-tasks-post secure_filename: ", filename)
                audio_dir = current_app.config['AUDIO_DIR']
                os.makedirs(audio_dir, exist_ok=True)
                
                #print("vista-tasks-post os.makedirs")
                file_path = os.path.join(audio_dir, filename)
                file.save(file_path)
                #print("file_path:", file_path)

                #user_id=current_user.id
                user_id = get_jwt_identity()
                new_task = Task(filename=filename, newformat=newformat, user=user_id, status="uploaded", upload_date=datetime.now())
                db.session.add(new_task)
                db.session.commit()

                user = db.session.query(User).filter(User.id==user_id).first()
                task_created = db.session.query(Task).filter(Task.user==user_id, Task.filename==filename, Task.newformat==newformat).first()
                message = {"id": task_created.id, 
                            "filepath": file_path, 
                            "filename": task_created.filename, 
                            "newformat": task_created.newformat, 
                            "username": user.username, 
                            "email": user.email}
                self.redis_cli.publish("audio", json.dumps(message))
                
                return task_schema.dump(new_task)
            return "Task was not created - empty file", 400
        return "Task was not created - file missing", 400


class VistaTask(Resource):

    def __init__(self) -> None:
        self.admin_email = 'c.solanor@uniandes.edu.co'
        self.redis_cli = redis.Redis(host="redis-converter", port=6379, decode_responses=True, encoding="utf-8", )
        super().__init__()

    @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))        

    @jwt_required()
    def delete(self, id_task):
        task = Task.query.get_or_404(id_task)
        if task.status == 'processed':
            filename = task.filename
            format = filename[len(filename)-3:]
            newFormat = task.newformat
            archivo = filename.replace(format, newFormat)
            audio_dir = current_app.config['AUDIO_DIR']
            file_path = os.path.join(audio_dir, archivo)
            if os.path.isfile(file_path):
                remove(file_path)
            db.session.delete(task)
            db.session.commit()
            return 'Task deleted successfully', 204
        else:
            return "The task could not be deleted", 400 

    @jwt_required()
    def put(self, id_task):
        user_id = get_jwt_identity()
        user = db.session.query(User).filter(User.id==user_id).first()
        task = db.session.query(Task).filter(Task.id==id_task).first()

        format = task.filename[len(task.filename)-3:]
        newformat = request.form["newFormat"]
        supported = False

        if format=="mp3" and (newformat=="ogg" or newformat=="wav"):
            supported = True
        elif format=="wav" and (newformat=="ogg" or newformat=="mp3"):
            supported = True
        elif format=="ogg" and (newformat=="wav" or newformat=="mp3"):
            supported = True

        if(not supported):
            return "Task was not created - formats not supported", 400

        audio_dir = current_app.config['AUDIO_DIR']
        os.makedirs(audio_dir, exist_ok=True)
        file_path = os.path.join(audio_dir, task.filename)

        print("")
        print("put: ", id_task, file_path, task.newformat, newformat, task.status)

        if(task.status=="processed"):
            if os.path.isfile(file_path):
                remove(file_path.replace(format, task.newformat))
            task.status = "uploaded"

        task.newformat = newformat
        db.session.add(task)
        db.session.commit()

        message = {"id": task.id, 
                    "filepath": file_path, 
                    "filename": task.filename, 
                    "newformat": task.newformat, 
                    "username": user.username, 
                    "email": user.email}

        self.redis_cli.publish("audio", json.dumps(message))
        return task_schema.dump(task)


class VistaFile(Resource):

    @jwt_required()
    def get(self, filename):
        try:
            return send_from_directory(current_app.config['AUDIO_DIR'], filename, as_attachment=True)
        except:
            if self.isFilePendingProcess(filename):
                return "File is not processed yet, please retry in a couple minutes"
            return "File is not available"
    
    def isFilePendingProcess(self,filename):
        required_file_ext = filename[-3:]

        # Valido si existe una tarea pendiente de procesar que devuelva el archivo requerido
        for file_ext in current_app.config['UPLOAD_EXTENSIONS']:
            filename_option = os.path.splitext(filename)[0] + file_ext
            file_pending_process = db.session.query(Task).filter(Task.filename.like(filename_option), Task.newformat.like(required_file_ext), Task.status.like("uploaded")).first()
            if file_pending_process is not None:
                return True
        return False
