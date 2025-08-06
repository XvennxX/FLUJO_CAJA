import React, { useState } from 'react';
import { User, Mail, Phone, MapPin, Calendar, Shield, Edit, Save, X, Camera } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '+57 300 123 4567',
    address: 'Bogotá, Colombia',
    department: 'Área Financiera',
    position: 'Analista Senior',
    startDate: '2023-01-15',
    bio: 'Profesional en finanzas con más de 5 años de experiencia en gestión de flujo de caja y análisis financiero.'
  });

  const getRoleDisplayName = (role: string) => {
    switch (role) {
      case 'administrador':
        return 'Administrador del Sistema';
      case 'tesoreria':
        return 'Analista de Tesorería';
      case 'pagaduria':
        return 'Especialista en Pagaduría';
      case 'mesa_dinero':
        return 'Operador Mesa de Dinero';
      default:
        return role;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'administrador':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'tesoreria':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'pagaduria':
        return 'bg-bolivar-100 text-bolivar-800 border-bolivar-200';
      case 'mesa_dinero':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-200 dark:border-gray-700';
    }
  };

  const handleSave = () => {
    // Aquí iría la lógica para guardar los cambios
    setIsEditing(false);
    console.log('Datos guardados:', formData);
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Restaurar datos originales
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      phone: '+57 300 123 4567',
      address: 'Bogotá, Colombia',
      department: 'Área Financiera',
      position: 'Analista Senior',
      startDate: '2023-01-15',
      bio: 'Profesional en finanzas con más de 5 años de experiencia en gestión de flujo de caja y análisis financiero.'
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Mi Perfil</h1>
        <p className="text-bolivar-100">Gestiona tu información personal y preferencias</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Información Principal */}
        <div className="lg:col-span-2 space-y-6">
          {/* Datos Personales */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                <User className="mr-2 text-bolivar-600" size={20} />
                Información Personal
              </h2>
              {!isEditing ? (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center space-x-2 px-3 py-2 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors"
                >
                  <Edit size={16} />
                  <span>Editar</span>
                </button>
              ) : (
                <div className="flex space-x-2">
                  <button
                    onClick={handleSave}
                    className="flex items-center space-x-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                  >
                    <Save size={16} />
                    <span>Guardar</span>
                  </button>
                  <button
                    onClick={handleCancel}
                    className="flex items-center space-x-2 px-3 py-2 bg-gray-50 dark:bg-gray-9000 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    <X size={16} />
                    <span>Cancelar</span>
                  </button>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre Completo</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                  />
                ) : (
                  <p className="text-gray-900 dark:text-white py-2">{formData.name}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Correo Electrónico</label>
                {isEditing ? (
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                  />
                ) : (
                  <p className="text-gray-900 dark:text-white py-2 flex items-center">
                    <Mail className="mr-2 text-gray-500 dark:text-gray-400" size={16} />
                    {formData.email}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Teléfono</label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                  />
                ) : (
                  <p className="text-gray-900 dark:text-white py-2 flex items-center">
                    <Phone className="mr-2 text-gray-500 dark:text-gray-400" size={16} />
                    {formData.phone}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Ubicación</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                  />
                ) : (
                  <p className="text-gray-900 dark:text-white py-2 flex items-center">
                    <MapPin className="mr-2 text-gray-500 dark:text-gray-400" size={16} />
                    {formData.address}
                  </p>
                )}
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Biografía</label>
              {isEditing ? (
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
                />
              ) : (
                <p className="text-gray-900 dark:text-white py-2">{formData.bio}</p>
              )}
            </div>
          </div>

          {/* Información Laboral */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Shield className="mr-2 text-bolivar-600" size={20} />
              Información Laboral
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Departamento</label>
                <p className="text-gray-900 dark:text-white py-2">{formData.department}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Cargo</label>
                <p className="text-gray-900 dark:text-white py-2">{formData.position}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rol en el Sistema</label>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getRoleColor(user?.role || '')}`}>
                  {getRoleDisplayName(user?.role || '')}
                </span>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha de Ingreso</label>
                <p className="text-gray-900 dark:text-white py-2 flex items-center">
                  <Calendar className="mr-2 text-gray-500 dark:text-gray-400" size={16} />
                  {new Date(formData.startDate).toLocaleDateString('es-CO')}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Avatar */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 text-center">
            <div className="relative inline-block">
              <div className="w-24 h-24 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-2xl">
                  {user?.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <button className="absolute bottom-0 right-0 p-2 bg-white dark:bg-gray-800 rounded-full shadow-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:bg-gray-900 transition-colors">
                <Camera size={16} className="text-gray-600 dark:text-gray-400" />
              </button>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{user?.name}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{getRoleDisplayName(user?.role || '')}</p>
          </div>

          {/* Estadísticas */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Estadísticas</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Sesiones Activas</span>
                <span className="font-medium text-gray-900 dark:text-white">1</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Último Acceso</span>
                <span className="font-medium text-gray-900 dark:text-white">Hoy</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Días Activo</span>
                <span className="font-medium text-gray-900 dark:text-white">127</span>
              </div>
            </div>
          </div>

          {/* Accesos Recientes */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Módulos Más Usados</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Panel</span>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div className="bg-bolivar-500 h-2 rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Conciliación</span>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div className="bg-bolivar-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Informes</span>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div className="bg-bolivar-500 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;


