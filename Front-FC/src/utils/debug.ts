// Debug helper para identificar errores en valores negativos
export const debugValue = (value: any, context: string) => {
  console.log(`🔍 Debug [${context}]:`, {
    value,
    type: typeof value,
    isNumber: typeof value === 'number',
    isFinite: isFinite(value),
    isNaN: isNaN(value),
    toString: value?.toString?.(),
  });
  
  return value;
};

export const safeFormatCurrency = (amount: number, context: string = 'unknown'): string => {
  try {
    console.log(`💰 Formateando [${context}]:`, amount);
    
    if (!isFinite(amount) || isNaN(amount)) {
      console.warn(`⚠️ Valor inválido en ${context}:`, amount);
      return '$0';
    }
    
    const result = new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
    
    console.log(`✅ Resultado [${context}]:`, result);
    return result;
  } catch (error) {
    console.error(`❌ Error formateando [${context}]:`, error, 'valor:', amount);
    return '$0';
  }
};

export const validateAndLogProps = (props: any, componentName: string) => {
  console.log(`🔧 Props de ${componentName}:`, props);
  
  Object.keys(props).forEach(key => {
    const value = props[key];
    console.log(`  - ${key}:`, {
      value,
      type: typeof value,
      isValid: typeof value === 'number' ? isFinite(value) && !isNaN(value) : true
    });
  });
};
