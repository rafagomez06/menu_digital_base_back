from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
import traceback
from app.main import db
from app.models.menu import CtlPlatillos
from app.utils.response import api_response
from app.utils.RaiseException import (DatabaseError,UnexpectedError)
from app.utils.Messages import (STATUS_CODE_200,STATUS_CODE_201,STATUS_CODE_404,STATUS_CODE_400,
    SUCCESS,ERROR,DESCRIPCION_PLATILLO_CORTO,NOMBRE_PLATILLO_CORTO,PLATILLO_SUCCESS_DELETED,
    DESCRIPCION_PLATILLO_LARGO,REGISTRO_NO_EXISTE,PLATILLO_SUCCESS_UPDATED,PRECIO_ERROR,
    IMAGEN_ERROR,IMAGEN_EMPTY,CAMPOS_REQUERIDOS,ERROR_EMPTY,PRECIO_MAX,PLATILLO_SUCCESS)
from app.utils.Logger import logger
import os
from app.utils.FileTools import FileTools  

LOG           = logger()
menu_bp  = Blueprint("menu", __name__)
UPLOAD_FOLDER = 'static/uploads/platillos'

# #####################################
# RUTAS PÚBLICAS (sin JWT)
# #####################################

@menu_bp.route("/platillos", methods=["GET"])
def listar_platillos():
    try:
        id_platillo                 = request.args.get("id_platillo")
        nombre                      = request.args.get("nombre")

        query = CtlPlatillos.query.filter(CtlPlatillos.activo == 1)
        
        if id_platillo:
            query = query.filter(CtlPlatillos.id_platillo == id_platillo)

        platillos = query.order_by(CtlPlatillos.fecha_creacion.desc()).all()

        if not platillos:
            LOG.info(f"GET /menu - {ERROR_EMPTY}")            
            return api_response(STATUS_CODE_404, {},ERROR,ERROR_EMPTY)
        
        LOG.info(f"GET /menu - {len(platillos)} resultados")
        menu_json = [c.to_dict() for c in platillos]
        
        return api_response(STATUS_CODE_200, menu_json, SUCCESS)
    
    except SQLAlchemyError as e: 
        LOG.error(f"DB error en listar_platillos: {str(e)}")
        raise DatabaseError("Error al consultar la base de datos")
    except ValueError as e: 
        LOG.warning(f"Parámetro inválido: {str(e)}")
        raise UnexpectedError("Parámetros de búsqueda inválidos")
    except Exception as e:  
        error_trace = traceback.format_exc()
        LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
        raise UnexpectedError("Ocurrió un error inesperado")

@menu_bp.route("/platillos", methods=["POST"])
def crear_platillo():
    try:
        data = request.form
        
        # campos para crear platillo req.
        campos_requeridos = [
            "nombre","precio","categoria_platillo_fk","descripcion",
        ]
        # Validamos que ingrese campos requeridos.
        campos_faltantes = [
            campo for campo in campos_requeridos 
            if campo not in data or data[campo] is None or data[campo] == ""
        ]
        # Validamos que venga la imagen
        if 'imagen' not in request.files:
                    campos_faltantes.append('imagen')

        if campos_faltantes:
            return api_response(STATUS_CODE_400,{},ERROR,CAMPOS_REQUERIDOS)
        
        foto = request.files['imagen']
        nombre_platillo = data.get("nombre")
        descripcion = data.get("descripcion")
        precio_raw = data.get("precio") 
        
        try:
            precio = float(precio_raw) if precio_raw else 0.0
        except ValueError:
            return api_response(STATUS_CODE_400, {}, ERROR, PRECIO_ERROR)
        if foto.filename == '':
            return api_response(STATUS_CODE_400, {}, ERROR, IMAGEN_EMPTY)


        # Validaciones
        if not nombre_platillo or not nombre_platillo.strip():
            return api_response(STATUS_CODE_400,{},ERROR,NOMBRE_PLATILLO_CORTO)
        if (len(nombre_platillo) > 100):
            return api_response(STATUS_CODE_400,{},ERROR,DESCRIPCION_PLATILLO_LARGO)        
        if (len(descripcion) > 350):
            return api_response(STATUS_CODE_400,{},ERROR,DESCRIPCION_PLATILLO_LARGO)
        if not descripcion or not descripcion.strip():
            return api_response(STATUS_CODE_400,{},ERROR,DESCRIPCION_PLATILLO_CORTO)
        if not (precio > 1):
            return api_response(STATUS_CODE_400,{},ERROR,PRECIO_MAX)

        #Validamos imagen
        nombre_archivo_guardado = FileTools.guardar_imagen(foto, UPLOAD_FOLDER)
        if not nombre_archivo_guardado:
            return api_response(STATUS_CODE_400, {}, ERROR, IMAGEN_ERROR)
        
        # Construimos la URL relativa que se guardará en la BD para el Frontend        
        imagen_url_db = f"/uploads/platillos/{nombre_archivo_guardado}"

        nuevo_platillo = CtlPlatillos(
            nombre=nombre_platillo,
            precio=precio,
            categoria_platillo_fk = int(data["categoria_platillo_fk"]),
            descripcion=descripcion,
            imagen_url=imagen_url_db
        )
        
        # Creamos nuevo platillo
        db.session.add(nuevo_platillo)
        db.session.commit()

        LOG.info(f"# Exito Nuevo Platillo Creado: {nuevo_platillo}")
        
        return api_response(STATUS_CODE_201,{},SUCCESS,PLATILLO_SUCCESS)
    
    except SQLAlchemyError as e: 
        db.session.rollback()
        if 'nombre_archivo_guardado' in locals() and nombre_archivo_guardado:
            FileTools.elimina_archivo(UPLOAD_FOLDER, nombre_archivo_guardado)

        LOG.error(f"DB error en listar_platillos: {str(e)}")
        raise DatabaseError("Error al consultar la base de datos")
    except ValueError as e: 
        LOG.warning(f"Parámetro inválido: {str(e)}")
        raise UnexpectedError("Parámetros de búsqueda inválidos")
    except Exception as e:  
        error_trace = traceback.format_exc()
        LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
        raise UnexpectedError("Ocurrió un error inesperado")
    

@menu_bp.route("/platillos/<int:id_platillo>", methods=["PUT"])
def editar_platillo(id_platillo):
    try:
        data = request.form
        # Buscamos si existe el platillo
        platillo = db.session.get(CtlPlatillos, id_platillo)

        if not platillo:
            return api_response(STATUS_CODE_404, {}, ERROR, REGISTRO_NO_EXISTE)
        
        campos_requeridos = ["nombre", "precio", "categoria_platillo_fk", "descripcion"]
        
        campos_faltantes = [
            campo for campo in campos_requeridos 
            if campo not in data or data[campo] is None or str(data[campo]).strip() == ""
        ]

        if campos_faltantes:
            return api_response(STATUS_CODE_400, {}, ERROR, CAMPOS_REQUERIDOS)

        nombre_platillo = data.get("nombre")
        descripcion = data.get("descripcion")
        precio_raw = data.get("precio")

        # Validaciones 
        try:
            precio = float(precio_raw)
        except ValueError:
            return api_response(STATUS_CODE_400, {}, ERROR, PRECIO_ERROR)

        if not nombre_platillo or not nombre_platillo.strip():
            return api_response(STATUS_CODE_400, {}, ERROR, NOMBRE_PLATILLO_CORTO)
        if len(nombre_platillo) > 100:
            return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_LARGO)        
        if len(descripcion) > 350:
            return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_LARGO)
        if not descripcion or not descripcion.strip():
            return api_response(STATUS_CODE_400, {}, ERROR, DESCRIPCION_PLATILLO_CORTO)
        if not (precio > 1):
            return api_response(STATUS_CODE_400, {}, ERROR, PRECIO_MAX)

        # validacion imagen
        imagen_url_db = platillo.imagen_url 
        archivo_viejo_a_eliminar = None

        if 'imagen' in request.files:
            foto = request.files['imagen']
            if foto and foto.filename != '':
                # Guardamos la nueva imagen 
                nombre_archivo_guardado = FileTools.guardar_imagen(foto, UPLOAD_FOLDER)
                if not nombre_archivo_guardado:
                    return api_response(STATUS_CODE_400, {}, ERROR, IMAGEN_ERROR)
                
                # Guardamos la referencia de la foto vieja para borrarla del disco SOLO si la BD hace commit con éxito
                if platillo.imagen_url:
                    archivo_viejo_a_eliminar = platillo.imagen_url.split('/')[-1]

                # Nueva URL para la BD
                imagen_url_db = f"/uploads/platillos/{nombre_archivo_guardado}"

        # Actualización de datos en el modelo
        platillo.nombre = nombre_platillo
        platillo.precio = precio
        platillo.categoria_platillo_fk = int(data["categoria_platillo_fk"])
        platillo.descripcion = descripcion
        platillo.imagen_url = imagen_url_db

        db.session.commit()

        # Limpieza del disco duro (solo si el commit fue exitoso)
        if archivo_viejo_a_eliminar:
            try:
                FileTools.elimina_archivo(UPLOAD_FOLDER, archivo_viejo_a_eliminar)
                LOG.info(f"Archivo viejo eliminado con éxito: {archivo_viejo_a_eliminar}")
            except Exception as file_err:
                LOG.warning(f"No se pudo eliminar el archivo físico viejo {archivo_viejo_a_eliminar}: {str(file_err)}")

        LOG.info(f"# Platillo Editado con éxito ID {id_platillo}: {platillo}")
        return api_response(STATUS_CODE_200, {}, SUCCESS, PLATILLO_SUCCESS_UPDATED)
    
    except SQLAlchemyError as e: 
        db.session.rollback()        
        if 'nombre_archivo_guardado' in locals() and nombre_archivo_guardado:
            FileTools.elimina_archivo(UPLOAD_FOLDER, nombre_archivo_guardado)
            
        LOG.error(f"DB error en editar_platillo: {str(e)}")
        raise DatabaseError("Error al actualizar la base de datos")
    except Exception as e:  
        error_trace = traceback.format_exc()
        LOG.error(f"Error inesperado en editar_platillo: {str(e)} | Trace: {error_trace}")
        raise UnexpectedError("Ocurrió un error inesperado")

@menu_bp.route("/platillos/<int:id_platillo>", methods=["DELETE"])
def eliminar_platillo(id_platillo):
    try:
        platillo = db.session.get(CtlPlatillos, id_platillo)      
        
        if not platillo:
            LOG.info(f"DELETE /menu/{id_platillo} - {ERROR_EMPTY}")            
            return api_response(STATUS_CODE_404,None,ERROR,ERROR_EMPTY)

        platillo.activo = 0
        db.session.commit()
        LOG.info(f"DELETE /menu/{id_platillo} - Platillo marcado como inactivo")
        return api_response(STATUS_CODE_200, {},SUCCESS,PLATILLO_SUCCESS_DELETED)
    
    except SQLAlchemyError as e: 
        db.session.rollback()            
        LOG.error(f"DB error en eliminar_platillo: {str(e)}")
        raise DatabaseError("Error al consultar la base de datos")
    except ValueError as e: 
        LOG.warning(f"Parámetro inválido: {str(e)}")
        raise UnexpectedError("Parámetros de búsqueda inválidos")
    except Exception as e:  
        error_trace = traceback.format_exc()
        LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
        raise UnexpectedError("Ocurrió un error inesperado")    



# # ─────────────────────────────────────────────────────────────────────────────
# # RUTAS DE ADMINISTRADOR (requieren JWT)
# # ─────────────────────────────────────────────────────────────────────────────

# @menu_bp.route("/admin/celulares", methods=["GET"])
# @jwt_required()
# def admin_listar_platillos():
#     """
#     GET /api/admin/celulares
#     Lista TODOS los equipos (activos e inactivos) para la tabla del panel admin.
#     """
#     try:
#         celulares = Celular.query.order_by(Celular.created_at.desc()).all()
#         return api_response(200, [c.to_dict() for c in celulares])
#     except SQLAlchemyError as e:
#         LOG.error(f"DB error en admin_listar_platillos: {str(e)}")
#         raise DatabaseError("Error al obtener los equipos")


# @menu_bp.route("/admin/celulares", methods=["POST"])
# @jwt_required()
# def admin_crear_celular():
#     """
#     POST /api/admin/celulares
#     Crea un nuevo equipo celular. Las imágenes se suben por separado.
#     Body JSON requerido:
#     {
#         "marca": "Samsung",
#         "nombre": "Galaxy S24",
#         "almacenamiento_gb": 256,
#         "precio": 12999.00,
#         "bateria_porcentaje": 90,
#         "estado_id": 1
#     }
#     """
#     try:
#         data = request.get_json()

#         campos_requeridos = ["marca", "nombre", "almacenamiento_gb", "precio", "bateria_porcentaje", "estado_id"]
#         faltantes = [c for c in campos_requeridos if not data.get(c)]
#         if faltantes:
#             raise MissingValueError(f"Campos requeridos faltantes: {', '.join(faltantes)}")

#         # Validar que el estado exista
#         estado = EstadoEquipo.query.get(data["estado_id"])
#         if not estado:
#             raise NotFoundError(f"Estado con id {data['estado_id']} no existe")

#         # Validar rango de batería
#         bateria = int(data["bateria_porcentaje"])
#         if not (0 <= bateria <= 100):
#             raise MissingValueError("bateria_porcentaje debe ser un valor entre 0 y 100")

#         nuevo = Celular(
#             marca              = data["marca"].strip(),
#             nombre             = data["nombre"].strip(),
#             almacenamiento_gb  = int(data["almacenamiento_gb"]),
#             precio             = float(data["precio"]),
#             bateria_porcentaje = bateria,
#             estado_id          = data["estado_id"],
#             activo             = data.get("activo", True),
#         )

#         db.session.add(nuevo)
#         db.session.commit()

#         LOG.info(f"Celular creado: {nuevo.marca} {nuevo.nombre} (id={nuevo.id})")
#         return api_response(201, nuevo.to_dict())

#     except (MissingValueError, NotFoundError):
#         raise
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         LOG.error(f"DB error en admin_crear_celular: {str(e)}")
#         raise DatabaseError("Error al crear el equipo")


# @menu_bp.route("/admin/celulares/<int:celular_id>", methods=["PUT"])
# @jwt_required()
# def admin_editar_celular(celular_id):
#     """
#     PUT /api/admin/celulares/<id>
#     Actualiza los datos de un equipo existente.
#     """
#     try:
#         celular = Celular.query.get(celular_id)
#         if not celular:
#             raise NotFoundError(f"Equipo con id {celular_id} no encontrado")

#         data = request.get_json()

#         # Actualiza solo los campos que vengan en el body
#         if "marca"              in data: celular.marca              = data["marca"].strip()
#         if "nombre"             in data: celular.nombre             = data["nombre"].strip()
#         if "almacenamiento_gb"  in data: celular.almacenamiento_gb  = int(data["almacenamiento_gb"])
#         if "precio"             in data: celular.precio             = float(data["precio"])
#         if "activo"             in data: celular.activo             = bool(data["activo"])

#         if "bateria_porcentaje" in data:
#             bateria = int(data["bateria_porcentaje"])
#             if not (0 <= bateria <= 100):
#                 raise MissingValueError("bateria_porcentaje debe ser un valor entre 0 y 100")
#             celular.bateria_porcentaje = bateria

#         if "estado_id" in data:
#             estado = EstadoEquipo.query.get(data["estado_id"])
#             if not estado:
#                 raise NotFoundError(f"Estado con id {data['estado_id']} no existe")
#             celular.estado_id = data["estado_id"]

#         db.session.commit()
#         LOG.info(f"Celular actualizado id={celular_id}")
#         return api_response(200, celular.to_dict())

#     except (MissingValueError, NotFoundError):
#         raise
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         LOG.error(f"DB error en admin_editar_celular: {str(e)}")
#         raise DatabaseError("Error al actualizar el equipo")


# @menu_bp.route("/admin/celulares/<int:celular_id>", methods=["DELETE"])
# @jwt_required()
# def admin_eliminar_celular(celular_id):
#     """
#     DELETE /api/admin/celulares/<id>
#     Elimina un equipo y todas sus imágenes asociadas.
#     """
#     try:
#         celular = Celular.query.get(celular_id)
#         if not celular:
#             raise NotFoundError(f"Equipo con id {celular_id} no encontrado")

#         db.session.delete(celular)   # cascade elimina también las imágenes
#         db.session.commit()

#         LOG.info(f"Celular eliminado id={celular_id}")
#         return api_response(200, {"mensaje": f"Equipo {celular_id} eliminado correctamente"})

#     except NotFoundError:
#         raise
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         LOG.error(f"DB error en admin_eliminar_celular: {str(e)}")
#         raise DatabaseError("Error al eliminar el equipo")
