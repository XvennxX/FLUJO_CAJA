/**
 * Servicio para manejar SALDOS INICIALES automáticos
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface SaldoInicialRequest {
  fecha: string; // YYYY-MM-DD
  cuenta_id?: number;
  compania_id?: number;
}

export interface SaldoInicialResponse {
  success: boolean;
  message: string;
  transacciones_creadas: number;
  transacciones: any[];
}

export interface SaldoFinalDiaAnteriorResponse {
  success: boolean;
  fecha_anterior: string;
  fecha_actual: string;
  saldo_final_dia_anterior: number;
  cuenta_id?: number;
}

export class SaldoInicialService {
  
  /**
   * Calcula y guarda automáticamente el SALDO INICIAL para una fecha específica
   */
  static async calcularSaldoInicial(request: SaldoInicialRequest): Promise<SaldoInicialResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/saldo-inicial/calcular-saldo-inicial`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error calculando SALDO INICIAL:', error);
      throw error;
    }
  }

  /**
   * Obtiene el SALDO FINAL del día anterior (preview)
   */
  static async obtenerSaldoFinalDiaAnterior(
    fecha: string,
    cuenta_id?: number
  ): Promise<SaldoFinalDiaAnteriorResponse> {
    try {
      const params = new URLSearchParams({ fecha });
      if (cuenta_id) {
        params.append('cuenta_id', cuenta_id.toString());
      }

      const response = await fetch(`${API_BASE_URL}/saldo-inicial/saldo-final-dia-anterior?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error obteniendo saldo final día anterior:', error);
      throw error;
    }
  }

  /**
   * Procesa automáticamente todos los SALDOS INICIALES para una fecha
   */
  static async autoProcesarSaldosIniciales(
    fecha: string,
    compania_id?: number
  ): Promise<any> {
    try {
      const params = new URLSearchParams({ fecha });
      if (compania_id) {
        params.append('compania_id', compania_id.toString());
      }

      const response = await fetch(`${API_BASE_URL}/saldo-inicial/auto-procesar-saldos-iniciales?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error en procesamiento automático:', error);
      throw error;
    }
  }

  /**
   * Procesa los SALDOS INICIALES para la fecha actual y todas las cuentas
   */
  static async procesarSaldosInicialesToday(compania_id?: number): Promise<SaldoInicialResponse> {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    
    return this.calcularSaldoInicial({
      fecha: today,
      compania_id
    });
  }

  /**
   * Verifica si es necesario procesar SALDOS INICIALES para una fecha
   */
  static async verificarNecesidadSaldosIniciales(
    fecha: string,
    compania_id?: number
  ): Promise<any> {
    try {
      const params = new URLSearchParams();
      if (compania_id) {
        params.append('compania_id', compania_id.toString());
      }

      const queryString = params.toString() ? `?${params}` : '';
      const response = await fetch(`${API_BASE_URL}/saldo-inicial/verificar-necesidad/${fecha}${queryString}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error verificando necesidad de SALDOS INICIALES:', error);
      throw error;
    }
  }

  /**
   * Verifica si necesita procesar SALDOS INICIALES para una fecha
   */
  static async verificarSaldosIniciales(_fecha: string): Promise<boolean> {
    try {
      // Verificar si ya existen transacciones de SALDO INICIAL para esta fecha
      // Esto se puede implementar consultando las transacciones existentes
      
      // Por ahora, siempre devolver true para que se puedan recalcular
      return true;
    } catch (error) {
      console.error('Error verificando SALDOS INICIALES:', error);
      return false;
    }
  }
}
