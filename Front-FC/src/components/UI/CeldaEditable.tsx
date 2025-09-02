import React, { useState, useEffect, useRef } from 'react';
import { formatCurrency } from '../../utils/formatters';

interface CeldaEditableProps {
  valor: number;
  conceptoId: number;
  cuentaId: number | null;
  companiaId?: number;
  onGuardar: (conceptoId: number, cuentaId: number | null, monto: number, companiaId?: number) => Promise<boolean>;
  disabled?: boolean;
}

export const CeldaEditable: React.FC<CeldaEditableProps> = ({
  valor,
  conceptoId,
  cuentaId,
  companiaId,
  onGuardar,
  disabled = false
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [hasError, setHasError] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Formatear el valor para mostrar
  const formatearValor = (val: number): string => {
    if (val === 0) return '';
    return val.toString();
  };

  // Parsear el valor del input
  const parsearValor = (val: string): number => {
    if (!val || val.trim() === '') return 0;
    
    // Remover caracteres no numéricos excepto punto, coma y signo negativo
    const cleanValue = val.replace(/[^\d.,-]/g, '');
    
    // Reemplazar coma por punto para el decimal
    const normalizedValue = cleanValue.replace(',', '.');
    
    const parsed = parseFloat(normalizedValue);
    return isNaN(parsed) ? 0 : parsed;
  };

  // Inicializar el valor del input cuando se abre la edición
  useEffect(() => {
    if (isEditing) {
      setInputValue(formatearValor(valor));
      setHasError(false);
      // Enfocar el input después de un pequeño delay
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.select();
      }, 10);
    }
  }, [isEditing, valor]);

  // Manejar el click para iniciar edición
  const handleClick = () => {
    if (!disabled) {
      setIsEditing(true);
    }
  };

  // Manejar el cambio en el input
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    setHasError(false);
  };

  // Manejar el guardado
  const handleSave = async () => {
    if (isSaving) return;

    const nuevoValor = parsearValor(inputValue);
    
    // Si el valor no cambió, cancelar edición
    if (nuevoValor === valor) {
      setIsEditing(false);
      return;
    }

    try {
      setIsSaving(true);
      const success = await onGuardar(conceptoId, cuentaId, nuevoValor, companiaId);
      
      if (success) {
        setIsEditing(false);
        setHasError(false);
      } else {
        setHasError(true);
        // Mantener el modo de edición para permitir correcciones
      }
    } catch (error) {
      console.error('Error saving cell:', error);
      setHasError(true);
    } finally {
      setIsSaving(false);
    }
  };

  // Manejar la cancelación
  const handleCancel = () => {
    setIsEditing(false);
    setInputValue(formatearValor(valor));
    setHasError(false);
  };

  // Manejar teclas
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  // Manejar pérdida de foco
  const handleBlur = () => {
    // Pequeño delay para permitir clicks en botones
    setTimeout(() => {
      if (isEditing && !isSaving) {
        handleSave();
      }
    }, 100);
  };

  // Determinar el estilo del valor
  const getValueStyle = (val: number) => {
    if (val === 0) return 'text-gray-400 dark:text-gray-500';
    return val < 0 
      ? 'text-red-700 dark:text-red-400' 
      : 'text-green-700 dark:text-green-400';
  };

  if (isEditing) {
    return (
      <div className="relative w-full h-full flex items-center justify-center">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          disabled={isSaving}
          className={`w-full h-5 px-1 text-xs text-center border rounded ${
            hasError 
              ? 'border-red-500 bg-red-50 dark:bg-red-900/20' 
              : 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
          } focus:outline-none focus:ring-1 focus:ring-blue-500`}
          placeholder="0"
        />
        {isSaving && (
          <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center">
            <div className="w-3 h-3 border border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
        {hasError && (
          <div className="absolute z-10 top-full left-0 mt-1 px-2 py-1 bg-red-500 text-white text-xs rounded shadow-lg whitespace-nowrap">
            Error al guardar
          </div>
        )}
      </div>
    );
  }

  return (
    <div 
      className="w-full h-full flex items-center justify-center cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors p-1"
      onClick={handleClick}
      title={disabled ? 'Campo no editable' : 'Click para editar'}
    >
      {valor === 0 ? (
        <span className="text-gray-400 dark:text-gray-500">—</span>
      ) : (
        <span className={getValueStyle(valor)}>
          {valor < 0 ? `(${formatCurrency(Math.abs(valor))})` : formatCurrency(valor)}
        </span>
      )}
    </div>
  );
};
