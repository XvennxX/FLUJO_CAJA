import React, { useState, useEffect, useRef } from 'react';
import { formatCurrency } from '../../utils/formatters';
import { esConceptoAutoCalculado } from '../../utils/conceptos';

interface CeldaEditableProps {
  valor: number;
  conceptoId: number;
  cuentaId: number | null;
  companiaId?: number;
  currency?: string; // Nueva prop para la moneda
  onGuardar: (conceptoId: number, cuentaId: number | null, monto: number, companiaId?: number) => Promise<boolean>;
  disabled?: boolean;
}

export const CeldaEditable: React.FC<CeldaEditableProps> = ({
  valor,
  conceptoId,
  cuentaId,
  companiaId,
  currency,
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
    
    // Verificar que el valor sea un número válido
    if (!isFinite(val) || isNaN(val)) {
      console.warn('Valor no válido en formatearValor:', val);
      return '';
    }
    
    return val.toString();
  };

  // Parsear el valor del input
  const parsearValor = (val: string): number => {
    if (!val || val.trim() === '') return 0;
    
    try {
      // Limpiar el valor de entrada
      let cleanValue = val.trim();
      
      // Manejar el signo negativo
      const isNegative = cleanValue.startsWith('-');
      if (isNegative) {
        cleanValue = cleanValue.substring(1);
      }
      
      // Remover caracteres no numéricos excepto punto y coma para decimales
      cleanValue = cleanValue.replace(/[^\d.,]/g, '');
      
      // Si después de limpiar no queda nada, retornar 0
      if (!cleanValue) {
        return 0;
      }
      
      // Reemplazar coma por punto para el decimal
      cleanValue = cleanValue.replace(',', '.');
      
      // Validar que solo haya un punto decimal
      const dotCount = (cleanValue.match(/\./g) || []).length;
      if (dotCount > 1) {
        console.warn('Formato decimal inválido:', val);
        return 0;
      }
      
      const parsed = parseFloat(cleanValue);
      
      // Verificar que el resultado sea un número válido
      if (isNaN(parsed) || !isFinite(parsed)) {
        console.warn('Valor parseado no válido:', parsed, 'de:', val);
        return 0;
      }
      
      // Aplicar el signo negativo si es necesario
      const result = isNegative ? -Math.abs(parsed) : parsed;
      
      console.log('💱 Parseando valor:', {
        original: val,
        cleaned: cleanValue,
        isNegative,
        parsed,
        result
      });
      
      return result;
    } catch (error) {
      console.error('Error parsing value:', error, 'valor:', val);
      return 0;
    }
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

  // Determinar si el campo está deshabilitado
  const isAutoCalculated = esConceptoAutoCalculado(conceptoId);
  const isDisabled = disabled || isAutoCalculated;

  // Manejar el click para iniciar edición
  const handleClick = () => {
    if (!isDisabled) {
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

    try {
      const nuevoValor = parsearValor(inputValue);
      
      console.log('💾 Intentando guardar:', {
        inputValue: inputValue,
        nuevoValor: nuevoValor,
        valorAnterior: valor,
        conceptoId: conceptoId,
        cuentaId: cuentaId,
        companiaId: companiaId
      });
      
      // Validar que el valor sea un número válido
      if (!isFinite(nuevoValor)) {
        console.error('❌ Valor no válido para guardar:', nuevoValor);
        setHasError(true);
        return;
      }
      
      // Si el valor no cambió, cancelar edición
      if (nuevoValor === valor) {
        console.log('✅ Valor sin cambios, cancelando edición');
        setIsEditing(false);
        return;
      }

      setIsSaving(true);
      console.log('🚀 Llamando onGuardar con valor:', nuevoValor);
      
      const success = await onGuardar(conceptoId, cuentaId, nuevoValor, companiaId);
      
      console.log('📝 Resultado de onGuardar:', success);
      
      if (success) {
        setIsEditing(false);
        setHasError(false);
        console.log('✅ Guardado exitoso');
      } else {
        setHasError(true);
        console.error('❌ onGuardar retornó false');
        // Mantener el modo de edición para permitir correcciones
      }
    } catch (error) {
      console.error('❌ Error en handleSave:', error);
      setHasError(true);
      // Mantener el modo de edición para permitir correcciones
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
    try {
      // Validar que el valor sea un número válido
      if (!isFinite(val) || isNaN(val)) {
        return 'text-red-500';
      }
      
      if (val === 0) return 'text-gray-400 dark:text-gray-500';
      return val < 0 
        ? 'text-red-700 dark:text-red-400' 
        : 'text-green-700 dark:text-green-400';
    } catch (error) {
      console.error('Error en getValueStyle:', error);
      return 'text-red-500';
    }
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
            Error al guardar. Verifique el valor e intente nuevamente.
          </div>
        )}
      </div>
    );
  }

  return (
    <div 
      className={`w-full h-full flex items-center justify-center transition-colors p-1 ${
        isDisabled 
          ? 'cursor-not-allowed bg-gray-100 dark:bg-gray-700/50 opacity-75'
          : 'cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20'
      }`}
      onClick={handleClick}
    >
      {(() => {
        try {
          // Validar que el valor sea un número válido
          if (!isFinite(valor) || isNaN(valor)) {
            return <span className="text-red-500 text-xs">Invalid</span>;
          }
          
          if (valor === 0) {
            return <span className="text-gray-400 dark:text-gray-500">—</span>;
          }
          
          return (
            <span className={`${getValueStyle(valor)} ${isDisabled ? 'text-gray-600 dark:text-gray-400' : ''}`}>
              {valor < 0 ? `(${formatCurrency(Math.abs(valor), currency)})` : formatCurrency(valor, currency)}
            </span>
          );
        } catch (error) {
          console.error('Error renderizando valor en CeldaEditable:', error);
          return <span className="text-red-500 text-xs">Error</span>;
        }
      })()}
    </div>
  );
};
