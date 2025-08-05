import { useState, useEffect } from 'react';

export interface AuditLog {
  id: string;
  usuario: string;
  accion: 'CREAR' | 'EDITAR' | 'ELIMINAR' | 'CONSULTAR' | 'EXPORTAR' | 'IMPORTAR';
  modulo: 'FLUJO_CAJA' | 'EMPRESAS' | 'CUENTAS' | 'REPORTES' | 'USUARIOS';
  descripcion: string;
  entidad: string;
  entidadId?: string;
  valorAnterior?: any;
  valorNuevo?: any;
  fechaHora: string;
  ip: string;
  navegador: string;
}

interface UseAuditoriaProps {
  usuario?: string;
}

export function useAuditoria({ usuario = 'Usuario Actual' }: UseAuditoriaProps = {}) {
  const [logs, setLogs] = useState<AuditLog[]>([]);

  // Cargar logs existentes del localStorage al iniciar
  useEffect(() => {
    const savedLogs = localStorage.getItem('auditLogs');
    if (savedLogs) {
      try {
        setLogs(JSON.parse(savedLogs));
      } catch (error) {
        console.error('Error al cargar logs de auditoría:', error);
        // Inicializar con datos de ejemplo si hay error
        initializeWithMockData();
      }
    } else {
      // Inicializar con datos de ejemplo si no hay logs
      initializeWithMockData();
    }
  }, []);

  // Guardar logs en localStorage cuando cambien
  useEffect(() => {
    if (logs.length > 0) {
      localStorage.setItem('auditLogs', JSON.stringify(logs));
    }
  }, [logs]);

  const initializeWithMockData = () => {
    const mockLogs: AuditLog[] = [
      {
        id: '1',
        usuario: 'Juan Pérez',
        accion: 'EDITAR',
        modulo: 'FLUJO_CAJA',
        descripcion: 'Modificó el saldo de CAPITALIZADORA en BANCO DAVIVIENDA',
        entidad: 'Flujo de Caja Diario',
        entidadId: '2025-01-22',
        valorAnterior: { saldo: 2800000.00 },
        valorNuevo: { saldo: 2850000.00 },
        fechaHora: '2025-01-22T14:30:15Z',
        ip: '192.168.1.100',
        navegador: 'Chrome 120.0.0.0'
      },
      {
        id: '2',
        usuario: 'María García',
        accion: 'CREAR',
        modulo: 'EMPRESAS',
        descripcion: 'Creó nueva empresa: SEGUROS GENERALES',
        entidad: 'Empresa',
        entidadId: 'emp_001',
        valorNuevo: { nombre: 'SEGUROS GENERALES', codigo: 'SG001' },
        fechaHora: '2025-01-22T13:45:22Z',
        ip: '192.168.1.101',
        navegador: 'Firefox 121.0.0.0'
      },
      {
        id: '3',
        usuario: 'Carlos López',
        accion: 'ELIMINAR',
        modulo: 'CUENTAS',
        descripcion: 'Eliminó cuenta bancaria de COMERCIALES',
        entidad: 'Cuenta Bancaria',
        entidadId: 'cuenta_005',
        valorAnterior: { banco: 'BANCO POPULAR', numero: '40195224' },
        fechaHora: '2025-01-22T12:20:45Z',
        ip: '192.168.1.102',
        navegador: 'Edge 120.0.0.0'
      },
      {
        id: '4',
        usuario: 'Ana Rodríguez',
        accion: 'EXPORTAR',
        modulo: 'REPORTES',
        descripcion: 'Exportó reporte de flujo mensual',
        entidad: 'Reporte',
        fechaHora: '2025-01-22T11:15:30Z',
        ip: '192.168.1.103',
        navegador: 'Safari 17.2.0'
      },
      {
        id: '5',
        usuario: 'Luis Martínez',
        accion: 'EDITAR',
        modulo: 'FLUJO_CAJA',
        descripcion: 'Actualizó transacción de CONSUMO para SEGUROS BOLÍVAR',
        entidad: 'Transacción',
        entidadId: 'trans_001',
        valorAnterior: { monto: -300000.00 },
        valorNuevo: { monto: -320000.00 },
        fechaHora: '2025-01-22T10:30:12Z',
        ip: '192.168.1.104',
        navegador: 'Chrome 120.0.0.0'
      },
      {
        id: '6',
        usuario: 'Sofia Chen',
        accion: 'IMPORTAR',
        modulo: 'FLUJO_CAJA',
        descripcion: 'Importó datos de flujo de caja del 2025-01-21',
        entidad: 'Flujo de Caja',
        entidadId: '2025-01-21',
        fechaHora: '2025-01-21T16:45:00Z',
        ip: '192.168.1.105',
        navegador: 'Chrome 120.0.0.0'
      }
    ];
    setLogs(mockLogs);
  };

  const getBrowserInfo = (): string => {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Chrome')) return 'Chrome';
    if (userAgent.includes('Firefox')) return 'Firefox';
    if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) return 'Safari';
    if (userAgent.includes('Edge')) return 'Edge';
    return 'Unknown';
  };

  const getClientIP = async (): Promise<string> => {
    try {
      // En un entorno de producción, esto se obtendría del servidor
      // Por ahora retornamos una IP simulada basada en el timestamp
      const timestamp = Date.now();
      const ip = `192.168.1.${(timestamp % 200) + 1}`;
      return ip;
    } catch {
      return '192.168.1.100';
    }
  };

  const addLog = async (logData: Omit<AuditLog, 'id' | 'fechaHora' | 'ip' | 'navegador' | 'usuario'>) => {
    const ip = await getClientIP();
    const navegador = getBrowserInfo();
    
    const newLog: AuditLog = {
      ...logData,
      id: Date.now().toString(),
      usuario,
      fechaHora: new Date().toISOString(),
      ip,
      navegador
    };

    setLogs(prevLogs => [newLog, ...prevLogs]);
    return newLog;
  };

  // Funciones específicas para diferentes tipos de acciones
  const logCashFlowChange = async (
    fecha: string,
    descripcion: string,
    valorAnterior?: any,
    valorNuevo?: any
  ) => {
    return addLog({
      accion: 'EDITAR',
      modulo: 'FLUJO_CAJA',
      descripcion,
      entidad: 'Flujo de Caja Diario',
      entidadId: fecha,
      valorAnterior,
      valorNuevo
    });
  };

  const logCompanyAction = async (
    accion: 'CREAR' | 'EDITAR' | 'ELIMINAR',
    companyId: string,
    descripcion: string,
    valorAnterior?: any,
    valorNuevo?: any
  ) => {
    return addLog({
      accion,
      modulo: 'EMPRESAS',
      descripcion,
      entidad: 'Empresa',
      entidadId: companyId,
      valorAnterior,
      valorNuevo
    });
  };

  const logAccountAction = async (
    accion: 'CREAR' | 'EDITAR' | 'ELIMINAR',
    accountId: string,
    descripcion: string,
    valorAnterior?: any,
    valorNuevo?: any
  ) => {
    return addLog({
      accion,
      modulo: 'CUENTAS',
      descripcion,
      entidad: 'Cuenta Bancaria',
      entidadId: accountId,
      valorAnterior,
      valorNuevo
    });
  };

  const logReportAction = async (
    accion: 'EXPORTAR' | 'CONSULTAR',
    descripcion: string,
    entidadId?: string
  ) => {
    return addLog({
      accion,
      modulo: 'REPORTES',
      descripcion,
      entidad: 'Reporte',
      entidadId
    });
  };

  const logUserAction = async (
    accion: 'CREAR' | 'EDITAR' | 'ELIMINAR',
    userId: string,
    descripcion: string,
    valorAnterior?: any,
    valorNuevo?: any
  ) => {
    return addLog({
      accion,
      modulo: 'USUARIOS',
      descripcion,
      entidad: 'Usuario',
      entidadId: userId,
      valorAnterior,
      valorNuevo
    });
  };

  const logImportAction = async (descripcion: string, entidadId?: string) => {
    return addLog({
      accion: 'IMPORTAR',
      modulo: 'FLUJO_CAJA',
      descripcion,
      entidad: 'Datos',
      entidadId
    });
  };

  const clearLogs = () => {
    setLogs([]);
    localStorage.removeItem('auditLogs');
  };

  return {
    logs,
    addLog,
    logCashFlowChange,
    logCompanyAction,
    logAccountAction,
    logReportAction,
    logUserAction,
    logImportAction,
    clearLogs
  };
}
