from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models.UsuarioModel import UsuarioAdmin
from app.utils.response import api_response
from app.utils.RaiseException import MissingValueError, UnauthorizedError, UnexpectedError
from app.utils.Logger import logger
from app.utils.Messages import *
from app.main import db, bcrypt
from app.services.AuthServices import AuthServices


LOG  = logger()
AuthController  = Blueprint("auth", __name__)

@AuthController.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    return AuthServices.login_admin(data)

@AuthController.route("/registrar", methods=["POST"])
def registrar_admin():
    data = request.get_json()
    return AuthServices.registrar_admin(data)
