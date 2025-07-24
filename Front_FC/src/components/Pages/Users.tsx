import React, { useState } from 'react';
import { Users as UsersIcon, Plus, Edit, Trash2, Shield, Mail, Calendar } from 'lucide-react';

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
      role: 'Tesorero',
      status: 'active',
      lastLogin: '2025-01-21',
      createdAt: '2024-02-20',
    },
    {
      id: '3',
      name: 'María López',
      email: 'maria.lopez@email.com',
      role: 'Contador',
      status: 'inactive',
      lastLogin: '2025-01-18',
      createdAt: '2024-03-10',
    },
  ]);

  const activeUsers = users.filter(u => u.status === 'active').length;
  const totalUsers = users.length;

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'Administrador':
        return 'bg-purple-100 text-purple-800';
      case 'Tesorero':
        return 'bg-blue-100 text-blue-800';
      case 'Contador':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-500">
              <UsersIcon className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Total Usuarios</p>
            <p className="text-2xl font-bold text-blue-600">{totalUsers}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
              <Shield className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Usuarios Activos</p>
            <p className="text-2xl font-bold text-green-600">{activeUsers}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
              <Mail className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Roles Activos</p>
            <p className="text-2xl font-bold text-purple-600">3</p>
          </div>
        </div>
      </div>

      {/* Users Management */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <h3 className="text-lg font-semibold text-gray-900">Gestión de Usuarios</h3>
          <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center space-x-2">
            <Plus className="h-4 w-4" />
            <span>Nuevo Usuario</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Último Acceso
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-medium text-sm">
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{user.name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
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
                      <span className="text-sm text-gray-900">
                        {new Date(user.lastLogin).toLocaleDateString('es-CO')}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button className="p-1 text-gray-400 hover:text-blue-600 transition-colors">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button className="p-1 text-gray-400 hover:text-red-600 transition-colors">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Roles */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Roles y Permisos</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-purple-500 rounded-full" />
              <h4 className="font-medium text-gray-900">Administrador</h4>
            </div>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Acceso completo al sistema</li>
              <li>• Gestión de usuarios</li>
              <li>• Configuración del sistema</li>
              <li>• Todos los reportes</li>
            </ul>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full" />
              <h4 className="font-medium text-gray-900">Tesorero</h4>
            </div>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Gestión de transacciones</li>
              <li>• Reportes financieros</li>
              <li>• Categorías</li>
              <li>• Flujo mensual</li>
            </ul>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-green-500 rounded-full" />
              <h4 className="font-medium text-gray-900">Contador</h4>
            </div>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Solo lectura de reportes</li>
              <li>• Exportar informes</li>
              <li>• Ver transacciones</li>
              <li>• Dashboard básico</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Users;