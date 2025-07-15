import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'

function ProtectedRoute({ children, requiredRole = null }) {
  const { user, isAuthenticated } = useAuthStore()
  const location = useLocation()

  // Si no está autenticado, redirigir al login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Si se requiere un rol específico y el usuario no lo tiene
  if (requiredRole && user?.rol !== requiredRole) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.764 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Acceso Restringido
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              No tienes permisos para acceder a esta sección. 
              Se requiere rol de {requiredRole === 'tesoreria' ? 'Tesorería' : requiredRole}.
            </p>
            <p className="mt-1 text-xs text-gray-400">
              Tu rol actual: {user?.rol === 'tesoreria' ? 'Tesorería' : 
                             user?.rol === 'pagaduria' ? 'Pagaduría' : 
                             user?.rol === 'mesa_dinero' ? 'Mesa de Dinero' : user?.rol}
            </p>
            <div className="mt-6">
              <button
                onClick={() => window.history.back()}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Volver
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return children
}

export default ProtectedRoute
