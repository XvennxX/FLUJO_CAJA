import { Menu, Bell, Search, ChevronDown } from 'lucide-react'

function Header({ user, onMenuClick, onLogout }) {
  const getRoleName = (rol) => {
    switch (rol) {
      case 'tesoreria': return 'Tesorería'
      case 'pagaduria': return 'Pagaduría'
      case 'mesa_dinero': return 'Mesa de Dinero'
      default: return rol
    }
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Botón de menú para móvil */}
        <div className="flex items-center">
          <button
            type="button"
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            onClick={onMenuClick}
          >
            <Menu className="h-6 w-6" />
          </button>
          
          {/* Breadcrumb o título de página */}
          <div className="hidden lg:block ml-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Sistema de Flujo de Caja
            </h2>
            <p className="text-sm text-gray-500">
              {new Date().toLocaleDateString('es-ES', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
        </div>

        {/* Barra de búsqueda central */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
              placeholder="Buscar transacciones, categorías..."
            />
          </div>
        </div>

        {/* Acciones del usuario */}
        <div className="flex items-center space-x-4">
          {/* Notificaciones */}
          <button className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-md relative">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400"></span>
          </button>

          {/* Dropdown del usuario */}
          <div className="relative">
            <button className="flex items-center space-x-3 text-sm rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 hover:bg-gray-50">
              <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                <span className="text-xs font-medium text-gray-600">
                  {user?.nombre?.split(' ').map(n => n[0]).join('') || 'U'}
                </span>
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-gray-900">
                  {user?.nombre || 'Usuario'}
                </p>
                <p className="text-xs text-gray-500">
                  {getRoleName(user?.rol)}
                </p>
              </div>
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </button>
            
            {/* Dropdown menu - Por ahora solo visual, se puede implementar después */}
            {/* 
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10">
              <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                Perfil
              </a>
              <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                Configuración
              </a>
              <hr className="my-1" />
              <button 
                onClick={onLogout}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Cerrar Sesión
              </button>
            </div>
            */}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
