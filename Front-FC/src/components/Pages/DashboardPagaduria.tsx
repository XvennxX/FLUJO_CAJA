import React, { useState, useEffect } from 'react';
import { Building2, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency } from '../../utils/formatters';
import { formatDateString } from '../../utils/dateUtils';
import { isConceptoAutoCalculado } from '../../utils/conceptos';
import { useTRM } from '../../hooks/useTRM';
import { useTRMByDate } from '../../hooks/useTRMByDate';
import { useConceptosFlujoCaja, ConceptoFlujoCaja } from '../../hooks/useConceptosFlujoCaja';
import { useTransaccionesFlujoCaja } from '../../hooks/useTransaccionesFlujoCaja';
import { useDiferenciaSaldos } from '../../hooks/useDiferenciaSaldos';
import DatePicker from '../Calendar/DatePicker';
import { useDashboardWebSocket } from '../../hooks/useWebSocket';
import { CeldaEditable } from '../UI/CeldaEditable';
import { FiltrosDashboard } from '../Dashboard/FiltrosDashboard';

interface Concepto {
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

const DashboardPagaduria: React.FC = () => {
  const { user } = useAuth();
  // Obtener la fecha actual en formato YYYY-MM-DD
  const getCurrentDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };
  
  const [selectedDate, setSelectedDate] = useState<string>(getCurrentDate());
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Estado para multi-moneda
  const [usarMultiMoneda, setUsarMultiMoneda] = useState<boolean>(false);
  
  // Estados para filtros
  const [companiasFiltradas, setCompaniasFiltradas] = useState<number[]>([]);
  const [bancosFiltrados, setBancosFiltrados] = useState<number[]>([]);
  
  // Hook para obtener TRM de la fecha seleccionada
  const { trm, loading: trmLoading, error: trmError, refetch: refetchTRM } = useTRMByDate(selectedDate);
  
  // Hook para obtener conceptos desde el backend
  const { conceptosPagaduria, loading: conceptosLoading, error: conceptosError } = useConceptosFlujoCaja();
  
  // Hook para manejar transacciones
  const { 
    transacciones, 
    loading: transaccionesLoading, 
    error: transaccionesError,
    cargarTransacciones,
    guardarTransaccion,
    obtenerMonto,
    setError: setTransaccionesError
  } = useTransaccionesFlujoCaja(selectedDate, 'pagaduria');

  // Hook para manejar diferencias saldos automáticas
  const { 
    calcularDiferenciaSaldos, 
    verificarNecesidadCalculo,
    loading: diferenciaSaldosLoading 
  } = useDiferenciaSaldos();

  // Hook para WebSocket - actualizaciones en tiempo real
  useDashboardWebSocket('pagaduria', cargarTransacciones);

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

  // Función para filtrar cuentas bancarias
  const obtenerCuentasFiltradas = (): BankAccount[] => {
    if (companiasFiltradas.length === 0 && bancosFiltrados.length === 0) {
      // Si no hay filtros, mostrar todas las cuentas
      return bankAccounts;
    }
    
    return bankAccounts.filter(account => {
      const cumpleCompania = companiasFiltradas.length === 0 || companiasFiltradas.includes(account.compania.id);
      const cumpleBanco = bancosFiltrados.length === 0 || bancosFiltrados.includes(account.banco.id);
      
      return cumpleCompania && cumpleBanco;
    });
  };

  // Funciones para manejar los filtros
  const handleCompaniasChange = (nuevasCompanias: number[]) => {
    setCompaniasFiltradas(nuevasCompanias);
  };

  const handleBancosChange = (nuevosBancos: number[]) => {
    setBancosFiltrados(nuevosBancos);
  };

  const handleLimpiarFiltros = () => {
    setCompaniasFiltradas([]);
    setBancosFiltrados([]);
  };

  // Función para convertir conceptos del backend al formato del frontend
  const convertirConceptosParaTabla = (conceptosBackend: ConceptoFlujoCaja[]): Concepto[] => {
    return conceptosBackend.map(concepto => ({
      codigo: concepto.codigo || '', // Usar el campo 'codigo' de la BD para la columna "OP"
      nombre: concepto.nombre,
      tipo: concepto.tipo, // Usar el campo 'tipo' de la BD para la columna "TIPO OP"
      id: concepto.id // Incluir ID para vincular con transacciones
    }));
  };

  // Función para calcular el total de una fila usando datos reales y fallback
  const calculateRowTotal = (concepto: Concepto) => {
    let total = 0;
    
    if (concepto.id) {
      // Obtener IDs de cuentas filtradas para calcular solo sus totales
      const cuentasFiltradas = obtenerCuentasFiltradas();
      const idsConCuentasFiltradas = cuentasFiltradas.map(c => c.id);
      
      // Sumar solo las transacciones de este concepto que pertenezcan a cuentas filtradas
      const transaccionesConcepto = transacciones.filter(t => 
        t.concepto_id === concepto.id && t.cuenta_id !== null && idsConCuentasFiltradas.includes(t.cuenta_id)
      );
      total = transaccionesConcepto.reduce((sum, t) => sum + t.monto, 0);
    }
    
    return total;
  };

  // Función para procesamiento automático de diferencias saldos
  const procesarDiferenciaSaldosAutomatica = async () => {
    try {
      console.log('🔍 Verificando necesidad de cálculo de diferencias saldos...');
      const necesitaCalculo = await verificarNecesidadCalculo(selectedDate);
      
      if (necesitaCalculo) {
        console.log('⚡ Calculando diferencias saldos automáticamente...');
        await calcularDiferenciaSaldos(selectedDate);
        console.log('✅ Diferencias saldos procesadas');
        // Recargar transacciones para mostrar los nuevos valores
        window.location.reload(); // Temporal - en producción usar mejor refetch
      } else {
        console.log('✅ Diferencias saldos ya están actualizadas');
      }
    } catch (error) {
      console.error('❌ Error procesando diferencias saldos:', error);
    }
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


  // Obtener conceptos: del backend si están disponibles, sino usar los hardcodeados como fallback
  const conceptos: Concepto[] = conceptosLoading || conceptosError ? 
    // Fallback a conceptos hardcodeados si hay error o están cargando
    [
      { codigo: '', nombre: 'DIFERENCIA SALDOS', tipo: 'neutral' },
      { codigo: '', nombre: 'SALDOS EN BANCOS', tipo: 'neutral' },
      { codigo: 'I', nombre: 'SALDO DIA ANTERIOR', tipo: 'ingreso' },
      { codigo: 'I', nombre: 'INGRESO', tipo: 'ingreso' },
      { codigo: 'E', nombre: 'EGRESO', tipo: 'egreso' },
      { codigo: 'E', nombre: 'CONSUMO NACIONAL', tipo: 'egreso' },
      { codigo: 'I', nombre: 'INGRESO CTA PAGADURIA', tipo: 'ingreso' },
      { codigo: 'I', nombre: 'FINANSEGUROS', tipo: 'ingreso' },
      { codigo: 'I', nombre: 'RECAUDOS LIBERTADOR', tipo: 'ingreso' },
      { codigo: 'I', nombre: 'RENDIMIENTOS FINANCIEROS', tipo: 'ingreso' },
      { codigo: 'I', nombre: 'INGRESOS REASEGUROS', tipo: 'ingreso' },
      { codigo: 'E', nombre: 'EGR. REASEGUROS', tipo: 'egreso' },
      { codigo: 'I', nombre: 'ING. COMPRA DE DIVISAS-REASEGUR', tipo: 'ingreso' },
      { codigo: 'E', nombre: 'EGR. VENTA DIVISAS-REASEGUROS', tipo: 'egreso' },
      { codigo: 'E', nombre: 'EGRESO - TRASLADOS COMPAÑÍAS', tipo: 'egreso' },
      { codigo: 'I', nombre: 'INGRESO - TRASLADOS COMPAÑÍAS', tipo: 'ingreso' },
      { codigo: 'E', nombre: 'EMBARGOS', tipo: 'egreso' },
      { codigo: 'E', nombre: 'OTROS PAGOS', tipo: 'egreso' },
      { codigo: 'E', nombre: 'VENTAN PROVEEDORES', tipo: 'egreso' },
      { codigo: '', nombre: 'INTERCIAS RELAC./INDUS', tipo: 'neutral' },
      { codigo: 'E', nombre: 'COMISIONES DAVIVIENDA', tipo: 'egreso' },
      { codigo: 'E', nombre: 'NOMINA CONSEJEROS', tipo: 'egreso' },
      { codigo: '', nombre: 'NOMINA ADMINISTRATIVA', tipo: 'neutral' },
      { codigo: '', nombre: 'NOMINA PENSIONES', tipo: 'neutral' },
      { codigo: 'E', nombre: 'PAGO SOI', tipo: 'egreso' },
      { codigo: 'E', nombre: 'PAGO IVA', tipo: 'egreso' },
      { codigo: 'E', nombre: 'OTROS IMPTOS', tipo: 'egreso' },
      { codigo: 'E', nombre: 'EGRESO DIVIDENDOS', tipo: 'egreso' },
      { codigo: 'E', nombre: 'CUATRO POR MIL', tipo: 'egreso' },
      { codigo: '', nombre: 'DIFERENCIA EN CAMBIO CTAS REASEGUROS', tipo: 'neutral' }
    ] :
    // Usar conceptos del backend
    convertirConceptosParaTabla(conceptosPagaduria);

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

  // Ejecutar procesamiento automático de diferencias saldos cuando cambien las transacciones
  useEffect(() => {
    if (!transaccionesLoading && transacciones.length > 0) {
      procesarDiferenciaSaldosAutomatica();
    }
  }, [selectedDate, transacciones.length]); // Solo cuando cambie la fecha o el número de transacciones

  const getRowColor = (tipo: string) => {
    switch (tipo) {
      case 'ingreso':
        return 'bg-green-100 dark:bg-green-900/30';
      case 'egreso':
        return 'bg-yellow-100 dark:bg-yellow-900/30';
      default:
        return 'bg-white dark:bg-gray-800';
    }
  };

  // Función para identificar conceptos especiales y asignar colores especiales
  const getSpecialRowColor = (concepto: Concepto) => {
    const nombreUpper = concepto.nombre.toUpperCase();
    
    // DIFERENCIA SALDOS - Color especial para mostrar que es calculado automáticamente
    if (nombreUpper.includes('DIFERENCIA SALDOS')) {
      return 'bg-yellow-100 dark:bg-yellow-900/30 font-medium border-l-4 border-yellow-400';
    }
    
    // SUBTOTAL MOVIMIENTO - Verde
    if (nombreUpper.includes('SUBTOTAL MOVIMIENTO') || nombreUpper.includes('SUBTOTAL MOVIMIENTO BANCARIA')) {
      return 'bg-green-200 dark:bg-green-800/40 font-bold';
    }
    
    // SUBTOTAL SALDO INICIAL - Gris/Morado
    if (nombreUpper.includes('SUBTOTAL SALDO INICIAL')) {
      return 'bg-gray-200 dark:bg-gray-700 font-bold';
    }
    
    // MOVIMIENTO TESORERÍA - Azul
    if (nombreUpper.includes('MOVIMIENTO TESORERIA') || nombreUpper.includes('MOVIMIENTO TESORERÍA')) {
      return 'bg-blue-200 dark:bg-blue-800/40 font-bold';
    }
    
    // SALDO TOTAL - Gris/Morado
    if (nombreUpper.includes('SALDO TOTAL EN BANCOS') || nombreUpper.includes('SALDO TOTAL')) {
      return 'bg-gray-200 dark:bg-gray-700 font-bold';
    }
    
    // Si no es especial, usar el color normal
    return getRowColor(concepto.tipo);
  };

  // Función para verificar si es un concepto especial
  const isSpecialConcept = (concepto: Concepto): boolean => {
    const nombreUpper = concepto.nombre.toUpperCase();
    return nombreUpper.includes('DIFERENCIA SALDOS') ||
           nombreUpper.includes('SUBTOTAL MOVIMIENTO') ||
           nombreUpper.includes('SUBTOTAL SALDO INICIAL') ||
           nombreUpper.includes('MOVIMIENTO TESORERIA') ||
           nombreUpper.includes('MOVIMIENTO TESORERÍA') ||
           nombreUpper.includes('SALDO TOTAL');
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
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Panel de Pagaduría</h1>
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
                  Conectado a BD ({conceptosPagaduria.length})
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
                    ({formatDateString(trm.fecha)})
                  </span>
                  <button 
                    onClick={refetchTRM}
                    className="ml-1 text-xs text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                    title="Actualizar TRM"
                  >
                    🔄
                  </button>
                </div>
              ) : (
                <span className="text-sm text-gray-400">N/A</span>
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

      {/* Filtros */}
      <FiltrosDashboard
        bankAccounts={bankAccounts}
        companiasFiltradas={companiasFiltradas}
        bancosFiltrados={bancosFiltrados}
        onCompaniasChange={handleCompaniasChange}
        onBancosChange={handleBancosChange}
        onLimpiarFiltros={handleLimpiarFiltros}
      />

      {/* Tabla estilo Excel - SIN fechas, solo compañías y cuentas */}
      <div className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          {(() => {
            // Obtener cuentas filtradas y expandir por moneda si está activado el modo multi-moneda
            const cuentasFiltradas = obtenerCuentasFiltradas();
            const cuentasExpandidas = expandirCuentasPorMoneda(cuentasFiltradas);
            
            return (
          <table className="w-full border-collapse text-xs">
            <thead>
              {/* FILA 1 - SOLO COMPAÑÍAS */}
              <tr>
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[60px]"></th>
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-[60px] z-20 min-w-[200px]"></th>
                {/* Compañías reales desde la base de datos - empiezan desde la tercera columna */}
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
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[60px]"></th>
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-[60px] z-20 min-w-[200px]"></th>
                {/* Bancos reales desde la base de datos - empiezan desde la tercera columna */}
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

              {/* FILA 3 - COD, CUENTA y NÚMEROS DE CUENTA */}
              <tr>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20 min-w-[60px]">
                  COD
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-20 min-w-[200px]">
                  CUENTA
                </th>
                {/* Cuentas bancarias reales desde la base de datos - empiezan desde la tercera columna */}
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

              {/* FILA 4 - TRM */}
              <tr>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20">
                  
                </th>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-20">
                  TRM
                </th>
                {/* Celdas TRM para cuentas bancarias reales - empiezan desde la tercera columna */}
                {cuentasExpandidas.map((account) => (
                  <th key={`trm-${account.cuenta_moneda_id}`} className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                    {trmLoading ? (
                      <span className="text-gray-400">Cargando...</span>
                    ) : trmError ? (
                      <span className="text-red-500" title={trmError}>Error</span>
                    ) : trm ? (
                      <span className="font-semibold text-blue-600 dark:text-blue-400">
                        ${parseFloat(trm.valor.toString()).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </span>
                    ) : (
                      <span className="text-gray-400">N/A</span>
                    )}
                  </th>
                ))}
                {/* Columna TOTALES */}
                <th className="bg-green-50 dark:bg-green-900 border-2 border-green-400 dark:border-green-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  {trmLoading ? (
                    <span className="text-gray-400">Cargando...</span>
                  ) : trmError ? (
                    <span className="text-red-500" title={trmError}>Error</span>
                  ) : trm ? (
                    <span className="font-semibold text-blue-600 dark:text-blue-400">
                      ${parseFloat(trm.valor.toString()).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  ) : (
                    <span className="text-gray-400">N/A</span>
                  )}
                </th>
              </tr>
            </thead>

            {/* BODY - CONCEPTOS Y DATOS */}
            <tbody>
              {conceptos.map((concepto, conceptoIdx) => (
                <tr key={conceptoIdx} className={getSpecialRowColor(concepto)}>
                  {/* COLUMNA DE CÓDIGO */}
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-center sticky left-0 z-10 ${getSpecialRowColor(concepto)}`}>
                    {/* Mostrar siempre un icono N para conceptos especiales, o el código real para conceptos normales */}
                    {isSpecialConcept(concepto) ? (
                      <span className="w-5 h-5 rounded text-xs flex items-center justify-center font-bold mx-auto bg-gray-500 text-white">
                        N
                      </span>
                    ) : concepto.codigo ? (
                      <span className={`w-5 h-5 rounded text-xs flex items-center justify-center font-bold mx-auto ${
                        concepto.codigo === 'E' 
                          ? 'bg-red-500 text-white' 
                          : concepto.codigo === 'I' 
                          ? 'bg-green-500 text-white' 
                          : 'bg-gray-500 text-white'
                      }`}>
                        {concepto.codigo}
                      </span>
                    ) : null}
                  </td>

                  {/* COLUMNA DE CUENTA/CONCEPTO */}
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium text-center sticky left-[60px] z-10 ${getSpecialRowColor(concepto)}`}>
                    <span className="text-xs leading-tight">{concepto.nombre}</span>
                  </td>

                  {/* CELDAS DE DATOS - Solo cuentas bancarias reales desde la tercera columna */}
                  {/* Columnas de cuentas bancarias reales */}
                  {cuentasExpandidas.map((account) => (
                    <td
                      key={`data-${account.cuenta_moneda_id}`}
                      className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs h-8 min-h-[32px]"
                    >
                      {/* Si es DIFERENCIA SALDOS, mostrar valor desde base de datos */}
                      {concepto.nombre === 'DIFERENCIA SALDOS' ? (
                        <div className="h-full flex items-center justify-center">
                          {(() => {
                            console.log(`🔍 Mostrando DIFERENCIA SALDOS para cuenta ${account.cuenta_moneda_id} (${account.numero_cuenta})`);
                            const transaccion = transacciones.find(t => 
                              t.cuenta_id === account.id && 
                              t.concepto_id === 52
                            );
                            const diferenciaOriginal = transaccion ? parseFloat(String(transaccion.monto)) || 0 : 0;
                            const diferencia = convertirMoneda(diferenciaOriginal, account.tipo_moneda);
                            console.log(`✅ Valor DIFERENCIA SALDOS cuenta ${account.cuenta_moneda_id}: ${diferenciaOriginal} -> ${diferencia} (${account.tipo_moneda})`);
                            
                            return diferencia !== 0 ? (
                              <span className={`font-medium ${diferencia < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                                {diferencia < 0 ? `(${formatCurrency(Math.abs(diferencia), account.tipo_moneda)})` : formatCurrency(diferencia, account.tipo_moneda)}
                              </span>
                            ) : (
                              <span className="text-gray-400 dark:text-gray-500">—</span>
                            );
                          })()}
                        </div>
                      ) : (
                        <CeldaEditable
                          conceptoId={concepto.id || 0}
                          cuentaId={account.id}
                          valor={obtenerMontoConConversion(concepto.id || 0, account.id, account.tipo_moneda)}
                          currency={account.tipo_moneda}
                          onGuardar={guardarTransaccion}
                          companiaId={account.compania?.id}
                          disabled={isConceptoAutoCalculado(concepto.id)} // 🚫 Deshabilitar conceptos auto-calculados
                        />
                      )}
                    </td>
                  ))}
                  
                  {/* Columna TOTALES */}
                  <td className="border-2 border-green-400 dark:border-green-500 px-2 py-1 text-center text-xs bg-green-50 dark:bg-green-900/20">
                    {(() => {
                      // Si es DIFERENCIA SALDOS, sumar totales desde base de datos
                      if (concepto.nombre === 'DIFERENCIA SALDOS') {
                        console.log(`🔍 Calculando DIFERENCIA SALDOS TOTAL`);
                        const total = transacciones
                          .filter(t => t.concepto_id === 52)
                          .reduce((sum, t) => sum + (parseFloat(String(t.monto)) || 0), 0);
                        console.log(`✅ Resultado DIFERENCIA SALDOS TOTAL: ${total}`);
                        return total !== 0 ? (
                          <span className={total < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}>
                            {total < 0 ? `(${formatCurrency(Math.abs(total))})` : formatCurrency(total)}
                          </span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        );
                      } else {
                        const total = calculateRowTotal(concepto);
                        return total !== 0 ? (
                          <span className={total < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}>
                            {total < 0 ? `(${formatCurrency(Math.abs(total))})` : formatCurrency(total)}
                          </span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        );
                      }
                    })()}
                  </td>
                </tr>
              ))}

              {/* SEPARADOR */}
              <tr>
                <td colSpan={3 + cuentasExpandidas.length} 
                    className="bg-gray-300 dark:bg-gray-600 h-2 border border-gray-400 dark:border-gray-500"></td>
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

export default DashboardPagaduria;
