import React, { useState, useEffect, useRef } from 'react';
import { BankAccount, Bank, CreateBankAccountData, UpdateBankAccountData, useBankAccounts } from '../hooks/useBankAccounts';
import { useToast } from '../hooks/useToast';

interface BankAccountsManagerProps {
  companyId: number;
  companyName: string;
  isOpen: boolean;
  onClose: () => void;
}

const BankAccountsManager: React.FC<BankAccountsManagerProps> = ({ companyId, companyName, isOpen, onClose }) => {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [banks, setBanks] = useState<Bank[]>([]);
  const [showBankDropdown, setShowBankDropdown] = useState(false);
  const [showTipoCuentaDropdown, setShowTipoCuentaDropdown] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingAccount, setEditingAccount] = useState<BankAccount | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const tipoCuentaDropdownRef = useRef<HTMLDivElement>(null);
  const [formData, setFormData] = useState<CreateBankAccountData>({
    numero_cuenta: '',
    banco_id: 0,
    monedas: ['COP'],
    tipo_cuenta: 'CORRIENTE'
  });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);

  const { 
    loading, 
    error, 
    getCompanyBankAccounts, 
    createBankAccount, 
    updateBankAccount, 
    deleteBankAccount, 
    getAllBanks 
  } = useBankAccounts();
  
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen, companyId]);

  // Cerrar dropdowns al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowBankDropdown(false);
      }
      if (tipoCuentaDropdownRef.current && !tipoCuentaDropdownRef.current.contains(event.target as Node)) {
        setShowTipoCuentaDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const loadData = async () => {
    try {
      console.log('Cargando datos para compañía:', companyId);
      const [accountsData, banksData] = await Promise.all([
        getCompanyBankAccounts(companyId),
        getAllBanks()
      ]);
      console.log('Cuentas bancarias:', accountsData);
      console.log('Bancos:', banksData);
      setAccounts(accountsData);
      setBanks(banksData);
    } catch (err) {
      console.error('Error al cargar datos:', err);
      showError('Error', 'Error al cargar los datos');
    }
  };

  const resetForm = () => {
    setFormData({
      numero_cuenta: '',
      banco_id: 0,
      monedas: ['COP'],
      tipo_cuenta: 'CORRIENTE'
    });
    setEditingAccount(null);
    setShowCreateForm(false);
    setShowBankDropdown(false);
    setShowTipoCuentaDropdown(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.numero_cuenta.trim() || formData.banco_id === 0) {
      showError('Error', 'Por favor, complete todos los campos obligatorios');
      return;
    }

    try {
      if (editingAccount) {
        const updateData: UpdateBankAccountData = {};
        if (formData.numero_cuenta !== editingAccount.numero_cuenta) {
          updateData.numero_cuenta = formData.numero_cuenta;
        }
        if (formData.banco_id !== editingAccount.banco_id) {
          updateData.banco_id = formData.banco_id;
        }
        if (JSON.stringify(formData.monedas) !== JSON.stringify(editingAccount.monedas)) {
          updateData.monedas = formData.monedas;
        }
        if (formData.tipo_cuenta !== editingAccount.tipo_cuenta) {
          updateData.tipo_cuenta = formData.tipo_cuenta;
        }

        if (Object.keys(updateData).length > 0) {
          await updateBankAccount(editingAccount.id, updateData);
          showSuccess('Éxito', 'Cuenta bancaria actualizada exitosamente');
        }
      } else {
        await createBankAccount(companyId, formData);
        showSuccess('Éxito', 'Cuenta bancaria creada exitosamente');
      }
      
      await loadData();
      resetForm();
    } catch (err) {
      showError('Error', error || 'Error al guardar la cuenta bancaria');
    }
  };

  const handleEdit = (account: BankAccount) => {
    setEditingAccount(account);
    setFormData({
      numero_cuenta: account.numero_cuenta,
      banco_id: account.banco_id,
      monedas: account.monedas,
      tipo_cuenta: account.tipo_cuenta
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (accountId: number) => {
    try {
      await deleteBankAccount(accountId);
      showSuccess('Éxito', 'Cuenta bancaria eliminada exitosamente');
      await loadData();
      setShowDeleteConfirm(null);
    } catch (err) {
      showError('Error', error || 'Error al eliminar la cuenta bancaria');
    }
  };

  const getBankName = (bankId: number) => {
    const bank = banks.find(b => b.id === bankId);
    return bank ? bank.nombre : 'Banco no encontrado';
  };

  const getMonedaDisplay = (monedas: string[]) => {
    const monedaLabels = {
      'COP': 'COP',
      'USD': 'USD',
      'EUR': 'EUR'
    };
    return monedas.map(m => monedaLabels[m as keyof typeof monedaLabels] || m).join(', ');
  };

  const getTipoCuentaDisplay = (tipo: string) => {
    const tipos = {
      'CORRIENTE': 'Cuenta Corriente',
      'AHORROS': 'Cuenta de Ahorros'
    };
    return tipos[tipo as keyof typeof tipos] || tipo;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-800">
              Cuentas Bancarias - {companyName}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Header con botón de crear */}
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-medium text-gray-800">
              Gestión de Cuentas Bancarias
            </h3>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Nueva Cuenta
            </button>
          </div>

          {/* Formulario de crear/editar */}
          {showCreateForm && (
            <div className="bg-gray-50 p-6 rounded-lg mb-6 border border-gray-200">
              <h4 className="text-lg font-medium text-gray-800 mb-6">
                {editingAccount ? 'Editar Cuenta Bancaria' : 'Nueva Cuenta Bancaria'}
              </h4>
              <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Número de Cuenta *
                  </label>
                  <input
                    type="text"
                    value={formData.numero_cuenta}
                    onChange={(e) => setFormData(prev => ({ ...prev, numero_cuenta: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Ingrese el número de cuenta"
                    required
                  />
                </div>

                <div className="relative" ref={dropdownRef}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Banco *
                  </label>
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => setShowBankDropdown(!showBankDropdown)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-left bg-white flex justify-between items-center"
                    >
                      <span className={formData.banco_id === 0 ? 'text-gray-500' : 'text-gray-900'}>
                        {formData.banco_id === 0 
                          ? 'Seleccione un banco' 
                          : banks.find(b => b.id === formData.banco_id)?.nombre || 'Seleccione un banco'
                        }
                      </span>
                      <svg className={`w-5 h-5 text-gray-400 transition-transform ${showBankDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {showBankDropdown && (
                      <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-50 max-h-60 overflow-y-auto">
                        <div
                          onClick={() => {
                            setFormData(prev => ({ ...prev, banco_id: 0 }));
                            setShowBankDropdown(false);
                          }}
                          className="px-3 py-2 text-gray-500 hover:bg-gray-50 cursor-pointer"
                        >
                          Seleccione un banco
                        </div>
                        {banks.map(bank => (
                          <div
                            key={bank.id}
                            onClick={() => {
                              setFormData(prev => ({ ...prev, banco_id: bank.id }));
                              setShowBankDropdown(false);
                            }}
                            className="px-3 py-2 text-gray-900 hover:bg-blue-50 cursor-pointer"
                          >
                            {bank.nombre}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monedas *
                  </label>
                  <div className="space-y-3 p-3 border border-gray-300 rounded-md bg-gray-50">
                    {(['COP', 'USD', 'EUR'] as const).map((moneda) => (
                      <label key={moneda} className="flex items-center cursor-pointer hover:bg-white hover:shadow-sm p-2 rounded transition-all">
                        <input
                          type="checkbox"
                          checked={formData.monedas.includes(moneda)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFormData(prev => ({
                                ...prev,
                                monedas: [...prev.monedas, moneda]
                              }));
                            } else {
                              setFormData(prev => ({
                                ...prev,
                                monedas: prev.monedas.filter(m => m !== moneda)
                              }));
                            }
                          }}
                          className="mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="text-sm text-gray-700 font-medium">
                          {moneda === 'COP' ? 'Pesos Colombianos (COP)' : 
                           moneda === 'USD' ? 'Dólares Americanos (USD)' : 
                           'Euros (EUR)'}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="relative" ref={tipoCuentaDropdownRef}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Cuenta *
                  </label>
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => setShowTipoCuentaDropdown(!showTipoCuentaDropdown)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-left bg-white flex justify-between items-center"
                    >
                      <span className="text-gray-900">
                        {formData.tipo_cuenta === 'CORRIENTE' ? 'Cuenta Corriente' : 'Cuenta de Ahorros'}
                      </span>
                      <svg className={`w-5 h-5 text-gray-400 transition-transform ${showTipoCuentaDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {showTipoCuentaDropdown && (
                      <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-50">
                        <div
                          onClick={() => {
                            setFormData(prev => ({ ...prev, tipo_cuenta: 'CORRIENTE' }));
                            setShowTipoCuentaDropdown(false);
                          }}
                          className="px-3 py-2 text-gray-900 hover:bg-blue-50 cursor-pointer"
                        >
                          Cuenta Corriente
                        </div>
                        <div
                          onClick={() => {
                            setFormData(prev => ({ ...prev, tipo_cuenta: 'AHORROS' }));
                            setShowTipoCuentaDropdown(false);
                          }}
                          className="px-3 py-2 text-gray-900 hover:bg-blue-50 cursor-pointer"
                        >
                          Cuenta de Ahorros
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="lg:col-span-2">
                  <div className="flex gap-4 pt-4">
                    <button
                      type="submit"
                      disabled={loading}
                      className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 font-medium"
                    >
                      {loading ? 'Guardando...' : (editingAccount ? 'Actualizar' : 'Crear')}
                    </button>
                    <button
                      type="button"
                      onClick={resetForm}
                      className="bg-gray-500 text-white px-6 py-2 rounded-md hover:bg-gray-600 transition-colors font-medium"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              </form>
            </div>
          )}

          {/* Lista de cuentas */}
          {loading && !showCreateForm ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Cargando cuentas bancarias...</p>
            </div>
          ) : accounts.length === 0 ? (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <p className="text-gray-500">No hay cuentas bancarias registradas</p>
              <p className="text-sm text-gray-400 mt-1">Haga clic en "Nueva Cuenta" para agregar una</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Número de Cuenta
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Banco
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo de Cuenta
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Moneda
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {accounts.map((account) => (
                    <tr key={account.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {account.numero_cuenta}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {getBankName(account.banco_id)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {getTipoCuentaDisplay(account.tipo_cuenta)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {getMonedaDisplay(account.monedas)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleEdit(account)}
                            className="text-blue-600 hover:text-blue-900 p-2 rounded-full hover:bg-blue-100"
                            title="Editar cuenta"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button
                            onClick={() => setShowDeleteConfirm(account.id)}
                            className="text-red-600 hover:text-red-900 p-2 rounded-full hover:bg-red-100"
                            title="Eliminar cuenta"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal de confirmación de eliminación */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                    <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                </div>
                <div className="text-center">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Confirmar Eliminación
                  </h3>
                  <p className="text-sm text-gray-500 mb-6">
                    ¿Está seguro de que desea eliminar esta cuenta bancaria? Esta acción no se puede deshacer.
                  </p>
                  <div className="flex gap-3 justify-center">
                    <button
                      onClick={() => handleDelete(showDeleteConfirm)}
                      disabled={loading}
                      className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors disabled:opacity-50"
                    >
                      {loading ? 'Eliminando...' : 'Eliminar'}
                    </button>
                    <button
                      onClick={() => setShowDeleteConfirm(null)}
                      className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BankAccountsManager;
