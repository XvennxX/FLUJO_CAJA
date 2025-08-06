import React, { useState } from 'react';
import { Plus, Edit, Trash2, Building2, CreditCard, Search, Filter } from 'lucide-react';
import { useCompanies, Company, Account } from '../../hooks/useCompanies.ts';

const Companies: React.FC = () => {
  const { companies, accounts, loading, error, addCompany, updateCompany, deleteCompany, addAccount, updateAccount, deleteAccount } = useCompanies();
  
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [editingCompany, setEditingCompany] = useState<Company | null>(null);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState(true);

  // Estados del formulario de compañía
  const [companyForm, setCompanyForm] = useState({
    nombre: ''
  });

  // Estados del formulario de cuenta
  const [accountForm, setAccountForm] = useState({
    banco: '',
    numeroCuenta: '',
    companyId: 0
  });

  const handleCompanySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingCompany) {
        await updateCompany(editingCompany.id, companyForm);
      } else {
        await addCompany(companyForm);
      }
      setShowCompanyModal(false);
      setEditingCompany(null);
      setCompanyForm({ nombre: '' });
    } catch (error) {
      console.error('Error al guardar compañía:', error);
    }
  };

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAccount) {
        await updateAccount(editingAccount.id, accountForm);
      } else {
        await addAccount(accountForm);
      }
      setShowAccountModal(false);
      setEditingAccount(null);
      setAccountForm({ banco: '', numeroCuenta: '', companyId: 0 });
    } catch (error) {
      console.error('Error al guardar cuenta:', error);
    }
  };

  const openCompanyModal = (company?: Company) => {
    if (company) {
      setEditingCompany(company);
      setCompanyForm({ nombre: company.nombre });
    } else {
      setEditingCompany(null);
      setCompanyForm({ nombre: '' });
    }
    setShowCompanyModal(true);
  };

  const openAccountModal = (companyId?: number, account?: Account) => {
    if (account) {
      setEditingAccount(account);
      setAccountForm({
        banco: account.banco,
        numeroCuenta: account.numeroCuenta,
        companyId: account.companyId
      });
    } else {
      setEditingAccount(null);
      setAccountForm({
        banco: '',
        numeroCuenta: '',
        companyId: companyId || 0
      });
    }
    setShowAccountModal(true);
  };

  const handleDeleteCompany = async (companyId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta compañía? Se eliminarán también todas sus cuentas.')) {
      try {
        await deleteCompany(companyId);
      } catch (error) {
        console.error('Error al eliminar compañía:', error);
      }
    }
  };

  const handleDeleteAccount = async (accountId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta cuenta?')) {
      try {
        await deleteAccount(accountId);
      } catch (error) {
        console.error('Error al eliminar cuenta:', error);
      }
    }
  };

  // Filtrar compañías
  const filteredCompanies = companies.filter((company: Company) => {
    const matchesSearch = company.nombre.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterActive ? company.estado : true;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-bolivar-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando compañías...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen flex items-center justify-center">
        <div className="text-center text-red-600">
          <p className="text-lg font-semibold mb-2">Error al cargar los datos</p>
          <p className="text-gray-600 dark:text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-2">Gestión de Compañías</h1>
        <p className="text-gray-600 dark:text-gray-400">Administra las compañías y sus cuentas bancarias</p>
      </div>

      {/* Controles superiores */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div className="flex flex-col lg:flex-row gap-4 lg:items-center lg:justify-between">
          <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar compañías..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full sm:w-64 h-10 pl-10 pr-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500 text-sm"
              />
            </div>
            
            <button
              onClick={() => setFilterActive(!filterActive)}
              className={`h-10 px-4 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 whitespace-nowrap ${
                filterActive
                  ? 'bg-bolivar-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200'
              }`}
            >
              <Filter className="w-4 h-4" />
              Solo activas
            </button>
          </div>

          <button
            onClick={() => openCompanyModal()}
            className="h-10 px-4 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors text-sm font-medium flex items-center justify-center gap-2 whitespace-nowrap"
          >
            <Plus className="w-4 h-4" />
            Nueva Compañía
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Compañías</p>
              <p className="text-2xl font-bold text-bolivar-600">{companies.length}</p>
            </div>
            <div className="p-3 bg-bolivar-100 rounded-full">
              <Building2 className="w-6 h-6 text-bolivar-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Cuentas</p>
              <p className="text-2xl font-bold text-green-600">{accounts.length}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <CreditCard className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Compañías Activas</p>
              <p className="text-2xl font-bold text-gold-600">{companies.filter((c: Company) => c.estado).length}</p>
            </div>
            <div className="p-3 bg-gold-100 rounded-full">
              <Building2 className="w-6 h-6 text-gold-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Lista de compañías */}
      <div className="space-y-6">
        {filteredCompanies.map((company: Company) => {
          const companyCuentas = accounts.filter((account: Account) => account.companyId === company.id);
          
          return (
            <div key={company.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
              {/* Header de la compañía */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-bolivar-100 rounded-full">
                      <Building2 className="w-6 h-6 text-bolivar-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">{company.nombre}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {companyCuentas.length} cuenta{companyCuentas.length !== 1 ? 's' : ''} bancaria{companyCuentas.length !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      company.estado 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {company.estado ? 'Activa' : 'Inactiva'}
                    </span>
                    
                    <button
                      onClick={() => openAccountModal(company.id)}
                      className="p-2 text-bolivar-600 hover:bg-bolivar-50 rounded-lg transition-colors"
                      title="Agregar cuenta"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={() => openCompanyModal(company)}
                      className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:bg-gray-900 rounded-lg transition-colors"
                      title="Editar compañía"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={() => handleDeleteCompany(company.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Eliminar compañía"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Lista de cuentas */}
              {companyCuentas.length > 0 && (
                <div className="p-6">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Cuentas Bancarias</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {companyCuentas.map((account: Account) => (
                      <div key={account.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <CreditCard className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                            <span className="font-medium text-gray-800 dark:text-gray-200">{account.banco}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => openAccountModal(company.id, account)}
                              className="p-1 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:bg-gray-900 rounded transition-colors"
                              title="Editar cuenta"
                            >
                              <Edit className="w-3 h-3" />
                            </button>
                            <button
                              onClick={() => handleDeleteAccount(account.id)}
                              className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Eliminar cuenta"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">{account.numeroCuenta}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Creada: {account.fechaCreacion.toLocaleDateString('es-CO')}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {companyCuentas.length === 0 && (
                <div className="p-6 text-center">
                  <p className="text-gray-500 dark:text-gray-400 text-sm">No hay cuentas bancarias registradas</p>
                  <button
                    onClick={() => openAccountModal(company.id)}
                    className="mt-2 text-bolivar-600 hover:text-bolivar-700 text-sm font-medium"
                  >
                    Agregar primera cuenta
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {filteredCompanies.length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
          <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">No hay compañías</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {searchTerm ? 'No se encontraron compañías que coincidan con tu búsqueda' : 'Comienza agregando tu primera compañía'}
          </p>
          <button
            onClick={() => openCompanyModal()}
            className="inline-flex items-center gap-2 px-4 py-2 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Nueva Compañía
          </button>
        </div>
      )}

      {/* Modal de Compañía */}
      {showCompanyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              {editingCompany ? 'Editar Compañía' : 'Nueva Compañía'}
            </h2>
            
            <form onSubmit={handleCompanySubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre de la Compañía *
                </label>
                <input
                  type="text"
                  value={companyForm.nombre}
                  onChange={(e) => setCompanyForm({ ...companyForm, nombre: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                  placeholder="Ej: CAPITALIZADORA"
                  required
                />
              </div>

              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowCompanyModal(false)}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors"
                >
                  {editingCompany ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Cuenta */}
      {showAccountModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              {editingAccount ? 'Editar Cuenta' : 'Nueva Cuenta Bancaria'}
            </h2>
            
            <form onSubmit={handleAccountSubmit}>
              {!editingAccount && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Compañía *
                  </label>
                  <select
                    value={accountForm.companyId}
                    onChange={(e) => setAccountForm({ ...accountForm, companyId: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                    required
                  >
                    <option value={0}>Seleccionar compañía</option>
                    {companies.filter((c: Company) => c.estado).map((company: Company) => (
                      <option key={company.id} value={company.id}>
                        {company.nombre}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Banco *
                </label>
                <input
                  type="text"
                  value={accountForm.banco}
                  onChange={(e) => setAccountForm({ ...accountForm, banco: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                  placeholder="Ej: BANCO DAVIVIENDA"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Número de Cuenta *
                </label>
                <input
                  type="text"
                  value={accountForm.numeroCuenta}
                  onChange={(e) => setAccountForm({ ...accountForm, numeroCuenta: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                  placeholder="Ej: 006069999420"
                  required
                />
              </div>

              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowAccountModal(false)}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors"
                >
                  {editingAccount ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Companies;


