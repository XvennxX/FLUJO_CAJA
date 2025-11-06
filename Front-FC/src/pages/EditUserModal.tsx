import React, { useState, useEffect } from 'react';
import { X, Loader2, AlertCircle, User, Mail, Shield, Lock } from 'lucide-react';

interface EditUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUserUpdated: () => void;
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
    estado: boolean;
  } | null;
}

const EditUserModal: React.FC<EditUserModalProps> = ({ isOpen, onClose, onUserUpdated, user }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    rol: '',
    password: '',
    estado: true
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [changePassword, setChangePassword] = useState(false);

  // Cargar datos del usuario cuando se abre el modal
  useEffect(() => {
    if (user && isOpen) {
      setFormData({
        nombre: user.name,
        email: user.email,
        rol: user.role,
        password: '',
        estado: user.estado
      });
      setChangePassword(false);
      setError(null);
    }
  }, [user, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!user) {
      setError('No hay usuario seleccionado');
      return;
    }

    // Validaciones
    if (!formData.nombre.trim()) {
      setError('El nombre es requerido');
      return;
    }

    if (!formData.email.trim()) {
      setError('El correo electrónico es requerido');
      return;
    }

    if (!formData.rol) {
      setError('Debe seleccionar un rol');
      return;
    }

    // Validar contraseña solo si se está cambiando
    if (changePassword && formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setIsSubmitting(true);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No hay token de autenticación');
        return;
      }

      // Preparar datos para enviar (solo incluir password si se está cambiando)
      const dataToSend: any = {
        nombre: formData.nombre.trim(),
        email: formData.email.trim().toLowerCase(),
        rol: formData.rol,
        estado: formData.estado
      };

      // Solo incluir password si se está cambiando
      if (changePassword && formData.password) {
        dataToSend.password = formData.password;
      }

      console.log('📤 Actualizando usuario:', user.id, dataToSend);

      const response = await fetch(`http://localhost:8000/api/v1/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(dataToSend)
      });

      if (response.ok) {
        const updatedUser = await response.json();
        console.log('✅ Usuario actualizado exitosamente:', updatedUser);
        
        // Resetear formulario
        setFormData({
          nombre: '',
          email: '',
          rol: '',
          password: '',
          estado: true
        });
        setChangePassword(false);
        
        // Notificar éxito
        onUserUpdated();
        onClose();
      } else {
        const errorData = await response.json();
        console.error('❌ Error del servidor:', errorData);
        setError(errorData.detail || 'Error al actualizar el usuario');
      }
    } catch (err) {
      console.error('💥 Error en la solicitud:', err);
      setError('Error de conexión al actualizar el usuario');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({
        ...prev,
        [name]: checked
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg">
              <User className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Editar Usuario</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Modificar información del usuario</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            disabled={isSubmitting}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
                <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Nombre Completo */}
            <div>
              <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span>Nombre Completo</span>
                </div>
              </label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="Juan Pérez García"
                required
                disabled={isSubmitting}
              />
            </div>

            {/* Correo Electrónico */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <div className="flex items-center space-x-2">
                  <Mail className="h-4 w-4" />
                  <span>Correo Electrónico</span>
                </div>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="usuario@segurosbolivar.com"
                required
                disabled={isSubmitting}
              />
            </div>

            {/* Rol */}
            <div>
              <label htmlFor="rol" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <div className="flex items-center space-x-2">
                  <Shield className="h-4 w-4" />
                  <span>Rol del Usuario</span>
                </div>
              </label>
              <select
                id="rol"
                name="rol"
                value={formData.rol}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                required
                disabled={isSubmitting}
              >
                <option value="">Seleccione un rol</option>
                <option value="Administrador">Administrador</option>
                <option value="Tesorería">Tesorería</option>
                <option value="Pagaduría">Pagaduría</option>
                <option value="Mesa de Dinero">Mesa de Dinero</option>
              </select>
            </div>

            {/* Cambiar Contraseña */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div className="flex items-center mb-4">
                <input
                  type="checkbox"
                  id="changePassword"
                  checked={changePassword}
                  onChange={(e) => setChangePassword(e.target.checked)}
                  className="h-4 w-4 text-blue-500 focus:ring-blue-500 border-gray-300 rounded"
                  disabled={isSubmitting}
                />
                <label htmlFor="changePassword" className="ml-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Cambiar contraseña
                </label>
              </div>

              {changePassword && (
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <div className="flex items-center space-x-2">
                      <Lock className="h-4 w-4" />
                      <span>Nueva Contraseña</span>
                    </div>
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                    placeholder="Mínimo 6 caracteres"
                    disabled={isSubmitting}
                  />
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Dejar en blanco para mantener la contraseña actual
                  </p>
                </div>
              )}
            </div>

            {/* Estado */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="estado" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Estado del Usuario
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    Activar o desactivar el acceso del usuario al sistema
                  </p>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="estado"
                    name="estado"
                    checked={formData.estado}
                    onChange={handleChange}
                    className="h-4 w-4 text-green-500 focus:ring-green-500 border-gray-300 rounded"
                    disabled={isSubmitting}
                  />
                  <label htmlFor="estado" className="ml-2 block text-sm text-gray-900 dark:text-white">
                    {formData.estado ? 'Activo' : 'Inactivo'}
                  </label>
                </div>
              </div>
            </div>

            {/* Información Adicional */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
                ℹ️ Información Importante
              </h4>
              <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                <li>• Los cambios se aplicarán inmediatamente</li>
                <li>• Si cambia el rol, los permisos se actualizarán</li>
                <li>• Si desactiva el usuario, perderá acceso al sistema</li>
                <li>• El email debe ser único en el sistema</li>
              </ul>
            </div>

            {/* Botones */}
            <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                disabled={isSubmitting}
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-all"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Guardando...</span>
                  </>
                ) : (
                  <>
                    <User className="h-5 w-5" />
                    <span>Guardar Cambios</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditUserModal;
