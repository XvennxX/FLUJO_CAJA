import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { Users, Plus, Edit, Trash2, Shield, UserCheck, UserX } from 'lucide-react'

function UsuariosPage() {
  const { user } = useAuthStore()
  const [usuarios, setUsuarios] = useState([])
  const [mostrarModal, setMostrarModal] = useState(false)
  const [usuarioEditando, setUsuarioEditando] = useState(null)

  // Solo Tesorería puede acceder a esta página
  const puedeGestionar = user?.rol === 'tesoreria'

  useEffect(() => {
    // Datos de ejemplo
    setUsuarios([
      {
        id: 1,
        nombre: 'Ana García',
        email: 'ana.garcia@empresa.com',
        rol: 'tesoreria',
        activo: true,
        fechaCreacion: '2025-01-01',
        ultimoAcceso: '2025-01-15',
        permisos: ['todas_las_funciones']
      },
      {
        id: 2,
        nombre: 'Carlos Ruiz',
        email: 'carlos.ruiz@empresa.com',
        rol: 'pagaduria',
        activo: true,
        fechaCreacion: '2025-01-02',
        ultimoAcceso: '2025-01-14',
        permisos: ['transacciones_egresos', 'categorias_egresos', 'reportes_limitados']
      },
      {
        id: 3,
        nombre: 'Miguel Torres',
        email: 'miguel.torres@empresa.com',
        rol: 'mesa_dinero',
        activo: true,
        fechaCreacion: '2025-01-03',
        ultimoAcceso: '2025-01-13',
        permisos: ['solo_lectura', 'reportes_consulta']
      },
      {
        id: 4,
        nombre: 'Laura Sánchez',
        email: 'laura.sanchez@empresa.com',
        rol: 'pagaduria',
        activo: false,
        fechaCreacion: '2024-12-15',
        ultimoAcceso: '2025-01-05',
        permisos: ['transacciones_egresos']
      }
    ])
  }, [])

  const rolesInfo = {
    tesoreria: {
      nombre: 'Tesorería',
      descripcion: 'Acceso completo al sistema',
      color: 'bg-purple-100 text-purple-800',
      icono: Shield
    },
    pagaduria: {
      nombre: 'Pagaduría',
      descripcion: 'Gestión de egresos y pagos',
      color: 'bg-blue-100 text-blue-800',
      icono: UserCheck
    },
    mesa_dinero: {
      nombre: 'Mesa de Dinero',
      descripcion: 'Solo lectura y consultas',
      color: 'bg-green-100 text-green-800',
      icono: Users
    }
  }

  const editarUsuario = (usuario) => {
    setUsuarioEditando(usuario)
    setMostrarModal(true)
  }

  const cambiarEstadoUsuario = (id, nuevoEstado) => {
    setUsuarios(usuarios.map(u => 
      u.id === id ? { ...u, activo: nuevoEstado } : u
    ))
  }

  const eliminarUsuario = (id) => {
    if (confirm('¿Está seguro de eliminar este usuario?')) {
      setUsuarios(usuarios.filter(u => u.id !== id))
    }
  }

  if (!puedeGestionar) {
    return (
      <div className="space-y-6">
        <div className="card bg-red-50 border-red-200">
          <div className="card-body text-center py-12">
            <Shield className="h-16 w-16 text-red-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-red-800 mb-2">Acceso Restringido</h2>
            <p className="text-red-600">
              Solo los usuarios con rol de Tesorería pueden gestionar usuarios del sistema.
            </p>
          </div>
        </div>
      </div>
    )
  }

  const usuariosActivos = usuarios.filter(u => u.activo)
  const usuariosInactivos = usuarios.filter(u => !u.activo)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-200 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
          <p className="text-gray-600 mt-2">Administración de usuarios y permisos del sistema</p>
        </div>
        <button 
          onClick={() => setMostrarModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Nuevo Usuario</span>
        </button>
      </div>

      {/* Resumen de roles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(rolesInfo).map(([rol, info]) => {
          const cantidad = usuarios.filter(u => u.rol === rol && u.activo).length
          const IconoRol = info.icono
          
          return (
            <div key={rol} className="card">
              <div className="card-body">
                <div className="flex items-center">
                  <div className={`p-3 rounded-lg ${info.color.replace('text-', 'bg-').replace('800', '100')}`}>
                    <IconoRol className={`h-6 w-6 ${info.color.replace('bg-', 'text-').replace('100', '600')}`} />
                  </div>
                  <div className="ml-4">
                    <div className="text-2xl font-bold text-gray-900">{cantidad}</div>
                    <div className="text-sm font-medium text-gray-600">{info.nombre}</div>
                    <div className="text-xs text-gray-500">{info.descripcion}</div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Usuarios activos */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium flex items-center">
            <UserCheck className="h-5 w-5 mr-2 text-green-600" />
            Usuarios Activos ({usuariosActivos.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Último Acceso
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Permisos
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {usuariosActivos.map((usuario) => {
                const rolInfo = rolesInfo[usuario.rol]
                const IconoRol = rolInfo.icono
                
                return (
                  <tr key={usuario.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                          <span className="text-sm font-medium text-gray-600">
                            {usuario.nombre.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{usuario.nombre}</div>
                          <div className="text-sm text-gray-500">{usuario.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${rolInfo.color}`}>
                        <IconoRol className="h-3 w-3 mr-1" />
                        {rolInfo.nombre}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(usuario.ultimoAcceso).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-xs text-gray-500">
                        {usuario.permisos.slice(0, 2).join(', ')}
                        {usuario.permisos.length > 2 && ` (+${usuario.permisos.length - 2} más)`}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="flex justify-center space-x-2">
                        <button 
                          onClick={() => editarUsuario(usuario)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button 
                          onClick={() => cambiarEstadoUsuario(usuario.id, false)}
                          className="text-orange-600 hover:text-orange-900"
                        >
                          <UserX className="h-4 w-4" />
                        </button>
                        <button 
                          onClick={() => eliminarUsuario(usuario.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Usuarios inactivos */}
      {usuariosInactivos.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium flex items-center">
              <UserX className="h-5 w-5 mr-2 text-orange-600" />
              Usuarios Inactivos ({usuariosInactivos.length})
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Usuario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Desactivado desde
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {usuariosInactivos.map((usuario) => {
                  const rolInfo = rolesInfo[usuario.rol]
                  
                  return (
                    <tr key={usuario.id} className="hover:bg-gray-50 opacity-60">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-600">
                              {usuario.nombre.split(' ').map(n => n[0]).join('')}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{usuario.nombre}</div>
                            <div className="text-sm text-gray-500">{usuario.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                          {rolInfo.nombre}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(usuario.ultimoAcceso).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex justify-center space-x-2">
                          <button 
                            onClick={() => cambiarEstadoUsuario(usuario.id, true)}
                            className="text-green-600 hover:text-green-900"
                          >
                            <UserCheck className="h-4 w-4" />
                          </button>
                          <button 
                            onClick={() => eliminarUsuario(usuario.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Información de permisos */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="card-header">
          <h4 className="text-lg font-medium text-blue-800">Estructura de Permisos</h4>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {Object.entries(rolesInfo).map(([rol, info]) => (
              <div key={rol} className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${info.color.replace('text-', 'bg-').replace('800', '100')}`}>
                  <info.icono className={`h-4 w-4 ${info.color.replace('bg-', 'text-').replace('100', '600')}`} />
                </div>
                <div>
                  <div className="font-medium text-blue-900">{info.nombre}</div>
                  <div className="text-sm text-blue-700">{info.descripcion}</div>
                  <div className="text-xs text-blue-600 mt-1">
                    {rol === 'tesoreria' && 'Todas las funciones del sistema'}
                    {rol === 'pagaduria' && 'Transacciones de egresos, categorías de gastos, reportes limitados'}
                    {rol === 'mesa_dinero' && 'Solo lectura de transacciones y reportes de consulta'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default UsuariosPage
