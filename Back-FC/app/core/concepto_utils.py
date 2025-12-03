"""
Utilidades para conceptos de flujo de caja
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.conceptos_flujo_caja import ConceptoFlujoCaja

def es_concepto_auto_calculado(concepto: "ConceptoFlujoCaja") -> bool:
    """
    Determina si un concepto es auto-calculado basándose en sus características.
    
    Un concepto es considerado auto-calculado si:
    - Tiene dependencias definidas (depende_de_concepto_id, tipo_dependencia, formula_dependencia)
    - Es uno de los conceptos especiales conocidos (SUB-TOTAL, SALDO FINAL, etc.)
    
    Args:
        concepto: Instancia del modelo ConceptoFlujoCaja
        
    Returns:
        bool: True si el concepto es auto-calculado, False en caso contrario
    """
    if not concepto:
        return False
    
    # Conceptos que sabemos que son auto-calculados por nombre
    conceptos_auto_calculados = {
        'SUB-TOTAL TESORERÍA',
        'SALDO FINAL CUENTAS', 
        'SALDO NETO INICIAL PAGADURÍA',
        'MOVIMIENTO TESORERÍA',
        'SALDO INICIAL'  # Puede ser auto-calculado desde día anterior
    }
    
    # Verificar por nombre
    if concepto.nombre in conceptos_auto_calculados:
        return True
    
    # Verificar por dependencias
    if (concepto.depende_de_concepto_id is not None or 
        concepto.tipo_dependencia is not None or 
        concepto.formula_dependencia is not None):
        return True
    
    return False

def es_concepto_editable(concepto: "ConceptoFlujoCaja") -> bool:
    """
    Determina si un concepto puede ser editado manualmente.
    
    Args:
        concepto: Instancia del modelo ConceptoFlujoCaja
        
    Returns:
        bool: True si el concepto es editable, False en caso contrario
    """
    return not es_concepto_auto_calculado(concepto)

def obtener_conceptos_editables_por_area(conceptos: list["ConceptoFlujoCaja"], area: str) -> list["ConceptoFlujoCaja"]:
    """
    Filtra conceptos editables por área específica.
    
    Args:
        conceptos: Lista de conceptos
        area: Área a filtrar ('tesoreria', 'pagaduria', 'ambas')
        
    Returns:
        list: Lista de conceptos editables del área especificada
    """
    return [
        concepto for concepto in conceptos
        if (concepto.area.value == area or concepto.area.value == 'ambas') 
        and es_concepto_editable(concepto)
        and concepto.activo
    ]