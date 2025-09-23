import { apiService } from './apiService';

export interface InformeConsolidadoResponse {
  periodo: {
    año: number;
    mes: number;
    fecha_inicio: string;
    fecha_fin: string;
    nombre_mes: string;
  };
  metadata: {
    total_transacciones: number;
    companias: Array<{ id: number; nombre: string }>;
    cuentas: Array<{ id: number; numero_cuenta: string; banco: string | null }>;
    conceptos_tesoreria: Array<{ id: number; nombre: string }>;
    conceptos_pagaduria: Array<{ id: number; nombre: string }>;
  };
  datos: {
    tesoreria: { [conceptoId: number]: { [companiaId: number]: { [cuentaId: number]: number } } };
    pagaduria: { [conceptoId: number]: { [companiaId: number]: { [cuentaId: number]: number } } };
  };
}

export interface ResumenMensualResponse {
  periodo: {
    año: number;
    mes: number;
    nombre_mes: string;
  };
  metricas: {
    total_ingresos: number;
    total_gastos: number;
    balance_neto: number;
    tasa_ahorro: number;
    total_transacciones: number;
  };
}

class InformesConsolidadosService {
  private baseUrl = '/api/v1/informes-consolidados';

  /**
   * Obtiene informe consolidado mensual
   */
  async obtenerInformeConsolidadoMensual(año: number, mes: number): Promise<InformeConsolidadoResponse> {
    try {
      console.log(`🔍 Obteniendo informe consolidado mensual: ${año}-${mes.toString().padStart(2, '0')}`);
      
      const response = await apiService.get<InformeConsolidadoResponse>(
        `${this.baseUrl}/mensual?año=${año}&mes=${mes}`
      );
      
      console.log(`✅ Informe consolidado obtenido: ${response.metadata.total_transacciones} transacciones`);
      return response;
    } catch (error) {
      console.error('❌ Error al obtener informe consolidado mensual:', error);
      throw error;
    }
  }

  /**
   * Obtiene resumen de métricas mensuales
   */
  async obtenerResumenMensual(año: number, mes: number): Promise<ResumenMensualResponse> {
    try {
      console.log(`🔍 Obteniendo resumen mensual: ${año}-${mes.toString().padStart(2, '0')}`);
      
      const response = await apiService.get<ResumenMensualResponse>(
        `${this.baseUrl}/resumen-mensual?año=${año}&mes=${mes}`
      );
      
      console.log(`✅ Resumen mensual obtenido: ${response.metricas.total_transacciones} transacciones`);
      return response;
    } catch (error) {
      console.error('❌ Error al obtener resumen mensual:', error);
      throw error;
    }
  }

  /**
   * Formatea monto como moneda
   */
  formatearMoneda(monto: number): string {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(monto);
  }

  /**
   * Obtiene color para el tipo de transacción
   */
  obtenerColorMonto(monto: number): string {
    if (monto > 0) return 'text-green-600';
    if (monto < 0) return 'text-red-600';
    return 'text-gray-500';
  }

  /**
   * Calcula total por concepto para todas las compañías y cuentas
   */
  calcularTotalConcepto(
    datosConcepto: { [companiaId: number]: { [cuentaId: number]: number } }
  ): number {
    let total = 0;
    
    for (const companiaId in datosConcepto) {
      for (const cuentaId in datosConcepto[companiaId]) {
        total += datosConcepto[companiaId][cuentaId];
      }
    }
    
    return total;
  }

  /**
   * Calcula total por compañía (todas las cuentas de esa compañía)
   */
  calcularTotalCompania(
    datos: { [conceptoId: number]: { [companiaId: number]: { [cuentaId: number]: number } } },
    companiaId: number
  ): number {
    let total = 0;
    
    for (const conceptoId in datos) {
      if (datos[conceptoId][companiaId]) {
        for (const cuentaId in datos[conceptoId][companiaId]) {
          total += datos[conceptoId][companiaId][cuentaId];
        }
      }
    }
    
    return total;
  }

  /**
   * Obtiene valor específico para compañía, concepto y cuenta
   */
  obtenerMontoEspecifico(
    datos: { [conceptoId: number]: { [companiaId: number]: { [cuentaId: number]: number } } },
    conceptoId: number,
    companiaId: number,
    cuentaId: number
  ): number {
    return datos[conceptoId]?.[companiaId]?.[cuentaId] || 0;
  }
}

export const informesConsolidadosService = new InformesConsolidadosService();