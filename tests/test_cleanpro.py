from decimal import Decimal

import pytest

from src.cleanpro import (
    CotizacionFormal,
    MontoInvalido,
    OrdenDeServicio,
    RequiereAutorizacionGerencia,
    ServicioSinFirma,
    SuperficieInvalida,
    calcular_penalizacion,
)


# ---- Regla A: descuento mayor al 10% requiere gerencia (RN-01) ----
def test_cp01_descuento_5_se_aplica_sin_autorizacion():
    cotizacion = CotizacionFormal("C-001", 100, 1000)
    cotizacion.aplicar_descuento(5)
    assert cotizacion.monto_final == Decimal(950)


def test_cp02_descuento_15_con_autorizacion_de_gerencia_se_aplica():
    cotizacion = CotizacionFormal("C-002", 100, 1000)
    cotizacion.aplicar_descuento(15, autorizado_por_gerencia=True)
    assert cotizacion.monto_final == Decimal(850)


def test_cp03_descuento_15_sin_autorizacion_se_rechaza():
    cotizacion = CotizacionFormal("C-003", 100, 1000)
    with pytest.raises(RequiereAutorizacionGerencia):
        cotizacion.aplicar_descuento(15)
    assert cotizacion.monto_final == Decimal(1000)


def test_cp04_limite_descuento_exactamente_10_se_aplica_sin_autorizacion():
    cotizacion = CotizacionFormal("C-004", 100, 1000)
    cotizacion.aplicar_descuento(10)
    assert cotizacion.monto_final == Decimal(900)


# ---- Regla B: autorizacion por superficie (>300 m2) o monto (>$8,000) ----
def test_cp05_cotizacion_pequena_no_requiere_autorizacion():
    assert not CotizacionFormal("C-005", 150, 3000).requiere_autorizacion_gerencia()


def test_cp06_limite_300_m2_y_8000_exactos_no_requieren_autorizacion():
    assert not CotizacionFormal("C-006", 300, 8000).requiere_autorizacion_gerencia()


@pytest.mark.parametrize("superficie, monto", [(301, 1000), (100, "8000.01")])
def test_cp07_limite_justo_por_encima_requiere_autorizacion(superficie, monto):
    assert CotizacionFormal("C-007", superficie, monto).requiere_autorizacion_gerencia()


@pytest.mark.parametrize("superficie", [0, -10])
def test_cp08_superficie_invalida_se_rechaza(superficie):
    with pytest.raises(SuperficieInvalida):
        CotizacionFormal("C-008", superficie, 1000)


# ---- Regla C: penalizaciones (RN-04, RN-05) y cierre con firma ----
def test_cp09_acceso_denegado_penaliza_100_por_ciento():
    assert calcular_penalizacion(1200, "ACCESO_DENEGADO") == Decimal(1200)


def test_cp10_cancelacion_tardia_penaliza_50_por_ciento():
    assert calcular_penalizacion(1200, "CANCELACION_TARDIA") == Decimal(600)


@pytest.mark.parametrize("firma", ["", "   ", None])
def test_cp11_cerrar_servicio_sin_firma_se_rechaza(firma):
    orden = OrdenDeServicio("OS-001")
    with pytest.raises(ServicioSinFirma):
        orden.cerrar(firma)
    assert orden.estado == "EN_EJECUCION"


def test_cp12_penalizacion_con_monto_negativo_se_rechaza():
    with pytest.raises(MontoInvalido):
        calcular_penalizacion(-100, "ACCESO_DENEGADO")


# ---- Complementarias ----
def test_comp01_cerrar_servicio_con_firma_cambia_estado():
    orden = OrdenDeServicio("OS-002")
    orden.cerrar("Cliente Demo")
    assert orden.estado == "CERRADO"
    assert orden.firma == "Cliente Demo"


def test_comp02_penalizacion_con_motivo_desconocido_se_rechaza():
    with pytest.raises(ValueError):
        calcular_penalizacion(1200, "OTRO")
