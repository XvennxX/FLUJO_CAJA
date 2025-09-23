import React, { useState, useEffect } from 'react';
import { Building2, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency } from '../../utils/formatters';
import { useTRM } from '../../hooks/useTRM';
import { useTRMByDate } from '../../hooks/useTRMByDate';
import { useConceptosFlujoCaja, ConceptoFlujoCaja } from '../../hooks/useConceptosFlujoCaja';
import { useTransaccionesFlujoCaja, TransaccionFlujoCaja } from '../../hooks/useTransaccionesFlujoCaja';
import { useDashboardWebSocket } from '../../hooks/useWebSocket';
import { CeldaEditable } from '../UI/CeldaEditable';
import { ErrorBoundary } from '../UI/ErrorBoundary';
import { SaldoInicialService } from '../../services/saldoInicialService';
import DatePicker from '../Calendar/DatePicker';
import DiasHabilesTest from '../DiasHabilesTest';
import { isConceptoAutoCalculado } from '../../utils/conceptos';

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
  
  // Estado para forzar re-render cuando cambien las transacciones
  const [forceUpdate, setForceUpdate] = useState(0);
  
  // Estado para multi-moneda
  const [usarMultiMoneda, setUsarMultiMoneda] = useState<boolean>(false);
  
  // Hook para obtener TRM de la fecha seleccionada
  const { trm, loading: trmLoading, error: trmError, refetch: refetchTRM } = useTRMByDate(selectedDate);
  
  // Hook para obtener conceptos desde el backend
  const { conceptosTesoreria, loading: conceptosLoading, error: conceptosError } = useConceptosFlujoCaja();
  
  // Hook para manejar transacciones
  const { 
    transacciones, 
    loading: transaccionesLoading, 
    error: transaccionesError,
    guardarTransaccion,
    obtenerMonto,
    cargarTransacciones,
    setError: setTransaccionesError
  } = useTransaccionesFlujoCaja(selectedDate, 'tesoreria');
  
  // 🔄 WebSocket para actualizaciones en tiempo real
  const { 
    isConnected: wsConnected, 
    updateCount, 
    lastUpdateTime 
  } = useDashboardWebSocket('tesoreria', () => {
    console.log('🔄 [TESORERÍA] Recargando datos por WebSocket...');
    cargarTransacciones();
  });
  
  // Función para conversión de moneda
  const convertirMoneda = (monto: number, tipoMonedaCuenta: string): number => {
    console.log(`🔄 convertirMoneda called:`, { monto, tipoMonedaCuenta, usarMultiMoneda, trmValue: trm?.valor });
    
    if (!usarMultiMoneda || !trm) {
      console.log(`❌ No conversion: usarMultiMoneda=${usarMultiMoneda}, trm=${!!trm}`);
      return monto;
    }
    
    // Si la cuenta es USD, convertir de COP a USD
    if (tipoMonedaCuenta === 'USD') {
      const convertido = Math.floor((monto / trm.valor) * 100) / 100; // Truncar a 2 decimales (no redondear)
      console.log(`💱 Converting ${monto} COP to ${convertido} USD (TRM: ${trm.valor})`);
      return convertido;
    }
    
    // Si la cuenta es COP, mantener el monto original
    console.log(`✅ Keeping COP value: ${monto}`);
    return monto;
  };

  // Función para obtener monto con conversión de moneda
  const obtenerMontoConConversion = (conceptoId: number, cuentaId: number, tipoMonedaCuenta?: string): number => {
    const montoOriginal = obtenerMonto(conceptoId, cuentaId);
    
    if (!usarMultiMoneda || !tipoMonedaCuenta) {
      return montoOriginal;
    }
    
    return convertirMoneda(montoOriginal, tipoMonedaCuenta);
  };
  
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

  // Función helper para validar y limpiar valores numéricos
  const safeNumericValue = (value: any): number => {
    if (typeof value === 'number' && isFinite(value) && !isNaN(value)) {
      return value;
    }
    console.warn('Valor no válido detectado:', value, 'tipo:', typeof value);
    return 0;
  };

  // Función para aplicar signo correcto basado en el código del concepto
  const aplicarSignoSegunCodigo = (valor: number, codigo: string): number => {
    try {
      // Validar que el valor sea un número válido
      if (!isFinite(valor) || isNaN(valor)) {
        console.warn('Valor no válido en aplicarSignoSegunCodigo:', valor);
        return 0;
      }
      
      // Convertir a número absoluto primero para evitar doble negativos
      const valorAbsoluto = Math.abs(valor);
      
      switch (codigo?.toUpperCase()) {
        case 'E': // Egresos - siempre negativos
          return -valorAbsoluto;
        case 'I': // Ingresos - siempre positivos
          return valorAbsoluto;
        case 'N': // Neutro - siempre positivos
          return valorAbsoluto;
        default: // Sin código o cualquier otro - siempre positivos
          return valorAbsoluto;
      }
    } catch (error) {
      console.error('Error en aplicarSignoSegunCodigo:', error);
      return 0;
    }
  };

  // Función para cargar transacciones del día anterior
  const cargarTransaccionesDiaAnterior = async (fecha: string) => {
    try {
      setLoadingDiaAnterior(true);
      const fechaAnterior = getPreviousDate(fecha);
      
      console.log('📅 Cargando transacciones del día anterior:', {
        fechaActual: fecha,
        fechaAnterior: fechaAnterior
      });
      
      const token = localStorage.getItem('access_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      };

      const url = `http://localhost:8000/api/v1/api/transacciones-flujo-caja/fecha/${fechaAnterior}?area=tesoreria`;
      console.log('🌐 URL de consulta:', url);

      const response = await fetch(url, { headers });

      console.log('📡 Respuesta del servidor:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });

      if (response.ok) {
        const data = await response.json();
        console.log('📊 Transacciones del día anterior cargadas:', {
          cantidad: data.length,
          transacciones: data.map((t: any) => ({
            id: t.id,
            concepto_id: t.concepto_id,
            cuenta_id: t.cuenta_id,
            monto: t.monto,
            fecha: t.fecha
          }))
        });
        setTransaccionesDiaAnterior(data);
      } else {
        console.warn('❌ No se pudieron cargar transacciones del día anterior');
        setTransaccionesDiaAnterior([]);
      }
    } catch (error) {
      console.error('💥 Error cargando transacciones del día anterior:', error);
      setTransaccionesDiaAnterior([]);
    } finally {
      setLoadingDiaAnterior(false);
    }
  };

  // Cargar transacciones del día anterior cuando cambie la fecha
  useEffect(() => {
    cargarTransaccionesDiaAnterior(selectedDate);
  }, [selectedDate]);

  // Forzar actualización cuando cambien las transacciones
  useEffect(() => {
    setForceUpdate(prev => prev + 1);
    console.log('🔄 Transacciones actualizadas, forzando re-render');
  }, [transacciones]);

  // Función para convertir conceptos del backend al formato del frontend
  const convertirConceptosParaTabla = (conceptosBackend: ConceptoFlujoCaja[]): Concepto[] => {
    return conceptosBackend.map(concepto => ({
      categoria: concepto.tipo, // Usar el campo 'tipo' de la BD para la columna "TIPO OP"
      codigo: concepto.codigo || '', // Usar el campo 'codigo' de la BD para la columna "OP"
      nombre: concepto.nombre,
      tipo: concepto.tipo,
      id: concepto.id // Incluir ID para vincular con transacciones
    }));
  };

  // Función para expandir cuentas por moneda manteniendo el orden
  const expandirCuentasPorMoneda = (cuentas: BankAccount[]) => {
    if (!usarMultiMoneda) {
      return cuentas.map(cuenta => ({
        ...cuenta,
        cuenta_moneda_id: `${cuenta.id}_${cuenta.monedas[0] || 'COP'}`,
        moneda_display: cuenta.monedas[0] || 'COP',
        tipo_moneda: cuenta.monedas[0] || 'COP', // Agregar tipo_moneda para compatibilidad
        nombre_con_moneda: `${cuenta.banco.nombre} ${cuenta.numero_cuenta.slice(-4)}`,
        es_expansion: false
      }));
    }

    const cuentasExpandidas: any[] = [];
    
    cuentas.forEach(cuenta => {
      const monedas = cuenta.monedas && cuenta.monedas.length > 0 ? cuenta.monedas : ['COP'];
      
      monedas.forEach((moneda, index) => {
        const cuentaExpandida = {
          ...cuenta,
          cuenta_moneda_id: `${cuenta.id}_${moneda}`,
          moneda_display: moneda,
          tipo_moneda: moneda, // Agregar tipo_moneda para compatibilidad
          nombre_con_moneda: `${cuenta.banco.nombre} ${cuenta.numero_cuenta.slice(-4)} (${moneda})`,
          es_expansion: index > 0 // Marcar si es una expansión de moneda adicional
        };
        console.log(`📊 Cuenta expandida:`, cuentaExpandida);
        cuentasExpandidas.push(cuentaExpandida);
      });
    });

    return cuentasExpandidas;
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
    try {
      let total = 0;
      
      // Manejar casos especiales de conceptos calculados
      if (concepto.nombre === 'SALDO INICIAL') {
        // Primero verificar si hay transacciones reales para SALDO INICIAL
        if (concepto.id && bankAccounts.length > 0) {
          total = bankAccounts.reduce((sum, account) => {
            const valorCuenta = obtenerMontoConSignos(concepto.id!, account.id);
            const valorValido = isFinite(valorCuenta) ? valorCuenta : 0;
            return sum + valorValido;
          }, 0);
          
          // Si hay valores reales, usarlos
          if (total !== 0) {
            return total;
          }
        }
        
        // Fallback: Si no hay transacciones reales, calcular desde día anterior
        total = calculateSaldoInicialDesdeDiaAnterior();
        return isFinite(total) ? total : 0;
      } else if (concepto.nombre === 'SALDO NETO INICIAL PAGADURÍA') {
        // Para SALDO NETO INICIAL PAGADURÍA, calcular sumando todas las cuentas
        
        if (bankAccounts.length > 0) {
          total = bankAccounts.reduce((sum, account) => {
            const saldoNetoCuenta = calculateSaldoNetoPagaduria(account.id);
            return sum + (isFinite(saldoNetoCuenta) ? saldoNetoCuenta : 0);
          }, 0);
        } else {
          // Fallback: si no hay cuentas, usar cálculo general
          total = calculateSaldoNetoPagaduria();
        }
        
        return isFinite(total) ? total : 0;
      }
      
      // Para conceptos normales, sumar el valor de todas las cuentas bancarias
      if (concepto.id && bankAccounts.length > 0) {
        total = bankAccounts.reduce((sum, account) => {
          const valorCuenta = obtenerMontoConSignos(concepto.id!, account.id);
          const valorValido = isFinite(valorCuenta) ? valorCuenta : 0;
          return sum + valorValido;
        }, 0);
      } else if (concepto.id) {
        // Fallback: si no hay cuentas cargadas, usar transacciones directamente
        const transaccionesConcepto = transacciones.filter(t => t.concepto_id === concepto.id);
        total = transaccionesConcepto.reduce((sum, t) => {
          const monto = Number(t.monto) || 0;
          return sum + (isFinite(monto) ? monto : 0);
        }, 0);
      }
      
      return isFinite(total) ? total : 0;
    } catch (error) {
      console.error('Error en calculateRowTotal:', error);
      return 0;
    }
  };

  // Función para calcular el SALDO NETO INICIAL PAGADURÍA (suma de SALDO INICIAL + CONSUMO + VENTANILLA)
  const calculateSaldoNetoPagaduria = (cuentaId?: number) => {
    try {
      // Encontrar los conceptos específicos de pagaduría por nombre exacto
      const consumo = conceptos.find(c => c.nombre === 'CONSUMO');
      const ventanilla = conceptos.find(c => c.nombre === 'VENTANILLA');

      let total = 0;

      // ✅ SALDO INICIAL: Usar el valor calculado desde el día anterior
      const montoSaldoInicial = calculateSaldoInicialDesdeDiaAnterior(cuentaId);
      
      // Validar el monto del saldo inicial
      if (isFinite(montoSaldoInicial)) {
        total += montoSaldoInicial;
      }

      // Sumar CONSUMO desde transacciones con signos aplicados
      if (consumo?.id) {
        if (cuentaId) {
          // Para cuenta específica, usar la función con signos
          const montoConsumo = obtenerMontoConSignos(consumo.id, cuentaId);
          if (isFinite(montoConsumo)) {
            total += montoConsumo;
          }
        } else {
          // Para todas las cuentas
          const transaccionesConsumo = transacciones.filter(t => 
            t && t.concepto_id === consumo.id
          );
          const montoConsumo = transaccionesConsumo.reduce((sum, t) => {
            const monto = Number(t.monto) || 0;
            const montoConSigno = aplicarSignoSegunCodigo(monto, consumo.codigo || '');
            return sum + (isFinite(montoConSigno) ? montoConSigno : 0);
          }, 0);
          total += montoConsumo;
        }
      }

      // Sumar VENTANILLA desde transacciones con signos aplicados
      if (ventanilla?.id) {
        if (cuentaId) {
          // Para cuenta específica, usar la función con signos
          const montoVentanilla = obtenerMontoConSignos(ventanilla.id, cuentaId);
          if (isFinite(montoVentanilla)) {
            total += montoVentanilla;
          }
        } else {
          // Para todas las cuentas
          const transaccionesVentanilla = transacciones.filter(t => 
            t && t.concepto_id === ventanilla.id
          );
          const montoVentanilla = transaccionesVentanilla.reduce((sum, t) => {
            const monto = Number(t.monto) || 0;
            const montoConSigno = aplicarSignoSegunCodigo(monto, ventanilla.codigo || '');
            return sum + (isFinite(montoConSigno) ? montoConSigno : 0);
          }, 0);
          total += montoVentanilla;
        }
      }

      const resultado = isFinite(total) ? total : 0;
      return resultado;
    } catch (error) {
      console.error('Error calculando saldo neto pagaduría:', error);
      return 0;
    }
  };

  // Función para obtener el SUB-TOTAL TESORERÍA desde la base de datos (ID 50)
  const calculateSubtotalTesoreria = (cuentaId?: number) => {
    try {
      // Buscar el concepto SUB-TOTAL TESORERÍA (ID 50)
      const subtotalConcepto = conceptos.find(c => c.nombre === 'SUB-TOTAL TESORERÍA');
      
      if (!subtotalConcepto?.id) {
        console.log('❌ No se encontró el concepto SUB-TOTAL TESORERÍA');
        return 0;
      }

      if (cuentaId) {
        // Para una cuenta específica, obtener el valor desde la BD
        const valorCuenta = obtenerMontoConSignos(subtotalConcepto.id, cuentaId);
        return isFinite(valorCuenta) ? valorCuenta : 0;
      } else {
        // Para todas las cuentas, sumar los valores de cada cuenta
        if (bankAccounts.length > 0) {
          const total = bankAccounts.reduce((sum, account) => {
            const valorCuenta = obtenerMontoConSignos(subtotalConcepto.id!, account.id);
            return sum + (isFinite(valorCuenta) ? valorCuenta : 0);
          }, 0);
          return total;
        } else {
          // Fallback: usar transacciones directamente
          const transaccionesSubtotal = transacciones.filter(t => 
            t && t.concepto_id === subtotalConcepto.id
          );
          const total = transaccionesSubtotal.reduce((sum, t) => {
            const monto = Number(t.monto) || 0;
            return sum + (isFinite(monto) ? monto : 0);
          }, 0);
          return total;
        }
      }
    } catch (error) {
      console.error('Error obteniendo SUB-TOTAL TESORERÍA desde BD:', error);
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
      console.log('🔍 Calculando saldo inicial desde día anterior...', {
        fechaSeleccionada: selectedDate,
        cuentaId: cuentaId || 'todas',
        tieneTransaccionesDiaAnterior: !!transaccionesDiaAnterior,
        cantidadTransacciones: transaccionesDiaAnterior?.length || 0
      });

      // Si no hay transacciones del día anterior, el saldo inicial es 0
      if (!transaccionesDiaAnterior || transaccionesDiaAnterior.length === 0) {
        console.log('❌ No hay transacciones del día anterior, saldo inicial = 0');
        return 0;
      }

      // Buscar el concepto "SALDO FINAL CUENTAS" 
      const saldoFinalCuentasConcepto = conceptos.find(c => c.nombre === 'SALDO FINAL CUENTAS');
      
      console.log('🎯 Buscando concepto SALDO FINAL CUENTAS:', {
        conceptoEncontrado: !!saldoFinalCuentasConcepto,
        conceptoId: saldoFinalCuentasConcepto?.id,
        todosLosConceptos: conceptos.map(c => ({ id: c.id, nombre: c.nombre }))
      });
      
      if (!saldoFinalCuentasConcepto) {
        console.warn('❌ No se encontró el concepto SALDO FINAL CUENTAS');
        return 0;
      }

      // Buscar las transacciones del día anterior para este concepto específico
      const transaccionesSaldoFinal = transaccionesDiaAnterior.filter(t => 
        t && 
        t.concepto_id === saldoFinalCuentasConcepto.id && 
        (cuentaId ? t.cuenta_id === cuentaId : true)
      );

      console.log('📊 Transacciones SALDO FINAL CUENTAS del día anterior:', {
        conceptoId: saldoFinalCuentasConcepto.id,
        transaccionesEncontradas: transaccionesSaldoFinal.length,
        transacciones: transaccionesSaldoFinal.map(t => ({
          id: t.id,
          monto: t.monto,
          cuenta_id: t.cuenta_id,
          fecha: t.fecha
        }))
      });

      // Sumar los montos de SALDO FINAL CUENTAS del día anterior
      const saldoFinalDiaAnterior = transaccionesSaldoFinal.reduce((sum, t) => {
        const monto = Number(t.monto) || 0;
        console.log(`  💰 Sumando transacción ID ${t.id}: ${monto}`);
        return sum + monto;
      }, 0);

      console.log('✅ Saldo inicial calculado desde SALDO FINAL CUENTAS del día anterior:', {
        conceptoId: saldoFinalCuentasConcepto.id,
        cuentaId: cuentaId || 'todas',
        transaccionesEncontradas: transaccionesSaldoFinal.length,
        saldoFinalDiaAnterior
      });

      // Si el resultado es NaN, undefined, null o no es un número válido, devolver 0
      if (isNaN(saldoFinalDiaAnterior) || !isFinite(saldoFinalDiaAnterior)) {
        console.warn('❌ Resultado inválido, devolviendo 0');
        return 0;
      }

      return saldoFinalDiaAnterior;
    } catch (error) {
      console.error('💥 Error calculando saldo inicial desde día anterior, usando 0:', error);
      return 0;
    }
  };

  // Función para guardar automáticamente el SALDO FINAL CUENTAS como transacción
  const guardarSaldoFinalCuentasAutomatico = async (cuentaId: number, saldoFinal: number) => {
    try {
      // Buscar el concepto SALDO FINAL CUENTAS
      const saldoFinalCuentasConcepto = conceptos.find(c => c.nombre === 'SALDO FINAL CUENTAS');
      
      if (!saldoFinalCuentasConcepto) {
        console.warn('❌ No se encontró el concepto SALDO FINAL CUENTAS para guardar');
        return false;
      }

      console.log('💾 Guardando SALDO FINAL CUENTAS automáticamente:', {
        conceptoId: saldoFinalCuentasConcepto.id,
        cuentaId: cuentaId,
        saldoFinal: saldoFinal,
        fecha: selectedDate
      });

      // Usar la función de guardar transacciones existente
      const resultado = await guardarTransaccion(
        saldoFinalCuentasConcepto.id!, 
        cuentaId, 
        saldoFinal
      );

      if (resultado) {
        console.log('✅ SALDO FINAL CUENTAS guardado correctamente para cuenta:', cuentaId);
        return true;
      } else {
        console.error('❌ Error guardando SALDO FINAL CUENTAS para cuenta:', cuentaId);
        return false;
      }
    } catch (error) {
      console.error('💥 Error guardando SALDO FINAL CUENTAS automáticamente:', error);
      return false;
    }
  };

  // Función para procesar SALDOS INICIALES usando el backend (automático y silencioso)
  const procesarSaldosInicialesAutomatico = async (fecha?: string) => {
    try {
      const fechaProceso = fecha || selectedDate;
      
      console.log('� Verificando necesidad de SALDOS INICIALES para fecha:', fechaProceso);
      
      // Primero verificar si es necesario procesar
      const verificacion = await SaldoInicialService.verificarNecesidadSaldosIniciales(fechaProceso);
      
      console.log('📋 Resultado de verificación:', verificacion);
      
      if (!verificacion.necesario) {
        console.log('✅ SALDOS INICIALES ya están actualizados:', verificacion.razon);
        return;
      }
      
      console.log('�🔥 Procesando SALDOS INICIALES automáticamente para fecha:', fechaProceso);
      
      // Llamar al servicio del backend
      const resultado = await SaldoInicialService.calcularSaldoInicial({
        fecha: fechaProceso
      });
      
      console.log('✅ Resultado automático del backend:', resultado);
      
      if (resultado.success && resultado.transacciones_creadas > 0) {
        console.log(`✅ SALDOS INICIALES procesados automáticamente:`, {
          fecha: fechaProceso,
          transacciones_creadas: resultado.transacciones_creadas,
          mensaje: resultado.message
        });
        
        // Forzar actualización de las transacciones sin recargar la página
        setForceUpdate(prev => prev + 1);
      }
      
    } catch (error) {
      console.error('❌ Error procesando SALDOS INICIALES automáticamente:', error);
      // No mostrar alerta, solo log para debugging
    }
  };

  // Función wrapper para obtener montos aplicando la lógica de signos automáticos
  const obtenerMontoConSignos = (conceptoId: number, cuentaId: number, tipoMonedaCuenta?: string): number => {
    try {
      // Validar parámetros de entrada
      if (!conceptoId || !cuentaId) {
        console.warn('Parámetros inválidos en obtenerMontoConSignos:', { conceptoId, cuentaId });
        return 0;
      }
      
      // Debug para SALDO INICIAL
      if (conceptoId === 1) {
        console.log('🔍 DEBUG SALDO INICIAL:', { conceptoId, cuentaId, selectedDate });
      }
      
      // Obtener el monto original con conversión de moneda
      const montoOriginal = obtenerMontoConConversion(conceptoId, cuentaId, tipoMonedaCuenta);
      
      // Debug para SALDO INICIAL
      if (conceptoId === 1) {
        console.log('📊 Monto obtenido:', montoOriginal);
      }
      
      // Validar que el monto sea un número válido
      if (!isFinite(montoOriginal) || isNaN(montoOriginal)) {
        console.warn('Monto no válido obtenido:', montoOriginal);
        return 0;
      }
      
      // Buscar el concepto para obtener su código
      const concepto = conceptos.find(c => c.id === conceptoId);
      
      if (!concepto) {
        console.warn('Concepto no encontrado para ID:', conceptoId);
        return montoOriginal; // Si no encontramos el concepto, devolver valor original
      }
      
      // Aplicar la lógica de signos según el código
      const resultado = aplicarSignoSegunCodigo(montoOriginal, concepto.codigo || '');
      
      return isFinite(resultado) ? resultado : 0;
      
    } catch (error) {
      console.error('Error aplicando signos al obtener monto:', error);
      // Fallback seguro al método original
      try {
        const fallback = obtenerMonto(conceptoId, cuentaId);
        return isFinite(fallback) ? fallback : 0;
      } catch (fallbackError) {
        console.error('Error en fallback de obtenerMontoConSignos:', fallbackError);
        return 0;
      }
    }
  };

  // Función wrapper para guardar transacciones aplicando la lógica de signos automáticos
  const guardarTransaccionConSignos = async (
    conceptoId: number, 
    cuentaId: number | null, 
    monto: number, 
    companiaId?: number
  ): Promise<boolean> => {
    try {
      // Buscar el concepto para obtener su código
      const concepto = conceptos.find(c => c.id === conceptoId);
      
      if (!concepto) {
        console.error('❌ No se encontró el concepto con ID:', conceptoId);
        return false;
      }
      
      console.log('💰 Guardando transacción:', {
        concepto: concepto.nombre,
        codigo: concepto.codigo,
        montoIngresado: monto,
        conceptoId,
        cuentaId,
        companiaId
      });
      
      // OPCIÓN 1: Respetar el valor que ingresa el usuario sin modificar el signo
      // El usuario es responsable de ingresar el signo correcto
      const montoFinal = monto;
      
      console.log('📤 Enviando al backend:', {
        montoFinal,
        sinModificacion: true
      });
      
      // Llamar a la función original con el monto sin modificar
      const resultado = await guardarTransaccion(conceptoId, cuentaId, montoFinal, companiaId);
      
      console.log('📋 Resultado del backend:', {
        success: resultado,
        concepto: concepto.nombre,
        monto: montoFinal
      });
      
      if (!resultado) {
        console.error('❌ El backend retornó false para:', {
          concepto: concepto.nombre,
          monto: montoFinal,
          errorContext: 'Operación de guardado falló'
        });
      } else {
        console.log('✅ Guardado exitoso en backend para:', {
          concepto: concepto.nombre,
          monto: montoFinal
        });
      }
      
      return resultado;
      
    } catch (error) {
      console.error('❌ Error aplicando signos a transacción:', error);
      return false;
    }
  };

  // 🔥 AUTO-PROCESAMIENTO DESHABILITADO TEMPORALMENTE
  // Interfiere con proyecciones de días hábiles
  // useEffect para procesar SALDOS INICIALES automáticamente
  // useEffect(() => {
  //   // Solo ejecutar si ya tenemos datos cargados
  //   if (!loading && bankAccounts.length > 0 && conceptos.length > 0) {
  //     
  //     // Ejecutar el procesamiento automático después de un pequeño delay
  //     // para asegurar que todos los datos estén listos
  //     const timer = setTimeout(() => {
  //       procesarSaldosInicialesAutomatico();
  //     }, 1000);

  //     return () => clearTimeout(timer);
  //   }
  // }, [selectedDate, loading, bankAccounts.length, conceptos.length]); // Re-ejecutar cuando cambie la fecha o se carguen los datos

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
            {/* Indicador TRM */}
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-sm text-gray-500 dark:text-gray-400">TRM:</span>
              {trmLoading ? (
                <span className="text-sm text-gray-400">Cargando...</span>
              ) : trmError ? (
                <span className="text-sm text-red-500" title={trmError}>Error al cargar TRM</span>
              ) : trm ? (
                <div className="flex items-center space-x-1">
                  <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                    ${parseFloat(trm.valor.toString()).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                  <span className="text-xs text-gray-400">
                    ({trm.fecha})
                  </span>
                </div>
              ) : (
                <span className="text-sm text-gray-400">No disponible</span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Selector de fecha específica para transacciones */}
          <div className="flex flex-col">
            <label className="text-xs text-gray-600 dark:text-gray-400 mb-1">Fecha específica:</label>
            <DatePicker 
              selectedDate={selectedDate}
              onDateChange={setSelectedDate}
              availableDates={[]}
              onlyBusinessDays={true}
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
                Error: {typeof transaccionesError === 'string' ? transaccionesError : 'Error desconocido'}
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
          
          {/* Toggle Multi-Moneda */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Multi-Moneda
            </label>
            <button
              onClick={() => setUsarMultiMoneda(!usarMultiMoneda)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                usarMultiMoneda ? 'bg-green-600' : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  usarMultiMoneda ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
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
          {(() => {
            // Expandir cuentas por moneda si está activado el modo multi-moneda
            const cuentasExpandidas = expandirCuentasPorMoneda(bankAccounts);
            
            return (
          <table className="w-full border-collapse text-xs">
            <thead>
              {/* FILA 1 - SOLO COMPAÑÍAS */}
              <tr>
                <th colSpan={3} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[100px]"></th>
                {/* Compañías reales desde la base de datos */}
                {cuentasExpandidas.map((account) => (
                  <th key={`company-${account.cuenta_moneda_id}`} className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
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
                {cuentasExpandidas.map((account) => (
                  <th key={`bank-${account.cuenta_moneda_id}`} className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                    {account.nombre_con_moneda || 'BANCO DESCONOCIDO'}
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
                {cuentasExpandidas.map((account) => (
                  <th key={account.cuenta_moneda_id} className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                    <div className="flex flex-col">
                      <span>{account.numero_cuenta}</span>
                      {usarMultiMoneda && (
                        <span className={`px-1 py-0.5 rounded text-xs font-bold ${
                          account.moneda_display === 'USD' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
                        }`}>
                          {account.moneda_display}
                        </span>
                      )}
                    </div>
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
              {conceptos
                .filter(concepto => 
                  // Filtrar los conceptos que ya se muestran como filas hardcodeadas al final
                  concepto.nombre !== 'SUB-TOTAL TESORERÍA' && 
                  concepto.nombre !== 'SALDO FINAL CUENTAS'
                )
                .map((concepto, conceptoIdx) => (
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
                  {cuentasExpandidas.map((account) => {
                    // Verificar si es el concepto "SALDO NETO INICIAL PAGADURÍA"
                    const esSaldoNetoPagaduria = concepto.nombre === 'SALDO NETO INICIAL PAGADURÍA';
                    // Verificar si es el concepto "SALDO INICIAL"
                    const esSaldoInicial = concepto.nombre === 'SALDO INICIAL';
                    
                    if (esSaldoNetoPagaduria) {
                      // Para SALDO NETO INICIAL PAGADURÍA, mostrar valor calculado (no editable)
                      const valorCalculado = safeNumericValue(calculateSaldoNetoPagaduria(account.id));
                      
                      return (
                        <td key={`data-${account.cuenta_moneda_id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs bg-yellow-50 dark:bg-yellow-900/20">
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
                      // Para SALDO INICIAL, primero buscar transacciones reales, luego fallback al día anterior
                      let valorSaldoInicial = 0;
                      
                      // Primero intentar obtener valor real de transacciones
                      if (concepto.id) {
                        valorSaldoInicial = obtenerMontoConSignos(concepto.id, account.id);
                      }
                      
                      // Si no hay valor real, calcular desde día anterior
                      if (valorSaldoInicial === 0) {
                        valorSaldoInicial = calculateSaldoInicialDesdeDiaAnterior(account.id);
                      }
                      
                      const valorSaldoInicialFinal = safeNumericValue(valorSaldoInicial);
                      
                      return (
                        <td key={`data-${account.cuenta_moneda_id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs bg-purple-50 dark:bg-purple-900/20">
                          {valorSaldoInicialFinal !== 0 ? (
                            <span className={`font-bold ${valorSaldoInicialFinal < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                              {valorSaldoInicialFinal < 0 ? `(${formatCurrency(Math.abs(valorSaldoInicialFinal))})` : formatCurrency(valorSaldoInicialFinal)}
                            </span>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500">—</span>
                          )}
                        </td>
                      );
                    } else {
                      // Para otros conceptos, usar celda editable normal
                      const valorCuenta = concepto.id ? obtenerMontoConSignos(concepto.id, account.id, account.tipo_moneda) : 0;
                      const valorSeguro = safeNumericValue(valorCuenta);
                      
                      return (
                        <td key={`data-${account.cuenta_moneda_id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs">
                          <CeldaEditable
                            valor={valorSeguro}
                            conceptoId={concepto.id || 0}
                            cuentaId={account.id}
                            companiaId={account.compania.id}
                            currency={account.tipo_moneda}
                            onGuardar={guardarTransaccionConSignos}
                            disabled={!concepto.id || transaccionesLoading || isConceptoAutoCalculado(concepto.id)}
                          />
                        </td>
                      );
                    }
                  })}
                  
                  {/* Columna TOTALES */}
                  <td className="border-2 border-green-400 dark:border-green-500 px-2 py-1 text-center text-xs bg-green-50 dark:bg-green-900/20">
                    {(() => {
                      try {
                        const total = safeNumericValue(calculateRowTotal(concepto));
                        return total !== 0 ? (
                          <span className={`font-bold ${total < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                            {total < 0 ? `(${formatCurrency(Math.abs(total))})` : formatCurrency(total)}
                          </span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        );
                      } catch (error) {
                        console.error('Error calculando total para concepto:', concepto.nombre, error);
                        return <span className="text-red-500 text-xs">Error</span>;
                      }
                    })()}
                  </td>
                </tr>
              ))}

              {/* SEPARADOR */}
              <tr>
                <td colSpan={4 + cuentasExpandidas.length} 
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
                {cuentasExpandidas.map((account) => {
                  const subtotalCuenta = calculateSubtotalTesoreria(account.id);
                  const subtotalValido = !isNaN(subtotalCuenta) && isFinite(subtotalCuenta) ? subtotalCuenta : 0;
                  
                  return (
                    <td key={`subtotal-${account.cuenta_moneda_id}`} className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">
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
                    // CORREGIDO: Sumar el SUB-TOTAL TESORERÍA de cada cuenta individual
                    const totalSubtotal = bankAccounts.reduce((sum, account) => {
                      const subtotalCuenta = calculateSubtotalTesoreria(account.id);
                      console.log(`🧮 SUB-TOTAL TESORERÍA - Cuenta ${account.numero_cuenta}: ${subtotalCuenta}`);
                      return sum + (Number(subtotalCuenta) || 0);
                    }, 0);
                    console.log(`🎯 SUB-TOTAL TESORERÍA - TOTAL CALCULADO: ${totalSubtotal}`);
                    
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
                {cuentasExpandidas.map((account) => {
                  const valorSaldoFinal = calculateSaldoFinalCuentas(account.id);
                  
                  return (
                    <td key={`saldo-final-${account.cuenta_moneda_id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs bg-blue-50 dark:bg-blue-900/20">
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
                    // CORREGIDO: Sumar el SALDO FINAL CUENTAS de cada cuenta individual
                    const totalSaldoFinal = bankAccounts.reduce((sum, account) => {
                      const saldoFinalCuenta = calculateSaldoFinalCuentas(account.id);
                      console.log(`🧮 SALDO FINAL CUENTAS - Cuenta ${account.numero_cuenta}: ${saldoFinalCuenta}`);
                      return sum + (Number(saldoFinalCuenta) || 0);
                    }, 0);
                    console.log(`🎯 SALDO FINAL CUENTAS - TOTAL CALCULADO: ${totalSaldoFinal}`);
                    
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
            );
          })()}
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

// Componente wrapper con ErrorBoundary
const DashboardTesoreriaWithErrorBoundary: React.FC = () => {
  return (
    <ErrorBoundary>
      <DashboardTesoreria />
    </ErrorBoundary>
  );
};

export default DashboardTesoreriaWithErrorBoundary;
