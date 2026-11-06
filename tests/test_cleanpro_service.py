from unittest.mock import Mock

import pytest

from src.cleanpro import (
    CotizacionFormal,
    OrdenDeServicio,
    RequiereAutorizacionGerencia,
    ServicioCotizacion,
    ServicioEjecucion,
    ServicioSinFirma,
)


def test_mock01_descuento_sin_autorizacion_notifica_a_gerencia():
    notificador = Mock()
    cotizacion = CotizacionFormal("C-010", 100, 1000)
    with pytest.raises(RequiereAutorizacionGerencia):
        ServicioCotizacion(notificador).aplicar_descuento(cotizacion, 15)
    notificador.notificar_solicitud.assert_called_once_with("C-010")
    assert cotizacion.estado == "PENDIENTE_AUTORIZACION"


def test_mock02_descuento_autorizado_no_notifica_a_gerencia():
    notificador = Mock()
    cotizacion = CotizacionFormal("C-011", 100, 1000)
    ServicioCotizacion(notificador).aplicar_descuento(cotizacion, 15, autorizado_por_gerencia=True)
    notificador.notificar_solicitud.assert_not_called()
    assert cotizacion.descuento_porcentaje == 15


def test_mock03_cierre_con_firma_emite_factura():
    facturador = Mock()
    orden = OrdenDeServicio("OS-010")
    ServicioEjecucion(facturador).cerrar_servicio(orden, "Cliente Demo")
    facturador.emitir.assert_called_once_with("OS-010")
    assert orden.estado == "CERRADO"


def test_mock04_cierre_sin_firma_no_emite_factura():
    facturador = Mock()
    orden = OrdenDeServicio("OS-011")
    with pytest.raises(ServicioSinFirma):
        ServicioEjecucion(facturador).cerrar_servicio(orden, "")
    facturador.emitir.assert_not_called()
