import { useState, useEffect } from 'react';

interface TRM {
  fecha: string;
  valor: number;
  fecha_creacion: string;
}

export const useTRMByDate = (fecha?: string) => {
  const [trm, setTrm] = useState<TRM | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTRMByDate = async (targetDate: string) => {
    if (!targetDate) return;
    
    try {
      setLoading(true);
      setError(null);
      
      console.log(`🔍 Obteniendo TRM para fecha: ${targetDate}`);
      
      // Intentar obtener TRM de la fecha específica
      const timestamp = new Date().getTime();
      let response = await fetch(`http://localhost:8000/api/v1/trm/by-date/${targetDate}?_t=${timestamp}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ TRM encontrada para ${targetDate}: ${data.valor}`);
        setTrm(data);
        return;
      }
      
      // Si no hay TRM para esa fecha, buscar la más cercana anterior
      console.log(`⚠️ No hay TRM para ${targetDate}, buscando TRM anterior más cercana...`);
      
      // Obtener TRM más reciente hasta esa fecha
      const rangeResponse = await fetch(
        `http://localhost:8000/api/v1/trm/range?fecha_fin=${targetDate}&limit=1&_t=${timestamp}`
      );
      
      if (rangeResponse.ok) {
        const rangeData = await rangeResponse.json();
        if (rangeData && rangeData.length > 0) {
          const closestTrm = rangeData[0];
          console.log(`✅ TRM más cercana encontrada (${closestTrm.fecha}): ${closestTrm.valor}`);
          setTrm(closestTrm);
          return;
        }
      }
      
      // Si no se encuentra ninguna TRM, usar la actual como fallback
      console.log(`⚠️ No se encontró TRM anterior, usando TRM actual como fallback`);
      const currentResponse = await fetch(`http://localhost:8000/api/v1/trm/current?_t=${timestamp}`);
      
      if (currentResponse.ok) {
        const currentData = await currentResponse.json();
        console.log(`⚠️ Usando TRM actual como fallback: ${currentData.valor}`);
        setTrm(currentData);
      } else {
        throw new Error('No se pudo obtener ninguna TRM');
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      console.error(`❌ Error obteniendo TRM para ${targetDate}:`, err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fecha) {
      fetchTRMByDate(fecha);
    }
  }, [fecha]);

  return {
    trm,
    loading,
    error,
    refetch: () => fecha && fetchTRMByDate(fecha)
  };
};