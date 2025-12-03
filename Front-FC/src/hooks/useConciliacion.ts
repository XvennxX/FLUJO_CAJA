/**
 * Hook para manejar conciliaciones contables
 */
import { useState, useCallback } from 'react';
import { format } from 'date-fns';

export interface EmpresaConciliacion {
  id: number;
  compania_id: number;
  compania: {
    id: number;
    nombre: string;
  };
  total_pagaduria: number;
  total_tesoreria: number;
  total_calculado: number;
  total_centralizadora: number | null;
  diferencia: number;
  estado: string;
  observaciones?: string;
}

export interface ConciliacionData {
  fecha: string;
  empresas: EmpresaConciliacion[];
}

export const useConciliacion = () => {
  const [conciliacionData, setConciliacionData] = useState<ConciliacionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fechaSeleccionada, setFechaSeleccionada] = useState<Date>(new Date());

  const obtenerConciliacionPorFecha = useCallback(async (fecha: Date) => {
    setLoading(true);
    setError(null);
    
    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      
      const response = await fetch('http://localhost:8000/api/v1/conciliacion/fecha', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          fecha: fechaStr
        })
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          throw new Error('No tienes autorización para acceder a esta funcionalidad. Por favor inicia sesión.');
        }
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: ConciliacionData = await response.json();
      setConciliacionData(data);
      setFechaSeleccionada(fecha);
      
    } catch (err) {
      console.error('Error obteniendo conciliación:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
      setConciliacionData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const actualizarTotalCentralizadora = useCallback(async (
    empresaId: number, 
    fecha: Date, 
    totalCentralizadora: number,
    observaciones?: string
  ) => {
    setLoading(true);
    setError(null);

    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      
      const params = new URLSearchParams({
        fecha: fechaStr,
        total_centralizadora: totalCentralizadora.toString()
      });
      
      if (observaciones) {
        params.append('observaciones', observaciones);
      }

      const response = await fetch(`http://localhost:8000/api/v1/conciliacion/centralizadora/${empresaId}?${params}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Recargar datos después de actualizar
      await obtenerConciliacionPorFecha(fecha);
      
      return result;
      
    } catch (err) {
      console.error('Error actualizando total centralizadora:', err);
      setError(err instanceof Error ? err.message : 'Error actualizando total centralizadora');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [obtenerConciliacionPorFecha]);

  const confirmarConciliacion = useCallback(async (empresaId: number, fecha: Date) => {
    setLoading(true);
    setError(null);

    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      
      const params = new URLSearchParams({
        fecha: fechaStr
      });

      const response = await fetch(`http://localhost:8000/api/v1/conciliacion/confirmar/${empresaId}?${params}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Recargar datos después de confirmar
      await obtenerConciliacionPorFecha(fecha);
      
      return result;
      
    } catch (err) {
      console.error('Error confirmando conciliación:', err);
      setError(err instanceof Error ? err.message : 'Error confirmando conciliación');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [obtenerConciliacionPorFecha]);

  const evaluarConciliacion = useCallback(async (empresaId: number, fecha: Date) => {
    setLoading(true);
    setError(null);

    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      
      const params = new URLSearchParams({
        fecha: fechaStr
      });

      const response = await fetch(`http://localhost:8000/api/v1/conciliacion/evaluar/${empresaId}?${params}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Recargar datos después de evaluar
      await obtenerConciliacionPorFecha(fecha);
      
      return result;
      
    } catch (err) {
      console.error('Error evaluando conciliación:', err);
      setError(err instanceof Error ? err.message : 'Error evaluando conciliación');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [obtenerConciliacionPorFecha]);

  const cerrarConciliacion = useCallback(async (empresaId: number, fecha: Date) => {
    setLoading(true);
    setError(null);

    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      
      const params = new URLSearchParams({
        fecha: fechaStr
      });

      const response = await fetch(`http://localhost:8000/api/v1/conciliacion/cerrar/${empresaId}?${params}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Recargar datos después de cerrar
      await obtenerConciliacionPorFecha(fecha);
      
      return result;
      
    } catch (err) {
      console.error('Error cerrando conciliación:', err);
      setError(err instanceof Error ? err.message : 'Error cerrando conciliación');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [obtenerConciliacionPorFecha]);

  const evaluarTodasConciliaciones = useCallback(async (fecha: Date) => {
    setLoading(true);
    setError(null);

    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      
      const params = new URLSearchParams({
        fecha: fechaStr
      });

      const response = await fetch(`http://localhost:8000/api/v1/conciliacion/evaluar-todas?${params}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Recargar datos después de evaluar
      await obtenerConciliacionPorFecha(fecha);
      
      return result;
      
    } catch (err) {
      console.error('Error evaluando conciliaciones:', err);
      setError(err instanceof Error ? err.message : 'Error evaluando conciliaciones');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [obtenerConciliacionPorFecha]);

  const cerrarTodasConciliaciones = useCallback(async (fecha: Date) => {
    setLoading(true);
    setError(null);

    try {
      const fechaStr = format(fecha, 'yyyy-MM-dd');
      
      const params = new URLSearchParams({
        fecha: fechaStr
      });

      const response = await fetch(`http://localhost:8000/api/v1/conciliacion/cerrar-todas?${params}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Recargar datos después de cerrar
      await obtenerConciliacionPorFecha(fecha);
      
      return result;
      
    } catch (err) {
      console.error('Error cerrando conciliaciones:', err);
      setError(err instanceof Error ? err.message : 'Error cerrando conciliaciones');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [obtenerConciliacionPorFecha]);

  return {
    // Estado
    conciliacionData,
    loading,
    error,
    fechaSeleccionada,
    
    // Acciones
    obtenerConciliacionPorFecha,
    actualizarTotalCentralizadora,
    evaluarConciliacion,
    confirmarConciliacion,
    cerrarConciliacion,
    evaluarTodasConciliaciones,
    cerrarTodasConciliaciones,
    
    // Helpers
    setFechaSeleccionada
  };
};
