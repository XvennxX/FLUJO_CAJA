import React, { useState, useEffect } from 'react';
import { Building2, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency } from '../../utils/formatters';
import { useConceptosFlujoCaja, ConceptoFlujoCaja } from '../../hooks/useConceptosFlujoCaja';
import { useTransaccionesFlujoCaja, TransaccionFlujoCaja } from '../../hooks/useTransaccionesFlujoCaja';
import { CeldaEditable } from '../UI/CeldaEditable';

interface Concepto {
  categoria: string;
  codigo: string;
  nombre: string;
  tipo: string;
  id?: number; // ID del concepto para vincular con transacciones
}

interface BankAccount {
  id: number;
  numero_cuenta: string;
  banco: {
    id: number;
    nombre: string;
  };
  monedas: string[];
  tipo_cuenta: string;
  compania: {
    id: number;
    nombre: string;
  };
}

const DashboardTesoreria: React.FC = () => {
  const { user } = useAuth();
  // Obtener la fecha actual en formato YYYY-MM-DD
  const getCurrentDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  // Obtener la fecha del día anterior
  const getPreviousDate = (fecha: string) => {
    const date = new Date(fecha);
    date.setDate(date.getDate() - 1);
    return date.toISOString().split('T')[0];
  };
  
  const [selectedDate, setSelectedDate] = useState<string>(getCurrentDate());
  
  // Estado para almacenar transacciones del día anterior
  const [transaccionesDiaAnterior, setTransaccionesDiaAnterior] = useState<TransaccionFlujoCaja[]>([]);
  const [loadingDiaAnterior, setLoadingDiaAnterior] = useState(false);
  
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Hook para obtener conceptos desde el backend
  const { conceptosTesoreria, loading: conceptosLoading, error: conceptosError } = useConceptosFlujoCaja();
  
  // Hook para manejar transacciones
  const { 
    transacciones, 
    loading: transaccionesLoading, 
    error: transaccionesError,
    guardarTransaccion,
    obtenerMonto,
    setError: setTransaccionesError
  } = useTransaccionesFlujoCaja(selectedDate, 'tesoreria');
  
  // Cargar todas las cuentas bancarias al inicializar el componente
  useEffect(() => {
    const loadAllBankAccounts = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/v1/bank-accounts/all', {
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` })
          }
        });
        
        if (response.ok) {
          const accounts = await response.json();
          setBankAccounts(accounts);
        } else {
          console.error('Error loading bank accounts');
        }
      } catch (error) {
        console.error('Error loading bank accounts:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAllBankAccounts();
  }, []);

  // Función para cargar transacciones del día anterior
  const cargarTransaccionesDiaAnterior = async (fecha: string) => {
    try {
      setLoadingDiaAnterior(true);
      const fechaAnterior = getPreviousDate(fecha);
      
      const token = localStorage.getItem('access_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      };

      const response = await fetch(
        `http://localhost:8000/api/v1/api/transacciones-flujo-caja/fecha/${fechaAnterior}?area=tesoreria`,
        { headers }
      );

      if (response.ok) {
        const data = await response.json();
        setTransaccionesDiaAnterior(data);
      } else {
        setTransaccionesDiaAnterior([]);
      }
    } catch (error) {
      console.error('Error cargando transacciones del día anterior:', error);
      setTransaccionesDiaAnterior([]);
    } finally {
      setLoadingDiaAnterior(false);
    }
  };

  // Cargar transacciones del día anterior cuando cambie la fecha
  useEffect(() => {
    cargarTransaccionesDiaAnterior(selectedDate);
  }, [selectedDate]);

  // Función para convertir conceptos del backend al formato del frontend
  const convertirConceptosParaTabla = (conceptosBackend: ConceptoFlujoCaja[]): Concepto[] => {
    return conceptosBackend.map(concepto => ({
      categoria: concepto.categoria || determinarCategoria(concepto.nombre),
      codigo: concepto.tipo_movimiento === 'ingreso' ? 'I' : 
              concepto.tipo_movimiento === 'egreso' ? 'E' : '',
      nombre: concepto.nombre,
      tipo: concepto.tipo_movimiento,
      id: concepto.id // Incluir ID para vincular con transacciones
    }));
  };

  // Función para determinar categoría basada en el nombre del concepto
  const determinarCategoria = (nombre: string): string => {
    const nombreUpper = nombre.toUpperCase();
    
    if (nombreUpper.includes('SALDO') || nombreUpper.includes('PAGADUR') || nombreUpper.includes('CONSUMO') || nombreUpper.includes('VENTANILLA')) {
      return 'PAGADURIA';
    } else if (nombreUpper.includes('TITULO') || nombreUpper.includes('INTERES') || nombreUpper.includes('REDENC') || 
               nombreUpper.includes('SIMULTANE') || nombreUpper.includes('FCP') || nombreUpper.includes('ENCARGO') ||
               nombreUpper.includes('APERTURA') || nombreUpper.includes('CANCEL') || nombreUpper.includes('COMPRA TÍTULOS') ||
               nombreUpper.includes('VENTA TÍTULOS')) {
      return 'RENTA FIJA';
    } else if (nombreUpper.includes('ACCION') || nombreUpper.includes('DIVIDEND') || nombreUpper.includes('ETF')) {
      return 'RENTA VARIABLE';
    } else if (nombreUpper.includes('SWAP') || nombreUpper.includes('OPCION') || nombreUpper.includes('FORWARD')) {
      return 'DERIVADOS';
    } else if (nombreUpper.includes('DIVISA') || nombreUpper.includes('COMPENSAC')) {
      return 'DIVISAS';
    } else {
      return 'OTROS';
    }
  };

  // Obtener conceptos: del backend si están disponibles, sino usar los hardcodeados como fallback
  const conceptos: Concepto[] = conceptosLoading || conceptosError ? 
    // Fallback a conceptos hardcodeados si hay error o están cargando
    [
      { categoria: 'PAGADURIA', codigo: '', nombre: 'SALDO INICIAL', tipo: 'neutral' },
      { categoria: 'PAGADURIA', codigo: '', nombre: 'CONSUMO', tipo: 'neutral' },
      { categoria: 'PAGADURIA', codigo: '', nombre: 'VENTANILLA', tipo: 'neutral' },
      { categoria: 'PAGADURIA', codigo: '', nombre: 'SALDO NETO INICIAL PAGADURÍA', tipo: 'neutral' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'PAGOS INTERCOMPAÑÍAS', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'PAGOS INTERCOMPAÑÍAS', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'INGRESOS INTERESES', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'INGRESO REDENCIÓN TÍTULOS', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'APERTURA ACTIVO FINANCIERO', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'CANCELACIÓN ACTIVO FINANCIERO', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'INTERESES ACTIVO FINANCIERO', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'CANCELACIÓN KW', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'PAGO INTERESES KW', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'APERTURA KW', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'COMPRA TÍTULOS', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'COMPRA SIMULTÁNEA ACTIVA', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'REDENCIÓN SIMULTÁNEA PASIVA', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'VENTA TÍTULOS', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'COMPRA SIMULTÁNEA PASIVA', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'REDENCIÓN SIMULTÁNEA ACTIVA', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'DISTRIBUCIÓN FCP', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'LLAMADO CAPITAL FCP', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: 'I', nombre: 'RETIRO DE CAPITAL ENCARGOS', tipo: 'ingreso' },
      { categoria: 'RENTA FIJA', codigo: 'E', nombre: 'INCREMENTO DE CAPITAL ENCARGOS', tipo: 'egreso' },
      { categoria: 'RENTA FIJA', codigo: '', nombre: 'TRASLADO ARL', tipo: 'neutral' },
      { categoria: 'RENTA VARIABLE', codigo: 'E', nombre: 'COMPRA ACCIONES', tipo: 'egreso' },
      { categoria: 'RENTA VARIABLE', codigo: 'I', nombre: 'VENTA ACCIONES', tipo: 'ingreso' },
      { categoria: 'RENTA VARIABLE', codigo: 'I', nombre: 'INGRESO DIVIDENDOS', tipo: 'ingreso' },
      { categoria: 'RENTA VARIABLE', codigo: 'E', nombre: 'EGRESO DIVIDENDOS', tipo: 'egreso' },
      { categoria: 'RENTA VARIABLE', codigo: 'I', nombre: 'INGRESO DIVIDENDOS ETF', tipo: 'ingreso' },
      { categoria: 'DERIVADOS', codigo: 'E', nombre: 'SWAP', tipo: 'egreso' },
      { categoria: 'DERIVADOS', codigo: 'E', nombre: 'OPCIONES', tipo: 'egreso' },
      { categoria: 'DERIVADOS', codigo: 'I', nombre: 'OPCIONES', tipo: 'ingreso' },
      { categoria: 'DERIVADOS', codigo: 'E', nombre: 'FORWARD', tipo: 'egreso' },
      { categoria: 'DERIVADOS', codigo: 'I', nombre: 'FORWARD', tipo: 'ingreso' },
      { categoria: 'DIVISAS', codigo: 'E', nombre: 'COMPRA DIVISAS OTRAS ÁREAS', tipo: 'egreso' },
      { categoria: 'DIVISAS', codigo: 'I', nombre: 'VENTA DIVISAS OTRAS ÁREAS', tipo: 'ingreso' },
      { categoria: 'DIVISAS', codigo: 'E', nombre: 'COMPRA DIVISAS REASEGUROS', tipo: 'egreso' },
      { categoria: 'DIVISAS', codigo: 'E', nombre: 'COMPRA DIVISAS COMPENSACIÓN', tipo: 'egreso' },
      { categoria: 'DIVISAS', codigo: 'I', nombre: 'VENTAS DIVISAS COMPENSACIÓN', tipo: 'ingreso' },
      { categoria: 'OTROS', codigo: 'I', nombre: 'GARANTÍA SIMULTÁNEA', tipo: 'ingreso' },
      { categoria: 'OTROS', codigo: 'E', nombre: 'GARANTÍA SIMULTÁNEA', tipo: 'egreso' },
      { categoria: 'OTROS', codigo: '', nombre: 'EMBARGOS', tipo: 'neutral' },
      { categoria: 'OTROS', codigo: 'I', nombre: 'RECAUDO PRIMAS', tipo: 'ingreso' },
      { categoria: 'OTROS', codigo: '', nombre: 'OTROS', tipo: 'neutral' },
      { categoria: 'OTROS', codigo: 'E', nombre: 'IMPUESTOS', tipo: 'egreso' },
      { categoria: 'OTROS', codigo: 'E', nombre: 'COMISIONES', tipo: 'egreso' },
      { categoria: 'OTROS', codigo: 'I', nombre: 'RENDIMIENTOS', tipo: 'ingreso' },
      { categoria: 'OTROS', codigo: 'E', nombre: 'GMF', tipo: 'egreso' }
    ] :
    // Usar conceptos del backend
    convertirConceptosParaTabla(conceptosTesoreria);

  const getRowColor = (categoria: string, tipo: string, nombre: string) => {
    // Grupo especial para las primeras 4 filas de PAGADURIA
    const saldosIniciales = [
      'SALDO INICIAL',
      'CONSUMO',
      'VENTANILLA',
      'SALDO NETO INICIAL PAGADURÍA'
    ];

    if (categoria === 'PAGADURIA' && saldosIniciales.includes(nombre)) {
      return 'bg-slate-300 dark:bg-slate-800/50'; // Color empresarial para el grupo especial
    }

    // Color base por categoría
    const categoryColors: { [key: string]: string } = {
      'PAGADURIA': 'bg-blue-50 dark:bg-blue-900/20',
      'RENTA FIJA': 'bg-green-50 dark:bg-green-900/20',
      'RENTA VARIABLE': 'bg-yellow-50 dark:bg-yellow-900/20',
      'DERIVADOS': 'bg-purple-50 dark:bg-purple-900/20',
      'DIVISAS': 'bg-orange-50 dark:bg-orange-900/20',
      'OTROS': 'bg-gray-50 dark:bg-gray-900/20'
    };

    // Si es ingreso o egreso, ajustar la intensidad
    if (tipo === 'ingreso') {
      return categoryColors[categoria].replace('/20', '/30');
    } else if (tipo === 'egreso') {
      return categoryColors[categoria].replace('/20', '/10');
    }

    return categoryColors[categoria] || 'bg-white dark:bg-gray-800';
  };

  // Función para calcular el total de una fila usando datos reales y fallback
  const calculateRowTotal = (concepto: Concepto) => {
    let total = 0;
    
    // Manejar casos especiales de conceptos calculados
    if (concepto.nombre === 'SALDO INICIAL') {
      // Para SALDO INICIAL, usar la suma del SALDO FINAL CUENTAS del día anterior para todas las cuentas
      total = calculateSaldoInicialDesdeDiaAnterior();
      return total;
    } else if (concepto.nombre === 'SALDO NETO INICIAL PAGADURÍA') {
      // Para SALDO NETO INICIAL PAGADURÍA, usar el cálculo automático
      total = calculateSaldoNetoPagaduria();
      return total;
    }
    
    // Para conceptos normales, sumar el valor de todas las cuentas bancarias
    if (concepto.id && bankAccounts.length > 0) {
      total = bankAccounts.reduce((sum, account) => {
        const valorCuenta = obtenerMonto(concepto.id!, account.id);
        return sum + (Number(valorCuenta) || 0);
      }, 0);
    } else if (concepto.id) {
      // Fallback: si no hay cuentas cargadas, usar transacciones directamente
      const transaccionesConcepto = transacciones.filter(t => t.concepto_id === concepto.id);
      total = transaccionesConcepto.reduce((sum, t) => sum + (Number(t.monto) || 0), 0);
    }
    
    return isNaN(total) ? 0 : total;
  };

  // Función para calcular el SALDO NETO INICIAL PAGADURÍA (suma de SALDO INICIAL + CONSUMO + VENTANILLA)
  const calculateSaldoNetoPagaduria = (cuentaId?: number) => {
    try {
      // Encontrar los conceptos específicos de pagaduría
      const saldoInicial = conceptos.find(c => c.nombre === 'SALDO INICIAL' && c.categoria === 'PAGADURIA');
      const consumo = conceptos.find(c => c.nombre === 'CONSUMO' && c.categoria === 'PAGADURIA');
      const ventanilla = conceptos.find(c => c.nombre === 'VENTANILLA' && c.categoria === 'PAGADURIA');

      let total = 0;

      // Sumar SALDO INICIAL
      if (saldoInicial?.id) {
        const transaccionesSaldo = transacciones.filter(t => 
          t && t.concepto_id === saldoInicial.id && (cuentaId ? t.cuenta_id === cuentaId : true)
        );
        const montoSaldo = transaccionesSaldo.reduce((sum, t) => sum + (Number(t.monto) || 0), 0);
        total += montoSaldo;
      }

      // Sumar CONSUMO
      if (consumo?.id) {
        const transaccionesConsumo = transacciones.filter(t => 
          t && t.concepto_id === consumo.id && (cuentaId ? t.cuenta_id === cuentaId : true)
        );
        const montoConsumo = transaccionesConsumo.reduce((sum, t) => sum + (Number(t.monto) || 0), 0);
        total += montoConsumo;
      }

      // Sumar VENTANILLA
      if (ventanilla?.id) {
        const transaccionesVentanilla = transacciones.filter(t => 
          t && t.concepto_id === ventanilla.id && (cuentaId ? t.cuenta_id === cuentaId : true)
        );
        const montoVentanilla = transaccionesVentanilla.reduce((sum, t) => sum + (Number(t.monto) || 0), 0);
        total += montoVentanilla;
      }

      return isNaN(total) ? 0 : total;
    } catch (error) {
      console.error('Error calculando saldo neto pagaduría:', error);
      return 0;
    }
  };

  // Función para calcular el subtotal de tesorería (excluyendo los primeros 4 conceptos de PAGADURIA)
  const calculateSubtotalTesoreria = (cuentaId?: number) => {
    try {
      // Filtrar conceptos que NO sean los primeros 4 de PAGADURIA
      const conceptosTesoreria = conceptos.filter(concepto => {
        const categoria = concepto.categoria?.toUpperCase() || '';
        // Excluir los conceptos de PAGADURIA (los primeros 4)
        return categoria !== 'PAGADURIA';
      });

      let subtotal = 0;
      conceptosTesoreria.forEach(concepto => {
        if (concepto.id && transacciones && Array.isArray(transacciones)) {
          if (cuentaId) {
            // Calcular para una cuenta específica
            const transaccionesCuenta = transacciones.filter(t => 
              t && t.concepto_id === concepto.id && t.cuenta_id === cuentaId
            );
            const montoCuenta = transaccionesCuenta.reduce((sum, t) => {
              const monto = Number(t.monto) || 0;
              return sum + monto;
            }, 0);
            subtotal += montoCuenta;
          } else {
            // Calcular total general (todas las cuentas)
            const transaccionesConcepto = transacciones.filter(t => 
              t && t.concepto_id === concepto.id
            );
            const montoTotal = transaccionesConcepto.reduce((sum, t) => {
              const monto = Number(t.monto) || 0;
              return sum + monto;
            }, 0);
            subtotal += montoTotal;
          }
        }
      });

      return isNaN(subtotal) ? 0 : subtotal;
    } catch (error) {
      console.error('Error calculando subtotal tesorería:', error);
      return 0;
    }
  };

  // Función para calcular el SALDO FINAL CUENTAS (suma de SALDO NETO INICIAL PAGADURÍA + SUB-TOTAL TESORERÍA)
  const calculateSaldoFinalCuentas = (cuentaId?: number) => {
    try {
      // Obtener el SALDO NETO INICIAL PAGADURÍA
      const saldoNetoPagaduria = calculateSaldoNetoPagaduria(cuentaId);
      
      // Obtener el SUB-TOTAL TESORERÍA
      const subtotalTesoreria = calculateSubtotalTesoreria(cuentaId);
      
      // Sumar ambos valores
      const saldoFinal = saldoNetoPagaduria + subtotalTesoreria;
      
      return isNaN(saldoFinal) ? 0 : saldoFinal;
    } catch (error) {
      console.error('Error calculando saldo final cuentas:', error);
      return 0;
    }
  };

  // Función para calcular el SALDO FINAL CUENTAS del día anterior (para usar como SALDO INICIAL del día actual)
  const calculateSaldoInicialDesdeDiaAnterior = (cuentaId?: number) => {
    try {
      if (!transaccionesDiaAnterior || transaccionesDiaAnterior.length === 0) {
        return 0;
      }

      // Calcular SALDO NETO INICIAL PAGADURÍA del día anterior
      const saldoInicial = conceptos.find(c => c.nombre === 'SALDO INICIAL' && c.categoria === 'PAGADURIA');
      const consumo = conceptos.find(c => c.nombre === 'CONSUMO' && c.categoria === 'PAGADURIA');
      const ventanilla = conceptos.find(c => c.nombre === 'VENTANILLA' && c.categoria === 'PAGADURIA');

      let saldoNetoPagaduria = 0;

      // Sumar conceptos de pagaduría del día anterior
      [saldoInicial, consumo, ventanilla].forEach(concepto => {
        if (concepto?.id) {
          const transaccionesConcepto = transaccionesDiaAnterior.filter(t => 
            t && t.concepto_id === concepto.id && (cuentaId ? t.cuenta_id === cuentaId : true)
          );
          const monto = transaccionesConcepto.reduce((sum, t) => sum + (Number(t.monto) || 0), 0);
          saldoNetoPagaduria += monto;
        }
      });

      // Calcular SUB-TOTAL TESORERÍA del día anterior
      const conceptosTesoreria = conceptos.filter(concepto => {
        const categoria = concepto.categoria?.toUpperCase() || '';
        return categoria !== 'PAGADURIA';
      });

      let subtotalTesoreria = 0;
      conceptosTesoreria.forEach(concepto => {
        if (concepto.id) {
          const transaccionesConcepto = transaccionesDiaAnterior.filter(t => 
            t && t.concepto_id === concepto.id && (cuentaId ? t.cuenta_id === cuentaId : true)
          );
          const monto = transaccionesConcepto.reduce((sum, t) => sum + (Number(t.monto) || 0), 0);
          subtotalTesoreria += monto;
        }
      });

      // El SALDO FINAL del día anterior = SALDO NETO PAGADURÍA + SUB-TOTAL TESORERÍA
      const saldoFinalDiaAnterior = saldoNetoPagaduria + subtotalTesoreria;

      return isNaN(saldoFinalDiaAnterior) ? 0 : saldoFinalDiaAnterior;
    } catch (error) {
      console.error('Error calculando saldo inicial desde día anterior:', error);
      return 0;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-bolivar-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando cuentas bancarias...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center space-x-3">
          <Building2 className="h-8 w-8 text-bolivar-600" />
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Panel de Tesoreria</h1>
              {/* Indicador de estado de conceptos */}
              {conceptosLoading ? (
                <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                  Cargando conceptos...
                </span>
              ) : conceptosError ? (
                <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                  Usando fallback
                </span>
              ) : (
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  Conectado a BD ({conceptosTesoreria.length})
                </span>
              )}
            </div>
            <p className="text-gray-600 dark:text-gray-400">Flujo de caja por compañías - {user?.name}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Selector de fecha específica para transacciones */}
          <div className="flex flex-col">
            <label className="text-xs text-gray-600 dark:text-gray-400 mb-1">Fecha específica:</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-bolivar-500 focus:border-transparent"
            />
          </div>

          {/* Indicadores de estado */}
          <div className="flex flex-col space-y-1">
            {/* Estado de transacciones */}
            {transaccionesLoading && (
              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full flex items-center">
                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                Cargando datos...
              </span>
            )}
            {transaccionesError && (
              <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full flex items-center">
                <AlertCircle className="w-3 h-3 mr-1" />
                Error: {transaccionesError}
              </span>
            )}
            {!transaccionesLoading && !transaccionesError && (
              <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                {transacciones.length} transacciones
              </span>
            )}
            
            {/* Botón para limpiar errores */}
            {transaccionesError && (
              <button
                onClick={() => setTransaccionesError(null)}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
              >
                Limpiar error
              </button>
            )}
          </div>
          
          <button className="flex items-center space-x-2 px-3 py-2 bg-bolivar-600 text-white rounded-lg hover:bg-bolivar-700 transition-colors text-sm">
            <RefreshCw className="h-4 w-4" />
            <span>Actualizar</span>
          </button>
          <button className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm">
            <Download className="h-4 w-4" />
            <span>Exportar</span>
          </button>
        </div>
      </div>

      {/* Tabla estilo Excel - SIN fechas, solo compañías y cuentas */}
      <div className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-xs">
            <thead>
              {/* FILA 1 - SOLO COMPAÑÍAS */}
              <tr>
                <th colSpan={3} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[100px]"></th>
                {/* Compañías reales desde la base de datos */}
                {bankAccounts.map((account) => (
                  <th key={`company-${account.id}`} className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                    {account.compania?.nombre || 'COMPAÑÍA DESCONOCIDA'}
                  </th>
                ))}
                {/* Columna TOTALES */}
                <th className="bg-green-200 dark:bg-green-800 border-2 border-green-400 dark:border-green-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  TOTALES
                </th>
              </tr>

              {/* FILA 2 - BANCOS */}
              <tr>
                <th colSpan={3} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[100px]"></th>
                {/* Bancos reales desde la base de datos */}
                {bankAccounts.map((account) => (
                  <th key={`bank-${account.id}`} className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                    {account.banco?.nombre || 'BANCO DESCONOCIDO'}
                  </th>
                ))}
                {/* Columna TOTALES */}
                <th className="bg-green-100 dark:bg-green-900/50 border-2 border-green-400 dark:border-green-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  TOTALES
                </th>
              </tr>

              {/* FILA 3 - TIPO OP, OP, CONCEPTO y NÚMEROS DE CUENTA */}
              <tr>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20 min-w-[100px]">
                  TIPO OP
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[100px] z-20 min-w-[60px]">
                  OP
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[160px] z-20 min-w-[200px]">
                  CONCEPTO
                </th>
                {/* Cuentas bancarias reales desde la base de datos */}
                {bankAccounts.map((account) => (
                  <th key={account.id} className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                    {account.numero_cuenta}
                  </th>
                ))}
                {/* Columna TOTALES */}
                <th className="bg-green-50 dark:bg-green-900 border-2 border-green-400 dark:border-green-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-bold text-center text-xs">
                  TOTALES
                </th>
              </tr>
            </thead>

            {/* BODY - CONCEPTOS Y DATOS */}
            <tbody>
              {conceptos.map((concepto, conceptoIdx) => (
                <tr key={conceptoIdx} className={getRowColor(concepto.categoria, concepto.tipo, concepto.nombre)}>
                  {/* COLUMNA DE TIPO OP */}
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium sticky left-0 z-10 ${getRowColor(concepto.categoria, concepto.tipo, concepto.nombre)}`}>
                    <span className="text-xs leading-tight">{concepto.categoria}</span>
                  </td>

                  {/* COLUMNA DE CÓDIGO */}
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-center sticky left-[100px] z-10 ${getRowColor(concepto.categoria, concepto.tipo, concepto.nombre)}`}>
                    {concepto.codigo && (
                      <span className={`w-5 h-5 rounded text-xs flex items-center justify-center font-bold mx-auto ${
                        concepto.codigo === 'E' 
                          ? 'bg-red-500 text-white' 
                          : concepto.codigo === 'I' 
                          ? 'bg-green-500 text-white' 
                          : 'bg-gray-500 text-white'
                      }`}>
                        {concepto.codigo}
                      </span>
                    )}
                  </td>

                  {/* COLUMNA DE CUENTA/CONCEPTO */}
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium text-center sticky left-[160px] z-20 min-w-[100px]" ${getRowColor(concepto.categoria, concepto.tipo, concepto.nombre)}`}>
                    <span className="text-xs leading-tight">{concepto.nombre}</span>
                  </td>

                  {/* CELDAS DE DATOS - Solo cuentas bancarias reales */}
                  {/* Columnas de cuentas bancarias reales */}
                  {bankAccounts.map((account) => {
                    // Verificar si es el concepto "SALDO NETO INICIAL PAGADURÍA"
                    const esSaldoNetoPagaduria = concepto.nombre === 'SALDO NETO INICIAL PAGADURÍA';
                    // Verificar si es el concepto "SALDO INICIAL"
                    const esSaldoInicial = concepto.nombre === 'SALDO INICIAL';
                    
                    if (esSaldoNetoPagaduria) {
                      // Para SALDO NETO INICIAL PAGADURÍA, mostrar valor calculado (no editable)
                      const valorCalculado = calculateSaldoNetoPagaduria(account.id);
                      
                      return (
                        <td key={`data-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs bg-yellow-50 dark:bg-yellow-900/20">
                          {valorCalculado !== 0 ? (
                            <span className={`font-bold ${valorCalculado < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                              {valorCalculado < 0 ? `(${formatCurrency(Math.abs(valorCalculado))})` : formatCurrency(valorCalculado)}
                            </span>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500">—</span>
                          )}
                        </td>
                      );
                    } else if (esSaldoInicial) {
                      // Para SALDO INICIAL, mostrar valor del SALDO FINAL CUENTAS del día anterior (no editable)
                      const valorSaldoInicialDiaAnterior = calculateSaldoInicialDesdeDiaAnterior(account.id);
                      
                      return (
                        <td key={`data-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs bg-purple-50 dark:bg-purple-900/20">
                          {valorSaldoInicialDiaAnterior !== 0 ? (
                            <span className={`font-bold ${valorSaldoInicialDiaAnterior < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                              {valorSaldoInicialDiaAnterior < 0 ? `(${formatCurrency(Math.abs(valorSaldoInicialDiaAnterior))})` : formatCurrency(valorSaldoInicialDiaAnterior)}
                            </span>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500">—</span>
                          )}
                        </td>
                      );
                    } else {
                      // Para otros conceptos, usar celda editable normal
                      const valorCuenta = concepto.id ? obtenerMonto(concepto.id, account.id) : 0;
                      
                      return (
                        <td key={`data-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs">
                          <CeldaEditable
                            valor={valorCuenta}
                            conceptoId={concepto.id || 0}
                            cuentaId={account.id}
                            companiaId={account.compania.id}
                            onGuardar={guardarTransaccion}
                            disabled={!concepto.id || transaccionesLoading}
                          />
                        </td>
                      );
                    }
                  })}
                  
                  {/* Columna TOTALES */}
                  <td className="border-2 border-green-400 dark:border-green-500 px-2 py-1 text-center text-xs bg-green-50 dark:bg-green-900/20">
                    {(() => {
                      const total = calculateRowTotal(concepto);
                      return total !== 0 ? (
                        <span className={`font-bold ${total < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                          {total < 0 ? `(${formatCurrency(Math.abs(total))})` : formatCurrency(total)}
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500">—</span>
                      );
                    })()}
                  </td>
                </tr>
              ))}

              {/* SEPARADOR */}
              <tr>
                <td colSpan={4 + bankAccounts.length} 
                    className="bg-gray-300 dark:bg-gray-600 h-2 border border-gray-400 dark:border-gray-500"></td>
              </tr>

              {/* FILA SUBTOTAL TESORERÍA */}
              <tr className="bg-blue-200 dark:bg-blue-800/40 font-bold">
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-0 z-20 min-w-[100px]"></td>
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-[100px] z-20 min-w-[60px]"></td>
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[160px] z-20 min-w-[60px]">
                  SUB-TOTAL TESORERÍA
                </td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => {
                  const subtotalCuenta = calculateSubtotalTesoreria(account.id);
                  const subtotalValido = !isNaN(subtotalCuenta) && isFinite(subtotalCuenta) ? subtotalCuenta : 0;
                  
                  return (
                    <td key={`subtotal-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">
                      {subtotalValido !== 0 ? (
                        <span className={subtotalValido < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}>
                          {subtotalValido < 0 ? `(${formatCurrency(Math.abs(subtotalValido))})` : formatCurrency(subtotalValido)}
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500">—</span>
                      )}
                    </td>
                  );
                })}
                {/* Columna TOTALES */}
                <td className="border-2 border-green-400 dark:border-green-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white bg-green-100 dark:bg-green-900/30">
                  {(() => {
                    const totalSubtotal = calculateSubtotalTesoreria();
                    const totalValido = !isNaN(totalSubtotal) && isFinite(totalSubtotal) ? totalSubtotal : 0;
                    
                    return totalValido !== 0 ? (
                      <span className={totalValido < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}>
                        {totalValido < 0 ? `(${formatCurrency(Math.abs(totalValido))})` : formatCurrency(totalValido)}
                      </span>
                    ) : (
                      <span className="text-gray-400 dark:text-gray-500">—</span>
                    );
                  })()}
                </td>
              </tr>

              {/* FILA SALDO FINAL CUENTAS */}
              <tr className="bg-gray-200 dark:bg-gray-700">
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-0 z-20 min-w-[100px]"></td>
                 <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-[100px] z-20 min-w-[60px]"></td>
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[160px] z-20 min-w-[200px]">
                  SALDO FINAL CUENTAS
                </td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => {
                  const valorSaldoFinal = calculateSaldoFinalCuentas(account.id);
                  
                  return (
                    <td key={`saldo-final-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs bg-blue-50 dark:bg-blue-900/20">
                      {valorSaldoFinal !== 0 ? (
                        <span className={`font-bold ${valorSaldoFinal < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                          {valorSaldoFinal < 0 ? `(${formatCurrency(Math.abs(valorSaldoFinal))})` : formatCurrency(valorSaldoFinal)}
                        </span>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500">—</span>
                      )}
                    </td>
                  );
                })}
                {/* Columna TOTALES */}
                <td className="border-2 border-green-400 dark:border-green-500 px-1 py-2 text-center text-xs bg-green-50 dark:bg-green-900/20">
                  {(() => {
                    const totalSaldoFinal = calculateSaldoFinalCuentas();
                    return totalSaldoFinal !== 0 ? (
                      <span className={`font-bold ${totalSaldoFinal < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                        {totalSaldoFinal < 0 ? `(${formatCurrency(Math.abs(totalSaldoFinal))})` : formatCurrency(totalSaldoFinal)}
                      </span>
                    ) : (
                      <span className="text-gray-400 dark:text-gray-500">—</span>
                    );
                  })()}
                </td>
              </tr>

             
            </tbody>
          </table>
        </div>
      </div>

      {/* Resumen por compañía - igual estructura para las 3 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        {/* CAPITALIZADORA */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-400 dark:border-blue-500 rounded p-4">
          <div className="text-center">
            <div className="text-lg font-bold text-blue-800 dark:text-blue-200 mb-3">CAPITALIZADORA</div>
            <div className="space-y-2">
              {/* Mov pagaduría + Mov tesorería */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Mov pagaduría + Mov tesorería</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">10.316,70</div>
              </div>
              {/* Total centralizadora */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Total centralizadora</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">$ 10.316,70</div>
              </div>
              {/* Diferencia */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Diferencia</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">0,00</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* BOLÍVAR */}
        <div className="bg-green-50 dark:bg-green-900/20 border-2 border-green-400 dark:border-green-500 rounded p-4">
          <div className="text-center">
            <div className="text-lg font-bold text-green-800 dark:text-green-200 mb-3">BOLÍVAR</div>
            <div className="space-y-2">
              {/* Mov pagaduría + Mov tesorería */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Mov pagaduría + Mov tesorería</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">15.403.909,46</div>
              </div>
              {/* Total centralizadora */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Total centralizadora</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">$ 15.403.909,46</div>
              </div>
              {/* Diferencia */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Diferencia</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">0,00</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* COMERCIALES */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-400 dark:border-yellow-500 rounded p-4">
          <div className="text-center">
            <div className="text-lg font-bold text-yellow-800 dark:text-yellow-200 mb-3">COMERCIALES</div>
            <div className="space-y-2">
              {/* Mov pagaduría + Mov tesorería */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Mov pagaduría + Mov tesorería</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">2.068.136,37</div>
              </div>
              {/* Total centralizadora */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Total centralizadora</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">$ 2.068.136,37</div>
              </div>
              {/* Diferencia */}
              <div className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 rounded p-2">
                <div className="text-xs font-medium text-gray-800 dark:text-gray-200">Diferencia</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">0,00</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardTesoreria;
