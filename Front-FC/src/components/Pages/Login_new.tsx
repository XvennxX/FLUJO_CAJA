import React, { useState } from 'react';
import { Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useAuditoria } from '../../hooks/useAuditoria';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const { addLog } = useAuditoria();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError('Por favor, completa todos los campos');
      return;
    }
    
    try {
      const success = await login(email, password);
      if (success) {
        // Registrar login exitoso en auditoría
        await addLog({
          accion: 'CONSULTAR',
          modulo: 'USUARIOS',
          descripcion: `Usuario inició sesión exitosamente: ${email}`,
          entidad: 'Sistema',
          entidadId: email
        });
      } else {
        setError('Credenciales incorrectas. Verifica tu correo y contraseña.');
        // Registrar intento fallido
        await addLog({
          accion: 'CONSULTAR',
          modulo: 'USUARIOS',
          descripcion: `Intento de login fallido para: ${email}`,
          entidad: 'Sistema',
          entidadId: email
        });
      }
    } catch (err) {
      setError('Error de conexión con el servidor. Intenta nuevamente.');
      console.error('Error en login:', err);
    }
  };

  return (
    <div className="min-h-screen flex relative">
      {/* Panel izquierdo - Formulario */}
      <div className="flex-1 flex flex-col bg-gray-100 dark:bg-gray-700">
        {/* Header con logo */}
        <div className="p-8">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-bolivar-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">SB</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">SEGUROS BOLÍVAR</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">SIFCO - Sistema Web</p>
            </div>
          </div>
        </div>

        {/* Formulario centrado */}
        <div className="flex-1 flex items-center justify-center px-8">
          <div className="w-full max-w-md">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Iniciar Sesión</h2>
                <p className="text-gray-600 dark:text-gray-400">Accede al sistema de flujo de caja</p>
              </div>

              {/* Mostrar error si existe */}
              {error && (
                <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5 text-red-500" />
                  <span className="text-red-700 dark:text-red-400 text-sm">{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Correo electrónico
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                    placeholder="tu@email.com"
                    required
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Contraseña
                  </label>
                  <div className="relative">
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 pr-12"
                      placeholder="••••••••"
                      required
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={isLoading}
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5 text-gray-400" />
                      ) : (
                        <Eye className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="h-4 w-4 text-bolivar-500 focus:ring-bolivar-500 border-gray-300 rounded"
                      disabled={isLoading}
                    />
                    <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Recordarme
                    </label>
                  </div>
                  <button
                    type="button"
                    className="text-sm text-bolivar-500 hover:text-bolivar-600 dark:text-bolivar-400"
                    disabled={isLoading}
                  >
                    ¿Olvidaste tu contraseña?
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-bolivar-500 text-white py-3 px-4 rounded-lg hover:bg-bolivar-600 focus:ring-2 focus:ring-bolivar-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-colors"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Iniciando sesión...</span>
                    </>
                  ) : (
                    <span>Entrar</span>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Panel derecho - Información */}
      <div className="hidden lg:flex lg:w-1/2 bg-bolivar-500 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-bolivar-600 via-bolivar-500 to-green-600"></div>
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <h2 className="text-4xl font-bold mb-6">
            Sistema de Flujo de Caja
          </h2>
          <p className="text-xl mb-8 text-bolivar-100">
            Gestiona y controla los movimientos financieros de las compañías del grupo Bolívar de manera eficiente y segura.
          </p>
          
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span className="text-bolivar-100">Control en tiempo real</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span className="text-bolivar-100">Reportes detallados</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span className="text-bolivar-100">Auditoría completa</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span className="text-bolivar-100">Acceso seguro por roles</span>
            </div>
          </div>

          {/* Información de acceso */}
          <div className="mt-12 p-6 bg-white/10 backdrop-blur-sm rounded-lg">
            <h3 className="font-semibold text-white mb-3 text-center">🔐 Acceso al Sistema</h3>
            <div className="space-y-2 text-sm">
              <div className="text-bolivar-100">
                <p>• Utiliza las credenciales proporcionadas por tu administrador</p>
                <p>• El acceso está restringido según tu rol asignado</p>
                <p>• Todas las acciones quedan registradas en auditoría</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Patrón decorativo */}
        <div className="absolute bottom-0 right-0 w-64 h-64 bg-white/5 rounded-full transform translate-x-32 translate-y-32"></div>
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full transform translate-x-16 -translate-y-16"></div>
      </div>
    </div>
  );
};

export default Login;
