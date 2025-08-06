import React, { useState } from 'react';
import { Users as UsersIcon, Plus, Edit, Trash2, Shield, Mail, Calendar, Search, Filter } from 'lucide-react';
import { useAuditoria } from '../../hooks/useAuditoria';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'inactive';
  lastLogin: string;
  createdAt: string;
}

const Users: React.FC = () => {
  const { logUserAction } = useAuditoria();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('todos');
  const [selectedStatus, setSelectedStatus] = useState<string>('todos');
  
  const [users] = useState<User[]>([
    {
      id: '1',
      name: 'Ana García',
      email: 'ana.garcia@email.com',
      role: 'Administrador',
      status: 'active',
      lastLogin: '2025-01-22',
      createdAt: '2024-01-15',
    },
    {
      id: '2',
      name: 'Carlos Rodríguez',
      email: 'carlos.rodriguez@email.com',
      role: 'Tesorería',
      status: 'active',
      lastLogin: '2025-01-21',
      createdAt: '2024-02-20',
    },
    {
      id: '3',
      name: 'María López',
      email: 'maria.lopez@email.com',
      role: 'Pagaduría',
      status: 'active',
      lastLogin: '2025-01-20',
      createdAt: '2024-03-10',
    },
    {
      id: '4',
      name: 'Luis Mendoza',
      email: 'luis.mendoza@email.com',
      role: 'Mesa de Dinero',
      status: 'active',
      lastLogin: '2025-01-21',
      createdAt: '2024-04-05',
    },
    {
      id: '5',
      name: 'Patricia Santos',
      email: 'patricia.santos@email.com',
      role: 'Tesorería',
      status: 'inactive',
      lastLogin: '2025-01-18',
      createdAt: '2024-05-12',
    },
  ]);

  // Funciones de manejo de usuarios con auditoría
  const handleCreateUser = async () => {
    await logUserAction(
      'CREAR',
      'Solicitó crear un nuevo usuario',
      'nuevo-usuario'
    );
    // Aquí iría la lógica para abrir modal de creación
    alert('Funcionalidad de crear usuario en desarrollo');
  };

  const handleEditUser = async (user: User) => {
    await logUserAction(
      'EDITAR',
      `Solicitó editar el usuario: ${user.name}`,
      user.id
    );
    // Aquí iría la lógica para abrir modal de edición
    alert(`Funcionalidad de editar usuario "${user.name}" en desarrollo`);
  };

  const handleDeleteUser = async (user: User) => {
    if (confirm(`¿Está seguro de eliminar el usuario "${user.name}"?`)) {
      await logUserAction(
        'ELIMINAR',
        `Eliminó el usuario: ${user.name}`,
        user.id,
        user,
        null
      );
      // Aquí iría la lógica para eliminar usuario
      alert(`Usuario "${user.name}" eliminado`);
    }
  };

  // Filtrado de usuarios
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'todos' || user.role === selectedRole;
    const matchesStatus = selectedStatus === 'todos' || user.status === selectedStatus;
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const activeUsers = users.filter(u => u.status === 'active').length;
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
                        user.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {user.status === 'active' ? 'Activo' : 'Inactivo'}
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
                          onClick={() => handleDeleteUser(user)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          title="Eliminar usuario"
                        >
                          <Trash2 className="h-4 w-4" />
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
    </div>
  );
};

export default Users;

