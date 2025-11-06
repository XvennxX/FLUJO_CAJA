import { useState, useEffect } from 'react';
import { Search, Eye, User, Clock, Edit, Trash2, Plus, FileText, RefreshCw, BarChart3 } from 'lucide-react';
import { useAuditoria, RegistroAuditoria, FiltrosAuditoria, UsuarioActivo } from '../hooks/useAuditoriaReal';
import { useAuth } from '../contexts/AuthContext';

export default function Auditoria() {
  const { user } = useAuth();
  const {
    registros,
    loading,
    error,
    usuariosActivos,
    totalRegistros,
    totalPaginas,
    obtenerRegistros,
    obtenerEstadisticas,
    estadisticas
  } = useAuditoria();

  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAction, setSelectedAction] = useState<string>('TODAS');
  const [selectedModule, setSelectedModule] = useState<string>('TODOS');
  const [selectedUser, setSelectedUser] = useState<string>('TODOS');
  const [dateRange, setDateRange] = useState({
    desde: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // Últimos 7 días
    hasta: new Date().toISOString().split('T')[0] // Hoy
  });
  
  // Estados para paginación
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  
  // Estados para detalles
  const [selectedLog, setSelectedLog] = useState<RegistroAuditoria | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const actions = ['TODAS', 'CREATE', 'UPDATE', 'DELETE', 'READ', 'EXPORT', 'IMPORT'];
  const modules = ['TODOS', 'FLUJO_CAJA', 'EMPRESAS', 'CUENTAS', 'REPORTES', 'USUARIOS', 'CONCEPTOS', 'SISTEMA'];

  // Función para aplicar filtros y cargar datos
  const aplicarFiltros = () => {
    const filtros: FiltrosAuditoria = {
      pagina: currentPage,
      limite: pageSize,
      busqueda: searchTerm || undefined,
      accion: selectedAction !== 'TODAS' ? selectedAction : undefined,
      modulo: selectedModule !== 'TODOS' ? selectedModule : undefined,
      usuario_id: selectedUser !== 'TODOS' ? parseInt(selectedUser) : undefined,
      fecha_inicio: dateRange.desde || undefined,
      fecha_fin: dateRange.hasta || undefined
    };

    console.log('🔍 Filtros aplicados:', filtros); // Debug
    obtenerRegistros(filtros);
  };

  // Cargar datos iniciales
  useEffect(() => {
    aplicarFiltros();
  }, [currentPage, pageSize]);

  // Aplicar filtros cuando cambien (excepto paginación)
  useEffect(() => {
    if (currentPage === 1) {
      aplicarFiltros();
    } else {
      setCurrentPage(1); // Esto triggereará el useEffect anterior
    }
  }, [searchTerm, selectedAction, selectedModule, selectedUser, dateRange]);

  // Cargar estadísticas
  useEffect(() => {
    obtenerEstadisticas(dateRange.desde, dateRange.hasta);
  }, [dateRange]);

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

  const showLogDetails = (log: RegistroAuditoria) => {
    setSelectedLog(log);
    setShowDetails(true);
  };

  const refrescarDatos = () => {
    aplicarFiltros();
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
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Total de registros: <span className="font-semibold text-bolivar-600">{totalRegistros}</span>
            </div>
            <button
              onClick={refrescarDatos}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-bolivar-600 text-white rounded-lg hover:bg-bolivar-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Refrescar datos"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refrescar</span>
            </button>
          </div>
        </div>

        {/* Filtros */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {/* Búsqueda */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Buscar</label>
            <Search className="absolute left-3 top-1/2 transform translate-y-0.5 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Descripción, usuario o entidad..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
            />
          </div>

          {/* Filtro por acción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Acción</label>
            <select
              value={selectedAction}
              onChange={(e) => setSelectedAction(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
            >
              {actions.map(action => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>
          </div>

          {/* Filtro por módulo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Módulo</label>
            <select
              value={selectedModule}
              onChange={(e) => setSelectedModule(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
            >
              {modules.map(module => (
                <option key={module} value={module}>{module.replace('_', ' ')}</option>
              ))}
            </select>
          </div>

          {/* Filtro por usuario */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Usuario</label>
            <select
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-bolivar-500"
            >
              <option value="TODOS">Todos los usuarios</option>
              {usuariosActivos.map(usuario => (
                <option key={usuario.id} value={usuario.id.toString()}>{usuario.nombre}</option>
              ))}
            </select>
          </div>
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
              {registros.map((log, index) => (
                <tr 
                  key={log.id} 
                  className={`${index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-900' : 'bg-white dark:bg-gray-800'} hover:bg-bolivar-50 transition-colors`}
                >
                  <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span>{formatDateTime(log.fecha_hora)}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex items-center space-x-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900 dark:text-white">{log.usuario_nombre}</span>
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
                    {log.ip_address}
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

        {/* Estado de carga */}
        {loading && (
          <div className="p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-bolivar-600 mb-4"></div>
            <p className="text-gray-500 dark:text-gray-400">Cargando registros de auditoría...</p>
          </div>
        )}

        {/* Estado de error */}
        {error && (
          <div className="p-12 text-center">
            <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-800 rounded-lg p-4 max-w-md mx-auto">
              <p className="text-red-700 dark:text-red-300 font-medium">Error al cargar los datos</p>
              <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error}</p>
              <button
                onClick={refrescarDatos}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
              >
                <RefreshCw className="w-4 h-4 inline mr-1" />
                Reintentar
              </button>
            </div>
          </div>
        )}

        {/* Estado vacío */}
        {registros.length === 0 && !loading && !error && (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No se encontraron registros</h3>
            <p className="text-gray-500 dark:text-gray-400">Ajusta los filtros para ver más resultados.</p>
          </div>
        )}

        {/* Paginación */}
        {totalPaginas > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <div className="text-sm text-gray-700 dark:text-gray-300">
              Página {currentPage} de {totalPaginas} ({totalRegistros} registros total)
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Anterior
              </button>
              <span className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400">
                {currentPage} / {totalPaginas}
              </span>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPaginas}
                className="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Siguiente
              </button>
            </div>
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
                  <p className="mt-1 text-sm text-gray-900 dark:text-white">{selectedLog.usuario_nombre}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Fecha y Hora</label>
                  <p className="mt-1 text-sm text-gray-900 dark:text-white">{formatDateTime(selectedLog.fecha_hora)}</p>
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
                  <p className="mt-1 text-sm text-gray-900 dark:text-white font-mono">{selectedLog.ip_address}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Navegador</label>
                  <p className="mt-1 text-sm text-gray-900 dark:text-white">{selectedLog.user_agent || 'Desconocido'}</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Descripción</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-white">{selectedLog.descripcion}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Entidad</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-white">
                  {selectedLog.entidad} {selectedLog.entidad_id && `(ID: ${selectedLog.entidad_id})`}
                </p>
              </div>

              {(selectedLog.valores_anteriores || selectedLog.valores_nuevos) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedLog.valores_anteriores && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Valor Anterior</label>
                      <pre className="mt-1 text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded border overflow-x-auto">
                        {JSON.stringify(selectedLog.valores_anteriores, null, 2)}
                      </pre>
                    </div>
                  )}
                  {selectedLog.valores_nuevos && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Valor Nuevo</label>
                      <pre className="mt-1 text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded border overflow-x-auto">
                        {JSON.stringify(selectedLog.valores_nuevos, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {/* Información adicional del sistema */}
              {(selectedLog.endpoint || selectedLog.metodo_http || selectedLog.duracion_ms) && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Información Técnica</h4>
                  {selectedLog.endpoint && (
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                      <strong>Endpoint:</strong> <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded">{selectedLog.metodo_http} {selectedLog.endpoint}</code>
                    </p>
                  )}
                  {selectedLog.duracion_ms && (
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                      <strong>Duración:</strong> {selectedLog.duracion_ms}ms
                    </p>
                  )}
                  {selectedLog.resultado !== 'EXITOSO' && selectedLog.mensaje_error && (
                    <div className="mt-2 p-2 bg-red-50 dark:bg-red-900 rounded">
                      <p className="text-xs text-red-600 dark:text-red-400">
                        <strong>Error:</strong> {selectedLog.mensaje_error}
                      </p>
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


