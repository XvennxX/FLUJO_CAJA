import React, { useState, useEffect } from 'react';
import { Download, RefreshCw, TrendingUp, BarChart3 } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';
import { informesConsolidadosService, InformeConsolidadoResponse, ResumenMensualResponse } from '../../services/informesConsolidadosService';
import { cuentasMultiMonedaService, InformeMultiMonedaResponse } from '../../services/cuentasMultiMonedaService';

const Reports: React.FC = () => {
  const [añoSeleccionado, setAñoSeleccionado] = useState<number>(new Date().getFullYear());
  const [mesSeleccionado, setMesSeleccionado] = useState<number>(new Date().getMonth() + 1);
  const [informeConsolidado, setInformeConsolidado] = useState<InformeConsolidadoResponse | null>(null);
  const [informeMultiMoneda, setInformeMultiMoneda] = useState<InformeMultiMonedaResponse | null>(null);
  const [resumenMensual, setResumenMensual] = useState<ResumenMensualResponse | null>(null);
  const [cargando, setCargando] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [usarMultiMoneda, setUsarMultiMoneda] = useState<boolean>(true);

  const cargarDatosConsolidados = async () => {
    setCargando(true);
    setError(null);
    
    try {
      console.log(`🔄 Cargando informe consolidado: ${añoSeleccionado}-${mesSeleccionado.toString().padStart(2, '0')}`);
      
      if (usarMultiMoneda) {
        // Usar el nuevo servicio multi-moneda
        const [informeMulti, resumen] = await Promise.all([
          cuentasMultiMonedaService.obtenerInformeConsolidadoMultiMoneda(añoSeleccionado, mesSeleccionado),
          informesConsolidadosService.obtenerResumenMensual(añoSeleccionado, mesSeleccionado)
        ]);
        
        setInformeMultiMoneda(informeMulti);
        setResumenMensual(resumen);
        
        console.log('✅ Datos multi-moneda cargados exitosamente:', informeMulti);
      } else {
        // Usar el servicio consolidado tradicional
        const [informe, resumen] = await Promise.all([
          informesConsolidadosService.obtenerInformeConsolidadoMensual(añoSeleccionado, mesSeleccionado),
          informesConsolidadosService.obtenerResumenMensual(añoSeleccionado, mesSeleccionado)
        ]);
        
        setInformeConsolidado(informe);
        setResumenMensual(resumen);
        
        console.log('✅ Datos consolidados tradicionales cargados exitosamente');
      }
      
    } catch (error) {
      console.error('❌ Error al cargar datos consolidados:', error);
      setError('Error al cargar los datos del informe consolidado');
    } finally {
      setCargando(false);
    }
  };

  // Cargar datos al montar el componente y cuando cambie el período o el modo
  useEffect(() => {
    cargarDatosConsolidados();
  }, [añoSeleccionado, mesSeleccionado, usarMultiMoneda]);

  const obtenerColorFila = (categoria: string, tipo: string, nombre: string): string => {
    // Misma lógica de colores que en DashboardTesoreria
    if (categoria === 'SALDOS') {
      if (nombre.includes('INICIAL')) return 'bg-blue-50 dark:bg-blue-900/20';
      if (nombre.includes('FINAL')) return 'bg-green-50 dark:bg-green-900/20';
    }
    
    if (tipo === 'CALCULADO') return 'bg-yellow-50 dark:bg-yellow-900/20';
    if (categoria === 'INGRESOS') return 'bg-green-50 dark:bg-green-900/20';
    if (categoria === 'GASTOS') return 'bg-red-50 dark:bg-red-900/20';
    
    return 'bg-white dark:bg-gray-800';
  };

  const renderTablaConsolidada = (
    titulo: string, 
    datos: { [conceptoId: number]: { [companiaId: number]: { [cuentaId: number]: number } } },
    conceptos: Array<{ id: number; nombre: string }>
  ) => {
    if (!informeConsolidado) return null;

    const { companias, cuentas } = informeConsolidado.metadata;

    // Verificar si hay datos para mostrar
    const tieneTransacciones = Object.keys(datos).length > 0;
    const totalConceptosConDatos = Object.keys(datos).length;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 bg-gradient-to-r from-bolivar-500 to-bolivar-600">
          <h3 className="text-lg font-semibold text-white">{titulo}</h3>
          <p className="text-bolivar-100 text-sm">
            Consolidado mensual - {informeConsolidado.periodo.nombre_mes}
          </p>
          <p className="text-bolivar-200 text-xs">
            {tieneTransacciones 
              ? `${totalConceptosConDatos} conceptos con datos | ${conceptos.length} conceptos totales`
              : 'Sin transacciones en este período'
            }
          </p>
        </div>
        
        <div className="overflow-x-auto max-h-[600px]">
          <table className="w-full border-collapse text-xs">
            <thead>
              {/* Header de compañías */}
              <tr>
                <th colSpan={3} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[100px]"></th>
                {companias.map((compania) => (
                  <th key={`company-${compania.id}`} className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                    {compania.nombre}
                  </th>
                ))}
                <th className="bg-green-200 dark:bg-green-800 border-2 border-green-400 dark:border-green-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  TOTAL MENSUAL
                </th>
              </tr>
              
              {/* Header de bancos */}
              <tr>
                <th colSpan={3} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[100px]"></th>
                {companias.map((compania) => {
                  const cuentasCompania = cuentas.filter(cuenta => 
                    informeConsolidado.metadata.cuentas.some(c => c.id === cuenta.id)
                  );
                  return (
                    <th key={`bank-${compania.id}`} className="bg-blue-100 dark:bg-blue-900/50 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                      {cuentasCompania.length > 0 ? cuentasCompania[0].banco || 'BANCO' : 'BANCO'}
                    </th>
                  );
                })}
                <th className="bg-green-100 dark:bg-green-900/50 border-2 border-green-400 dark:border-green-500 px-2 py-1 text-gray-800 dark:text-gray-200 font-semibold text-center text-xs">
                  CONSOLIDADO
                </th>
              </tr>
              
              {/* Header de columnas */}
              <tr>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-0 z-20 min-w-[100px]">
                  Concepto
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[100px] z-20 min-w-[60px]">
                  ID
                </th>
                <th className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center sticky left-[160px] z-20 min-w-[200px]">
                  Descripción
                </th>
                {companias.map((compania) => (
                  <th key={compania.id} className="bg-gray-100 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-medium text-center text-xs">
                    ${compania.nombre.substring(0, 10)}...
                  </th>
                ))}
                <th className="bg-green-50 dark:bg-green-900 border-2 border-green-400 dark:border-green-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-bold text-center text-xs">
                  TOTAL MES
                </th>
              </tr>
            </thead>
            
            <tbody>
              {conceptos.length > 0 ? conceptos.map((concepto) => {
                const totalConcepto = informesConsolidadosService.calcularTotalConcepto(datos[concepto.id] || {});
                
                return (
                  <tr key={concepto.id}>
                    <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium sticky left-0 z-10 ${obtenerColorFila('', '', concepto.nombre)}`}>
                      {concepto.nombre.substring(0, 20)}
                    </td>
                    <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-center sticky left-[100px] z-10 ${obtenerColorFila('', '', concepto.nombre)}`}>
                      <span className="bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 px-1 py-0.5 rounded text-xs font-mono">
                        {concepto.id}
                      </span>
                    </td>
                    <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium text-center sticky left-[160px] z-20 min-w-[100px] ${obtenerColorFila('', '', concepto.nombre)}`}>
                      {concepto.nombre}
                    </td>
                    
                    {/* Columnas por compañía */}
                    {companias.map((compania) => {
                      const montoCompania = informesConsolidadosService.calcularTotalCompania(
                        { [concepto.id]: datos[concepto.id] || {} }, 
                        compania.id
                      );
                      
                      return (
                        <td key={compania.id} className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs">
                          <span className={`font-semibold ${informesConsolidadosService.obtenerColorMonto(montoCompania)}`}>
                            {montoCompania !== 0 ? informesConsolidadosService.formatearMoneda(montoCompania) : '—'}
                          </span>
                        </td>
                      );
                    })}
                    
                    {/* Columna total */}
                    <td className="bg-green-50 dark:bg-green-900 border-2 border-green-400 dark:border-green-500 px-1 py-1 text-center text-xs">
                      <span className={`font-bold ${informesConsolidadosService.obtenerColorMonto(totalConcepto)}`}>
                        {totalConcepto !== 0 ? informesConsolidadosService.formatearMoneda(totalConcepto) : '—'}
                      </span>
                    </td>
                  </tr>
                );
              }) : (
                <tr>
                  <td colSpan={companias.length + 4} className="border border-gray-400 dark:border-gray-500 px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    <div className="flex flex-col items-center space-y-2">
                      <p className="text-lg font-medium">Sin conceptos configurados</p>
                      <p className="text-sm">No hay conceptos definidos para esta área</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderTablaMultiMoneda = (
    titulo: string, 
    datos: any,
    conceptos: Array<{ id: number; nombre: string }>
  ) => {
    if (!informeMultiMoneda) return null;

    const { companias } = informeMultiMoneda.metadata;

    // Determinar qué monedas tiene cada compañía
    const monedasPorCompania: { [companiaId: number]: Set<string> } = {};
    informeMultiMoneda.cuentas_expandidas.forEach(cuenta => {
      if (!monedasPorCompania[cuenta.compania_id]) {
        monedasPorCompania[cuenta.compania_id] = new Set();
      }
      monedasPorCompania[cuenta.compania_id].add(cuenta.moneda);
    });

    // Crear columnas de compañía-moneda
    const columnasCompaniaMoneda: Array<{companiaId: number, moneda: string, companiaNombre: string}> = [];
    companias.forEach(compania => {
      const monedas = monedasPorCompania[compania.id] || new Set(['COP']);
      Array.from(monedas).sort().forEach(moneda => {
        columnasCompaniaMoneda.push({
          companiaId: compania.id,
          moneda: moneda,
          companiaNombre: compania.nombre
        });
      });
    });

    // Verificar si hay datos
    const tieneTransacciones = Object.keys(datos).length > 0;
    const totalConceptosConDatos = Object.keys(datos).length;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 bg-gradient-to-r from-bolivar-500 to-bolivar-600">
          <h3 className="text-lg font-semibold text-white">{titulo} - Multi-Moneda</h3>
          <p className="text-bolivar-100 text-sm">
            Consolidado mensual - {informeMultiMoneda.periodo.nombre_mes}
          </p>
          <p className="text-bolivar-200 text-xs">
            {tieneTransacciones 
              ? `${totalConceptosConDatos} conceptos con datos | TRM: ${cuentasMultiMonedaService.formatearMonto(informeMultiMoneda.conversion.trm_promedio, 'COP')}`
              : 'Sin transacciones en este período'
            }
          </p>
        </div>
        
        <div className="overflow-x-auto max-h-[600px]">
          <table className="w-full border-collapse text-xs">
            <thead>
              {/* Header de compañías-moneda */}
              <tr>
                <th colSpan={3} className="bg-white dark:bg-gray-800 border border-gray-400 dark:border-gray-500 sticky left-0 z-20 min-w-[100px]"></th>
                {columnasCompaniaMoneda.map((columna) => (
                  <th key={`company-${columna.companiaId}-${columna.moneda}`} 
                      className="bg-blue-200 dark:bg-blue-800 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                    <div className="flex flex-col">
                      <span className="text-sm">{columna.companiaNombre}</span>
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        columna.moneda === 'USD' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
                      }`}>
                        {columna.moneda}
                      </span>
                    </div>
                  </th>
                ))}
                <th className="bg-green-200 dark:bg-green-800 border-2 border-green-400 dark:border-green-500 px-2 py-1 text-gray-900 dark:text-white font-bold text-center min-w-[120px]">
                  TOTAL MENSUAL
                </th>
              </tr>
              
              {/* Header secundario */}
              <tr>
                <th className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold sticky left-0 z-20 text-xs">
                  CONCEPTO
                </th>
                <th className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-900 dark:text-white font-bold sticky left-[100px] z-20 text-xs">
                  ID
                </th>
                <th className="bg-gray-200 dark:bg-gray-700 border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-bold sticky left-[140px] z-20 text-xs">
                  DESCRIPCIÓN
                </th>
                
                {columnasCompaniaMoneda.map((columna) => (
                  <th key={`header-${columna.companiaId}-${columna.moneda}`} 
                      className="bg-blue-100 dark:bg-blue-900 border border-gray-400 dark:border-gray-500 px-1 py-1 text-gray-900 dark:text-white font-bold text-center text-xs">
                    {columna.companiaNombre.substring(0, 10)}... ({columna.moneda})
                  </th>
                ))}
                
                <th className="bg-green-50 dark:bg-green-900 border-2 border-green-400 dark:border-green-500 px-1 py-1 text-gray-700 dark:text-gray-300 font-bold text-center text-xs">
                  TOTAL MES
                </th>
              </tr>
            </thead>
            
            <tbody>
              {conceptos.length > 0 ? conceptos.map((concepto) => {
                // Calcular total del concepto sumando todos los montos en COP
                let totalConcepto = 0;
                const datosConcepto = datos[concepto.id] || {};
                
                Object.keys(datosConcepto).forEach(companiaIdStr => {
                  Object.keys(datosConcepto[companiaIdStr] || {}).forEach(cuentaMonedaId => {
                    const datoCuenta = datosConcepto[companiaIdStr][cuentaMonedaId];
                    if (datoCuenta && datoCuenta.monto_cop) {
                      totalConcepto += datoCuenta.monto_cop;
                    }
                  });
                });
                
                return (
                  <tr key={concepto.id}>
                    <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium sticky left-0 z-10 ${obtenerColorFila('', '', concepto.nombre)}`}>
                      {concepto.nombre.substring(0, 20)}
                    </td>
                    <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-center sticky left-[100px] z-10 ${obtenerColorFila('', '', concepto.nombre)}`}>
                      <span className="bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 px-1 py-0.5 rounded text-xs font-mono">
                        {concepto.id}
                      </span>
                    </td>
                    <td className={`border border-gray-400 dark:border-gray-500 px-2 py-1 text-gray-900 dark:text-white font-medium text-center sticky left-[140px] z-20 min-w-[100px] ${obtenerColorFila('', '', concepto.nombre)}`}>
                      {concepto.nombre}
                    </td>
                    
                    {/* Columnas por compañía-moneda */}
                    {columnasCompaniaMoneda.map((columna) => {
                      // Calcular el total de esta compañía en esta moneda para este concepto
                      let montoCompaniaMoneda = 0;
                      const datosCompania = datosConcepto[columna.companiaId] || {};
                      
                      // Sumar todas las cuentas de esta compañía que sean de esta moneda
                      Object.keys(datosCompania).forEach(cuentaMonedaId => {
                        const cuenta = informeMultiMoneda.cuentas_expandidas.find(c => 
                          c.cuenta_moneda_id === cuentaMonedaId && 
                          c.compania_id === columna.companiaId && 
                          c.moneda === columna.moneda
                        );
                        
                        if (cuenta) {
                          const datoCuenta = datosCompania[cuentaMonedaId];
                          if (datoCuenta && datoCuenta.monto_original) {
                            montoCompaniaMoneda += datoCuenta.monto_original;
                          }
                        }
                      });
                      
                      return (
                        <td key={`${concepto.id}-${columna.companiaId}-${columna.moneda}`} 
                            className="border border-gray-400 dark:border-gray-500 px-1 py-1 text-center text-xs">
                          <span className={`font-semibold ${informesConsolidadosService.obtenerColorMonto(montoCompaniaMoneda)}`}>
                            {montoCompaniaMoneda !== 0 ? cuentasMultiMonedaService.formatearMonto(montoCompaniaMoneda, columna.moneda) : '—'}
                          </span>
                        </td>
                      );
                    })}
                    
                    {/* Columna total */}
                    <td className="bg-green-50 dark:bg-green-900 border-2 border-green-400 dark:border-green-500 px-1 py-1 text-center text-xs">
                      <span className={`font-bold ${informesConsolidadosService.obtenerColorMonto(totalConcepto)}`}>
                        {totalConcepto !== 0 ? cuentasMultiMonedaService.formatearMonto(totalConcepto, 'COP') : '—'}
                      </span>
                    </td>
                  </tr>
                );
              }) : (
                <tr>
                  <td colSpan={columnasCompaniaMoneda.length + 4} className="border border-gray-400 dark:border-gray-500 px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                    <div className="flex flex-col items-center space-y-2">
                      <p className="text-lg font-medium">Sin conceptos configurados</p>
                      <p className="text-sm">No hay conceptos definidos para esta área</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Informes Consolidados Mensuales</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Consolidado de todas las compañías y cuentas por mes
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {/* Selector de Año */}
            <select
              value={añoSeleccionado}
              onChange={(e) => setAñoSeleccionado(parseInt(e.target.value))}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {[2024, 2025, 2026].map(año => (
                <option key={año} value={año}>{año}</option>
              ))}
            </select>
            
            {/* Selector de Mes */}
            <select
              value={mesSeleccionado}
              onChange={(e) => setMesSeleccionado(parseInt(e.target.value))}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {[
                { valor: 1, nombre: 'Enero' },
                { valor: 2, nombre: 'Febrero' },
                { valor: 3, nombre: 'Marzo' },
                { valor: 4, nombre: 'Abril' },
                { valor: 5, nombre: 'Mayo' },
                { valor: 6, nombre: 'Junio' },
                { valor: 7, nombre: 'Julio' },
                { valor: 8, nombre: 'Agosto' },
                { valor: 9, nombre: 'Septiembre' },
                { valor: 10, nombre: 'Octubre' },
                { valor: 11, nombre: 'Noviembre' },
                { valor: 12, nombre: 'Diciembre' }
              ].map(mes => (
                <option key={mes.valor} value={mes.valor}>{mes.nombre}</option>
              ))}
            </select>
            
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

            <button 
              onClick={cargarDatosConsolidados}
              disabled={cargando}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${cargando ? 'animate-spin' : ''}`} />
              <span>Actualizar</span>
            </button>
            
            <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-bolivar-500 to-bolivar-600 text-white rounded-lg hover:from-bolivar-600 hover:to-bolivar-700 transition-all">
              <Download className="h-4 w-4" />
              <span>Exportar</span>
            </button>
          </div>
        </div>
      </div>

      {/* Estado de carga y errores */}
      {cargando && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-8 text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-bolivar-500" />
          <p className="text-gray-600 dark:text-gray-400">Cargando informe consolidado...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
          <p className="text-red-700 dark:text-red-300 font-medium">{error}</p>
        </div>
      )}

      {/* Key Metrics */}
      {resumenMensual && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-gradient-to-r from-green-500 to-green-600">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Ingresos Mensual</p>
              <p className="text-xl font-bold text-green-600">
                {formatCurrency(resumenMensual.metricas.total_ingresos)}
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-gradient-to-r from-red-500 to-rose-500">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Gastos Mensual</p>
              <p className="text-xl font-bold text-red-600">
                {formatCurrency(resumenMensual.metricas.total_gastos)}
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Balance Neto</p>
              <p className={`text-xl font-bold ${resumenMensual.metricas.balance_neto >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(resumenMensual.metricas.balance_neto)}
              </p>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-lg bg-gradient-to-r from-bolivar-600 to-bolivar-700">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Transacciones</p>
              <p className="text-xl font-bold text-bolivar-600">{resumenMensual.metricas.total_transacciones}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tablas Consolidadas */}
      {((usarMultiMoneda && informeMultiMoneda) || (!usarMultiMoneda && informeConsolidado)) && !cargando && (
        <div className="space-y-8">
          {/* Dashboard Tesorería Consolidado */}
          <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-t-xl p-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl">
              {usarMultiMoneda && informeMultiMoneda ? 
                renderTablaMultiMoneda(
                  '💰 Dashboard Tesorería',
                  informeMultiMoneda.datos.tesoreria,
                  informeMultiMoneda.metadata.conceptos_tesoreria
                )
                :
                informeConsolidado && renderTablaConsolidada(
                  '💰 Dashboard Tesorería - Consolidado Mensual',
                  informeConsolidado.datos.tesoreria,
                  informeConsolidado.metadata.conceptos_tesoreria
                )
              }
            </div>
          </div>
          
          {/* Dashboard Pagaduría Consolidado */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-t-xl p-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl">
              {usarMultiMoneda && informeMultiMoneda ? 
                renderTablaMultiMoneda(
                  '👥 Dashboard Pagaduría',
                  informeMultiMoneda.datos.pagaduria,
                  informeMultiMoneda.metadata.conceptos_pagaduria
                )
                :
                informeConsolidado && renderTablaConsolidada(
                  '👥 Dashboard Pagaduría - Consolidado Mensual',
                  informeConsolidado.datos.pagaduria,
                  informeConsolidado.metadata.conceptos_pagaduria
                )
              }
            </div>
          </div>

          {/* Resumen de Totales */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              📊 Resumen Consolidado Mensual {usarMultiMoneda ? '(Multi-Moneda)' : ''}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-green-600 mb-2">Tesorería</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Conceptos: {usarMultiMoneda && informeMultiMoneda 
                    ? informeMultiMoneda.metadata.conceptos_tesoreria.length 
                    : informeConsolidado?.metadata.conceptos_tesoreria.length || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Total configurado: ID 1-51
                </p>
                {usarMultiMoneda && informeMultiMoneda && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Cuentas expandidas: {informeMultiMoneda.metadata.cuentas_expandidas}
                  </p>
                )}
              </div>
              <div>
                <h4 className="font-semibold text-blue-600 mb-2">Pagaduría</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Conceptos: {usarMultiMoneda && informeMultiMoneda 
                    ? informeMultiMoneda.metadata.conceptos_pagaduria.length 
                    : informeConsolidado?.metadata.conceptos_pagaduria.length || 0}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Total configurado: ID 52+
                </p>
                {usarMultiMoneda && informeMultiMoneda && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    TRM promedio: {cuentasMultiMonedaService.formatearMonto(informeMultiMoneda.conversion.trm_promedio, 'COP')}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;

