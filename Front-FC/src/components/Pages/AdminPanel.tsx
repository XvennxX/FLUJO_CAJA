import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Users, 
  Database, 
  Activity, 
  Settings, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  Clock,
  HardDrive,
  Cpu,
  BarChart3,
  FileText,
  Download,
  Upload,
  RefreshCw,
  Eye,
  UserCheck,
  Lock
} from 'lucide-react';

const AdminPanel: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  // Datos simulados para el panel de administración
  const systemStats = {
    totalUsers: 156,
    activeUsers: 89,
    totalTransactions: 12847,
    systemUptime: '99.8%',
    databaseSize: '2.4 GB',
    cpuUsage: 45,
    memoryUsage: 67,
    lastBackup: '2025-08-06 02:00:00'
  };

  const recentActivities = [
    { id: 1, user: 'María González', action: 'Creó nueva transacción', time: '10:30 AM', type: 'create' },
    { id: 2, user: 'Carlos Pérez', action: 'Modificó configuración', time: '09:15 AM', type: 'edit' },
    { id: 3, user: 'Ana Rodríguez', action: 'Generó reporte mensual', time: '08:45 AM', type: 'report' },
    { id: 4, user: 'Luis Martínez', action: 'Eliminó usuario inactivo', time: '08:30 AM', type: 'delete' },
    { id: 5, user: 'Sistema', action: 'Backup automático completado', time: '02:00 AM', type: 'system' }
  ];

  const pendingApprovals = [
    { id: 1, type: 'Nuevo Usuario', details: 'Sofia Herrera - Área Tesorería', priority: 'alta' },
    { id: 2, type: 'Transacción Grande', details: '$50,000,000 - Pago Proveedores', priority: 'alta' },
    { id: 3, type: 'Cambio de Rol', details: 'Pedro Silva - De Usuario a Supervisor', priority: 'media' },
    { id: 4, type: 'Configuración', details: 'Nuevo límite de transacciones', priority: 'baja' }
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'create': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'edit': return <Settings className="h-4 w-4 text-blue-500" />;
      case 'report': return <FileText className="h-4 w-4 text-purple-500" />;
      case 'delete': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'system': return <Cpu className="h-4 w-4 text-gray-500 dark:text-gray-400" />;
      default: return <Activity className="h-4 w-4 text-gray-500 dark:text-gray-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'alta': return 'bg-red-100 text-red-800 border-red-200';
      case 'media': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'baja': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-200 dark:border-gray-700';
    }
  };

  const handleQuickAction = (action: string) => {
    console.log(`Ejecutando acción: ${action}`);
    // Aquí iría la lógica real para cada acción
  };

  const tabs = [
    { id: 'overview', label: 'Resumen General', icon: BarChart3 },
    { id: 'users', label: 'Gestión de Usuarios', icon: Users },
    { id: 'system', label: 'Sistema', icon: Database },
    { id: 'security', label: 'Seguridad', icon: Shield }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Panel de Administración</h1>
            <p className="text-bolivar-100 mt-1">
              Bienvenido, {user?.name} - Gestiona el sistema SIFCO desde aquí
            </p>
          </div>
          <div className="flex items-center space-x-2 bg-white dark:bg-gray-800/20 rounded-lg px-4 py-2">
            <Shield className="h-5 w-5" />
            <span className="font-medium">Admin Panel</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-bolivar-500 text-bolivar-600'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:text-gray-300 hover:border-gray-300 dark:border-gray-600'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Estadísticas del Sistema */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <Users className="h-8 w-8 text-blue-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-blue-600">Usuarios Totales</p>
                      <p className="text-2xl font-bold text-blue-900">{systemStats.totalUsers}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <UserCheck className="h-8 w-8 text-green-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-green-600">Usuarios Activos</p>
                      <p className="text-2xl font-bold text-green-900">{systemStats.activeUsers}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <BarChart3 className="h-8 w-8 text-purple-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-purple-600">Transacciones</p>
                      <p className="text-2xl font-bold text-purple-900">{systemStats.totalTransactions.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <CheckCircle className="h-8 w-8 text-yellow-600" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-yellow-600">Uptime</p>
                      <p className="text-2xl font-bold text-yellow-900">{systemStats.systemUptime}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actividad Reciente y Aprobaciones Pendientes */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Actividad Reciente */}
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                      <Activity className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                      Actividad Reciente
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-3">
                      {recentActivities.map((activity) => (
                        <div key={activity.id} className="flex items-center space-x-3">
                          {getActivityIcon(activity.type)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{activity.user}</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{activity.action}</p>
                          </div>
                          <div className="text-xs text-gray-400">{activity.time}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Aprobaciones Pendientes */}
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                      <Clock className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                      Aprobaciones Pendientes
                    </h3>
                  </div>
                  <div className="p-4">
                    <div className="space-y-3">
                      {pendingApprovals.map((approval) => (
                        <div key={approval.id} className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{approval.type}</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{approval.details}</p>
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(approval.priority)}`}>
                            {approval.priority}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recursos del Sistema */}
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                    <HardDrive className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                    Recursos del Sistema
                  </h3>
                </div>
                <div className="p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>CPU</span>
                        <span>{systemStats.cpuUsage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{width: `${systemStats.cpuUsage}%`}}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Memoria</span>
                        <span>{systemStats.memoryUsage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{width: `${systemStats.memoryUsage}%`}}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Base de Datos</span>
                        <span>{systemStats.databaseSize}</span>
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        Último backup: {systemStats.lastBackup}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Gestión de Usuarios</h3>
                <button
                  onClick={() => handleQuickAction('create-user')}
                  className="bg-bolivar-500 text-white px-4 py-2 rounded-lg hover:bg-bolivar-600 transition-colors"
                >
                  Crear Usuario
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => handleQuickAction('view-all-users')}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-left"
                >
                  <Users className="h-8 w-8 text-blue-600 mb-2" />
                  <h4 className="font-medium">Ver Todos los Usuarios</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Gestionar todos los usuarios del sistema</p>
                </button>

                <button
                  onClick={() => handleQuickAction('manage-roles')}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-left"
                >
                  <Lock className="h-8 w-8 text-green-600 mb-2" />
                  <h4 className="font-medium">Gestionar Roles</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Configurar permisos y roles</p>
                </button>

                <button
                  onClick={() => handleQuickAction('user-activity')}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-left"
                >
                  <Eye className="h-8 w-8 text-purple-600 mb-2" />
                  <h4 className="font-medium">Actividad de Usuarios</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Monitor de sesiones y actividad</p>
                </button>
              </div>
            </div>
          )}

          {activeTab === 'system' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Configuración del Sistema</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <button
                  onClick={() => handleQuickAction('backup')}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-left"
                >
                  <Download className="h-8 w-8 text-blue-600 mb-2" />
                  <h4 className="font-medium">Crear Backup</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Generar copia de seguridad del sistema</p>
                </button>

                <button
                  onClick={() => handleQuickAction('restore')}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-left"
                >
                  <Upload className="h-8 w-8 text-green-600 mb-2" />
                  <h4 className="font-medium">Restaurar Sistema</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Restaurar desde backup</p>
                </button>

                <button
                  onClick={() => handleQuickAction('maintenance')}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-left"
                >
                  <Settings className="h-8 w-8 text-orange-600 mb-2" />
                  <h4 className="font-medium">Modo Mantenimiento</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Activar/desactivar mantenimiento</p>
                </button>

                <button
                  onClick={() => handleQuickAction('update-system')}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-left"
                >
                  <RefreshCw className="h-8 w-8 text-purple-600 mb-2" />
                  <h4 className="font-medium">Actualizar Sistema</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Verificar y aplicar actualizaciones</p>
                </button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Configuración de Seguridad</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <Shield className="h-8 w-8 text-red-600 mb-2" />
                  <h4 className="font-medium">Logs de Seguridad</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">Revisar intentos de acceso y actividad sospechosa</p>
                  <button
                    onClick={() => handleQuickAction('security-logs')}
                    className="text-bolivar-600 hover:text-bolivar-700 text-sm font-medium"
                  >
                    Ver Logs →
                  </button>
                </div>

                <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <Lock className="h-8 w-8 text-blue-600 mb-2" />
                  <h4 className="font-medium">Políticas de Contraseña</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">Configurar requisitos de seguridad</p>
                  <button
                    onClick={() => handleQuickAction('password-policy')}
                    className="text-bolivar-600 hover:text-bolivar-700 text-sm font-medium"
                  >
                    Configurar →
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;


