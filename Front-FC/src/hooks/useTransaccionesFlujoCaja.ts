import { useState, useEffect, useCallback } from 'react';

export interface TransaccionFlujoCaja {
  id?: number;
  fecha: string;
  concepto_id: number;
  cuenta_id: number | null;
  monto: number;
  descripcion?: string;
  area: 'tesoreria' | 'pagaduria';
  compania_id?: number;
}

export interface TransaccionCreate {
  fecha: string;
  concepto_id: number;
  cuenta_id: number | null;
  monto: number;
  descripcion?: string;
  area: 'tesoreria' | 'pagaduria';
  compania_id?: number;
}

export interface TransaccionUpdate {
  monto?: number;
  descripcion?: string;
}

export const useTransaccionesFlujoCaja = (fecha: string, area: 'tesoreria' | 'pagaduria') => {
  const [transacciones, setTransacciones] = useState<TransaccionFlujoCaja[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Obtener token de autenticación
  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  };

  // Cargar transacciones para una fecha y área específica
  const cargarTransacciones = useCallback(async () => {
    if (!fecha) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:8000/api/v1/api/transacciones-flujo-caja/fecha/${fecha}?area=${area}`,
        {
          headers: getAuthHeaders()
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTransacciones(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error al cargar transacciones');
      }
    } catch (err) {
      setError('Error de conexión al cargar transacciones');
      console.error('Error loading transactions:', err);
    } finally {
      setLoading(false);
    }
  }, [fecha, area]);

  // Crear o actualizar transacción
  const guardarTransaccion = useCallback(async (
    conceptoId: number, 
    cuentaId: number | null, 
    monto: number,
    companiaId?: number
  ): Promise<boolean> => {
    try {
      // Buscar si ya existe una transacción para este concepto y cuenta
      const transaccionExistente = transacciones.find(
        t => t.concepto_id === conceptoId && t.cuenta_id === cuentaId
      );

      if (transaccionExistente) {
        // Actualizar transacción existente
        const updateData: TransaccionUpdate = {
          monto: monto,
          descripcion: `Actualizado desde dashboard ${area}`
        };

        const response = await fetch(
          `http://localhost:8000/api/v1/api/transacciones-flujo-caja/${transaccionExistente.id}`,
          {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(updateData)
          }
        );

        if (response.ok) {
          await cargarTransacciones(); // Recargar datos
          return true;
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Error al actualizar transacción');
          return false;
        }
      } else {
        // Crear nueva transacción
        const createData: TransaccionCreate = {
          fecha: fecha,
          concepto_id: conceptoId,
          cuenta_id: cuentaId,
          monto: monto,
          area: area,
          descripcion: `Creado desde dashboard ${area}`,
          ...(companiaId && { compania_id: companiaId })
        };

        const response = await fetch(
          'http://localhost:8000/api/v1/api/transacciones-flujo-caja/',
          {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(createData)
          }
        );

        if (response.ok) {
          await cargarTransacciones(); // Recargar datos
          return true;
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Error al crear transacción');
          return false;
        }
      }
    } catch (err) {
      setError('Error de conexión al guardar transacción');
      console.error('Error saving transaction:', err);
      return false;
    }
  }, [transacciones, fecha, area, cargarTransacciones]);

  // Obtener el monto de una transacción específica
  const obtenerMonto = useCallback((conceptoId: number, cuentaId: number | null): number => {
    const transaccion = transacciones.find(
      t => t.concepto_id === conceptoId && t.cuenta_id === cuentaId
    );
    return transaccion ? transaccion.monto : 0;
  }, [transacciones]);

  // Eliminar transacción
  const eliminarTransaccion = useCallback(async (conceptoId: number, cuentaId: number | null): Promise<boolean> => {
    try {
      const transaccion = transacciones.find(
        t => t.concepto_id === conceptoId && t.cuenta_id === cuentaId
      );

      if (!transaccion || !transaccion.id) {
        return true; // No existe, considerarlo como eliminado
      }

      const response = await fetch(
        `http://localhost:8000/api/v1/api/transacciones-flujo-caja/${transaccion.id}`,
        {
          method: 'DELETE',
          headers: getAuthHeaders()
        }
      );

      if (response.ok) {
        await cargarTransacciones(); // Recargar datos
        return true;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error al eliminar transacción');
        return false;
      }
    } catch (err) {
      setError('Error de conexión al eliminar transacción');
      console.error('Error deleting transaction:', err);
      return false;
    }
  }, [transacciones, cargarTransacciones]);

  // Cargar transacciones cuando cambie la fecha o área
  useEffect(() => {
    cargarTransacciones();
  }, [cargarTransacciones]);

  return {
    transacciones,
    loading,
    error,
    cargarTransacciones,
    guardarTransaccion,
    obtenerMonto,
    eliminarTransaccion,
    setError
  };
};
