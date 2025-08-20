import React, { useState, useEffect } from 'react';
import { Building2, Download, RefreshCw } from 'lucide-react';
import DatePicker from '../Calendar/DatePicker';
import { useAuth } from '../../contexts/AuthContext';
import { formatCurrency } from '../../utils/formatters';

interface Concepto {
  categoria: string;
  codigo: string;
  nombre: string;
  tipo: string;
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
  const [selectedMonth, setSelectedMonth] = useState<string>('2025-05');
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  
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

  // Conceptos exactos del Excel con los códigos correctos
  const conceptos: Concepto[] = [
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
  ];

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

  // Función para calcular el total de una fila
  const calculateRowTotal = (concepto: Concepto) => {
    let total = 0;
    
    // Valores basados en el Excel proporcionado
    if (concepto.nombre === 'SALDO INICIAL') {
      total += -7647.80; // CAPITALIZADORA
      total += -10696649.83; // BOLIVAR  
      total += 4499667.48; // COMERCIALES
    } else if (concepto.nombre === 'INCREMENTO DE CAPITAL ENCARGOS') {
      total += -4000.00; // CAPITALIZADORA
      total += -4670000.00; // BOLIVAR
      total += -12300000.00; // COMERCIALES
    } else if (concepto.nombre === 'CONSUMO') {
      // Valores de consumo si los hay
      total += 0; // Por ahora 0
    } else if (concepto.nombre === 'VENTANILLA') {
      // Valores de ventanilla si los hay
      total += 0; // Por ahora 0
    } else if (concepto.nombre === 'SALDO NETO INICIAL PAGADURÍA') {
      // Este sería la suma de los anteriores de pagaduría
      total += 0; // Por ahora 0
    }
    
    // Agregar valores de conceptos de renta fija, renta variable, etc.
    // Por ahora estos valores están en 0, pero se pueden agregar según el Excel real
    
    return total;
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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Panel de Tesoreria</h1>
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
                <th colSpan={3} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[100px]"></th>
                {/* Primeras 3 compañías fijas de ejemplo */}
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  CAPITALIZADORA
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  BOLIVAR
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  COMERCIALES
                </th>
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
                {/* Primeros 3 bancos fijos de ejemplo */}
                <th className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  BANCO DAVIVIENDA
                </th>
                <th className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  BANCO DAVIVIENDA
                </th>
                <th className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  BANCO DAVIVIENDA
                </th>
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
                {/* Primeras 3 columnas fijas de ejemplo */}
                <th className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  482800001257
                </th>
                <th className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  482800001273
                </th>
                <th className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                  482800002024
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

                  {/* CELDAS DE DATOS - Primeras 3 columnas fijas + Cuentas bancarias reales */}
                  {/* Primeras 3 columnas fijas de ejemplo */}
                  {[
                    'CAPITALIZADORA', 'BOLIVAR', 'COMERCIALES'
                  ].map((companiaNombre, compIdx) => {
                    // Datos de ejemplo basados en el Excel
                    let valor = null;
                    if (concepto.nombre === 'SALDO INICIAL' && companiaNombre === 'CAPITALIZADORA') valor = -7647.80;
                    else if (concepto.nombre === 'SALDO INICIAL' && companiaNombre === 'BOLIVAR') valor = -10696649.83;
                    else if (concepto.nombre === 'SALDO INICIAL' && companiaNombre === 'COMERCIALES') valor = 4499667.48;
                    else if (concepto.nombre === 'INCREMENTO DE CAPITAL ENCARGOS' && companiaNombre === 'CAPITALIZADORA') valor = -4000.00;
                    else if (concepto.nombre === 'INCREMENTO DE CAPITAL ENCARGOS' && companiaNombre === 'BOLIVAR') valor = -4670000.00;
                    else if (concepto.nombre === 'INCREMENTO DE CAPITAL ENCARGOS' && companiaNombre === 'COMERCIALES') valor = -12300000.00;

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
                <td colSpan={7 + bankAccounts.length} 
                    className="bg-gray-300 dark:bg-gray-600 h-2 border border-gray-400 dark:border-gray-500"></td>
              </tr>

              {/* FILA SUBTOTAL TESORERÍA */}
              <tr className="bg-blue-200 dark:bg-blue-800/40 font-bold">
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-0 z-20 min-w-[100px]"></td>
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-[100px] z-20 min-w-[60px]"></td>
                <td className="bg-blue-200 dark:bg-blue-800/40 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[160px] z-20 min-w-[60px]">
                  SUB-TOTAL TESORERÍA
                </td>
                {/* Primeras 3 columnas fijas */}
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">-4.000,00</td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">-4.674.268,98</td>
                <td className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">-12.300.000,00</td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => (
                  <td key={`subtotal-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white">—</td>
                ))}
                {/* Columna TOTALES */}
                <td className="border-2 border-green-400 dark:border-green-500 px-2 py-2 text-center font-bold text-gray-900 dark:text-white bg-green-100 dark:bg-green-900/30">
                  <span className="text-red-700 dark:text-red-400">(16.978.268,98)</span>
                </td>
              </tr>

              {/* FILA SALDO FINAL CUENTAS */}
              <tr className="bg-gray-200 dark:bg-gray-700">
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-0 z-20 min-w-[100px]"></td>
                 <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-center sticky left-0 z-10 sticky left-[100px] z-20 min-w-[60px]"></td>
                <td className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-2 text-gray-900 dark:text-white font-bold text-center sticky left-[160px] z-20 min-w-[200px]">
                  SALDO FINAL CUENTAS
                </td>
                {/* Primeras 3 columnas fijas */}
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                <td className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
                {/* Columnas de cuentas bancarias reales */}
                {bankAccounts.map((account) => (
                  <td key={`saldo-final-${account.id}`} className="border border-gray-400 dark:border-gray-500 px-1 py-2 text-center text-xs text-red-600 dark:text-red-400">#REF!</td>
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

export default DashboardTesoreria;
