import React, { useState } from 'react';
import { Building2, Download, RefreshCw } from 'lucide-react';
import DatePicker from '../Calendar/DatePicker';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency } from '../../utils/formatters';

const DashboardPagaduria: React.FC = () => {
  const { user } = useAuth();
  const [selectedMonth, setSelectedMonth] = useState<string>('2025-05');

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

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center space-x-3">
          <Building2 className="h-8 w-8 text-bolivar-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Panel de Pagaduría</h1>
            <p className="text-gray-600 dark:text-gray-400">Flujo de caja por compañías - {user?.name}</p>
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
                <th colSpan={2} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500"></th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  CAPITALIZADORA
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  BOLIVAR
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  COMERCIALES
                </th>
              </tr>

              {/* FILA 2 - BANCOS */}
              <tr>
                <th colSpan={2} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500"></th>
                <th className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  BANCO DAVIVIENDA
                </th>
                <th className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  BANCO DAVIVIENDA
                </th>
                <th className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  BANCO DAVIVIENDA
                </th>
              </tr>

              {/* FILA 3 - COD, CUENTA y NÚMEROS DE CUENTA */}
              <tr>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20 min-w-[60px]">
                  COD
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[200px]">
                  CUENTA
                </th>
                <th className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  000659999420
                </th>
                <th className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  000659999412
                </th>
                <th className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  000659999404
                </th>
              </tr>

              {/* FILA 4 - TRM */}
              <tr>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20">
                  
                </th>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center">
                  TRM
                </th>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  
                </th>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  
                </th>
                <th className="bg-gray-50 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  
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
                  <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium text-center ${getRowColor(concepto.tipo)}`}>
                    <span className="text-xs leading-tight">{concepto.nombre}</span>
                  </td>

                  {/* CELDAS DE DATOS - Solo las 3 compañías principales */}
                  {['CAPITALIZADORA', 'BOLIVAR', 'COMERCIALES'].map((companiaNombre, compIdx) => {
                    // Datos de ejemplo para algunas celdas específicas
                    let valor = null;
                    if (concepto.nombre === 'INGRESO' && companiaNombre === 'CAPITALIZADORA') valor = 19500.00;
                    else if (concepto.nombre === 'INGRESO' && companiaNombre === 'BOLIVAR') valor = 18869144.37;
                    else if (concepto.nombre === 'INGRESO' && companiaNombre === 'COMERCIALES') valor = 8249535.88;
                    else if (concepto.nombre === 'CONSUMO NACIONAL' && companiaNombre === 'BOLIVAR') valor = -182539.64;
                    else if (concepto.nombre === 'CONSUMO NACIONAL' && companiaNombre === 'COMERCIALES') valor = -2385.68;
                    else if (concepto.nombre === 'RECAUDOS LIBERTADOR' && companiaNombre === 'COMERCIALES') valor = 148715.11;
                    else if (concepto.nombre === 'EMBARGOS' && companiaNombre === 'BOLIVAR') valor = -51577.82;
                    else if (concepto.nombre === 'OTROS PAGOS' && companiaNombre === 'CAPITALIZADORA') valor = -189.03;
                    else if (concepto.nombre === 'OTROS PAGOS' && companiaNombre === 'BOLIVAR') valor = -106690.93;
                    else if (concepto.nombre === 'OTROS PAGOS' && companiaNombre === 'COMERCIALES') valor = -41626.75;
                    else if (concepto.nombre === 'VENTAN PROVEEDORES' && companiaNombre === 'CAPITALIZADORA') valor = -1494.26;
                    else if (concepto.nombre === 'VENTAN PROVEEDORES' && companiaNombre === 'BOLIVAR') valor = -1960138.88;
                    else if (concepto.nombre === 'VENTAN PROVEEDORES' && companiaNombre === 'COMERCIALES') valor = -5064601.19;
                    else if (concepto.nombre === 'NOMINA ADMINISTRATIVA' && companiaNombre === 'BOLIVAR') valor = 142.35;

                    return (
                      <td
                        key={compIdx}
                        className="border border-gray-400 dark:border-gray-500 px-2 py-1 text-center text-xs"
                      >
                        {valor !== null ? (
                          <span className={valor < 0 ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}>
                            {valor < 0 ? `(${formatCurrency(Math.abs(valor))})` : formatCurrency(valor)}
                          </span>
                        ) : (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}

              {/* SEPARADOR */}
              <tr>
                <td colSpan={5} 
                    className="bg-gray-300 dark:bg-gray-600 h-2 border border-gray-400 dark:border-gray-500"></td>
              </tr>

              {/* FILA SUBTOTAL MOVIMIENTO BANCARIA */}
              <tr className="bg-green-200 dark:bg-green-800/40 font-bold">
                <td className="bg-green-200 dark:bg-green-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-green-200 dark:bg-green-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center">
                  SUBTOTAL MOVIMIENTO BANCARIA
                </td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">17.816,70</td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">16.568.339,46</td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">3.287.136,37</td>
              </tr>

              {/* FILA SUBTOTAL SALDO INICIAL */}
              <tr className="bg-gray-200 dark:bg-gray-700">
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center">
                  SUBTOTAL SALDO INICIAL PAGADURIA
                </td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
              </tr>

              {/* FILA MOVIMIENTO TESORERIA */}
              <tr className="bg-blue-200 dark:bg-blue-800/40 font-bold">
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center">
                  MOVIMIENTO TESORERIA
                </td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-red-700 dark:text-red-400">(7.500,00)</td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-red-700 dark:text-red-400">(1.164.430,00)</td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-red-700 dark:text-red-400">(1.219.000,00)</td>
              </tr>

              {/* FILA SALDO TOTAL */}
              <tr className="bg-gray-200 dark:bg-gray-700">
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10"></td>
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center">
                  SALDO TOTAL EN BANCOS
                </td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Resumen inferior igual al Excel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div className="bg-gray-200 dark:bg-gray-700 border-2 border-gray-400 dark:border-gray-500 rounded p-4">
          <div className="text-center">
            <div className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-1">Mov pagaduría +Mov tesorería</div>
            <div className="text-xl font-bold text-gray-900 dark:text-white">10.316,70</div>
          </div>
        </div>
        
        <div className="bg-gray-200 dark:bg-gray-700 border-2 border-gray-400 dark:border-gray-500 rounded p-4">
          <div className="text-center">
            <div className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-1">Total centralizadora</div>
            <div className="text-xl font-bold text-gray-900 dark:text-white">$ 10.316,70</div>
          </div>
        </div>
        
        <div className="bg-gray-200 dark:bg-gray-700 border-2 border-gray-400 dark:border-gray-500 rounded p-4">
          <div className="text-center">
            <div className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-1">Diferencia</div>
            <div className="text-xl font-bold text-gray-900 dark:text-white">0,00</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPagaduria;
