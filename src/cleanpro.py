"""Dominio de CleanPro (PIA): cotizaciones, penalizaciones y cierre de servicio.

Reglas tomadas de la Actividad 3 (arquitectura de CleanPro):
- RN-01: un descuento mayor al 10% requiere autorizacion de gerencia.
- Inmuebles mayores a 300 m2 o cobros mayores a $8,000 requieren autorizacion.
- RN-04 / RN-05: cancelacion tardia penaliza 50%; acceso denegado penaliza 100%.
- Un servicio no puede cerrarse sin la firma del cliente.
"""

from dataclasses import dataclass
from decimal import Decimal

DESCUENTO_MAX_SIN_AUTORIZACION = Decimal(10)
SUPERFICIE_MAX_SIN_AUTORIZACION = Decimal(300)
MONTO_MAX_SIN_AUTORIZACION = Decimal(8000)
TASAS_PENALIZACION = {
    "CANCELACION_TARDIA": Decimal("0.50"),
    "ACCESO_DENEGADO": Decimal("1.00"),
}
CENTAVOS = Decimal("0.01")


class CleanProError(Exception):
    """Error base del dominio de CleanPro."""


class SuperficieInvalida(CleanProError):
    pass


class MontoInvalido(CleanProError):
    pass


class RequiereAutorizacionGerencia(CleanProError):
    pass


class ServicioSinFirma(CleanProError):
    pass


def _decimal(valor):
    return Decimal(str(valor))


@dataclass(frozen=True)
class Superficie:
    metros: Decimal

    def __post_init__(self):
        object.__setattr__(self, "metros", _decimal(self.metros))
        if self.metros <= 0:
            raise SuperficieInvalida("la superficie debe ser mayor a 0")


@dataclass(frozen=True)
class Dinero:
    cantidad: Decimal

    def __post_init__(self):
        object.__setattr__(self, "cantidad", _decimal(self.cantidad))
        if self.cantidad < 0:
            raise MontoInvalido("el monto no puede ser negativo")


class CotizacionFormal:
    def __init__(self, folio, superficie_m2, monto):
        self.folio = folio
        self.superficie = Superficie(superficie_m2)
        self.monto = Dinero(monto)
        self.descuento_porcentaje = Decimal(0)
        self.estado = "COTIZADA"

    @property
    def monto_final(self):
        factor = (Decimal(100) - self.descuento_porcentaje) / Decimal(100)
        return (self.monto.cantidad * factor).quantize(CENTAVOS)

    def requiere_autorizacion_gerencia(self):
        return (
            self.superficie.metros > SUPERFICIE_MAX_SIN_AUTORIZACION
            or self.monto.cantidad > MONTO_MAX_SIN_AUTORIZACION
        )

    def aplicar_descuento(self, porcentaje, autorizado_por_gerencia=False):
        porcentaje = _decimal(porcentaje)
        if porcentaje > DESCUENTO_MAX_SIN_AUTORIZACION and not autorizado_por_gerencia:
            raise RequiereAutorizacionGerencia(
                "descuento mayor al 10% requiere autorizacion de gerencia"
            )
        self.descuento_porcentaje = porcentaje

    def marcar_pendiente_autorizacion(self):
        self.estado = "PENDIENTE_AUTORIZACION"


def calcular_penalizacion(monto, motivo):
    dinero = Dinero(monto)
    if motivo not in TASAS_PENALIZACION:
        raise ValueError("motivo de penalizacion desconocido")
    return (dinero.cantidad * TASAS_PENALIZACION[motivo]).quantize(CENTAVOS)


class OrdenDeServicio:
    def __init__(self, folio):
        self.folio = folio
        self.estado = "EN_EJECUCION"
        self.firma = None

    def cerrar(self, firma):
        if not firma or not firma.strip():
            raise ServicioSinFirma("no se puede cerrar el servicio sin firma del cliente")
        self.firma = firma.strip()
        self.estado = "CERRADO"


class ServicioCotizacion:
    """Orquesta el caso de uso; las reglas viven en CotizacionFormal."""

    def __init__(self, notificador):
        self.notificador = notificador

    def aplicar_descuento(self, cotizacion, porcentaje, autorizado_por_gerencia=False):
        try:
            cotizacion.aplicar_descuento(porcentaje, autorizado_por_gerencia)
        except RequiereAutorizacionGerencia:
            cotizacion.marcar_pendiente_autorizacion()
            self.notificador.notificar_solicitud(cotizacion.folio)
            raise


class ServicioEjecucion:
    def __init__(self, facturador):
        self.facturador = facturador

    def cerrar_servicio(self, orden, firma):
        orden.cerrar(firma)
        self.facturador.emitir(orden.folio)
