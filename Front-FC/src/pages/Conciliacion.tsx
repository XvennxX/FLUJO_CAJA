import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Check, 
  X, 
  Building2, 
  FileText,
  Lock,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  Edit,
  Save,
  RefreshCw,
  Calculator,
  MessageSquare,
  ChevronRight
} from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { useConciliacion } from '../../hooks/useConciliacion';
import { formatCurrency } from '../../utils/formatters';

const Conciliacion: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [editingCentralizadora, setEditingCentralizadora] = useState<number | null>(null);
  const [tempCentralizadora, setTempCentralizadora] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  
  // Estados para modal de observaciones
  const [showObservacionesModal, setShowObservacionesModal] = useState(false);
  const [empresaSeleccionada, setEmpresaSeleccionada] = useState<number | null>(null);
  const [observacionesTemp, setObservacionesTemp] = useState<string>('');
  const [observacionesSoloLectura, setObservacionesSoloLectura] = useState(false);
  
  const { 
    conciliacionData,
    obtenerConciliacionPorFecha,
    actualizarTotalCentralizadora,
    evaluarConciliacion,
    confirmarConciliacion,
    cerrarConciliacion,
    evaluarTodasConciliaciones,
    cerrarTodasConciliaciones
  } = useConciliacion();

  // Verificar autenticación al cargar
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
  }, []);

  // Cargar datos al cambiar fecha
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const cargarDatos = async () => {
      setLoading(true);
      try {
        await obtenerConciliacionPorFecha(selectedDate);
      } catch (error) {
        console.error('Error al cargar conciliación:', error);
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
  }, [selectedDate, obtenerConciliacionPorFecha, isAuthenticated]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pendiente':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'evaluado':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'confirmado':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'cerrado':
        return <Lock className="h-5 w-5 text-gray-500 dark:text-gray-400" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800';
      case 'evaluado':
        return 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800';
      case 'confirmado':
        return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800';
      case 'cerrado':
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-200 dark:border-gray-700';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-200 dark:border-gray-700';
    }
  };

  const getDiferenciaColor = (diferencia: number) => {
    // Convertir a número y redondear para evitar problemas de precisión
    const diff = Number(diferencia);
    const rounded = Math.round(diff * 100) / 100; // Redondear a 2 decimales
    
    if (rounded === 0) {
      return 'text-green-600 dark:text-green-400'; // Verde: Cuadra perfecto
    } else if (rounded > 0) {
      return 'text-blue-600 dark:text-blue-400'; // Azul: Total > Centralizadora (excedente)
    } else {
      return 'text-red-600 dark:text-red-400'; // Rojo: Total < Centralizadora (déficit)
    }
  };

  const handleEditCentralizadora = (id: number, currentValue: number) => {
    setEditingCentralizadora(id);
    setTempCentralizadora(currentValue.toString());
  };

  const handleSaveCentralizadora = async (id: number) => {
    try {
      const valor = parseFloat(tempCentralizadora) || 0;
      await actualizarTotalCentralizadora(id, selectedDate, valor);
      setEditingCentralizadora(null);
      setTempCentralizadora('');
    } catch (error) {
      console.error('Error al actualizar total centralizadora:', error);
    }
  };

  const handleCancelEdit = () => {
    setEditingCentralizadora(null);
    setTempCentralizadora('');
  };

  const handleOpenObservaciones = (empresaId: number, observacionesActuales: string | undefined, estadoCerrado: boolean = false) => {
    setEmpresaSeleccionada(empresaId);
    setObservacionesTemp(observacionesActuales || '');
    setObservacionesSoloLectura(estadoCerrado);
    setShowObservacionesModal(true);
  };

  const handleSaveObservaciones = async () => {
    if (empresaSeleccionada === null) return;
    
    try {
      // Buscar la empresa actual para obtener su total centralizadora
      const empresa = conciliacionData?.empresas.find(e => e.id === empresaSeleccionada);
      if (!empresa) return;
      
      await actualizarTotalCentralizadora(
        empresaSeleccionada, 
        selectedDate, 
        empresa.total_centralizadora || 0,
        observacionesTemp
      );
      
      setShowObservacionesModal(false);
      setEmpresaSeleccionada(null);
      setObservacionesTemp('');
    } catch (error) {
      console.error('Error al guardar observaciones:', error);
    }
  };

  const handleCloseObservacionesModal = () => {
    setShowObservacionesModal(false);
    setEmpresaSeleccionada(null);
    setObservacionesTemp('');
    setObservacionesSoloLectura(false);
  };

  const handleCambiarEstado = async (empresaId: number, nuevoEstado: string, estadoActual: string) => {
    try {
      const nuevoEstadoLower = nuevoEstado.toLowerCase();
      const estadoActualLower = estadoActual.toLowerCase();
      
      // Si es el mismo estado, no hacer nada
      if (nuevoEstadoLower === estadoActualLower) return;
      
      // Llamar a la función apropiada según el nuevo estado
      if (nuevoEstadoLower === 'evaluado') {
        await evaluarConciliacion(empresaId, selectedDate);
      } else if (nuevoEstadoLower === 'confirmado') {
        await confirmarConciliacion(empresaId, selectedDate);
      } else if (nuevoEstadoLower === 'cerrado') {
        await cerrarConciliacion(empresaId, selectedDate);
      }
    } catch (error) {
      console.error('Error cambiando estado:', error);
      // Recargar datos para mostrar el estado actual
      await obtenerConciliacionPorFecha(selectedDate);
    }
  };

  // Si no está autenticado, mostrar mensaje
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Lock className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Acceso Restringido
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Debes iniciar sesión para acceder a la funcionalidad de conciliación contable.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <Calculator className="h-8 w-8 text-bolivar-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Conciliación Contable</h1>
            <p className="text-gray-600 dark:text-gray-400">Conciliación diaria por compañía</p>
          </div>
        </div>
        
        {/* Selector de Fecha */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-gray-500" />
            <input
              type="date"
              value={format(selectedDate, 'yyyy-MM-dd')}
              onChange={(e) => {
                // Parsear la fecha como hora local para evitar problemas de zona horaria
                const [year, month, day] = e.target.value.split('-').map(Number);
                setSelectedDate(new Date(year, month - 1, day));
              }}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent"
            />
          </div>
          
          {loading && (
            <RefreshCw className="h-5 w-5 text-bolivar-600 animate-spin" />
          )}
        </div>
      </div>

      {/* Información de la fecha seleccionada */}
      {conciliacionData && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-bolivar-600" />
              <span className="text-lg font-medium text-gray-900 dark:text-white">
                Conciliación del {format(selectedDate, 'dd \'de\' MMMM \'de\' yyyy', { locale: es })}
              </span>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {conciliacionData.empresas.length} empresa(s)
            </div>
          </div>
        </div>
      )}

      {/* Tabla de Conciliación por Compañía */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
            <Building2 className="h-5 w-5" />
            <span>Conciliación por Compañía</span>
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Nombre de la Compañía
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Pagaduría
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Tesorería
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Total Centralizadora
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Diferencia
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center">
                    <div className="flex items-center justify-center space-x-2">
                      <RefreshCw className="h-5 w-5 animate-spin text-bolivar-600" />
                      <span className="text-gray-500 dark:text-gray-400">Cargando conciliación...</span>
                    </div>
                  </td>
                </tr>
              ) : conciliacionData?.empresas.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                    No hay datos de conciliación para la fecha seleccionada
                  </td>
                </tr>
              ) : (
                conciliacionData?.empresas.map((empresa) => (
                  <tr key={empresa.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-3">
                        <Building2 className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {empresa.compania.nombre}
                        </span>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 text-center">
                      <span className={`text-sm font-semibold ${empresa.total_pagaduria >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                        {formatCurrency(empresa.total_pagaduria)}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4 text-center">
                      <span className={`text-sm font-semibold ${empresa.total_tesoreria >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                        {formatCurrency(empresa.total_tesoreria)}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4 text-center">
                      <span className={`text-lg font-bold ${empresa.total_calculado >= 0 ? 'text-bolivar-700' : 'text-red-700'}`}>
                        {formatCurrency(empresa.total_calculado)}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4 text-center">
                      {editingCentralizadora === empresa.id ? (
                        <div className="flex items-center space-x-2">
                          <input
                            type="number"
                            value={tempCentralizadora}
                            onChange={(e) => setTempCentralizadora(e.target.value)}
                            className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-bolivar-500 focus:border-transparent"
                            step="0.01"
                          />
                          <button
                            onClick={() => handleSaveCentralizadora(empresa.id)}
                            className="p-1 text-green-600 hover:text-green-800"
                            title="Guardar"
                          >
                            <Save className="h-4 w-4" />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="p-1 text-red-600 hover:text-red-800"
                            title="Cancelar"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center space-x-2">
                          <span className="text-sm font-semibold text-gray-900 dark:text-white">
                            {formatCurrency(empresa.total_centralizadora || 0)}
                          </span>
                          {/* Solo permitir editar si NO está cerrado */}
                          {empresa.estado.toLowerCase() !== 'cerrado' && (
                            <button
                              onClick={() => handleEditCentralizadora(empresa.id, empresa.total_centralizadora || 0)}
                              className="p-1 text-gray-500 hover:text-gray-700"
                              title="Editar total centralizadora"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      )}
                    </td>
                    
                    <td className="px-6 py-4 text-center">
                      <span className={`text-sm font-bold ${getDiferenciaColor(empresa.diferencia || 0)}`}>
                        {formatCurrency(empresa.diferencia || 0)}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4 text-center">
                      {/* Estado: solo mostrar badge con icono */}
                      <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-lg text-xs font-medium border ${getStatusColor(empresa.estado)}`}>
                        {getStatusIcon(empresa.estado)}
                        <span className="capitalize">{empresa.estado}</span>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center space-x-2">
                        {/* Botón de observaciones - Siempre visible excepto en Cerrado */}
                        {empresa.estado.toLowerCase() !== 'cerrado' && (
                          <button
                            onClick={() => handleOpenObservaciones(empresa.id, empresa.observaciones, false)}
                            className={`p-2 ${empresa.observaciones ? 'text-purple-600 hover:text-purple-800 hover:bg-purple-100' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'} rounded-lg transition-colors`}
                            title={empresa.observaciones ? 'Ver/Editar observaciones' : 'Agregar observaciones'}
                          >
                            <MessageSquare className="h-5 w-5" />
                          </button>
                        )}
                        
                        {/* Botón para confirmar: visible en Evaluado y Cerrado (para reabrir) */}
                        {(empresa.estado.toLowerCase() === 'evaluado' || empresa.estado.toLowerCase() === 'cerrado') && (
                          <button
                            onClick={() => handleCambiarEstado(empresa.id, 'Confirmado', empresa.estado)}
                            className="p-2 text-green-600 hover:text-green-800 hover:bg-green-100 rounded-lg transition-colors"
                            title={empresa.estado.toLowerCase() === 'cerrado' ? 'Reabrir como Confirmado' : 'Confirmar conciliación'}
                          >
                            <CheckCircle className="h-5 w-5" />
                          </button>
                        )}
                        
                        {/* Botón para cerrar: visible en Evaluado, Confirmado y Cerrado (para alternar) */}
                        {(empresa.estado.toLowerCase() === 'evaluado' || empresa.estado.toLowerCase() === 'confirmado' || empresa.estado.toLowerCase() === 'cerrado') && (
                          <button
                            onClick={() => handleCambiarEstado(empresa.id, 'Cerrado', empresa.estado)}
                            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
                            title="Cerrar conciliación"
                            disabled={empresa.estado.toLowerCase() === 'cerrado'}
                          >
                            <Lock className="h-5 w-5" />
                          </button>
                        )}
                        
                        {/* Si está cerrado, solo mostrar icono de observaciones sin editar */}
                        {empresa.estado.toLowerCase() === 'cerrado' && empresa.observaciones && (
                          <button
                            onClick={() => handleOpenObservaciones(empresa.id, empresa.observaciones, true)}
                            className="p-2 text-purple-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                            title="Ver observaciones (solo lectura)"
                          >
                            <MessageSquare className="h-5 w-5" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Acciones Globales */}
      {conciliacionData && conciliacionData.empresas.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Acciones de Cierre</h3>
          <div className="flex flex-wrap gap-3">
            <button
              className="flex items-center space-x-2 px-4 py-2 bg-orange-100 text-orange-800 border border-orange-300 rounded-lg hover:bg-orange-200 transition-colors"
              onClick={() => evaluarTodasConciliaciones(selectedDate)}
              disabled={loading}
            >
              <FileText className="h-4 w-4" />
              <span>Evaluar Todas</span>
            </button>
            
            <button
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              onClick={() => cerrarTodasConciliaciones(selectedDate)}
              disabled={loading}
            >
              <Lock className="h-4 w-4" />
              <span>Cerrar Todas</span>
            </button>
          </div>
        </div>
      )}

      {/* Modal de Observaciones */}
      {showObservacionesModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
                <MessageSquare className="h-5 w-5 text-bolivar-600" />
                <span>Observaciones de Conciliación</span>
                {observacionesSoloLectura && (
                  <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                    Solo lectura
                  </span>
                )}
              </h3>
              <button
                onClick={handleCloseObservacionesModal}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="px-6 py-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Observaciones
              </label>
              <textarea
                value={observacionesTemp}
                onChange={(e) => setObservacionesTemp(e.target.value)}
                rows={6}
                readOnly={observacionesSoloLectura}
                disabled={observacionesSoloLectura}
                className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent resize-none ${observacionesSoloLectura ? 'opacity-60 cursor-not-allowed' : ''}`}
                placeholder={observacionesSoloLectura ? '' : 'Ingrese observaciones sobre esta conciliación...'}
              />
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
              <button
                onClick={handleCloseObservacionesModal}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                {observacionesSoloLectura ? 'Cerrar' : 'Cancelar'}
              </button>
              {!observacionesSoloLectura && (
                <button
                  onClick={handleSaveObservaciones}
                  className="px-4 py-2 text-sm font-medium text-white bg-bolivar-600 hover:bg-bolivar-700 rounded-lg transition-colors flex items-center space-x-2"
                >
                  <Save className="h-4 w-4" />
                  <span>Guardar</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Conciliacion;


