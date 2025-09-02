/**
 * Utilidades para manejo de fechas
 */

/**
 * Formatea una fecha en formato YYYY-MM-DD a DD/MM/YYYY sin problemas de zona horaria
 */
export const formatDateString = (dateString: string): string => {
  if (!dateString) return '';
  
  // Separar la fecha en componentes
  const [year, month, day] = dateString.split('-');
  
  // Retornar en formato DD/MM/YYYY
  return `${day}/${month}/${year}`;
};

/**
 * Formatea una fecha en formato YYYY-MM-DD a formato local sin conversión de zona horaria
 */
export const formatDateStringLocale = (dateString: string, locale: string = 'es-CO'): string => {
  if (!dateString) return '';
  
  // Crear una fecha agregando 'T12:00:00' para evitar problemas de zona horaria
  const dateWithTime = `${dateString}T12:00:00`;
  const date = new Date(dateWithTime);
  
  return date.toLocaleDateString(locale);
};

/**
 * Convierte una fecha YYYY-MM-DD a objeto Date sin problemas de zona horaria
 */
export const parseDateString = (dateString: string): Date => {
  if (!dateString) return new Date();
  
  const [year, month, day] = dateString.split('-').map(Number);
  return new Date(year, month - 1, day); // month - 1 porque los meses van de 0-11
};
