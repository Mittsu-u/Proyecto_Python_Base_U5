from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.cleanpro import CotizacionFormal
from src.cleanpro_repository import SqlCotizacionRepository, make_cleanpro_engine


def test_pers01_guardar_y_recuperar_cotizacion_con_commit():
    engine = make_cleanpro_engine()
    with Session(engine) as session:
        cotizacion = CotizacionFormal("C-020", 120, 2500)
        cotizacion.aplicar_descuento(5)
        SqlCotizacionRepository(session).save(cotizacion)
        session.commit()
    with Session(engine) as session:
        guardada = SqlCotizacionRepository(session).get("C-020")
        assert guardada is not None
        assert guardada.monto_final == Decimal(2375)
        assert guardada.estado == "COTIZADA"


def test_pers02_rollback_descarta_la_cotizacion():
    engine = make_cleanpro_engine()
    with Session(engine) as session:
        repo = SqlCotizacionRepository(session)
        repo.save(CotizacionFormal("C-021", 100, 1000))
        session.rollback()
        assert repo.get("C-021") is None


def test_pers03_folio_duplicado_viola_unicidad():
    engine = make_cleanpro_engine()
    with Session(engine) as session:
        SqlCotizacionRepository(session).save(CotizacionFormal("C-022", 100, 1000))
        session.commit()
    with Session(engine) as session:
        SqlCotizacionRepository(session).save(CotizacionFormal("C-022", 50, 500))
        with pytest.raises(IntegrityError):
            session.commit()
