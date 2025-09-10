import { useState, useEffect } from 'react';

export interface ConceptoFlujoCaja {
  id: number;
  codigo: string;
  nombre: string;
  area: 'tesoreria' | 'pagaduria' | 'ambas';
  tipo: string; // Cambiado a string para aceptar cualquier valor
  activo: boolean;
  orden_display: number;
  depende_de_concepto_id?: number;
  tipo_dependencia?: 'copia' | 'suma' | 'resta';
  concepto_dependiente?: ConceptoFlujoCaja | null;
  created_at: string;
  updated_at: string;
}

export interface UseConceptosFlujoCajaResult {
  conceptos: ConceptoFlujoCaja[];
  conceptosTesoreria: ConceptoFlujoCaja[];
  conceptosPagaduria: ConceptoFlujoCaja[];
  loading: boolean;
  error: string | null;
  refetchConceptos: () => Promise<void>;
}

export const useConceptosFlujoCaja = (): UseConceptosFlujoCajaResult => {
  const [conceptos, setConceptos] = useState<ConceptoFlujoCaja[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchConceptos = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('access_token');
      console.log('🔍 Fetching conceptos...', { 
        hasToken: !!token, 
        tokenPreview: token ? `${token.substring(0, 20)}...` : 'No token',
        tokenLength: token?.length 
      });
      
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      };
      
      console.log('📤 Headers being sent:', headers);
      
      const response = await fetch('http://localhost:8000/api/v1/api/conceptos-flujo-caja/', {
        headers
      });

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API Error:', { status: response.status, statusText: response.statusText, body: errorText });
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Conceptos loaded:', { count: data.length, sample: data[0] });
      setConceptos(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      console.error('❌ Error fetching conceptos:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConceptos();
  }, []);

  // Filtrar conceptos por área
  const conceptosTesoreria = conceptos
    .filter(concepto => concepto.area === 'tesoreria' || concepto.area === 'ambas')
    .sort((a, b) => a.orden_display - b.orden_display);

  const conceptosPagaduria = conceptos
    .filter(concepto => concepto.area === 'pagaduria' || concepto.area === 'ambas')
    .sort((a, b) => a.orden_display - b.orden_display);

  return {
    conceptos,
    conceptosTesoreria,
    conceptosPagaduria,
    loading,
    error,
    refetchConceptos: fetchConceptos
  };
};
