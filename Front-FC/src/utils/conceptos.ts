/**
 * Utilidades para el manejo de conceptos auto-calculados
 */

/**
 * Determina si un concepto debe estar deshabilitado por ser auto-calculado
 * @param conceptoId ID del concepto a verificar
 * @returns true si el concepto es auto-calculado y no debe ser editable
 */
export const esConceptoAutoCalculado = (conceptoId: number | undefined): boolean => {
  if (!conceptoId) return false;
  
  // Lista de conceptos que se auto-calculan y no deben ser editables manualmente
  const conceptosAutoCalculados = [
    2,  // CONSUMO (auto-calculado desde SUBTOTAL MOVIMIENTO PAGADURIA)
    52, // DIFERENCIA SALDOS
    54, // SALDO DIA ANTERIOR
    82, // SUBTOTAL MOVIMIENTO PAGADURIA
    83, // SUBTOTAL SALDO INICIAL PAGADURIA
    84, // MOVIMIENTO TESORERIA
    85  // SALDO TOTAL EN BANCOS
  ];
  
  return conceptosAutoCalculados.includes(conceptoId);
};

/**
 * Alias para compatibilidad con código existente
 */
export const isConceptoAutoCalculado = esConceptoAutoCalculado;
