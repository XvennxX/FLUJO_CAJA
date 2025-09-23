/**
 * Servicio para manejar cuentas bancarias con múltiples monedas
 */

import { apiService } from './apiService';

export interface CuentaExpandida {
  id: number;
  cuenta_moneda_id: string;
  numero_cuenta: string;
  compania_id: number;
  banco_id: number;
  tipo_cuenta?: string;
  moneda: string;
  banco: {
    id: number;
    nombre: string;
  } | null;
  compania: {
    id: number;
    nombre: string;
  } | null;
  nombre_completo: string;
  nombre_display: string;
  trm?: {
    fecha: string;
    valor: number;
  };
}

export interface CuentasExpandidasResponse {
  cuentas: CuentaExpandida[];
  total_cuentas_originales: number;
  total_cuentas_expandidas: number;
  trm_actual?: {
    fecha: string;
    valor: number;
  };
}

export interface InformeMultiMonedaResponse {
  periodo: {
    año: number;
    mes: number;
    fecha_inicio: string;
    fecha_fin: string;
    nombre_mes: string;
  };
  conversion: {
    trm_promedio: number;
    fecha_trm: string;
  };
  metadata: {
    total_transacciones: number;
    cuentas_expandidas: number;
    companias: Array<{ id: number; nombre: string }>;
    conceptos_tesoreria: Array<{ id: number; nombre: string }>;
    conceptos_pagaduria: Array<{ id: number; nombre: string }>;
  };
  cuentas_expandidas: CuentaExpandida[];
  datos: {
    tesoreria: any;
    pagaduria: any;
  };
}

export const cuentasMultiMonedaService = {
  /**
   * Obtiene todas las cuentas bancarias expandidas por moneda
   */
  async obtenerCuentasExpandidas(incluirTrm: boolean = true): Promise<CuentasExpandidasResponse> {
    try {
      console.log('🔍 Obteniendo cuentas expandidas por moneda...');
      
      const queryParams = incluirTrm ? '?incluir_trm=true' : '?incluir_trm=false';
      const data = await apiService.get<CuentasExpandidasResponse>(`/api/v1/cuentas-multi-moneda/expandidas${queryParams}`);
      
      console.log('✅ Cuentas expandidas obtenidas:', data);
      return data;
    } catch (error) {
      console.error('❌ Error al obtener cuentas expandidas:', error);
      throw error;
    }
  },

  /**
   * Obtiene cuentas expandidas para una compañía específica
   */
  async obtenerCuentasExpandidasPorCompania(
    companiaId: number, 
    incluirTrm: boolean = true
  ): Promise<any> {
    try {
      console.log(`🔍 Obteniendo cuentas expandidas para compañía ${companiaId}...`);
      
      const queryParams = incluirTrm ? '?incluir_trm=true' : '?incluir_trm=false';
      const data = await apiService.get<any>(`/api/v1/cuentas-multi-moneda/por-compania/${companiaId}${queryParams}`);
      
      console.log('✅ Cuentas expandidas por compañía obtenidas:', data);
      return data;
    } catch (error) {
      console.error('❌ Error al obtener cuentas expandidas por compañía:', error);
      throw error;
    }
  },

  /**
   * Obtiene informe consolidado mensual con soporte multi-moneda
   */
  async obtenerInformeConsolidadoMultiMoneda(
    año: number, 
    mes: number
  ): Promise<InformeMultiMonedaResponse> {
    try {
      console.log(`🔍 Obteniendo informe consolidado multi-moneda para ${mes}/${año}...`);
      
      const data = await apiService.get<InformeMultiMonedaResponse>(`/api/v1/informes-consolidados/mensual-multi-moneda?año=${año}&mes=${mes}`);
      
      console.log('✅ Informe consolidado multi-moneda obtenido:', data);
      return data;
    } catch (error) {
      console.error('❌ Error al obtener informe consolidado multi-moneda:', error);
      throw error;
    }
  },

  /**
   * Convierte un monto de USD a COP usando la TRM
   */
  convertirUsdACop(montoUsd: number, trm: number): number {
    return montoUsd * trm;
  },

  /**
   * Convierte un monto de COP a USD usando la TRM
   */
  convertirCopAUsd(montoCop: number, trm: number): number {
    return montoCop / trm;
  },

  /**
   * Formatea un monto según la moneda
   */
  formatearMonto(monto: number, moneda: string): string {
    const opciones: Intl.NumberFormatOptions = {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    };

    if (moneda === 'USD') {
      return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD',
        ...opciones
      }).format(monto);
    } else if (moneda === 'COP') {
      return new Intl.NumberFormat('es-CO', { 
        style: 'currency', 
        currency: 'COP',
        ...opciones
      }).format(monto);
    } else {
      return new Intl.NumberFormat('es-CO', opciones).format(monto);
    }
  },

  /**
   * Obtiene el símbolo de la moneda
   */
  obtenerSimboloMoneda(moneda: string): string {
    switch (moneda) {
      case 'USD':
        return '$';
      case 'COP':
        return '$';
      case 'EUR':
        return '€';
      default:
        return '$';
    }
  },

  /**
   * Procesa los datos del informe para separar por monedas
   */
  procesarDatosMultiMoneda(datos: any): any {
    const procesados: any = {
      tesoreria: {},
      pagaduria: {}
    };

    // Procesar Tesorería
    Object.keys(datos.tesoreria || {}).forEach(conceptoId => {
      procesados.tesoreria[conceptoId] = {};
      
      Object.keys(datos.tesoreria[conceptoId]).forEach(companiaId => {
        procesados.tesoreria[conceptoId][companiaId] = {};
        
        Object.keys(datos.tesoreria[conceptoId][companiaId]).forEach(cuentaMonedaId => {
          const datosCuenta = datos.tesoreria[conceptoId][companiaId][cuentaMonedaId];
          procesados.tesoreria[conceptoId][companiaId][cuentaMonedaId] = {
            ...datosCuenta,
            monto_formateado: this.formatearMonto(datosCuenta.monto_original, datosCuenta.moneda),
            monto_cop_formateado: this.formatearMonto(datosCuenta.monto_cop, 'COP')
          };
        });
      });
    });

    // Procesar Pagaduría
    Object.keys(datos.pagaduria || {}).forEach(conceptoId => {
      procesados.pagaduria[conceptoId] = {};
      
      Object.keys(datos.pagaduria[conceptoId]).forEach(companiaId => {
        procesados.pagaduria[conceptoId][companiaId] = {};
        
        Object.keys(datos.pagaduria[conceptoId][companiaId]).forEach(cuentaMonedaId => {
          const datosCuenta = datos.pagaduria[conceptoId][companiaId][cuentaMonedaId];
          procesados.pagaduria[conceptoId][companiaId][cuentaMonedaId] = {
            ...datosCuenta,
            monto_formateado: this.formatearMonto(datosCuenta.monto_original, datosCuenta.moneda),
            monto_cop_formateado: this.formatearMonto(datosCuenta.monto_cop, 'COP')
          };
        });
      });
    });

    return procesados;
  }
};

export default cuentasMultiMonedaService;