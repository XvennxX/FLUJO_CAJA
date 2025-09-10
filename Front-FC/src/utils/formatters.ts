export const formatCurrency = (amount: number): string => {
  // Validar que el amount sea un número válido
  if (!isFinite(amount) || isNaN(amount)) {
    console.warn('Valor inválido pasado a formatCurrency:', amount);
    return '$0';
  }
  
  try {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  } catch (error) {
    console.error('Error formateando moneda:', error, 'valor:', amount);
    return '$0';
  }
};

export const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const getRelativeDate = (date: string): string => {
  const today = new Date();
  const transactionDate = new Date(date);
  const diffTime = today.getTime() - transactionDate.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Hoy';
  if (diffDays === 1) return 'Ayer';
  if (diffDays < 7) return `Hace ${diffDays} días`;
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semana${Math.floor(diffDays / 7) > 1 ? 's' : ''}`;
  return formatDate(date);
};