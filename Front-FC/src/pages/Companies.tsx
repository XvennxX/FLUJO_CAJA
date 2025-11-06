import React, { useState } from 'react';
import { Plus, Edit, Trash2, Building2, Search, Filter, Download, Upload, AlertCircle, CheckCircle, CreditCard } from 'lucide-react';
import { useCompanies, Company } from '../hooks/useCompanies';
import BankAccountsManager from './BankAccountsManager';

const Companies: React.FC = () => {
  const { companies, loading, error, addCompany, updateCompany, deleteCompany, refetch } = useCompanies();
  
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [editingCompany, setEditingCompany] = useState<Company | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [companyToDelete, setCompanyToDelete] = useState<Company | null>(null);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Estados para gestión de cuentas bancarias
  const [showBankAccountsModal, setShowBankAccountsModal] = useState(false);
  const [selectedCompanyForBanks, setSelectedCompanyForBanks] = useState<Company | null>(null);

  // Estados del formulario de compañía
  const [companyForm, setCompanyForm] = useState({
    nombre: ''
  });

  // Estados de validación
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});

  const validateForm = () => {
    const errors: { [key: string]: string } = {};
    
    if (!companyForm.nombre.trim()) {
      errors.nombre = 'El nombre de la compañía es requerido';
    } else if (companyForm.nombre.trim().length < 2) {
      errors.nombre = 'El nombre debe tener al menos 2 caracteres';
    } else if (companyForm.nombre.trim().length > 100) {
      errors.nombre = 'El nombre no puede exceder los 100 caracteres';
    }

    // Verificar duplicados (excluyendo la compañía actual si estamos editando)
    const duplicateCompany = companies.find(company => 
      company.nombre.toLowerCase() === companyForm.nombre.trim().toLowerCase() &&
      company.id !== editingCompany?.id
    );
    
    if (duplicateCompany) {
      errors.nombre = 'Ya existe una compañía con este nombre';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setShowSuccessMessage(true);
    setTimeout(() => setShowSuccessMessage(false), 3000);
  };

  const handleCompanySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      if (editingCompany) {
        const success = await updateCompany(editingCompany.id, companyForm);
        if (success) {
          showSuccess('Compañía actualizada exitosamente');
          setShowCompanyModal(false);
          setEditingCompany(null);
          setCompanyForm({ nombre: '' });
          setFormErrors({});
        }
      } else {
        const success = await addCompany(companyForm);
        if (success) {
          showSuccess('Compañía creada exitosamente');
          setShowCompanyModal(false);
          setCompanyForm({ nombre: '' });
          setFormErrors({});
        }
      }
    } catch (error) {
      console.error('Error al guardar compañía:', error);
    }
  };

  const handleEditCompany = (company: Company) => {
    setEditingCompany(company);
    setCompanyForm({ nombre: company.nombre });
    setFormErrors({});
    setShowCompanyModal(true);
  };

  const handleDeleteConfirm = (company: Company) => {
    setCompanyToDelete(company);
    setShowDeleteModal(true);
  };

  const handleDeleteCompany = async () => {
    if (!companyToDelete) return;
    
    try {
      const success = await deleteCompany(companyToDelete.id);
      if (success) {
        showSuccess('Compañía eliminada exitosamente');
        setShowDeleteModal(false);
        setCompanyToDelete(null);
      }
    } catch (error) {
      console.error('Error al eliminar compañía:', error);
    }
  };

  const handleManageBankAccounts = (company: Company) => {
    setSelectedCompanyForBanks(company);
    setShowBankAccountsModal(true);
  };

  const handleCloseBankAccounts = () => {
    setShowBankAccountsModal(false);
    setSelectedCompanyForBanks(null);
  };

  const handleAddCompany = () => {
    setEditingCompany(null);
    setCompanyForm({ nombre: '' });
    setFormErrors({});
    setShowCompanyModal(true);
  };

  const handleRefresh = async () => {
    await refetch();
    showSuccess('Lista de compañías actualizada');
  };

  // Filtrar compañías por término de búsqueda
  const filteredCompanies = companies.filter(company =>
    company.nombre.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleExport = () => {
    const csvContent = [
      ['ID', 'Nombre'],
      ...filteredCompanies.map(company => [company.id.toString(), company.nombre])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `companias_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Cargando compañías...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Mensaje de éxito */}
      {showSuccessMessage && (
        <div className="fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-lg z-50 flex items-center">
          <CheckCircle className="h-5 w-5 mr-2" />
          {successMessage}
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <Building2 className="h-8 w-8 text-blue-600 mr-3" />
            Gestión de Compañías
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Administra las compañías del sistema ({filteredCompanies.length} de {companies.length})
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleRefresh}
            className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 flex items-center space-x-2 transition-colors"
            title="Actualizar lista"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={handleExport}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2 transition-colors"
            title="Exportar a CSV"
          >
            <Download className="h-5 w-5" />
            <span>Exportar</span>
          </button>
          <button
            onClick={handleAddCompany}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>Nueva Compañía</span>
          </button>
        </div>
      </div>

      {/* Mensajes de error */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {/* Búsqueda y filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Buscar compañías por nombre..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <Filter className="h-5 w-5" />
            <span>Filtros</span>
          </button>
        </div>

        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Filtros adicionales pueden ser agregados aquí (por fecha, estado, etc.)
            </p>
          </div>
        )}
      </div>

      {/* Lista de Compañías */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Nombre
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredCompanies.map((company) => (
                <tr key={company.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-medium">
                    #{company.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Building2 className="h-5 w-5 text-blue-500 mr-3 flex-shrink-0" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {company.nombre}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => handleEditCompany(company)}
                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 p-2 rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                        title="Editar compañía"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleManageBankAccounts(company)}
                        className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300 p-2 rounded-md hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors"
                        title="Gestionar cuentas bancarias"
                      >
                        <CreditCard className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteConfirm(company)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 p-2 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                        title="Eliminar compañía"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredCompanies.length === 0 && (
            <div className="text-center py-12">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {searchTerm ? 'No se encontraron compañías' : 'No hay compañías registradas'}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {searchTerm 
                  ? `No hay compañías que coincidan con "${searchTerm}"` 
                  : 'Comienza agregando tu primera compañía al sistema'
                }
              </p>
              {!searchTerm && (
                <button
                  onClick={handleAddCompany}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Agregar Primera Compañía
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Modal de Compañía */}
      {showCompanyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4 max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                {editingCompany ? 'Editar Compañía' : 'Nueva Compañía'}
              </h3>
              <button
                onClick={() => {
                  setShowCompanyModal(false);
                  setEditingCompany(null);
                  setCompanyForm({ nombre: '' });
                  setFormErrors({});
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <form onSubmit={handleCompanySubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre de la Compañía *
                </label>
                <input
                  type="text"
                  value={companyForm.nombre}
                  onChange={(e) => {
                    setCompanyForm({ ...companyForm, nombre: e.target.value });
                    // Limpiar error al escribir
                    if (formErrors.nombre) {
                      setFormErrors({ ...formErrors, nombre: '' });
                    }
                  }}
                  className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors
                           ${formErrors.nombre 
                             ? 'border-red-300 dark:border-red-600' 
                             : 'border-gray-300 dark:border-gray-600'
                           }`}
                  required
                  placeholder="Ingrese el nombre de la compañía"
                  maxLength={100}
                />
                {formErrors.nombre && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {formErrors.nombre}
                  </p>
                )}
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {companyForm.nombre.length}/100 caracteres
                </p>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-600">
                <button
                  type="button"
                  onClick={() => {
                    setShowCompanyModal(false);
                    setEditingCompany(null);
                    setCompanyForm({ nombre: '' });
                    setFormErrors({});
                  }}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-medium"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {loading ? 'Guardando...' : (editingCompany ? 'Actualizar' : 'Crear')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Confirmación de Eliminación */}
      {showDeleteModal && companyToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
                <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Confirmar Eliminación
                </h3>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                ¿Estás seguro de que deseas eliminar la compañía{' '}
                <span className="font-semibold text-gray-900 dark:text-white">
                  "{companyToDelete.nombre}"
                </span>?
              </p>
              <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                Esta acción no se puede deshacer.
              </p>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setCompanyToDelete(null);
                }}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-medium"
              >
                Cancelar
              </button>
              <button
                onClick={handleDeleteCompany}
                disabled={loading}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de gestión de cuentas bancarias */}
      {selectedCompanyForBanks && (
        <BankAccountsManager
          companyId={selectedCompanyForBanks.id}
          companyName={selectedCompanyForBanks.nombre}
          isOpen={showBankAccountsModal}
          onClose={handleCloseBankAccounts}
        />
      )}
    </div>
  );
};

export default Companies;
