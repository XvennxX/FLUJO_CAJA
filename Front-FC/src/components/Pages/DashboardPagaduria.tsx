import React, { useState, useEffect } from 'react';
import { Building2, Download, RefreshCw } from 'lucide-react';
import DatePicker from '../Calendar/DatePicker';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency } from '../../utils/formatters';
import { useTRM } from '../../hooks/useTRM';

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
  const [selectedMonth, setSelectedMonth] = useState<string>('2025-05');
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Hook para obtener TRM
  const { trm, loading: trmLoading, error: trmError } = useTRM();

  // Conceptos exactos del Excel con los códigos correctos
  const conceptos = [
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
  ];

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

  // Función para calcular el total de una fila
  const calculateRowTotal = (concepto: any) => {
    let total = 0;
    
    // Para el Dashboard de Pagaduría, los totales se calculan basándose en 
    // los valores que normalmente estarían en las cuentas bancarias reales
    // Por ahora usamos valores de ejemplo, pero esto se debería conectar con datos reales
    
    if (concepto.nombre === 'INGRESO') {
      // Ejemplo: suma de ingresos de todas las cuentas bancarias
      total += 27138180.25; // Total estimado de ingresos
    } else if (concepto.nombre === 'CONSUMO NACIONAL') {
      total += -184925.32; // Total estimado de consumo nacional
    } else if (concepto.nombre === 'RECAUDOS LIBERTADOR') {
      total += 148715.11; // Total de recaudos
    } else if (concepto.nombre === 'EMBARGOS') {
      total += -51577.82; // Total de embargos
    } else if (concepto.nombre === 'OTROS PAGOS') {
      total += -148505.71; // Total de otros pagos
    } else if (concepto.nombre === 'VENTAN PROVEEDORES') {
      total += -7026234.33; // Total de pagos a proveedores
    } else if (concepto.nombre === 'NOMINA ADMINISTRATIVA') {
      total += 142.35; // Total nómina administrativa
    }
    
    // En una implementación real, esto debería iterar sobre bankAccounts
    // y sumar los valores reales de cada cuenta para el concepto específico
    
    return total;
  };

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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Panel de Pagaduría</h1>
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
                  <span className="text-xs text-gray-400">({new Date(trm.fecha).toLocaleDateString('es-CO')})</span>
                </div>
              ) : (
                <span className="text-sm text-gray-400">N/A</span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <DatePicker 
            selectedDate={selectedMonth} 
            onDateChange={setSelectedMonth}
          />
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
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[60px]"></th>
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-[60px] z-20 min-w-[200px]"></th>
                {/* Compañías reales desde la base de datos - empiezan desde la tercera columna */}
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
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[60px]"></th>
                <th className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-[60px] z-20 min-w-[200px]"></th>
                {/* Bancos reales desde la base de datos - empiezan desde la tercera columna */}
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

              {/* FILA 3 - COD, CUENTA y NÚMEROS DE CUENTA */}
              <tr>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20 min-w-[60px]">
                  COD
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-20 min-w-[200px]">
                  CUENTA
                </th>
                {/* Cuentas bancarias reales desde la base de datos - empiezan desde la tercera columna */}
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

              {/* FILA 4 - TRM */}
              <tr>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20">
                  
                </th>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-20">
                  TRM
                </th>
                {/* Celdas TRM para cuentas bancarias reales - empiezan desde la tercera columna */}
                {bankAccounts.map((account) => (
                  <th key={`trm-${account.id}`} className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
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
                <tr key={conceptoIdx} className={getRowColor(concepto.tipo)}>
                  {/* COLUMNA DE CÓDIGO */}
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-center sticky left-0 z-10 ${getRowColor(concepto.tipo)}`}>
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
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium text-center sticky left-[60px] z-10 ${getRowColor(concepto.tipo)}`}>
                    <span className="text-xs leading-tight">{concepto.nombre}</span>
                  </td>

                  {/* CELDAS DE DATOS - Solo cuentas bancarias reales desde la tercera columna */}
                  {/* Columnas de cuentas bancarias reales */}
                  {bankAccounts.map((account) => (
                    <td
                      key={`data-${account.id}`}
                      className="border border-gray-400 dark:border-gray-500 px-2 py-1 text-center text-xs"
                    >
                      <span className="text-gray-400 dark:text-gray-500">—</span>
                    </td>
                  ))}
                  
                  {/* Columna TOTALES */}
                  <td className="border-2 border-green-400 dark:border-green-500 px-2 py-1 text-center text-xs bg-green-50 dark:bg-green-900/20">
                    {(() => {
                      const total = calculateRowTotal(concepto);
                      return total !== 0 ? (
                        <span className={total < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}>
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
                <td colSpan={3 + bankAccounts.length} 
                    className="bg-gray-300 dark:bg-gray-600 h-2 border border-gray-400 dark:border-gray-500"></td>
              </tr>

              {/* FILA SUBTOTAL MOVIMIENTO BANCARIA */}
              <tr className="bg-green-200 dark:bg-green-800/40 font-bold">
                <td className="bg-green-200 dark:bg-green-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-green-200 dark:bg-green-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-10">
                  SUBTOTAL MOVIMIENTO BANCARIA
                </td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => (
                  <td key={`subtotal-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">—</td>
                ))}
                {/* Columna TOTALES */}
                <td className="border-2 border-green-400 dark:border-green-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white bg-green-100 dark:bg-green-900/30">
                  <span className="text-green-700 dark:text-green-400">19.873.292,53</span>
                </td>
              </tr>

              {/* FILA SUBTOTAL SALDO INICIAL */}
              <tr className="bg-gray-200 dark:bg-gray-700">
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-10">
                  SUBTOTAL SALDO INICIAL PAGADURIA
                </td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => (
                  <td key={`saldo-inicial-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                ))}
                {/* Columna TOTALES */}
                <td className="border-2 border-green-400 dark:border-green-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400 bg-green-50 dark:bg-green-900/20">
                  #REF!
                </td>
              </tr>

              {/* FILA MOVIMIENTO TESORERIA */}
              <tr className="bg-blue-200 dark:bg-blue-800/40 font-bold">
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-10">
                  MOVIMIENTO TESORERIA
                </td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => (
                  <td key={`movimiento-tesoreria-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">—</td>
                ))}
                {/* Columna TOTALES */}
                <td className="border-2 border-green-400 dark:border-green-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white bg-green-100 dark:bg-green-900/30">
                  <span className="text-red-700 dark:text-red-400">(2.390.930,00)</span>
                </td>
              </tr>

              {/* FILA SALDO TOTAL */}
              <tr className="bg-gray-200 dark:bg-gray-700">
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[60px] z-10">
                  SALDO TOTAL EN BANCOS
                </td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => (
                  <td key={`saldo-total-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                ))}
                {/* Columna TOTALES */}
                <td className="border-2 border-green-400 dark:border-green-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400 bg-green-50 dark:bg-green-900/20">
                  #REF!
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

export default DashboardPagaduria;
