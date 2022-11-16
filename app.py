import os
#import google.cloud.logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from os.path import abspath, dirname, join

from modelos import db
from vistas import  VistaSignup, VistaLogin, VistaTasks, VistaTask, VistaFile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'S3CR3T-K3Y-4204'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['BASE_DIR'] = dirname(dirname(abspath(__file__)))
#app.config['BASE_DIR'] = "/nfs/general/" 
app.config['AUDIO_DIR'] = join(app.config['BASE_DIR'], 'audio')
app.config['BUCKET'] = os.getenv("AUDIO_BUCKET") 
app.config['TOPIC'] = os.getenv("TOPIC_ID") 
app.config['PROJECT'] = os.getenv("PROJECT_ID") 
app.config['UPLOAD_EXTENSIONS'] = ['.mp3', '.wav', '.ogg']

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

#client = google.cloud.logging.Client()
#client.setup_logging()

api = Api(app)
api.add_resource(VistaSignup, '/api/auth/signup')
api.add_resource(VistaLogin, '/api/auth/login')
api.add_resource(VistaTasks, '/api/tasks')
api.add_resource(VistaTask, '/api/tasks/<int:id_task>')
api.add_resource(VistaFile, '/api/files/<path:filename>')
#api.add_resource(VistaFiles, '/api/files/<string:filename>')

jwt = JWTManager(app)
