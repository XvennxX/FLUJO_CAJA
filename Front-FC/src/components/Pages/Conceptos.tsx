import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, AlertCircle, CheckCircle, X, Save, Building, Users, Globe } from 'lucide-react';
import { useConceptosFlujoCaja, ConceptoFlujoCaja } from '../../hooks/useConceptosFlujoCaja';

interface ConceptoFormData {
  nombre: string;
  codigo: string;
  tipo: string;
  area: 'tesoreria' | 'pagaduria' | 'ambas';
  orden_display: number;
  activo: boolean;
  depende_de_concepto_id?: number;
  tipo_dependencia?: 'copia' | 'suma' | 'resta';
}

const TIPOS_MOVIMIENTO = [
  'pagaduria',
  'renta fija',
  'renta variable', 
  'derivados',
  'divisas',
  'otros'
];

const Conceptos: React.FC = () => {
  const { conceptos, loading, error, refetchConceptos } = useConceptosFlujoCaja();
  const [activeTab, setActiveTab] = useState<'tesoreria' | 'pagaduria' | 'ambas'>('tesoreria');
  const [searchTerm, setSearchTerm] = useState('');
  const [showInactiveOnly, setShowInactiveOnly] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingConcepto, setEditingConcepto] = useState<ConceptoFlujoCaja | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  const [formData, setFormData] = useState<ConceptoFormData>({
    nombre: '',
    codigo: '',
    tipo: '',
    area: 'tesoreria',
    orden_display: 0,
    activo: true
  });

  // Filtrar conceptos por área activa
  const getConceptosByArea = (area: 'tesoreria' | 'pagaduria' | 'ambas') => {
    return conceptos.filter(concepto => {
      const matchesArea = concepto.area === area || (area === 'ambas' && concepto.area === 'ambas');
      const matchesSearch = concepto.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           concepto.codigo?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           concepto.tipo?.toLowerCase().includes(searchTerm.toLowerCase());
      // Si showInactiveOnly es true, mostrar solo inactivos; si es false, mostrar todos
      const matchesStatus = showInactiveOnly ? !concepto.activo : true;
      return matchesArea && matchesSearch && matchesStatus;
    }).sort((a, b) => a.orden_display - b.orden_display);
  };

  // Get statistics for each area
  const getAreaStats = (area: 'tesoreria' | 'pagaduria' | 'ambas') => {
    const conceptosArea = conceptos.filter(c => c.area === area || (area === 'ambas' && c.area === 'ambas'));
    return {
      total: conceptosArea.length,
      activos: conceptosArea.filter(c => c.activo).length,
      inactivos: conceptosArea.filter(c => !c.activo).length
    };
  };

  // Limpiar formulario
  const resetForm = () => {
    setFormData({
      nombre: '',
      codigo: '',
      tipo: '',
      area: activeTab,
      orden_display: 0,
      activo: true
    });
    setEditingConcepto(null);
  };

  // Abrir modal para crear
  const handleCreate = (area?: 'tesoreria' | 'pagaduria' | 'ambas') => {
    resetForm();
    if (area) {
      setFormData(prev => ({ ...prev, area }));
    }
    setShowModal(true);
  };

  // Abrir modal para editar
  const handleEdit = (concepto: ConceptoFlujoCaja) => {
    setEditingConcepto(concepto);
    setFormData({
      nombre: concepto.nombre,
      codigo: concepto.codigo || '',
      tipo: concepto.tipo || '',
      area: concepto.area,
      orden_display: concepto.orden_display,
      activo: concepto.activo,
      depende_de_concepto_id: concepto.depende_de_concepto_id,
      tipo_dependencia: concepto.tipo_dependencia
    });
    setShowModal(true);
  };

  // Eliminar concepto
  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de que desea eliminar este concepto?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/api/conceptos-flujo-caja/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Error al eliminar el concepto');
      }

      setNotification({ type: 'success', message: 'Concepto eliminado exitosamente' });
      refetchConceptos();
    } catch (error) {
      setNotification({ type: 'error', message: 'Error al eliminar el concepto' });
    }
  };

  // Guardar concepto (crear o actualizar)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const token = localStorage.getItem('access_token');
      const url = editingConcepto 
        ? `http://localhost:8000/api/v1/api/conceptos-flujo-caja/${editingConcepto.id}`
        : 'http://localhost:8000/api/v1/api/conceptos-flujo-caja/';
      
      const method = editingConcepto ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al guardar el concepto');
      }

      setNotification({ 
        type: 'success', 
        message: editingConcepto ? 'Concepto actualizado exitosamente' : 'Concepto creado exitosamente'
      });
      
      setShowModal(false);
      resetForm();
      refetchConceptos();
    } catch (error) {
      setNotification({ 
        type: 'error', 
        message: error instanceof Error ? error.message : 'Error al guardar el concepto' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Obtener conceptos disponibles para dependencias
  const getConceptosParaDependencia = () => {
    return conceptos.filter(c => 
      c.id !== editingConcepto?.id && (c.area === formData.area || c.area === 'ambas')
    );
  };

  // Auto-ocultar notificaciones
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Cambiar formulario area cuando cambie tab activo
  useEffect(() => {
    if (!editingConcepto) {
      setFormData(prev => ({ ...prev, area: activeTab }));
    }
  }, [activeTab, editingConcepto]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando conceptos...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
          <span className="text-red-700 dark:text-red-300">Error: {error}</span>
        </div>
      </div>
    );
  }

  const tesoreriaStats = getAreaStats('tesoreria');
  const pagaduriaStats = getAreaStats('pagaduria');
  const ambasStats = getAreaStats('ambas');
  const currentAreaConceptos = getConceptosByArea(activeTab);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Gestión de Conceptos
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Administra los conceptos de flujo de caja organizados por áreas
          </p>
        </div>
        <button
          onClick={() => handleCreate(activeTab)}
          className="mt-4 sm:mt-0 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Nuevo en {activeTab === 'tesoreria' ? 'Tesorería' : activeTab === 'pagaduria' ? 'Pagaduría' : 'Ambas'}</span>
        </button>
      </div>

      {/* Notificación */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          notification.type === 'success' 
            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
            : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
        }`}>
          <div className="flex items-center">
            {notification.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
            )}
            <span className={`${
              notification.type === 'success' 
                ? 'text-green-700 dark:text-green-300' 
                : 'text-red-700 dark:text-red-300'
            }`}>
              {notification.message}
            </span>
            <button
              onClick={() => setNotification(null)}
              className="ml-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Pestañas de Áreas */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('tesoreria')}
              className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === 'tesoreria'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <Building className="w-4 h-4" />
              <span>Tesorería</span>
              <span className={`ml-1 px-2 py-1 text-xs rounded-full ${
                activeTab === 'tesoreria'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }`}>
                {tesoreriaStats.total}
              </span>
            </button>
            
            <button
              onClick={() => setActiveTab('pagaduria')}
              className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === 'pagaduria'
                  ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Pagaduría</span>
              <span className={`ml-1 px-2 py-1 text-xs rounded-full ${
                activeTab === 'pagaduria'
                  ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }`}>
                {pagaduriaStats.total}
              </span>
            </button>
            
            <button
              onClick={() => setActiveTab('ambas')}
              className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === 'ambas'
                  ? 'border-green-500 text-green-600 dark:text-green-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <Globe className="w-4 h-4" />
              <span>Ambas Áreas</span>
              <span className={`ml-1 px-2 py-1 text-xs rounded-full ${
                activeTab === 'ambas'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
              }`}>
                {ambasStats.total}
              </span>
            </button>
          </nav>
        </div>

        {/* Estadísticas del área activa */}
        <div className="p-6 bg-gray-50 dark:bg-gray-700/50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {activeTab === 'tesoreria' ? tesoreriaStats.total : 
                 activeTab === 'pagaduria' ? pagaduriaStats.total : ambasStats.total}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Conceptos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {activeTab === 'tesoreria' ? tesoreriaStats.activos : 
                 activeTab === 'pagaduria' ? pagaduriaStats.activos : ambasStats.activos}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Activos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                {activeTab === 'tesoreria' ? tesoreriaStats.inactivos : 
                 activeTab === 'pagaduria' ? pagaduriaStats.inactivos : ambasStats.inactivos}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Inactivos</div>
            </div>
          </div>
        </div>

        {/* Barra de búsqueda y filtros */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder={`Buscar conceptos en ${activeTab === 'tesoreria' ? 'Tesorería' : activeTab === 'pagaduria' ? 'Pagaduría' : 'Ambas Áreas'}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            
            {/* Filtro de estado */}
            <div className="flex items-center space-x-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showInactiveOnly}
                  onChange={(e) => setShowInactiveOnly(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  Solo mostrar inactivos
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Tabla de conceptos del área activa */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Concepto
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Código
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Orden
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Dependencia
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {currentAreaConceptos.map((concepto) => (
                <tr key={concepto.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {concepto.nombre}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      concepto.codigo === 'I' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                        : concepto.codigo === 'E'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300'
                    }`}>
                      {concepto.codigo || '-'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {concepto.tipo || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {concepto.orden_display}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      concepto.activo
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
                    }`}>
                      {concepto.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {concepto.depende_de_concepto_id ? (
                      <div className="flex items-center space-x-1">
                        {concepto.tipo_dependencia === 'suma' && <span className="text-green-600">+</span>}
                        {concepto.tipo_dependencia === 'resta' && <span className="text-red-600">-</span>}
                        {concepto.tipo_dependencia === 'copia' && <span className="text-blue-600">=</span>}
                        <span className="text-xs">{concepto.concepto_dependiente?.nombre || 'N/A'}</span>
                      </div>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => handleEdit(concepto)}
                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 p-1 rounded"
                        title="Editar"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(concepto.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 p-1 rounded"
                        title="Eliminar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {currentAreaConceptos.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 dark:text-gray-500 text-lg mb-2">
                No se encontraron conceptos
              </div>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {showInactiveOnly 
                  ? `No hay conceptos inactivos en ${activeTab === 'tesoreria' ? 'Tesorería' : activeTab === 'pagaduria' ? 'Pagaduría' : 'Ambas Áreas'}`
                  : searchTerm 
                    ? `No hay conceptos que coincidan con "${searchTerm}" en ${activeTab === 'tesoreria' ? 'Tesorería' : activeTab === 'pagaduria' ? 'Pagaduría' : 'Ambas Áreas'}`
                    : `No hay conceptos en ${activeTab === 'tesoreria' ? 'Tesorería' : activeTab === 'pagaduria' ? 'Pagaduría' : 'Ambas Áreas'}`
                }
              </p>
              {!showInactiveOnly && !searchTerm && (
                <button
                  onClick={() => handleCreate(activeTab)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 mx-auto transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Crear primer concepto</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Modal de creación/edición */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  {editingConcepto ? 'Editar Concepto' : 'Nuevo Concepto'}
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Nombre */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Nombre del Concepto *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.nombre}
                    onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Ej: Ingresos por ventas"
                  />
                </div>

                {/* Código y Tipo en la misma fila */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Código
                    </label>
                    <select
                      value={formData.codigo}
                      onChange={(e) => setFormData({...formData, codigo: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Sin código</option>
                      <option value="I">I - Ingreso</option>
                      <option value="E">E - Egreso</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Tipo de Movimiento
                    </label>
                    <select
                      value={formData.tipo}
                      onChange={(e) => setFormData({...formData, tipo: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Seleccionar tipo...</option>
                      {TIPOS_MOVIMIENTO.map(tipo => (
                        <option key={tipo} value={tipo}>{tipo}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Área y Orden en la misma fila */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Área *
                    </label>
                    <select
                      required
                      value={formData.area}
                      onChange={(e) => setFormData({...formData, area: e.target.value as 'tesoreria' | 'pagaduria' | 'ambas'})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="tesoreria">Tesorería</option>
                      <option value="pagaduria">Pagaduría</option>
                      <option value="ambas">Ambas áreas</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Orden de visualización
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={formData.orden_display}
                      onChange={(e) => setFormData({...formData, orden_display: parseInt(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>

                {/* Dependencias */}
                <div className="border-t border-gray-200 dark:border-gray-600 pt-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                    Configuración de Dependencias (Opcional)
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Depende de concepto
                      </label>
                      <select
                        value={formData.depende_de_concepto_id || ''}
                        onChange={(e) => setFormData({
                          ...formData, 
                          depende_de_concepto_id: e.target.value ? parseInt(e.target.value) : undefined
                        })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="">Sin dependencia</option>
                        {getConceptosParaDependencia().map(concepto => (
                          <option key={concepto.id} value={concepto.id}>
                            {concepto.nombre}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Tipo de dependencia
                      </label>
                      <select
                        value={formData.tipo_dependencia || ''}
                        onChange={(e) => setFormData({
                          ...formData, 
                          tipo_dependencia: e.target.value as 'copia' | 'suma' | 'resta' | undefined
                        })}
                        disabled={!formData.depende_de_concepto_id}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50"
                      >
                        <option value="">Seleccionar...</option>
                        <option value="copia">Copia (=) - Replica el valor</option>
                        <option value="suma">Suma (+) - Suma el valor</option>
                        <option value="resta">Resta (-) - Resta el valor</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Estado activo */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="activo"
                    checked={formData.activo}
                    onChange={(e) => setFormData({...formData, activo: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="activo" className="ml-2 block text-sm text-gray-900 dark:text-white">
                    Concepto activo
                  </label>
                </div>

                {/* Botones */}
                <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-600">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Guardando...</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        <span>{editingConcepto ? 'Actualizar' : 'Crear'}</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Conceptos;