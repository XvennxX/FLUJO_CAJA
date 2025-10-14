import React, { useState, useEffect } from 'react';
import { Users as UsersIcon, Plus, Edit, Trash2, Shield, Mail, Calendar, Search, Filter, UserCheck } from 'lucide-react';
import { useAuditoria } from '../../hooks/useAuditoria';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../hooks/useToast';
import CreateUserModal from './CreateUserModal';
import EditUserModal from './EditUserModal';
import ConfirmModal from './ConfirmModal';
import ToastContainer from '../Layout/ToastContainer';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  estado: boolean;
  status: 'active' | 'inactive';
  lastLogin: string;
  createdAt: string;
}

const Users: React.FC = () => {
  const { logUserAction } = useAuditoria();
  const { user } = useAuth(); // Usuario actual para obtener token
  const { toasts, addToast, removeToast } = useToast();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('todos');
  const [selectedStatus, setSelectedStatus] = useState<string>('todos');
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedUserToEdit, setSelectedUserToEdit] = useState<User | null>(null);
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const [confirmModalData, setConfirmModalData] = useState<{
    user: User | null;
    action: string;
    title: string;
    message: string;
  }>({
    user: null,
    action: '',
    title: '',
    message: ''
  });

  // Función para obtener usuarios de la API
  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No hay token de autenticación');
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/users/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const apiUsers = await response.json();
        
        // Transformar los datos de la API al formato que espera el componente
        const transformedUsers: User[] = apiUsers.map((apiUser: any) => ({
          id: apiUser.id.toString(),
          name: apiUser.nombre,
          email: apiUser.email,
          role: apiUser.rol,
          estado: apiUser.estado,
          status: apiUser.estado ? 'active' as const : 'inactive' as const,
          lastLogin: new Date().toISOString().split('T')[0], // Fecha actual como placeholder
          createdAt: '2024-01-01' // Placeholder, se puede agregar a la DB en el futuro
        }));
        
        setUsers(transformedUsers);
        console.log('✅ Usuarios cargados desde API:', transformedUsers.length);
      } else {
        setError(`Error al cargar usuarios: ${response.status}`);
        console.error('❌ Error al cargar usuarios:', response.status);
      }
    } catch (err) {
      setError('Error de conexión al cargar usuarios');
      console.error('❌ Error de conexión:', err);
    } finally {
      setLoading(false);
    }
  };

  // Cargar usuarios al montar el componente
  useEffect(() => {
    if (user) {
      fetchUsers();
    }
  }, [user]);

  // Funciones de manejo de usuarios con auditoría
  const handleCreateUser = async () => {
    await logUserAction(
      'CREAR',
      'Solicitó crear un nuevo usuario',
      'nuevo-usuario'
    );
    setIsCreateModalOpen(true);
  };

  const handleCloseCreateModal = () => {
    setIsCreateModalOpen(false);
  };

  const handleUserCreated = () => {
    fetchUsers(); // Recargar la lista de usuarios
    setIsCreateModalOpen(false);
    
    // Mostrar toast de éxito
    addToast({
      type: 'success',
      title: 'Usuario Creado',
      message: 'El nuevo usuario ha sido creado exitosamente',
      duration: 4000
    });
  };

  const handleEditUser = async (user: User) => {
    await logUserAction(
      'EDITAR',
      `Solicitó editar el usuario: ${user.name}`,
      user.id
    );
    setSelectedUserToEdit(user);
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setSelectedUserToEdit(null);
  };

  const handleUserUpdated = () => {
    fetchUsers(); // Recargar la lista de usuarios
    setIsEditModalOpen(false);
    setSelectedUserToEdit(null);
    
    // Mostrar toast de éxito
    addToast({
      type: 'success',
      title: 'Usuario Actualizado',
      message: 'El usuario ha sido actualizado exitosamente',
      duration: 4000
    });
  };

  const handleToggleUserStatus = async (user: User) => {
    const action = user.estado ? 'desactivar' : 'activar';
    
    // Configurar y mostrar modal de confirmación
    setConfirmModalData({
      user,
      action,
      title: `${action.charAt(0).toUpperCase() + action.slice(1)} Usuario`,
      message: `¿Está seguro de ${action} el usuario "${user.name}"?`
    });
    setIsConfirmModalOpen(true);
  };

  const handleConfirmToggleStatus = async () => {
    const { user, action } = confirmModalData;
    if (!user) return;

    const newStatus = !user.estado;

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        addToast({
          type: 'error',
          title: 'Error de Autenticación',
          message: 'No hay token de autenticación',
          duration: 5000
        });
        return;
      }

      const response = await fetch(`http://localhost:8000/api/v1/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          estado: newStatus
        })
      });

      if (response.ok) {
        await logUserAction(
          'EDITAR',
          `${newStatus ? 'Activó' : 'Desactivó'} el usuario: ${user.name}`,
          user.id,
          user,
          null
        );
        
        // Recargar la lista de usuarios
        fetchUsers();
        
        // Mostrar toast de éxito
        addToast({
          type: 'success',
          title: newStatus ? 'Usuario Activado' : 'Usuario Desactivado',
          message: `El usuario "${user.name}" ha sido ${newStatus ? 'activado' : 'desactivado'} exitosamente`,
          duration: 4000
        });
      } else {
        const errorData = await response.json();
        addToast({
          type: 'error',
          title: 'Error',
          message: errorData.detail || `Error al ${action} usuario`,
          duration: 5000
        });
      }
    } catch (error) {
      console.error(`Error al ${action} usuario:`, error);
      addToast({
        type: 'error',
        title: 'Error de Conexión',
        message: `No se pudo conectar con el servidor para ${action} el usuario`,
        duration: 5000
      });
    } finally {
      // Cerrar modal de confirmación
      setIsConfirmModalOpen(false);
    }
  };

  const handleCancelToggleStatus = () => {
    setIsConfirmModalOpen(false);
  };

  // Filtrado de usuarios
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'todos' || user.role === selectedRole;
    const matchesStatus = selectedStatus === 'todos' || 
                         (selectedStatus === 'active' && user.estado) ||
                         (selectedStatus === 'inactive' && !user.estado);
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const activeUsers = users.filter(u => u.estado).length;
  const totalUsers = users.length;

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'Administrador':
        return 'bg-purple-100 text-purple-800';
      case 'Tesorería':
        return 'bg-blue-100 text-blue-800';
      case 'Pagaduría':
        return 'bg-green-100 text-green-800';
      case 'Mesa de Dinero':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  return (
    <>
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-bolivar-500 to-bolivar-600">
              <UsersIcon className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Usuarios</p>
            <p className="text-2xl font-bold text-bolivar-600">{totalUsers}</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-bolivar-600 to-bolivar-700">
              <Shield className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Usuarios Activos</p>
            <p className="text-2xl font-bold text-bolivar-600">{activeUsers}</p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-gold-500 to-gold-600">
              <Mail className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Roles Activos</p>
            <p className="text-2xl font-bold text-gold-600">4</p>
          </div>
        </div>
      </div>

      {/* Users Management */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Gestión de Usuarios</h3>
          <button 
            onClick={handleCreateUser}
            className="bg-gradient-to-r from-bolivar-500 to-bolivar-600 text-white px-4 py-2 rounded-lg hover:from-bolivar-600 hover:to-bolivar-700 transition-all flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Nuevo Usuario</span>
          </button>
        </div>

        {/* Filtros */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Buscar usuarios..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent"
            />
          </div>
          
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent appearance-none bg-white dark:bg-gray-800"
            >
              <option value="todos">Todos los roles</option>
              <option value="Administrador">Administrador</option>
              <option value="Tesorería">Tesorería</option>
              <option value="Pagaduría">Pagaduría</option>
              <option value="Mesa de Dinero">Mesa de Dinero</option>
            </select>
          </div>
          
          <div className="relative">
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent appearance-none bg-white dark:bg-gray-800"
            >
              <option value="todos">Todos los estados</option>
              <option value="active">Activos</option>
              <option value="inactive">Inactivos</option>
            </select>
          </div>
          
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span>{filteredUsers.length} de {totalUsers} usuarios</span>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-bolivar-600"></div>
            <span className="ml-2 text-gray-600 dark:text-gray-400">Cargando usuarios...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="text-red-400 flex-shrink-0">
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800 dark:text-red-200">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Table */}
        {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Rol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Último Acceso
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50 dark:bg-gray-900 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-full flex items-center justify-center">
                          <span className="text-white font-medium text-sm">
                            {user.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{user.name}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.estado 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.estado ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-gray-900 dark:text-white">
                          {new Date(user.lastLogin).toLocaleDateString('es-CO')}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button 
                          onClick={() => handleEditUser(user)}
                          className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Editar usuario"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button 
                          onClick={() => handleToggleUserStatus(user)}
                          className={`p-1 transition-colors ${
                            user.estado 
                              ? 'text-gray-400 hover:text-red-600' 
                              : 'text-gray-400 hover:text-green-600'
                          }`}
                          title={user.estado ? "Desactivar usuario" : "Activar usuario"}
                        >
                          {user.estado ? (
                            <Trash2 className="h-4 w-4" />
                          ) : (
                            <UserCheck className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center space-y-3">
                      <UsersIcon className="h-12 w-12 text-gray-400" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1">No se encontraron usuarios</h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {searchTerm || selectedRole !== 'todos' || selectedStatus !== 'todos'
                            ? 'Intenta ajustar los filtros de búsqueda'
                            : 'No hay usuarios registrados en el sistema'
                          }
                        </p>
                      </div>
                      {searchTerm || selectedRole !== 'todos' || selectedStatus !== 'todos' ? (
                        <button
                          onClick={() => {
                            setSearchTerm('');
                            setSelectedRole('todos');
                            setSelectedStatus('todos');
                          }}
                          className="text-sm text-bolivar-600 hover:text-bolivar-700 font-medium"
                        >
                          Limpiar filtros
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        )}
      </div>

      {/* User Roles */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Roles y Permisos</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-purple-500 rounded-full" />
              <h4 className="font-medium text-gray-900 dark:text-white">Administrador</h4>
            </div>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Acceso completo al sistema</li>
              <li>• Gestión de usuarios</li>
              <li>• Configuración del sistema</li>
              <li>• Todos los reportes</li>
              <li>• Auditoría completa</li>
            </ul>
          </div>

          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full" />
              <h4 className="font-medium text-gray-900 dark:text-white">Tesorería</h4>
            </div>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Flujo de caja diario</li>
              <li>• Gestión de cuentas</li>
              <li>• Reportes financieros</li>
              <li>• Movimientos bancarios</li>
              <li>• Conciliaciones</li>
            </ul>
          </div>

          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-green-500 rounded-full" />
              <h4 className="font-medium text-gray-900 dark:text-white">Pagaduría</h4>
            </div>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Gestión de pagos</li>
              <li>• Nómina y proveedores</li>
              <li>• Autorización de egresos</li>
              <li>• Reportes de pagos</li>
              <li>• Control presupuestal</li>
            </ul>
          </div>

          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-orange-500 rounded-full" />
              <h4 className="font-medium text-gray-900 dark:text-white">Mesa de Dinero</h4>
            </div>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Inversiones financieras</li>
              <li>• Títulos valores</li>
              <li>• Operaciones simultáneas</li>
              <li>• Rendimientos</li>
              <li>• Análisis de mercado</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Create User Modal */}
      <CreateUserModal
        isOpen={isCreateModalOpen}
        onClose={handleCloseCreateModal}
        onUserCreated={handleUserCreated}
      />

      {/* Edit User Modal */}
      <EditUserModal
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        onUserUpdated={handleUserUpdated}
        user={selectedUserToEdit}
      />

      {/* Confirm Modal */}
      <ConfirmModal
        isOpen={isConfirmModalOpen}
        title={confirmModalData.title}
        message={confirmModalData.message}
        confirmText="Aceptar"
        cancelText="Cancelar"
        onConfirm={handleConfirmToggleStatus}
        onCancel={handleCancelToggleStatus}
        type={confirmModalData.action === 'desactivar' ? 'danger' : 'info'}
      />
    </div>
    
    {/* Toast Notifications - Positioned outside main container */}
    <ToastContainer 
      toasts={toasts}
      onClose={removeToast}
    />
    </>
  );
};

export default Users;

