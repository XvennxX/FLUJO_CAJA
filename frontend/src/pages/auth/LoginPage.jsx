import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { login as apiLogin } from '../../services/auth'
import toast from 'react-hot-toast'
import { Building2, Lock, Mail } from 'lucide-react'

function LoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [isLoading, setIsLoading] = useState(false)
  
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Usuarios de ejemplo para modo demo (sin backend)
      const usuariosDemo = [
        {
          email: 'tesoreria@empresa.com',
          password: '123456',
          usuario: {
            id: 1,
            nombre: 'Ana García',
            email: 'tesoreria@empresa.com',
            rol: 'tesoreria',
            permisos: ['todas_las_funciones']
          }
        },
        {
          email: 'pagaduria@empresa.com', 
          password: '123456',
          usuario: {
            id: 2,
            nombre: 'Carlos Ruiz',
            email: 'pagaduria@empresa.com',
            rol: 'pagaduria',
            permisos: ['transacciones_egresos', 'categorias_egresos', 'reportes_limitados']
          }
        },
        {
          email: 'mesa@empresa.com',
          password: '123456', 
          usuario: {
            id: 3,
            nombre: 'Miguel Torres',
            email: 'mesa@empresa.com',
            rol: 'mesa_dinero',
            permisos: ['solo_lectura', 'reportes_consulta']
          }
        }
      ]

      // Simular delay de red
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Buscar usuario
      const usuarioEncontrado = usuariosDemo.find(
        u => u.email === formData.email && u.password === formData.password
      )

      if (usuarioEncontrado) {
        const fakeToken = 'demo-token-' + Date.now()
        login(usuarioEncontrado.usuario, fakeToken)
        toast.success(`¡Bienvenido, ${usuarioEncontrado.usuario.nombre}!`)
        navigate('/dashboard')
      } else {
        toast.error('Credenciales incorrectas. Revisa los usuarios de ejemplo.')
      }

      // Para conectar con API real, descomenta esto:
      // const response = await apiLogin(formData.email, formData.password)
      // login(response.usuario, response.access_token)
      // toast.success(`¡Bienvenido, ${response.usuario.nombre}!`)
      // navigate('/dashboard')
      
    } catch (error) {
      console.error('Error de login:', error)
      toast.error('Error al iniciar sesión')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo y título */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <Building2 className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Sistema de Flujo de Caja
          </h1>
          <p className="text-gray-600">
            Ingresa tus credenciales para acceder al sistema
          </p>
        </div>

        {/* Formulario */}
        <div className="card">
          <div className="card-body">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="label-field">
                  <Mail className="h-4 w-4 inline mr-2" />
                  Correo electrónico
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="usuario@empresa.com"
                  required
                  autoComplete="email"
                />
              </div>

              <div>
                <label className="label-field">
                  <Lock className="h-4 w-4 inline mr-2" />
                  Contraseña
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="••••••••"
                  required
                  autoComplete="current-password"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full py-3"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                    Iniciando sesión...
                  </div>
                ) : (
                  'Iniciar Sesión'
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Información de roles */}
        <div className="mt-6 card">
          <div className="card-body">
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              👥 Usuarios de ejemplo (Modo Demo):
            </h3>
            <div className="space-y-3 text-sm">
              <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                <div className="font-medium text-purple-900">🏦 Tesorería</div>
                <div className="text-purple-700 mt-1">
                  <strong>Email:</strong> tesoreria@empresa.com<br/>
                  <strong>Contraseña:</strong> 123456<br/>
                  <span className="text-xs">Acceso completo al sistema</span>
                </div>
              </div>
              
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="font-medium text-blue-900">💰 Pagaduría</div>
                <div className="text-blue-700 mt-1">
                  <strong>Email:</strong> pagaduria@empresa.com<br/>
                  <strong>Contraseña:</strong> 123456<br/>
                  <span className="text-xs">Solo gestión de egresos</span>
                </div>
              </div>
              
              <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="font-medium text-green-900">📊 Mesa de Dinero</div>
                <div className="text-green-700 mt-1">
                  <strong>Email:</strong> mesa@empresa.com<br/>
                  <strong>Contraseña:</strong> 123456<br/>
                  <span className="text-xs">Solo lectura y reportes</span>
                </div>
              </div>
            </div>
            
            <div className="mt-4 p-2 bg-yellow-50 rounded border border-yellow-200">
              <p className="text-xs text-yellow-800">
                💡 <strong>Nota:</strong> Este es el modo demo sin backend. 
                Los datos son de ejemplo y no se guardan permanentemente.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
