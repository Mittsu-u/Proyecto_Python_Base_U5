from decimal import Decimal

from sqlalchemy import Float, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from src.cleanpro import CotizacionFormal


class Base(DeclarativeBase):
    pass


class CotizacionRow(Base):
    __tablename__ = "cotizaciones"

    folio: Mapped[str] = mapped_column(String, primary_key=True)
    superficie: Mapped[float] = mapped_column(Float)
    monto: Mapped[float] = mapped_column(Float)
    descuento: Mapped[float] = mapped_column(Float)
    estado: Mapped[str] = mapped_column(String)


def make_cleanpro_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


class SqlCotizacionRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, cotizacion):
        self.session.add(
            CotizacionRow(
                folio=cotizacion.folio,
                superficie=float(cotizacion.superficie.metros),
                monto=float(cotizacion.monto.cantidad),
                descuento=float(cotizacion.descuento_porcentaje),
                estado=cotizacion.estado,
            )
        )

    def get(self, folio):
        row = self.session.scalar(select(CotizacionRow).where(CotizacionRow.folio == folio))
        if row is None:
            return None
        cotizacion = CotizacionFormal(row.folio, row.superficie, row.monto)
        cotizacion.descuento_porcentaje = Decimal(str(row.descuento))
        cotizacion.estado = row.estado
        return cotizacion
