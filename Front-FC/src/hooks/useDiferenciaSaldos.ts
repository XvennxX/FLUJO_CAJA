import { useState } from 'react';

interface DiferenciaSaldosHookResult {
  calcularDiferenciaSaldos: (fecha: string) => Promise<void>;
  verificarNecesidadCalculo: (fecha: string) => Promise<boolean>;
  loading: boolean;
  error: string | null;
}

export const useDiferenciaSaldos = (): DiferenciaSaldosHookResult => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calcularDiferenciaSaldos = async (fecha: string): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        'http://localhost:8000/api/v1/diferencia-saldos/calcular-diferencia-saldos',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ fecha }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error calculando diferencias saldos');
      }

      const data = await response.json();
      console.log('✅ Diferencias saldos calculadas:', data);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      console.error('❌ Error calculando diferencias saldos:', errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const verificarNecesidadCalculo = async (fecha: string): Promise<boolean> => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/api/v1/diferencia-saldos/verificar-necesidad/${fecha}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Error verificando necesidad de cálculo');
      }

      const data = await response.json();
      return data.necesita_calculo;
      
    } catch (err) {
      console.error('❌ Error verificando necesidad de cálculo:', err);
      return false;
    }
  };

  return {
    calcularDiferenciaSaldos,
    verificarNecesidadCalculo,
    loading,
    error,
  };
};
