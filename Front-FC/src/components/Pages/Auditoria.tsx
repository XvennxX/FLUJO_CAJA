import { useState, useEffect } from 'react';
import { Search, Eye, User, Clock, Edit, Trash2, Plus, FileText } from 'lucide-react';
import { useAuditoria, AuditLog } from '../../hooks/useAuditoria';

export default function Auditoria() {
  const { logs: auditLogs } = useAuditoria();
  const [filteredLogs, setFilteredLogs] = useState<AuditLog[]>(auditLogs);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAction, setSelectedAction] = useState<string>('TODAS');
  const [selectedModule, setSelectedModule] = useState<string>('TODOS');
  const [selectedUser, setSelectedUser] = useState<string>('TODOS');
  const [dateRange, setDateRange] = useState({
    desde: '2025-01-20',
    hasta: '2025-01-22'
  });
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const actions = ['TODAS', 'CREAR', 'EDITAR', 'ELIMINAR', 'CONSULTAR', 'EXPORTAR', 'IMPORTAR'];
  const modules = ['TODOS', 'FLUJO_CAJA', 'EMPRESAS', 'CUENTAS', 'REPORTES', 'USUARIOS'];
  const users = ['TODOS', ...Array.from(new Set(auditLogs.map(log => log.usuario)))];

  useEffect(() => {
    setFilteredLogs(auditLogs);
  }, [auditLogs]);

  useEffect(() => {
    filterLogs();
  }, [searchTerm, selectedAction, selectedModule, selectedUser, dateRange, auditLogs]);

  const filterLogs = () => {
    let filtered = auditLogs;

    // Filtro por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(log =>
        log.descripcion.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.usuario.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.entidad.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtro por acción
    if (selectedAction !== 'TODAS') {
      filtered = filtered.filter(log => log.accion === selectedAction);
    }

    // Filtro por módulo
    if (selectedModule !== 'TODOS') {
      filtered = filtered.filter(log => log.modulo === selectedModule);
    }

    // Filtro por usuario
    if (selectedUser !== 'TODOS') {
      filtered = filtered.filter(log => log.usuario === selectedUser);
    }

    // Filtro por rango de fechas
    if (dateRange.desde && dateRange.hasta) {
      filtered = filtered.filter(log => {
        const logDate = new Date(log.fechaHora).toISOString().split('T')[0];
        return logDate >= dateRange.desde && logDate <= dateRange.hasta;
      });
    }

    setFilteredLogs(filtered.sort((a, b) => new Date(b.fechaHora).getTime() - new Date(a.fechaHora).getTime()));
  };

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'CREAR': return <Plus className="w-4 h-4 text-green-600" />;
      case 'EDITAR': return <Edit className="w-4 h-4 text-blue-600" />;
      case 'ELIMINAR': return <Trash2 className="w-4 h-4 text-red-600" />;
      case 'CONSULTAR': return <Eye className="w-4 h-4 text-gray-600 dark:text-gray-400" />;
      case 'EXPORTAR': return <FileText className="w-4 h-4 text-purple-600" />;
      case 'IMPORTAR': return <FileText className="w-4 h-4 text-orange-600" />;
      default: return <FileText className="w-4 h-4 text-gray-600 dark:text-gray-400" />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'CREAR': return 'bg-green-100 text-green-800';
      case 'EDITAR': return 'bg-blue-100 text-blue-800';
      case 'ELIMINAR': return 'bg-red-100 text-red-800';
      case 'CONSULTAR': return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
      case 'EXPORTAR': return 'bg-purple-100 text-purple-800';
      case 'IMPORTAR': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const getModuleColor = (module: string) => {
    switch (module) {
      case 'FLUJO_CAJA': return 'bg-bolivar-100 text-bolivar-800';
      case 'EMPRESAS': return 'bg-gold-100 text-gold-800';
      case 'CUENTAS': return 'bg-green-100 text-green-800';
      case 'REPORTES': return 'bg-purple-100 text-purple-800';
      case 'USUARIOS': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const showLogDetails = (log: AuditLog) => {
    setSelectedLog(log);
    setShowDetails(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Auditoría del Sistema</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Historial de actividades y cambios realizados por los usuarios</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Total de registros: <span className="font-semibold text-bolivar-600">{filteredLogs.length}</span>
            </div>
          </div>
        </div>

        {/* Filtros */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {/* Búsqueda */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar por descripción, usuario o entidad..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
            />
          </div>

          {/* Filtro por acción */}
          <select
            value={selectedAction}
            onChange={(e) => setSelectedAction(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
          >
            {actions.map(action => (
              <option key={action} value={action}>{action}</option>
            ))}
          </select>

          {/* Filtro por módulo */}
          <select
            value={selectedModule}
            onChange={(e) => setSelectedModule(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
          >
            {modules.map(module => (
              <option key={module} value={module}>{module.replace('_', ' ')}</option>
            ))}
          </select>

          {/* Filtro por usuario */}
          <select
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
          >
            {users.map(user => (
              <option key={user} value={user}>{user}</option>
            ))}
          </select>
        </div>

        {/* Filtros de fecha */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha desde</label>
            <input
              type="date"
              value={dateRange.desde}
              onChange={(e) => setDateRange(prev => ({ ...prev, desde: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha hasta</label>
            <input
              type="date"
              value={dateRange.hasta}
              onChange={(e) => setDateRange(prev => ({ ...prev, hasta: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
            />
          </div>
        </div>
      </div>

      {/* Tabla de logs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-bolivar-600 text-white">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold">Fecha y Hora</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Usuario</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Acción</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Módulo</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">Descripción</th>
                <th className="px-4 py-3 text-left text-sm font-semibold">IP</th>
                <th className="px-4 py-3 text-center text-sm font-semibold">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log, index) => (
                <tr 
                  key={log.id} 
                  className={`${index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-900' : 'bg-white dark:bg-gray-800'} hover:bg-bolivar-50 transition-colors`}
                >
                  <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span>{formatDateTime(log.fechaHora)}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex items-center space-x-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900 dark:text-white">{log.usuario}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex items-center space-x-2">
                      {getActionIcon(log.accion)}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionColor(log.accion)}`}>
                        {log.accion}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getModuleColor(log.modulo)}`}>
                      {log.modulo.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900 dark:text-white max-w-xs truncate" title={log.descripcion}>
                    {log.descripcion}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 font-mono">
                    {log.ip}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => showLogDetails(log)}
                      className="inline-flex items-center px-3 py-1 border border-gray-300 dark:border-gray-600 shadow-sm text-xs font-medium rounded text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-bolivar-500"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      Ver detalles
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Estado vacío */}
        {filteredLogs.length === 0 && (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No se encontraron registros</h3>
            <p className="text-gray-500 dark:text-gray-400">Ajusta los filtros para ver más resultados.</p>
          </div>
        )}
      </div>

      {/* Modal de detalles */}
      {showDetails && selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Detalles de la Auditoría</h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600 dark:text-gray-400"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="px-6 py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Usuario</label>
                  <p className="mt-1 text-sm text-gray-900 dark:text-white">{selectedLog.usuario}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Fecha y Hora</label>
                  <p className="mt-1 text-sm text-gray-900 dark:text-white">{formatDateTime(selectedLog.fechaHora)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Acción</label>
                  <div className="mt-1 flex items-center space-x-2">
                    {getActionIcon(selectedLog.accion)}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionColor(selectedLog.accion)}`}>
                      {selectedLog.accion}
                    </span>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Módulo</label>
                  <span className={`inline-block mt-1 px-2 py-1 rounded-full text-xs font-medium ${getModuleColor(selectedLog.modulo)}`}>
                    {selectedLog.modulo.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">IP</label>
                  <p className="mt-1 text-sm text-gray-900 dark:text-white font-mono">{selectedLog.ip}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Navegador</label>
                  <p className="mt-1 text-sm text-gray-900 dark:text-white">{selectedLog.navegador}</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Descripción</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-white">{selectedLog.descripcion}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Entidad</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-white">
                  {selectedLog.entidad} {selectedLog.entidadId && `(ID: ${selectedLog.entidadId})`}
                </p>
              </div>

              {(selectedLog.valorAnterior || selectedLog.valorNuevo) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedLog.valorAnterior && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Valor Anterior</label>
                      <pre className="mt-1 text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded border overflow-x-auto">
                        {JSON.stringify(selectedLog.valorAnterior, null, 2)}
                      </pre>
                    </div>
                  )}
                  {selectedLog.valorNuevo && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Valor Nuevo</label>
                      <pre className="mt-1 text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded border overflow-x-auto">
                        {JSON.stringify(selectedLog.valorNuevo, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
              <button
                onClick={() => setShowDetails(false)}
                className="px-4 py-2 bg-bolivar-600 text-white rounded-lg hover:bg-bolivar-700 transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


