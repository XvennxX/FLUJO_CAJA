import { useState, useEffect } from 'react';

// Tipos para auditoría
export interface RegistroAuditoria {
  id: number;
  usuario_id: number;
  usuario_nombre: string;
  usuario_email: string;
  accion: 'CREATE' | 'UPDATE' | 'DELETE' | 'READ' | 'EXPORT' | 'IMPORT';
  modulo: 'FLUJO_CAJA' | 'EMPRESAS' | 'CUENTAS' | 'REPORTES' | 'USUARIOS' | 'CONCEPTOS' | 'SISTEMA';
  entidad: string;
  entidad_id?: string;
  descripcion: string;
  valores_anteriores?: any;
  valores_nuevos?: any;
  ip_address: string;
  user_agent?: string;
  endpoint?: string;
  metodo_http?: string;
  fecha_hora: string;
  duracion_ms?: number;
  resultado: 'EXITOSO' | 'ERROR' | 'ADVERTENCIA';
  mensaje_error?: string;
}

export interface UsuarioActivo {
  id: number;
  nombre: string;
}

export interface FiltrosAuditoria {
  usuario_id?: number;
  accion?: string;
  modulo?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  busqueda?: string;
  pagina: number;
  limite: number;
}

export interface RespuestaAuditoria {
  registros: RegistroAuditoria[];
  total: number;
  pagina: number;
  limite: number;
  total_paginas: number;
}

export interface EstadisticasAuditoria {
  total_registros: number;
  registros_hoy: number;
  registros_semana: number;
  registros_mes: number;
  acciones: Array<{ nombre: string; total: number }>;
  modulos: Array<{ nombre: string; total: number }>;
  usuarios_activos: Array<{ nombre: string; total: number }>;
  ips_frecuentes: Array<{ nombre: string; total: number }>;
}

// Hook principal para manejar auditoría
export function useAuditoria() {
  const [registros, setRegistros] = useState<RegistroAuditoria[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [estadisticas, setEstadisticas] = useState<EstadisticasAuditoria | null>(null);
  const [usuariosActivos, setUsuariosActivos] = useState<UsuarioActivo[]>([]);
  const [totalRegistros, setTotalRegistros] = useState(0);
  const [totalPaginas, setTotalPaginas] = useState(0);

  // Función para obtener registros de auditoría
  const obtenerRegistros = async (filtros: FiltrosAuditoria) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      params.append('pagina', filtros.pagina.toString());
      params.append('limite', filtros.limite.toString());
      
      if (filtros.usuario_id) params.append('usuario_id', filtros.usuario_id.toString());
      if (filtros.accion && filtros.accion !== 'TODAS') params.append('accion', filtros.accion);
      if (filtros.modulo && filtros.modulo !== 'TODOS') params.append('modulo', filtros.modulo);
      if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio);
      if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin);
      if (filtros.busqueda) params.append('busqueda', filtros.busqueda);

      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/auditoria/registros?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: RespuestaAuditoria = await response.json();
      setRegistros(data.registros);
      setTotalRegistros(data.total);
      setTotalPaginas(data.total_paginas);
      
    } catch (err) {
      console.error('Error obteniendo registros de auditoría:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
      setRegistros([]);
    } finally {
      setLoading(false);
    }
  };

  // Función para obtener estadísticas
  const obtenerEstadisticas = async (fechaInicio?: string, fechaFin?: string) => {
    try {
      const params = new URLSearchParams();
      if (fechaInicio) params.append('fecha_inicio', fechaInicio);
      if (fechaFin) params.append('fecha_fin', fechaFin);

      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/auditoria/estadisticas?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data: EstadisticasAuditoria = await response.json();
      setEstadisticas(data);
      
    } catch (err) {
      console.error('Error obteniendo estadísticas de auditoría:', err);
    }
  };

  // Función para obtener usuarios activos
  const obtenerUsuariosActivos = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/auditoria/usuarios-activos', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setUsuariosActivos(data.usuarios);
      
    } catch (err) {
      console.error('Error obteniendo usuarios activos:', err);
    }
  };

  // Función para obtener detalle de un registro
  const obtenerDetalleRegistro = async (registroId: number): Promise<RegistroAuditoria | null> => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/auditoria/registro/${registroId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
      
    } catch (err) {
      console.error('Error obteniendo detalle del registro:', err);
      return null;
    }
  };

  // Función para registrar acción manual (solo administradores)
  const registrarAccionManual = async (
    accion: string,
    modulo: string,
    entidad: string,
    descripcion: string,
    entidad_id?: string,
    valores_anteriores?: any,
    valores_nuevos?: any
  ) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/auditoria/registro', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          accion,
          modulo,
          entidad,
          entidad_id,
          descripcion,
          valores_anteriores,
          valores_nuevos
        })
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      return await response.json();
      
    } catch (err) {
      console.error('Error registrando acción manual:', err);
      throw err;
    }
  };

  // Cargar usuarios activos al inicializar
  useEffect(() => {
    obtenerUsuariosActivos();
  }, []);

  return {
    // Estado
    registros,
    loading,
    error,
    estadisticas,
    usuariosActivos,
    totalRegistros,
    totalPaginas,
    
    // Funciones
    obtenerRegistros,
    obtenerEstadisticas,
    obtenerUsuariosActivos,
    obtenerDetalleRegistro,
    registrarAccionManual,
    
    // Funciones de utilidad
    setError
  };
}

// Hook simplificado para compatibilidad con el código existente
export function useAuditoriaLegacy() {
  const {
    registros,
    loading,
    error,
    obtenerRegistros
  } = useAuditoria();

  // Convertir formato para compatibilidad
  const logs = registros.map(registro => ({
    id: registro.id.toString(),
    usuario: registro.usuario_nombre,
    accion: registro.accion,
    modulo: registro.modulo,
    descripcion: registro.descripcion,
    entidad: registro.entidad,
    entidadId: registro.entidad_id,
    valorAnterior: registro.valores_anteriores,
    valorNuevo: registro.valores_nuevos,
    fechaHora: registro.fecha_hora,
    ip: registro.ip_address,
    navegador: registro.user_agent || 'Desconocido'
  }));

  // Función para cargar con filtros por defecto
  useEffect(() => {
    const filtrosDefault: FiltrosAuditoria = {
      pagina: 1,
      limite: 50
    };
    obtenerRegistros(filtrosDefault);
  }, []);

  return {
    logs,
    loading,
    error
  };
}

// Alias para mantener compatibilidad
export type AuditLog = RegistroAuditoria;