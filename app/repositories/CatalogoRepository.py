
from app.main import db
from app.models.CatalogoModel import CatCategoriasPlatillos
from sqlalchemy.exc import SQLAlchemyError
from app.utils.RaiseException import ( DatabaseError,  UnexpectedError)
from app.utils.FileTools import FileTools  
from app.utils.Messages import *
from app.main import db
from app.utils.Logger import logger
LOG = logger()

class CatalogoRepository:
    @staticmethod
    def obtener_categorias_activas():
        try:
            # Obtenemos platillos activos
            query = CatCategoriasPlatillos.query.filter(CatCategoriasPlatillos.activo == 1)                        
            return query.order_by(CatCategoriasPlatillos.id_categoria.asc()).all()
        except SQLAlchemyError as e: 
            LOG.error(f"DB error en obtener_categorias_activas: {str(e)}")
            raise DatabaseError("Error al consultar la base de datos")