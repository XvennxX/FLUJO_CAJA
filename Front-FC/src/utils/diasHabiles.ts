/**
 * Utilidades para manejo de días hábiles en el frontend.
 * Proporciona funciones para validar y trabajar con días laborables.
 */

import { ApiResponse } from '../types/api';

export interface DiaInfo {
  fecha: string;
  es_habil: boolean;
  es_fin_semana: boolean;
  es_festivo: boolean;
  festivo?: {
    id: number;
    nombre: string;
    descripcion: string;
    tipo: string;
  } | null;
  dia_semana: string;
  proximo_habil: string;
  anterior_habil: string;
}

export interface DiaHabilResponse {
  fecha_referencia: string;
  proximo_dia_habil: string;
  incluyo_actual: boolean;
}

export interface RangoDiasHabiles {
  fecha_inicio: string;
  fecha_fin: string;
  dias_habiles: string[];
  total: number;
}

export interface InfoMes {
  año: number;
  mes: number;
  primer_dia_habil: string;
  ultimo_dia_habil: string;
  total_dias_habiles: number;
  dias_habiles: string[];
}

export interface Festivo {
  id: number;
  fecha: string;
  nombre: string;
  descripcion: string;
  tipo: string;
  activo: boolean;
}

class DiasHabilesService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000/api/v1/dias-habiles') {
    this.baseUrl = baseUrl;
  }

  /**
   * Validar si una fecha es día hábil.
   */
  async validarDiaHabil(fecha: string): Promise<DiaInfo> {
    const response = await fetch(`${this.baseUrl}/validar/${fecha}`);
    const result: ApiResponse<DiaInfo> = await response.json();
    
    if (!result.success) {
      throw new Error('Error al validar día hábil');
    }
    
    return result.data;
  }

  /**
   * Obtener el próximo día hábil desde una fecha.
   */
  async obtenerProximoDiaHabil(
    fecha: string, 
    incluirActual: boolean = false
  ): Promise<DiaHabilResponse> {
    const url = `${this.baseUrl}/proximo/${fecha}?incluir_actual=${incluirActual}`;
    const response = await fetch(url);
    const result: ApiResponse<DiaHabilResponse> = await response.json();
    
    if (!result.success) {
      throw new Error('Error al obtener próximo día hábil');
    }
    
    return result.data;
  }

  /**
   * Obtener el día hábil anterior a una fecha.
   */
  async obtenerAnteriorDiaHabil(
    fecha: string, 
    incluirActual: boolean = false
  ): Promise<DiaHabilResponse> {
    const url = `${this.baseUrl}/anterior/${fecha}?incluir_actual=${incluirActual}`;
    const response = await fetch(url);
    const result: ApiResponse<DiaHabilResponse> = await response.json();
    
    if (!result.success) {
      throw new Error('Error al obtener día hábil anterior');
    }
    
    return result.data;
  }

  /**
   * Obtener días hábiles en un rango de fechas.
   */
  async obtenerDiasHabilesRango(
    fechaInicio: string,
    fechaFin: string,
    soloContar: boolean = false
  ): Promise<RangoDiasHabiles> {
    const url = `${this.baseUrl}/rango?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&solo_contar=${soloContar}`;
    const response = await fetch(url);
    const result: ApiResponse<RangoDiasHabiles> = await response.json();
    
    if (!result.success) {
      throw new Error('Error al obtener rango de días hábiles');
    }
    
    return result.data;
  }

  /**
   * Obtener información de días hábiles de un mes.
   */
  async obtenerDiasHabilesMes(año: number, mes: number): Promise<InfoMes> {
    const response = await fetch(`${this.baseUrl}/mes/${año}/${mes}`);
    const result: ApiResponse<InfoMes> = await response.json();
    
    if (!result.success) {
      throw new Error('Error al obtener días hábiles del mes');
    }
    
    return result.data;
  }

  /**
   * Obtener información del día actual.
   */
  async obtenerInfoHoy(): Promise<{
    hoy: DiaInfo;
    proximo_dia_habil: string;
    es_hoy_habil: boolean;
  }> {
    const response = await fetch(`${this.baseUrl}/hoy`);
    const result = await response.json();
    
    if (!result.success) {
      throw new Error('Error al obtener información de hoy');
    }
    
    return result.data;
  }

  /**
   * Obtener lista de días festivos.
   */
  async obtenerFestivos(año?: number, mes?: number): Promise<Festivo[]> {
    let url = `${this.baseUrl.replace('/dias-habiles', '')}/festivos`;
    const params = new URLSearchParams();
    
    if (año) params.append('año', año.toString());
    if (mes) params.append('mes', mes.toString());
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    const response = await fetch(url);
    const result = await response.json();
    
    if (!result.success) {
      throw new Error('Error al obtener festivos');
    }
    
    return result.data.festivos;
  }
}

/**
 * Utilidades para trabajo con fechas y días hábiles en el cliente.
 */
export class DiasHabilesUtils {
  /**
   * Convertir string de fecha a objeto Date.
   */
  static stringToDate(fechaStr: string): Date {
    return new Date(fechaStr + 'T00:00:00.000Z');
  }

  /**
   * Convertir Date a string en formato YYYY-MM-DD.
   */
  static dateToString(fecha: Date): string {
    return fecha.toISOString().split('T')[0];
  }

  /**
   * Validar si una fecha es fin de semana (lado cliente).
   */
  static esFinDeSemana(fecha: Date): boolean {
    const diaSemana = fecha.getDay();
    return diaSemana === 0 || diaSemana === 6; // Domingo = 0, Sábado = 6
  }

  /**
   * Obtener el nombre del día de la semana en español.
   */
  static obtenerNombreDia(fecha: Date): string {
    const dias = [
      'Domingo', 'Lunes', 'Martes', 'Miércoles', 
      'Jueves', 'Viernes', 'Sábado'
    ];
    return dias[fecha.getDay()];
  }

  /**
   * Obtener el nombre del mes en español.
   */
  static obtenerNombreMes(mes: number): string {
    const meses = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    return meses[mes - 1];
  }

  /**
   * Formatear fecha para mostrar en la UI.
   */
  static formatearFecha(fecha: Date | string): string {
    const fechaObj = typeof fecha === 'string' ? this.stringToDate(fecha) : fecha;
    const dia = fechaObj.getDate().toString().padStart(2, '0');
    const mes = (fechaObj.getMonth() + 1).toString().padStart(2, '0');
    const año = fechaObj.getFullYear();
    
    return `${dia}/${mes}/${año}`;
  }

  /**
   * Formatear fecha con nombre del día.
   */
  static formatearFechaCompleta(fecha: Date | string): string {
    const fechaObj = typeof fecha === 'string' ? this.stringToDate(fecha) : fecha;
    const nombreDia = this.obtenerNombreDia(fechaObj);
    const fechaFormateada = this.formatearFecha(fechaObj);
    
    return `${nombreDia}, ${fechaFormateada}`;
  }

  /**
   * Obtener rango de fechas para un mes específico.
   */
  static obtenerRangoMes(año: number, mes: number): { inicio: string; fin: string } {
    const inicio = new Date(año, mes - 1, 1);
    const fin = new Date(año, mes, 0); // Último día del mes
    
    return {
      inicio: this.dateToString(inicio),
      fin: this.dateToString(fin)
    };
  }

  /**
   * Validar si una fecha está en el futuro.
   */
  static esFechaFutura(fecha: Date | string): boolean {
    const fechaObj = typeof fecha === 'string' ? this.stringToDate(fecha) : fecha;
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    fechaObj.setHours(0, 0, 0, 0);
    
    return fechaObj > hoy;
  }

  /**
   * Obtener fecha de hoy en formato string.
   */
  static obtenerHoy(): string {
    return this.dateToString(new Date());
  }
}

// Instancia singleton del servicio
export const diasHabilesService = new DiasHabilesService();

// Exportar para uso directo
export { DiasHabilesService };