import React, { useState, useEffect } from 'react';
import { Building2, Download, RefreshCw, AlertCircle, Settings, Check, X } from 'lucide-react';
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
import { ErrorBoundary } from '../UI/ErrorBoundary';

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

interface DashboardPagaduriaProps {
  readOnly?: boolean;
}

const DashboardPagaduria: React.FC<DashboardPagaduriaProps> = ({ readOnly = false }) => {
  const { user } = useAuth();
  // Obtener la fecha actual en formato YYYY-MM-DD
  const getCurrentDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };
  
  const [selectedDate, setSelectedDate] = useState<string>(getCurrentDate());
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Estado para multi-moneda - SIEMPRE activado
  const [usarMultiMoneda, setUsarMultiMoneda] = useState<boolean>(true);
  
  // Estados para filtros
  const [companiasFiltradas, setCompaniasFiltradas] = useState<number[]>([]);
  const [bancosFiltrados, setBancosFiltrados] = useState<number[]>([]);
  
  // Estados para Cuatro por Mil (similar a GMF en Tesorería)
  const [cuatroPorMilConfig, setCuatroPorMilConfig] = useState<Map<number, number[]>>(new Map());
  const [cuatroPorMilModalOpen, setCuatroPorMilModalOpen] = useState(false);
  const [currentCuatroPorMilAccount, setCurrentCuatroPorMilAccount] = useState<number | null>(null);
  const [loadingCuatroPorMilConfig, setLoadingCuatroPorMilConfig] = useState(false);
  // Lista fija de conceptos permitidos para Cuatro por Mil
  const CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS: number[] = [
    68,  // EMBARGOS
    69,  // OTROS PAGOS
    76,  // PAGO SOI
    78,  // OTROS IMPTOS
  ];
  
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
    
    // Los valores ya están guardados en su moneda nativa (USD para cuentas USD, COP para cuentas COP)
    // No necesitan conversión para mostrar en la misma moneda
    console.log(`✅ Returning native value: ${monto} ${tipoMonedaCuenta}`);
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

  // ==================== FUNCIONES CUATRO POR MIL ====================
  
  // Cargar configuración de Cuatro por Mil desde el backend
  const cargarConfiguracionCuatroPorMil = async () => {
    if (!user || (user.role !== 'administrador' && user.role !== 'pagaduria')) return;
    
    setLoadingCuatroPorMilConfig(true);
    try {
      const token = localStorage.getItem('access_token');
      
      // Cargar configuraciones vigentes para la fecha seleccionada
      const configMap = new Map<number, number[]>();
      
      for (const account of bankAccounts) {
        // Pasar fecha como parámetro para obtener config vigente para ese día
        const response = await fetch(`http://localhost:8000/api/v1/cuatro-por-mil/config/${account.id}?fecha=${selectedDate}`, {
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` })
          }
        });
        
        if (response.ok) {
          const config = await response.json();
          if (config.conceptos_seleccionados && config.conceptos_seleccionados.length > 0) {
            // Asegurar que siempre sean números (IDs)
            const ids = config.conceptos_seleccionados.map((item: any) => {
              if (typeof item === 'object' && item.id) return Number(item.id);
              return Number(item);
            }).filter((id: number) => !isNaN(id) && CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS.includes(id));
            // Si queda vacío tras filtrado, usar todos permitidos
            configMap.set(account.id, ids.length ? ids : [...CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS]);
          } else {
            // Si no hay configuración, usar todos los permitidos por defecto
            configMap.set(account.id, [...CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS]);
          }
        }
      }
      
      setCuatroPorMilConfig(configMap);
    } catch (error) {
      console.error('Error cargando configuración Cuatro por Mil:', error);
    } finally {
      setLoadingCuatroPorMilConfig(false);
    }
  };

  // Guardar configuración de Cuatro por Mil
  const guardarConfiguracionCuatroPorMil = async (cuentaId: number, conceptos: number[]) => {
    if (!user || (user.role !== 'administrador' && user.role !== 'pagaduria')) return;
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/cuatro-por-mil/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: JSON.stringify({
          cuenta_bancaria_id: cuentaId,
          conceptos_seleccionados: conceptos,
          fecha_vigencia_desde: selectedDate
        })
      });
      
      if (response.ok) {
        // Actualizar configuración local
        const nuevaConfig = new Map(cuatroPorMilConfig);
        nuevaConfig.set(cuentaId, conceptos);
        setCuatroPorMilConfig(nuevaConfig);
      }
    } catch (error) {
      console.error('Error guardando configuración Cuatro por Mil:', error);
    }
  };

  // Abrir modal de configuración Cuatro por Mil
  const abrirModalCuatroPorMil = (cuentaId: number) => {
    if (!user || (user.role !== 'administrador' && user.role !== 'pagaduria')) return;
    
    setCurrentCuatroPorMilAccount(cuentaId);
    
    // Si no hay configuración, asignar todos los permitidos por defecto
    if (!cuatroPorMilConfig.has(cuentaId)) {
      const nuevaConfig = new Map(cuatroPorMilConfig);
      nuevaConfig.set(cuentaId, [...CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS]);
      setCuatroPorMilConfig(nuevaConfig);
    }
    
    setCuatroPorMilModalOpen(true);
  };

  // Cerrar modal de configuración Cuatro por Mil
  const cerrarModalCuatroPorMil = () => {
    setCurrentCuatroPorMilAccount(null);
    setCuatroPorMilModalOpen(false);
  };

  // Guardar y recalcular Cuatro por Mil
  const guardarConceptosCuatroPorMil = async (cuentaId: number) => {
    if (!cuentaId) return;
    
    const conceptos = cuatroPorMilConfig.get(cuentaId) || [];
    console.log('🔧 [Cuatro por Mil] Guardando conceptos para cuenta:', cuentaId, 'Conceptos:', conceptos, 'Fecha:', selectedDate);
    
    // Guardar configuración y esperar respuesta
    await guardarConfiguracionCuatroPorMil(cuentaId, conceptos);
    console.log('✅ [Cuatro por Mil] Configuración guardada');
    
    // Forzar recálculo en backend
    try {
      const token = localStorage.getItem('access_token');
      console.log('🔄 [Cuatro por Mil] Iniciando recálculo para fecha:', selectedDate, 'cuenta:', cuentaId);
      
      const response = await fetch('http://localhost:8000/api/v1/cuatro-por-mil/recalculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: JSON.stringify({
          fecha: selectedDate,
          cuenta_bancaria_id: cuentaId
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error en recálculo: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('✅ [Cuatro por Mil] Recálculo completado:', result);
      
      // Esperar 1 segundo para asegurar que el backend persistió completamente
      console.log('⏱️ [Cuatro por Mil] Esperando 1 segundo antes de recargar...');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Recargar configuración
      await cargarConfiguracionCuatroPorMil();
      console.log('✅ [Cuatro por Mil] Configuración recargada');
      
      // Recargar transacciones
      console.log('🔄 [Cuatro por Mil] Recargando transacciones...');
      await cargarTransacciones();
      
      console.log('✅ [Cuatro por Mil] Transacciones recargadas');
    } catch (error) {
      console.error('❌ [Cuatro por Mil] Error forzando recálculo:', error);
      alert('Error al recalcular Cuatro por Mil. Por favor, recarga la página.');
    }
    
    cerrarModalCuatroPorMil();
  };

  // ==================== FIN FUNCIONES CUATRO POR MIL ====================

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
      
      // Si no hay código definido (null, undefined, o string vacío), devolver el valor original
      // Esto es importante para conceptos calculados que ya tienen el signo correcto en BD
      if (!codigo || codigo.trim() === '') {
        return valor; // Retornar valor original con su signo tal como está en BD
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
        default: // Para cualquier otro código no reconocido, devolver valor original
          return valor;
      }
    } catch (error) {
      console.error('Error en aplicarSignoSegunCodigo:', error);
      return 0;
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
      
      console.log('💰 [PAGADURÍA] Guardando transacción:', {
        concepto: concepto.nombre,
        codigo: concepto.codigo,
        montoIngresado: monto,
        conceptoId,
        cuentaId,
        companiaId
      });
      
      // 🔧 CORRECCIÓN: Aplicar lógica de signos según el código del concepto
      // E (Egreso) → Siempre negativo
      // I (Ingreso) → Siempre positivo  
      // N (Neutro) o sin código → Respetar el signo ingresado por el usuario
      let montoFinal = monto;
      
      if (concepto.codigo && concepto.codigo.trim() !== '' && concepto.codigo.trim().toUpperCase() !== 'N') {
        // Aplicar lógica de signos automática SOLO para E (Egreso) e I (Ingreso)
        montoFinal = aplicarSignoSegunCodigo(Math.abs(monto), concepto.codigo);
        console.log('🔧 [PAGADURÍA] Signo aplicado automáticamente:', {
          concepto: concepto.nombre,
          montoOriginal: monto,
          montoAbsoluto: Math.abs(monto),
          codigo: concepto.codigo,
          montoFinal: montoFinal,
          razon: 'Concepto tipo E o I con código definido',
          logicaAplicada: concepto.codigo.toUpperCase() === 'E' ? 'Egreso → Negativo' : 
                         concepto.codigo.toUpperCase() === 'I' ? 'Ingreso → Positivo' : 'Código desconocido'
        });
      } else {
        // Para conceptos NEUTROS (N) o sin código, respetar el valor ingresado por el usuario
        montoFinal = monto;
        console.log('✋ [PAGADURÍA] Valor respetado tal como ingresó el usuario:', {
          concepto: concepto.nombre,
          codigo: concepto.codigo || 'sin código',
          montoIngresadoPorUsuario: monto,
          montoFinal: montoFinal,
          esNegativo: monto < 0,
          razon: concepto.codigo?.toUpperCase() === 'N' ? 'Concepto Neutro - el usuario define el signo' : 'Concepto sin código definido'
        });
      }
      
      console.log('📤 [PAGADURÍA] Enviando al backend:', {
        montoFinal,
        aplicacionSignos: concepto.codigo ? 'automática' : 'manual'
      });
      
      // Llamar a la función original con el monto final
      const resultado = await guardarTransaccion(conceptoId, cuentaId, montoFinal, companiaId);
      
      console.log('📋 [PAGADURÍA] Resultado del backend:', {
        success: resultado,
        concepto: concepto.nombre,
        monto: montoFinal
      });
      
      if (!resultado) {
        console.error('❌ [PAGADURÍA] El backend retornó false para:', {
          concepto: concepto.nombre,
          monto: montoFinal,
          errorContext: 'Operación de guardado falló'
        });
      } else {
        console.log('✅ [PAGADURÍA] Guardado exitoso en backend para:', {
          concepto: concepto.nombre,
          monto: montoFinal
        });
      }
      
      return resultado;
      
    } catch (error) {
      console.error('❌ [PAGADURÍA] Error aplicando signos a transacción:', error);
      return false;
    }
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
      const idsConCuentasFiltradas = cuentasFiltradas.map(c => Number(c.id));
      
      // Sumar todas las transacciones de este concepto
      // Si hay filtros aplicados, solo sumar las de cuentas filtradas
      // Si no hay filtros, sumar TODAS las transacciones del concepto
      const transaccionesConcepto = transacciones.filter(t => {
        if (t.concepto_id !== concepto.id) return false;
        
        // Si hay filtros de compañía o banco, aplicar el filtro de cuentas
        if (companiasFiltradas.length > 0 || bancosFiltrados.length > 0) {
          return t.cuenta_id !== null && idsConCuentasFiltradas.includes(Number(t.cuenta_id));
        }
        
        // Si no hay filtros, incluir todas las transacciones del concepto
        return true;
      });
      
      total = transaccionesConcepto.reduce((sum, t) => sum + (Number(t.monto) || 0), 0);
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
        tipo_moneda: cuenta.monedas[0] || 'COP',
        nombre_con_moneda: `${cuenta.banco.nombre} ${cuenta.numero_cuenta.slice(-4)}`,
        es_expansion: false,
        es_cop_autocalculado: false,
        cuenta_usd_par_id: null
      }));
    }

    const cuentasExpandidas: any[] = [];
    
    cuentas.forEach(cuenta => {
      const monedas = cuenta.monedas && cuenta.monedas.length > 0 ? cuenta.monedas : ['COP'];
      const tieneUSD = monedas.includes('USD');
      const tieneCOP = monedas.includes('COP');
      const esMultiMoneda = tieneUSD && tieneCOP;
      
      // Ordenar monedas: USD primero (editable), luego COP (calculado)
      const monedasOrdenadas = [...monedas].sort((a, b) => {
        if (a === 'USD' && b === 'COP') return -1;
        if (a === 'COP' && b === 'USD') return 1;
        return 0;
      });
      
      let cuentaUsdId: number | null = null;
      
      monedasOrdenadas.forEach((moneda, index) => {
        const esCopAutocalculado = esMultiMoneda && moneda === 'COP';
        
        if (esMultiMoneda && moneda === 'USD') {
          cuentaUsdId = cuenta.id;
        }
        
        const cuentaExpandida = {
          ...cuenta,
          cuenta_moneda_id: `${cuenta.id}_${moneda}`,
          moneda_display: moneda,
          tipo_moneda: moneda,
          nombre_con_moneda: `${cuenta.banco.nombre} ${cuenta.numero_cuenta.slice(-4)} (${moneda})`,
          es_expansion: index > 0,
          es_cop_autocalculado: esCopAutocalculado,
          cuenta_usd_par_id: esCopAutocalculado ? cuentaUsdId : null
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

  // Cargar configuración de Cuatro por Mil cuando las cuentas están listas
  useEffect(() => {
    if (bankAccounts.length > 0 && user && (user.role === 'administrador' || user.role === 'pagaduria')) {
      cargarConfiguracionCuatroPorMil();
    }
  }, [bankAccounts, selectedDate, user]);

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
          

          {!readOnly && (
            <>
              <button className="flex items-center space-x-2 px-3 py-2 bg-bolivar-600 text-white rounded-lg hover:bg-bolivar-700 transition-colors text-sm">
                <RefreshCw className="h-4 w-4" />
                <span>Actualizar</span>
              </button>
              <button className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm">
                <Download className="h-4 w-4" />
                <span>Exportar</span>
              </button>
            </>
          )}
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
                      <span className={`px-1 py-0.5 rounded text-xs font-bold ${
                        account.moneda_display === 'USD' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
                      }`}>
                        {account.moneda_display}
                      </span>
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
                      className={`border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs h-8 min-h-[32px] ${concepto.nombre === 'CUATRO POR MIL' ? 'bg-orange-50 dark:bg-orange-900/20' : ''}`}
                    >
                      {/* Si es CUATRO POR MIL, mostrar valor desde BD + botón de configuración */}
                      {concepto.nombre === 'CUATRO POR MIL' ? (
                        (() => {
                          const valorCuatroPorMilPersistido = concepto.id ? obtenerMonto(concepto.id, account.id) : 0;
                          const valorSeguro = safeNumericValue(valorCuatroPorMilPersistido);
                          
                          return (
                            <div className="flex items-center justify-between">
                              <div className="flex-1 text-center">
                                {valorSeguro !== 0 ? (
                                  <span className={`font-medium ${valorSeguro < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
                                    {valorSeguro < 0 ? `(${formatCurrency(Math.abs(valorSeguro))})` : formatCurrency(valorSeguro)}
                                  </span>
                                ) : (
                                  <span className="text-gray-400 dark:text-gray-500">—</span>
                                )}
                              </div>
                              
                              {/* Ícono de configuración - Alineado a la derecha */}
                              {!readOnly && (user?.role === 'administrador' || user?.role === 'pagaduria') && (
                                <button
                                  onClick={() => abrirModalCuatroPorMil(account.id)}
                                  className="p-1 text-orange-600 hover:text-orange-800 dark:text-orange-400 dark:hover:text-orange-200 transition-colors hover:bg-orange-100 dark:hover:bg-orange-900/20 rounded"
                                  title="Configurar conceptos Cuatro por Mil"
                                >
                                  <Settings className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>
                          );
                        })()
                      ) : concepto.nombre === 'DIFERENCIA SALDOS' ? (
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
                      ) : account.es_cop_autocalculado && account.cuenta_usd_par_id && trm ? (
                        // Celda COP auto-calculada desde USD × TRM / 1000 (BLOQUEADA)
                        (() => {
                          const valorUSD = obtenerMontoConConversion(concepto.id || 0, account.cuenta_usd_par_id, 'USD');
                          const valorCOPCalculado = (valorUSD * trm.valor) / 1000;
                          
                          return valorCOPCalculado !== 0 ? (
                            <span className={`font-medium ${valorCOPCalculado < 0 ? 'text-red-600 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'}`} title="Valor auto-calculado desde USD × TRM">
                              {valorCOPCalculado < 0 ? `(${formatCurrency(Math.abs(valorCOPCalculado))})` : formatCurrency(valorCOPCalculado)}
                            </span>
                          ) : (
                            <span className="text-gray-400 dark:text-gray-500">—</span>
                          );
                        })()
                      ) : (
                        <CeldaEditable
                          conceptoId={concepto.id || 0}
                          cuentaId={account.id}
                          valor={obtenerMontoConConversion(concepto.id || 0, account.id, account.tipo_moneda)}
                          currency={account.tipo_moneda}
                          onGuardar={guardarTransaccionConSignos}
                          companiaId={account.compania?.id}
                          disabled={readOnly || isConceptoAutoCalculado(concepto.id)}
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

      {/* Modal de configuración Cuatro por Mil */}
      {cuatroPorMilModalOpen && currentCuatroPorMilAccount && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full m-4">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Configurar Conceptos Cuatro por Mil
                </h3>
                <button
                  onClick={cerrarModalCuatroPorMil}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Selecciona los conceptos que se incluirán en el cálculo del Cuatro por Mil para esta cuenta:
                </p>
                
                {loadingCuatroPorMilConfig ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin text-gray-400" />
                    <span className="ml-2 text-gray-600 dark:text-gray-400">Cargando configuración...</span>
                  </div>
                ) : (
                  <div>
                    <div className="flex justify-between items-center mb-2 text-xs text-gray-600 dark:text-gray-400">
                      <span>Seleccionados: {cuatroPorMilConfig.get(currentCuatroPorMilAccount)?.length || 0} / {CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS.length}</span>
                      <div className="space-x-2">
                        <button
                          onClick={() => {
                            const nuevaConfig = new Map(cuatroPorMilConfig);
                            nuevaConfig.set(currentCuatroPorMilAccount, [...CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS]);
                            setCuatroPorMilConfig(nuevaConfig);
                          }}
                          className="px-2 py-1 border rounded text-xs hover:bg-gray-50 dark:hover:bg-gray-700"
                        >Todos</button>
                        <button
                          onClick={() => {
                            const nuevaConfig = new Map(cuatroPorMilConfig);
                            nuevaConfig.set(currentCuatroPorMilAccount, []);
                            setCuatroPorMilConfig(nuevaConfig);
                          }}
                          className="px-2 py-1 border rounded text-xs hover:bg-gray-50 dark:hover:bg-gray-700"
                        >Limpiar</button>
                      </div>
                    </div>
                    <div className="max-h-64 overflow-y-auto border rounded-md p-3 space-y-2">
                      {conceptos
                        .filter(concepto => CONCEPTOS_CUATRO_POR_MIL_PERMITIDOS.includes(concepto.id || 0))
                        .map((concepto) => {
                          const isSelected = cuatroPorMilConfig.get(currentCuatroPorMilAccount)?.includes(concepto.id || 0) || false;
                          return (
                            <label key={concepto.id} className="flex items-center space-x-2 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={(e) => {
                                  const conceptosActuales = cuatroPorMilConfig.get(currentCuatroPorMilAccount) || [];
                                  let nuevosConceptos;
                                  if (e.target.checked) {
                                    nuevosConceptos = [...conceptosActuales, concepto.id || 0];
                                  } else {
                                    nuevosConceptos = conceptosActuales.filter(id => id !== concepto.id);
                                  }
                                  const nuevaConfig = new Map(cuatroPorMilConfig);
                                  nuevaConfig.set(currentCuatroPorMilAccount, nuevosConceptos);
                                  setCuatroPorMilConfig(nuevaConfig);
                                }}
                                className="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                              />
                              <span className="text-sm text-gray-700 dark:text-gray-300">{concepto.nombre}</span>
                            </label>
                          );
                        })}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={cerrarModalCuatroPorMil}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => guardarConceptosCuatroPorMil(currentCuatroPorMilAccount)}
                  disabled={loadingCuatroPorMilConfig}
                  className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  {loadingCuatroPorMilConfig ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      Guardar
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Componente wrapper con ErrorBoundary
const DashboardPagaduriaWithErrorBoundary: React.FC<DashboardPagaduriaProps> = ({ readOnly = false }) => {
  return (
    <ErrorBoundary>
      <DashboardPagaduria readOnly={readOnly} />
    </ErrorBoundary>
  );
};

export default DashboardPagaduriaWithErrorBoundary;
