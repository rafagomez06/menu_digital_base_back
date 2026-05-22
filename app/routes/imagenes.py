import os
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from app.main import db
from app.utils.response import api_response
from app.utils.RaiseException import (
    DatabaseError, MissingValueError, NotFoundError, FileUploadError
)
from app.utils.FileTools import FileTools
from app.utils.Logger import logger

LOG          = logger()
imagenes_bp  = Blueprint("imagenes", __name__)

MAX_IMAGENES = 5


@imagenes_bp.route("/celulares/<int:celular_id>/imagenes", methods=["POST"])
@jwt_required()
def subir_imagenes(celular_id):
    """
    POST /api/admin/celulares/<id>/imagenes
    Sube una o más imágenes para un equipo. Máximo 5 en total.
    Recibe multipart/form-data con campo 'imagenes' (puede ser múltiple).
    """
    try:
        celular = Celular.query.get(celular_id)
        if not celular:
            raise NotFoundError(f"Equipo con id {celular_id} no encontrado")

        archivos = request.files.getlist("imagenes")
        if not archivos or all(f.filename == "" for f in archivos):
            raise MissingValueError("No se recibieron imágenes")

        # Verificar que no se supere el límite de 5 imágenes
        total_actuales = CelularImagen.query.filter_by(celular_id=celular_id).count()
        if total_actuales + len(archivos) > MAX_IMAGENES:
            raise MissingValueError(
                f"El equipo ya tiene {total_actuales} imágenes. "
                f"Solo se permiten {MAX_IMAGENES} en total."
            )

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        imagenes_guardadas = []

        for archivo in archivos:
            nombre_guardado = FileTools.guardar_imagen(archivo, upload_folder)
            if not nombre_guardado:
                raise FileUploadError(f"No se pudo guardar: {archivo.filename}. Verifica que sea JPG, PNG o WebP.")

            # Determinar el siguiente número de orden
            ultimo_orden = (
                db.session.query(db.func.max(CelularImagen.orden))
                .filter_by(celular_id=celular_id)
                .scalar() or 0
            )

            imagen = CelularImagen(
                celular_id = celular_id,
                url        = f"/static/uploads/{nombre_guardado}",
                orden      = ultimo_orden + 1,
            )
            db.session.add(imagen)
            imagenes_guardadas.append(imagen)

        db.session.commit()
        LOG.info(f"{len(imagenes_guardadas)} imagen(es) subida(s) para celular id={celular_id}")

        return api_response(201, [img.to_dict() for img in imagenes_guardadas])

    except (NotFoundError, MissingValueError, FileUploadError):
        raise
    except SQLAlchemyError as e:
        db.session.rollback()
        LOG.error(f"DB error en subir_imagenes: {str(e)}")
        raise DatabaseError("Error al guardar las imágenes")


@imagenes_bp.route("/celulares/<int:celular_id>/imagenes/<int:imagen_id>", methods=["DELETE"])
@jwt_required()
def eliminar_imagen(celular_id, imagen_id):
    """
    DELETE /api/admin/celulares/<celular_id>/imagenes/<imagen_id>
    Elimina una imagen específica de un equipo del disco y de la BD.
    """
    try:
        imagen = CelularImagen.query.filter_by(
            id=imagen_id, celular_id=celular_id
        ).first()

        if not imagen:
            raise NotFoundError(f"Imagen {imagen_id} no encontrada para el equipo {celular_id}")

        # Eliminar el archivo físico del disco
        upload_folder  = current_app.config["UPLOAD_FOLDER"]
        nombre_archivo = imagen.url.split("/")[-1]
        FileTools.elimina_archivo(upload_folder, nombre_archivo)

        db.session.delete(imagen)
        db.session.commit()

        LOG.info(f"Imagen id={imagen_id} eliminada del equipo id={celular_id}")
        return api_response(200, {"mensaje": f"Imagen {imagen_id} eliminada correctamente"})

    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.session.rollback()
        LOG.error(f"DB error en eliminar_imagen: {str(e)}")
        raise DatabaseError("Error al eliminar la imagen")
