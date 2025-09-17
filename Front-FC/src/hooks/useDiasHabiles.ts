/**
 * Hook personalizado para manejo de días hábiles en React.
 * Proporciona funcionalidades reactivas para trabajar con días laborables.
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  diasHabilesService, 
  DiaInfo, 
  DiaHabilResponse, 
  InfoMes, 
  Festivo,
  DiasHabilesUtils 
} from '../utils/diasHabiles';

export interface UseDiasHabilesState {
  loading: boolean;
  error: string | null;
}

/**
 * Hook para validar si una fecha es día hábil.
 */
export function useDiaHabil(fecha?: string) {
  const [state, setState] = useState<UseDiasHabilesState & { diaInfo: DiaInfo | null }>({
    loading: false,
    error: null,
    diaInfo: null
  });

  const validar = useCallback(async (fechaValidar: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const diaInfo = await diasHabilesService.validarDiaHabil(fechaValidar);
      setState(prev => ({ ...prev, loading: false, diaInfo }));
      return diaInfo;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      throw error;
    }
  }, []);

  useEffect(() => {
    if (fecha) {
      validar(fecha);
    }
  }, [fecha, validar]);

  return {
    ...state,
    validar,
    esHabil: state.diaInfo?.es_habil ?? false,
    esFestivo: state.diaInfo?.es_festivo ?? false,
    esFinSemana: state.diaInfo?.es_fin_semana ?? false
  };
}

/**
 * Hook para obtener el próximo día hábil.
 */
export function useProximoDiaHabil() {
  const [state, setState] = useState<UseDiasHabilesState & { proximoDia: string | null }>({
    loading: false,
    error: null,
    proximoDia: null
  });

  const obtener = useCallback(async (fecha: string, incluirActual: boolean = false) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const resultado = await diasHabilesService.obtenerProximoDiaHabil(fecha, incluirActual);
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        proximoDia: resultado.proximo_dia_habil 
      }));
      return resultado;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      throw error;
    }
  }, []);

  return {
    ...state,
    obtenerProximo: obtener
  };
}

/**
 * Hook para obtener días hábiles de un mes.
 */
export function useDiasHabilesMes(año?: number, mes?: number) {
  const [state, setState] = useState<UseDiasHabilesState & { infoMes: InfoMes | null }>({
    loading: false,
    error: null,
    infoMes: null
  });

  const obtener = useCallback(async (añoParam: number, mesParam: number) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const infoMes = await diasHabilesService.obtenerDiasHabilesMes(añoParam, mesParam);
      setState(prev => ({ ...prev, loading: false, infoMes }));
      return infoMes;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      throw error;
    }
  }, []);

  useEffect(() => {
    if (año && mes) {
      obtener(año, mes);
    }
  }, [año, mes, obtener]);

  return {
    ...state,
    obtener,
    diasHabiles: state.infoMes?.dias_habiles ?? [],
    totalDiasHabiles: state.infoMes?.total_dias_habiles ?? 0,
    primerDiaHabil: state.infoMes?.primer_dia_habil,
    ultimoDiaHabil: state.infoMes?.ultimo_dia_habil
  };
}

/**
 * Hook para obtener festivos.
 */
export function useFestivos(año?: number, mes?: number) {
  const [state, setState] = useState<UseDiasHabilesState & { festivos: Festivo[] }>({
    loading: false,
    error: null,
    festivos: []
  });

  const obtener = useCallback(async (añoParam?: number, mesParam?: number) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const festivos = await diasHabilesService.obtenerFestivos(añoParam, mesParam);
      setState(prev => ({ ...prev, loading: false, festivos }));
      return festivos;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      throw error;
    }
  }, []);

  useEffect(() => {
    obtener(año, mes);
  }, [año, mes, obtener]);

  return {
    ...state,
    obtener,
    refetch: () => obtener(año, mes)
  };
}

/**
 * Hook para información del día actual.
 */
export function useInfoHoy() {
  const [state, setState] = useState<UseDiasHabilesState & {
    infoHoy: DiaInfo | null;
    proximoDiaHabil: string | null;
    esHoyHabil: boolean;
  }>({
    loading: false,
    error: null,
    infoHoy: null,
    proximoDiaHabil: null,
    esHoyHabil: false
  });

  const obtener = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const resultado = await diasHabilesService.obtenerInfoHoy();
      setState(prev => ({ 
        ...prev, 
        loading: false,
        infoHoy: resultado.hoy,
        proximoDiaHabil: resultado.proximo_dia_habil,
        esHoyHabil: resultado.es_hoy_habil
      }));
      return resultado;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      throw error;
    }
  }, []);

  useEffect(() => {
    obtener();
  }, [obtener]);

  return {
    ...state,
    refetch: obtener
  };
}

/**
 * Hook para filtrar fechas habilitadas en un calendario.
 */
export function useCalendarioHabiles(año: number, mes: number) {
  const { diasHabiles, loading, error } = useDiasHabilesMes(año, mes);
  const { festivos } = useFestivos(año, mes);

  const esFechaHabilitada = useCallback((fecha: Date): boolean => {
    const fechaStr = DiasHabilesUtils.dateToString(fecha);
    return diasHabiles.includes(fechaStr);
  }, [diasHabiles]);

  const obtenerInfoFecha = useCallback((fecha: Date) => {
    const fechaStr = DiasHabilesUtils.dateToString(fecha);
    const esHabil = diasHabiles.includes(fechaStr);
    const esFinSemana = DiasHabilesUtils.esFinDeSemana(fecha);
    const festivo = festivos.find(f => f.fecha === fechaStr);
    
    return {
      esHabil,
      esFinSemana,
      esFestivo: !!festivo,
      festivo,
      nombreDia: DiasHabilesUtils.obtenerNombreDia(fecha),
      fechaFormateada: DiasHabilesUtils.formatearFecha(fecha)
    };
  }, [diasHabiles, festivos]);

  return {
    loading,
    error,
    diasHabiles,
    festivos,
    esFechaHabilitada,
    obtenerInfoFecha
  };
}

/**
 * Hook para navegación inteligente entre días hábiles.
 */
export function useNavegacionHabiles() {
  const [fechaActual, setFechaActual] = useState<string>(DiasHabilesUtils.obtenerHoy());
  const { obtenerProximo } = useProximoDiaHabil();

  const irProximoDiaHabil = useCallback(async (incluirActual: boolean = false) => {
    try {
      const resultado = await obtenerProximo(fechaActual, incluirActual);
      setFechaActual(resultado.proximo_dia_habil);
      return resultado.proximo_dia_habil;
    } catch (error) {
      console.error('Error al navegar al próximo día hábil:', error);
      throw error;
    }
  }, [fechaActual, obtenerProximo]);

  const irAnteriorDiaHabil = useCallback(async (incluirActual: boolean = false) => {
    try {
      const resultado = await diasHabilesService.obtenerAnteriorDiaHabil(fechaActual, incluirActual);
      setFechaActual(resultado.proximo_dia_habil); // El API usa el mismo campo para anterior
      return resultado.proximo_dia_habil;
    } catch (error) {
      console.error('Error al navegar al día hábil anterior:', error);
      throw error;
    }
  }, [fechaActual]);

  const establecerFecha = useCallback((nuevaFecha: string) => {
    setFechaActual(nuevaFecha);
  }, []);

  return {
    fechaActual,
    establecerFecha,
    irProximoDiaHabil,
    irAnteriorDiaHabil
  };
}