import React, { useState } from 'react';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
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
      setError('Error al iniciar sesión. Intenta nuevamente.');
    }
  };

  return (
    <div className="min-h-screen flex relative">
      {/* Panel izquierdo - Formulario */}
      <div className="flex-1 flex flex-col bg-gray-100">
        {/* Header con logo */}
        <div className="p-8">
          <div className="flex items-center space-x-3">
            {/* Logo placeholder - solicitar logo real */}
            <div className="w-16 h-16 bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">SB</span>
            </div>
            <div>
              <div className="text-bolivar-600 font-bold text-xl">SEGUROS</div>
              <div className="text-bolivar-600 font-bold text-xl -mt-1">BOLÍVAR</div>
            </div>
          </div>
        </div>

        {/* Formulario centrado */}
        <div className="flex-1 flex items-center justify-center px-8 pb-20">
          <div className="w-full max-w-sm">
            <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
              <h1 className="text-xl font-medium text-bolivar-600 mb-2 text-center">
                Iniciar Sesión
              </h1>
              <p className="text-sm text-gray-600 mb-8 text-center">SIFCO - Sistema Web</p>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Correo electrónico
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-3 py-3 border border-gray-300 rounded-md focus:ring-1 focus:ring-bolivar-500 focus:border-bolivar-500 transition-all text-sm"
                    placeholder=""
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contraseña
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-3 py-3 pr-10 border border-gray-300 rounded-md focus:ring-1 focus:ring-bolivar-500 focus:border-bolivar-500 transition-all text-sm"
                      placeholder=""
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    id="remember-me"
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="h-4 w-4 text-bolivar-600 focus:ring-bolivar-500 border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                    Recordarme
                  </label>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-bolivar-600 text-white py-3 px-4 rounded-md hover:bg-bolivar-700 focus:ring-2 focus:ring-bolivar-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center font-medium"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="animate-spin h-4 w-4 mr-2" />
                      Iniciando...
                    </>
                  ) : (
                    'Entrar'
                  )}
                </button>
              </form>

              {/* Credenciales de prueba */}
              <div className="mt-6 p-3 bg-gray-50 rounded-md">
                <p className="text-xs text-gray-600 text-center">
                  <strong>Credenciales de prueba:</strong><br />
                  Email: ana@email.com<br />
                  Contraseña: password
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Panel derecho - Información */}
      <div className="w-96 bg-bolivar-600 text-white p-8 flex flex-col justify-center">
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-6 leading-tight">
            VISITA LAS POLÍTICAS DE PRIVACIDAD DE ESTE SITIO
          </h2>
          
          <div className="space-y-4 text-sm leading-relaxed">
            <p>
              El acceso a este sistema está permitido solo a las personas{' '}
              <span className="font-semibold">expresamente autorizadas por</span>{' '}
              las normativas de seguridad.
            </p>
            
            <p>
              Los usuarios que accedan sin autorización serán sujetos a investigaciones y podrán 
              recibir acusaciones penales y/o sanciones disciplinarias por parte de la{' '}
              <span className="font-semibold">Organización.</span>
            </p>
            
            <p>
              Conozca más sobre las políticas de privacidad 
              del sitio.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 bg-bolivar-700 text-white py-3">
        <div className="container mx-auto px-8">
          <div className="flex justify-center space-x-8 text-xs mb-1">
            <a href="#" className="hover:text-gold-400 transition-colors">
              Políticas de privacidad
            </a>
            <a href="#" className="hover:text-gold-400 transition-colors">
              Términos y Condiciones de uso
            </a>
            <a href="#" className="hover:text-gold-400 transition-colors">
              Asistencia al usuario
            </a>
          </div>
          <div className="text-center text-xs text-gray-300">
            © 2025 Seguros Bolívar S.A. - Todos los derechos reservados
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
