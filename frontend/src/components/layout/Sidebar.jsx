import { NavLink } from 'react-router-dom'
import { 
  Home, 
  ArrowUpDown, 
  Calendar, 
  Tag, 
  BarChart3, 
  Users, 
  LogOut,
  X,
  DollarSign
} from 'lucide-react'

function Sidebar({ user, onLogout, onClose, isMobile = false }) {
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Transacciones', href: '/transacciones', icon: ArrowUpDown },
    { name: 'Flujo Mensual', href: '/flujo-mensual', icon: Calendar },
    { name: 'Categorías', href: '/categorias', icon: Tag },
    { name: 'Reportes', href: '/reportes', icon: BarChart3 },
  ]

  // Solo mostrar usuarios si es Tesorería
  if (user?.rol === 'tesoreria') {
    navigation.push({ name: 'Usuarios', href: '/usuarios', icon: Users })
  }

  const getRoleName = (rol) => {
    switch (rol) {
      case 'tesoreria': return 'Tesorería'
      case 'pagaduria': return 'Pagaduría'
      case 'mesa_dinero': return 'Mesa de Dinero'
      default: return rol
    }
  }

  const getRoleColor = (rol) => {
    switch (rol) {
      case 'tesoreria': return 'bg-purple-100 text-purple-800'
      case 'pagaduria': return 'bg-blue-100 text-blue-800'
      case 'mesa_dinero': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200">
      {/* Header del sidebar */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <DollarSign className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">Flujo Caja</h1>
            <p className="text-xs text-gray-500">Sistema Web</p>
          </div>
        </div>
        {isMobile && (
          <button
            onClick={onClose}
            className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Información del usuario */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
            <span className="text-sm font-medium text-gray-600">
              {user?.nombre?.split(' ').map(n => n[0]).join('') || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.nombre || 'Usuario'}
            </p>
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(user?.rol)}`}>
              {getRoleName(user?.rol)}
            </span>
          </div>
        </div>
      </div>

      {/* Navegación */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={isMobile ? onClose : undefined}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
              {item.name}
            </NavLink>
          )
        })}
      </nav>

      {/* Footer con logout */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onLogout}
          className="flex items-center w-full px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-50 hover:text-gray-900 transition-colors"
        >
          <LogOut className="mr-3 h-5 w-5 flex-shrink-0" />
          Cerrar Sesión
        </button>
      </div>
    </div>
  )
}

export default Sidebar
