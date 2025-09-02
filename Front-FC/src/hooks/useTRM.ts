import { useState, useEffect } from 'react';

interface TRM {
  fecha: string;
  valor: number;
  fecha_creacion: string;
}

export const useTRM = () => {
  const [trm, setTrm] = useState<TRM | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCurrentTRM = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Agregar timestamp para evitar cache
      const timestamp = new Date().getTime();
      const response = await fetch(`http://localhost:8000/api/v1/trm/current?_t=${timestamp}`);
      
      if (!response.ok) {
        throw new Error('Error al obtener TRM');
      }
      
      const data = await response.json();
      setTrm(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error fetching TRM:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTRMByDate = async (fecha: string) => {
    try {
      setLoading(true);
      setError(null);
      
      // Agregar timestamp para evitar cache
      const timestamp = new Date().getTime();
      const response = await fetch(`http://localhost:8000/api/v1/trm/by-date/${fecha}?_t=${timestamp}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`No se encontró TRM para la fecha ${fecha}`);
        }
        throw new Error('Error al obtener TRM');
      }
      
      const data = await response.json();
      setTrm(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error fetching TRM by date:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTRMRange = async (fechaInicio?: string, fechaFin?: string, limit = 30): Promise<TRM[]> => {
    try {
      // Agregar timestamp para evitar cache
      const timestamp = new Date().getTime();
      let url = `http://localhost:8000/api/v1/trm/range?limit=${limit}&_t=${timestamp}`;
      
      if (fechaInicio) {
        url += `&fecha_inicio=${fechaInicio}`;
      }
      
      if (fechaFin) {
        url += `&fecha_fin=${fechaFin}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error('Error al obtener rango de TRM');
      }
      
      return await response.json();
    } catch (err) {
      console.error('Error fetching TRM range:', err);
      throw err;
    }
  };

  useEffect(() => {
    fetchCurrentTRM();
  }, []);

  return {
    trm,
    loading,
    error,
    refetch: fetchCurrentTRM,
    fetchByDate: fetchTRMByDate,
    getTRMRange
  };
};
