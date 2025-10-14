import React, { useState, useEffect } from 'react';
import { Calendar, RefreshCw, AlertCircle, Maximize2, Minimize2, X } from 'lucide-react';
import { informesConsolidadosService, InformeConsolidadoResponse } from '../../services/informesConsolidadosService';

const Reports: React.FC = () => {
  const [mes, setMes] = useState<number>(new Date().getMonth() + 1);
  const [año, setAño] = useState<number>(new Date().getFullYear());
  const [cargando, setCargando] = useState<boolean>(false);
  const [informeConsolidado, setInformeConsolidado] = useState<InformeConsolidadoResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [dashboardExpandido, setDashboardExpandido] = useState<string | null>(null);

  const meses = [
    { value: 1, label: 'Enero' }, { value: 2, label: 'Febrero' }, { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' }, { value: 5, label: 'Mayo' }, { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' }, { value: 8, label: 'Agosto' }, { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' }, { value: 11, label: 'Noviembre' }, { value: 12, label: 'Diciembre' }
  ];

  const años = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - 2 + i);

  // Columnas específicas para Tesorería
  const columnasTesoreria = [
    { empresa: 'CAPITALIZADORA', moneda: 'COP', acronimo: 'CAP' },
    { empresa: 'SEGUROS BOLÍVAR', moneda: 'COP', acronimo: 'BOL' },
    { empresa: 'COMERCIALES', moneda: 'COP', acronimo: 'CLS' },
    { empresa: 'GRUPO BOLÍVAR', moneda: 'COP', acronimo: 'SOC' },
    { empresa: 'OTRAS', moneda: 'COP', acronimo: 'OTRAS' },
    { empresa: 'CAPITALIZADORA', moneda: 'USD', acronimo: 'CAP US$' },
    { empresa: 'CAPITALIZADORA', moneda: 'COP', acronimo: 'CAP PESOS' },
    { empresa: 'SEGUROS BOLÍVAR', moneda: 'USD', acronimo: 'BOL US$' },
    { empresa: 'SEGUROS BOLÍVAR', moneda: 'COP', acronimo: 'BOL PESOS' },
    { empresa: 'COMERCIALES', moneda: 'USD', acronimo: 'CLS US$' },
    { empresa: 'COMERCIALES', moneda: 'COP', acronimo: 'CLS PESOS' },
    { empresa: 'SEGUROS BOLÍVAR', moneda: 'COP', acronimo: 'BOL REASEG', tipo: 'REASEGUROS' },
    { empresa: 'COMERCIALES', moneda: 'COP', acronimo: 'CLS REASEG', tipo: 'REASEGUROS' }
  ];

  // Columnas específicas para Pagaduría (orden correcto según especificación)
  const columnasPagaduria = [
    { empresa: 'CAPITALIZADORA', moneda: 'COP', acronimo: 'CAP COP' },           // 0
    { empresa: 'SEGUROS BOLÍVAR', moneda: 'COP', acronimo: 'BOL COP' },          // 1  
    { empresa: 'COMERCIALES', moneda: 'COP', acronimo: 'CLS COP' },              // 2
    { empresa: 'GRUPO BOLÍVAR', moneda: 'COP', acronimo: 'SOC COP' },            // 3
    { empresa: 'OTRAS', moneda: 'COP', acronimo: 'OTRAS COP' },                  // 4
    { empresa: 'CAPITALIZADORA', moneda: 'USD', acronimo: 'CAP USD' },           // 5
    { empresa: 'SEGUROS BOLÍVAR REASEGUROS', moneda: 'USD', acronimo: 'BOL RE USD' }, // 6
    { empresa: 'SEGUROS BOLÍVAR REASEGUROS', moneda: 'COP', acronimo: 'BOL RE COP' }, // 7
    { empresa: 'COMERCIALES', moneda: 'USD', acronimo: 'CLS USD' },              // 8
    { empresa: 'COMERCIALES', moneda: 'COP', acronimo: 'CLS COP (USD)' },        // 9
    { empresa: 'FUND', moneda: 'COP', acronimo: 'FUND COP', tipo: 'SPECIAL' }    // 10
  ];

  // Seleccionar columnas según el área
  const columnasEspecificas = dashboardExpandido === 'tesoreria' ? columnasTesoreria : 
                             dashboardExpandido === 'pagaduria' ? columnasPagaduria : 
                             columnasTesoreria; // Por defecto Tesorería

  const cargarDatos = async () => {
    setCargando(true);
    setError('');
    
    try {
      const response = await informesConsolidadosService.obtenerInformeConsolidadoMensual(año, mes);
      console.log('📊 Estructura del informe consolidado:', response);
      console.log('📊 Datos tesorería:', response.datos?.tesoreria);
      console.log('📊 Datos pagaduría:', response.datos?.pagaduria);
      setInformeConsolidado(response);
    } catch (err) {
      console.error('Error al cargar datos:', err);
      setError('Error al cargar los datos del informe');
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, [mes, año]);

  const formatearMonto = (monto: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(monto);
  };

  // Función helper para formatear período sin duplicación
  const formatearPeriodo = (nombreMes: string, año: number): string => {
    const añoStr = año.toString();
    // Si el nombre del mes ya incluye el año, solo retornar el nombre del mes
    if (nombreMes.includes(añoStr)) {
      return nombreMes;
    }
    // Si no, concatenar mes y año
    return `${nombreMes} ${año}`;
  };

  // Mapeo de cuentas bancarias por columna para Tesorería
  const cuentasPorColumnaTesoreria = {
    'CAPITALIZADORA_COP': [1,4,8,29,34,38,42,45,57,60,63,66,49],
    'SEGUROS_BOLIVAR_COP': [2,5,9,30,35,39,43,46,58,61,64,67,70,6,31,40,50,52,53,54,72,73,74,75,76,77,78,79],
    'COMERCIALES_COP': [3,7,10,32,36,41,44,47,59,62,65,68,69,71,51,56],
    'GRUPO_BOLIVAR_COP': [20,23,33,48,37],
    'OTRAS_COP': [21,22,24,25,26,27,28],
    'CAPITALIZADORA_USD': [11,17],
    'SEGUROS_BOLIVAR_USD': [12,18,15],
    'COMERCIALES_USD': [13,19,16],
    'BOL_REASEGUROS': [55],
    'CLS_REASEGUROS': [56]
  };

  // Mapeo de cuentas bancarias por columna para Pagaduría
  const cuentasPorColumnaPagaduria = {
    'CAPITALIZADORA_COP': [1,4,8,29,34,38,42,45,57,60,63,66,49],
    'SEGUROS_BOLIVAR_COP': [2,5,9,30,35,39,43,46,58,61,64,67,70,6,31,40,50,52,53,54,72,73,74,75,76,77,78,79],
    'COMERCIALES_COP_PAG': [3,7,10,32,36,41,44,47,59,62,65,68,69,71,51,56],
    'GRUPO_BOLIVAR_COP': [20,23,33,48,37],
    'OTRAS_COP': [21,22,24,25,26,27,28],
    'CAPITALIZADORA_USD': [11,17],
    'SEGUROS_BOLIVAR_REASEGUROS_USD': [55],
    'SEGUROS_BOLIVAR_REASEGUROS_COP': [55], // Mismo valor que USD pero convertido
    'COMERCIALES_USD': [56],
    'COMERCIALES_COP_CONVERSION': [56], // Mismo valor que USD pero convertido
    'FUND_CUENTAS_EXTRA': [11,12,18,17,13,19] // Cuentas adicionales para FUND
  };



  // Función para calcular el monto de una columna específica
  // Función para calcular el monto de una celda específica para un dashboard específico
  const calcularMontoCeldaParaDashboard = (conceptoId: number, columnaIndex: number, tipoDashboard: string): number => {
    if (!informeConsolidado) {
      console.log('❌ No hay informe consolidado');
      return 0;
    }
    
    const esTesoreria = conceptoId <= 51;
    const esPagaduria = conceptoId >= 52;
    
    // Si es Tesorería y estamos en dashboard de Pagaduría, o viceversa, retornar 0
    if ((esTesoreria && tipoDashboard === 'pagaduria') || (esPagaduria && tipoDashboard === 'tesoreria')) {
      return 0;
    }
    
    // Seleccionar columnas según el tipo de dashboard
    const columnas = tipoDashboard === 'tesoreria' ? columnasTesoreria : columnasPagaduria;
    const columna = columnas[columnaIndex];
    
    if (!columna) {
      console.log('❌ No se encontró la columna', columnaIndex);
      return 0;
    }
    
    // Lógica específica para Pagaduría
    if (esPagaduria && tipoDashboard === 'pagaduria') {
      return calcularMontoPagaduria(conceptoId, columnaIndex, columna);
    }
    
    // Lógica específica para Tesorería
    if (esTesoreria && tipoDashboard === 'tesoreria') {
      return calcularMontoTesoreria(conceptoId, columnaIndex, columna);
    }
    
    return 0;
  };

  // Función para calcular el monto de una celda específica (mantener compatibilidad)
  const calcularMontoCelda = (conceptoId: number, columnaIndex: number): number => {
    if (!informeConsolidado) {
      console.log('❌ No hay informe consolidado');
      return 0;
    }
    
    const esTesoreria = conceptoId <= 51;
    const esPagaduria = conceptoId >= 52;
    
    // Si es Tesorería y estamos en dashboard de Pagaduría, o viceversa, retornar 0
    if ((esTesoreria && dashboardExpandido === 'pagaduria') || (esPagaduria && dashboardExpandido === 'tesoreria')) {
      return 0;
    }
    
    const columna = columnasEspecificas[columnaIndex];
    if (!columna) {
      console.log('❌ No se encontró la columna', columnaIndex);
      return 0;
    }
    
    // Lógica específica para Pagaduría
    if (esPagaduria && dashboardExpandido === 'pagaduria') {
      return calcularMontoPagaduria(conceptoId, columnaIndex, columna);
    }
    
    // Lógica específica para Tesorería
    if (esTesoreria && (dashboardExpandido === 'tesoreria' || !dashboardExpandido)) {
      return calcularMontoTesoreria(conceptoId, columnaIndex, columna);
    }
    
    return 0;
  };

  // Función específica para cálculos de Tesorería
  const calcularMontoTesoreria = (conceptoId: number, columnaIndex: number, columna: any): number => {
    let cuentasTarget: number[] = [];
    let esConversionUSD = false;
    
    // Determinar qué cuentas usar según la columna para Tesorería
    switch (columnaIndex) {
      case 0: // CAPITALIZADORA COP
        cuentasTarget = cuentasPorColumnaTesoreria.CAPITALIZADORA_COP;
        break;
      case 1: // SEGUROS BOLÍVAR COP
        cuentasTarget = cuentasPorColumnaTesoreria.SEGUROS_BOLIVAR_COP;
        break;
      case 2: // COMERCIALES COP
        cuentasTarget = cuentasPorColumnaTesoreria.COMERCIALES_COP;
        break;
      case 3: // GRUPO BOLÍVAR COP
        cuentasTarget = cuentasPorColumnaTesoreria.GRUPO_BOLIVAR_COP;
        break;
      case 4: // OTRAS COP
        cuentasTarget = cuentasPorColumnaTesoreria.OTRAS_COP;
        break;
      case 5: // CAPITALIZADORA USD
        cuentasTarget = cuentasPorColumnaTesoreria.CAPITALIZADORA_USD;
        break;
      case 6: // CAPITALIZADORA COP (de USD)
        cuentasTarget = cuentasPorColumnaTesoreria.CAPITALIZADORA_USD;
        esConversionUSD = true;
        break;
      case 7: // SEGUROS BOLÍVAR USD
        cuentasTarget = cuentasPorColumnaTesoreria.SEGUROS_BOLIVAR_USD;
        break;
      case 8: // SEGUROS BOLÍVAR COP (de USD)
        cuentasTarget = cuentasPorColumnaTesoreria.SEGUROS_BOLIVAR_USD;
        esConversionUSD = true;
        break;
      case 9: // COMERCIALES USD
        cuentasTarget = cuentasPorColumnaTesoreria.COMERCIALES_USD;
        break;
      case 10: // COMERCIALES COP (de USD)
        cuentasTarget = cuentasPorColumnaTesoreria.COMERCIALES_USD;
        esConversionUSD = true;
        break;
      case 11: // BOL REASEGUROS
        cuentasTarget = cuentasPorColumnaTesoreria.BOL_REASEGUROS;
        break;
      case 12: // CLS REASEGUROS
        cuentasTarget = cuentasPorColumnaTesoreria.CLS_REASEGUROS;
        break;
      default:
        return 0;
    }
    
    return calcularMontoBasico(conceptoId, cuentasTarget, esConversionUSD, columna);
  };

  // Función específica para cálculos de Pagaduría
  const calcularMontoPagaduria = (conceptoId: number, columnaIndex: number, columna: any): number => {
    // Casos específicos según el orden correcto para Pagaduría
    switch (columnaIndex) {
      case 0: // CAPITALIZADORA (COP) - cuentas: 1,4,8,29,34,38,42,45,57,60,63,66,49
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.CAPITALIZADORA_COP, false, columna);
      case 1: // SEGUROS BOLÍVAR (COP) - cuentas: 2,5,9,30,35,39,43,46,58,61,64,67,70,6,31,40,50,52,53,54,72,73,74,75,76,77,78,79
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.SEGUROS_BOLIVAR_COP, false, columna);
      case 2: // COMERCIALES (COP) - cuentas: 3,7,10,32,36,41,44,47,59,62,65,68,69,71,51,56
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.COMERCIALES_COP_PAG, false, columna);
      case 3: // GRUPO BOLÍVAR (COP) - cuentas: 20,23,33,48,37
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.GRUPO_BOLIVAR_COP, false, columna);
      case 4: // OTRAS (COP) - cuentas: 21,22,24,25,26,27,28
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.OTRAS_COP, false, columna);
      case 5: // CAPITALIZADORA (USD) - cuentas: 11,17
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.CAPITALIZADORA_USD, false, columna);
      case 6: // SEGUROS BOLÍVAR REASEGUROS (USD) - cuenta: 55
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.SEGUROS_BOLIVAR_REASEGUROS_USD, false, columna);
      case 7: // SEGUROS BOLÍVAR REASEGUROS (COP) - cuenta: 55 convertida a COP
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.SEGUROS_BOLIVAR_REASEGUROS_COP, true, columna);
      case 8: // COMERCIALES (USD) - cuenta: 56
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.COMERCIALES_USD, false, columna);
      case 9: // COMERCIALES (COP) - cuenta: 56 convertida a COP
        return calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.COMERCIALES_COP_CONVERSION, true, columna);
      case 10: // FUND (COP) - suma especial
        return calcularMontoFund(conceptoId);
      default:
        return 0;
    }
  };

  // Función para calcular FUND (suma de columnas específicas + cuentas extra)
  const calcularMontoFund = (conceptoId: number): number => {
    if (!informeConsolidado) return 0;
    
    let montoFund = 0;
    
    // Sumar las columnas específicas para FUND:
    // SEGUROS BOLIVAR REASEGUROS (COP) - columna 7
    montoFund += calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.SEGUROS_BOLIVAR_REASEGUROS_COP, true, { moneda: 'COP' });
    // OTRAS (COP) - columna 4
    montoFund += calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.OTRAS_COP, false, { moneda: 'COP' });
    // GRUPO BOLIVAR (COP) - columna 3
    montoFund += calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.GRUPO_BOLIVAR_COP, false, { moneda: 'COP' });
    // COMERCIALES (COP) - columna 2
    montoFund += calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.COMERCIALES_COP_PAG, false, { moneda: 'COP' });
    // SEGUROS BOLIVAR (COP) - columna 1
    montoFund += calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.SEGUROS_BOLIVAR_COP, false, { moneda: 'COP' });
    // CAPITALIZADORA (COP) - columna 0
    montoFund += calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.CAPITALIZADORA_COP, false, { moneda: 'COP' });
    
    // Agregar las cuentas extra
    montoFund += calcularMontoBasico(conceptoId, cuentasPorColumnaPagaduria.FUND_CUENTAS_EXTRA, false, { moneda: 'COP' });
    
    return montoFund;
  };

  // Función básica para calcular montos basada en cuentas
  const calcularMontoBasico = (conceptoId: number, cuentasTarget: number[], esConversionUSD: boolean, columna: any): number => {
    if (!informeConsolidado) return 0;
    
    console.log(`🔍 Calculando concepto ${conceptoId}, cuentas:`, cuentasTarget);
    
    let montoTotal = 0;
    
    // Buscar en los datos del informe consolidado
    const datosArea = conceptoId <= 51 ? 
      informeConsolidado?.datos?.tesoreria : 
      informeConsolidado?.datos?.pagaduria;
    
    console.log(`📂 Área de datos (${conceptoId <= 51 ? 'tesorería' : 'pagaduría'}):`, datosArea);
    
    if (!datosArea) {
      console.log('❌ No hay datos para el área');
      return 0;
    }
    
    const datosConcepto = datosArea[conceptoId];
    console.log(`📋 Datos del concepto ${conceptoId}:`, datosConcepto);
    
    if (!datosConcepto) {
      console.log(`❌ No hay datos para el concepto ${conceptoId}`);
      return 0;
    }
    
    // Si datosConcepto es un número simple, lo devolvemos directamente
    if (typeof datosConcepto === 'number') {
      console.log(`💰 Monto directo encontrado: ${datosConcepto}`);
      return datosConcepto;
    }
    
    // Recorrer todas las compañías
    Object.keys(datosConcepto).forEach(companiaIdStr => {
      const companiaData = (datosConcepto as any)[companiaIdStr];
      console.log(`🏢 Procesando compañía ${companiaIdStr}:`, companiaData);
      
      if (!companiaData) return;
      
      // Si companiaData es un número, usarlo directamente
      if (typeof companiaData === 'number') {
        montoTotal += companiaData;
        console.log(`💰 Agregado monto directo de compañía: ${companiaData}, total: ${montoTotal}`);
        return;
      }
      
      // Recorrer todas las cuentas de la compañía
      Object.keys(companiaData).forEach(cuentaId => {
        const cuentaNumero = parseInt(cuentaId.split('_')[0] || cuentaId);
        console.log(`🏦 Procesando cuenta ${cuentaId} (número: ${cuentaNumero})`);
        
        // Verificar si esta cuenta está en nuestro grupo objetivo
        if (cuentasTarget.includes(cuentaNumero)) {
          const cuentaData = companiaData[cuentaId];
          console.log(`✅ Cuenta ${cuentaNumero} encontrada en objetivo:`, cuentaData);
          
          let montoAUsar = 0;
          
          if (typeof cuentaData === 'number') {
            montoAUsar = cuentaData;
          } else if (esConversionUSD && cuentaData?.monto) {
            // Para columnas USD convertidas a COP, usar el monto ya convertido
            montoAUsar = cuentaData.monto;
          } else if (!esConversionUSD && cuentaData?.monto_original && columna.moneda === 'USD') {
            // Para columnas USD puras, usar monto original
            montoAUsar = cuentaData.monto_original;
          } else if (cuentaData?.monto) {
            // Para columnas COP normales
            montoAUsar = cuentaData.monto;
          }
          
          montoTotal += montoAUsar;
          console.log(`💰 Agregado: ${montoAUsar}, total acumulado: ${montoTotal}`);
        } else {
          console.log(`⏭️ Cuenta ${cuentaNumero} no está en el objetivo`);
        }
      });
    });
    
    console.log(`🎉 Monto total final para concepto ${conceptoId}: ${montoTotal}`);
    return montoTotal;
  };

  const renderDashboard = (
    titulo: string,
    icono: string,
    conceptos: Array<{ id: number; nombre: string; activo?: boolean }>,
    dashboardId: string
  ) => {
    if (!informeConsolidado) return null;

    // Seleccionar las columnas correctas según el tipo de dashboard
    const columnasDashboard = dashboardId === 'tesoreria' ? columnasTesoreria : columnasPagaduria;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        {/* Header del Dashboard mejorado */}
        <div className="bg-gradient-to-r from-bolivar-600 via-bolivar-500 to-bolivar-600 relative overflow-hidden">
          {/* Patrón de fondo decorativo */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 left-0 w-32 h-32 bg-white rounded-full -translate-x-16 -translate-y-16"></div>
            <div className="absolute bottom-0 right-0 w-24 h-24 bg-white rounded-full translate-x-12 translate-y-12"></div>
          </div>
          
          <div className="relative p-6">
            <div className="flex items-center justify-between">
              {/* Información principal */}
              <div className="flex items-start gap-4">
                <div className="bg-white/20 rounded-xl p-3 backdrop-blur-sm">
                  <span className="text-3xl">{icono}</span>
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">
                    {titulo}
                  </h2>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2 text-bolivar-100">
                      <Calendar className="w-4 h-4" />
                      <span className="font-medium">
                        Período: {formatearPeriodo(informeConsolidado.periodo.nombre_mes, informeConsolidado.periodo.año)}
                      </span>
                    </div>
                    <div className="h-4 w-px bg-white/30"></div>
                    <div className="flex items-center gap-2 text-bolivar-100">
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                      <span className="text-xs font-medium">
                        {columnasDashboard.length} Columnas de Análisis
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Estadísticas y controles */}
              <div className="flex items-center gap-6">
                {/* Estadísticas de conceptos */}
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-3 min-w-[140px]">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">{conceptos.length}</div>
                    <div className="text-xs text-bolivar-100 mb-2">Conceptos</div>
                    <div className="flex justify-center gap-3 text-xs">
                      <div className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                        <span className="text-green-200 font-medium">
                          {conceptos.filter(c => c.activo !== false).length}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-red-400 rounded-full"></span>
                        <span className="text-red-200 font-medium">
                          {conceptos.filter(c => c.activo === false).length}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>



                {/* Botón de expansión mejorado */}
                <button
                  onClick={() => setDashboardExpandido(dashboardExpandido === dashboardId ? null : dashboardId)}
                  className="group relative bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-xl p-3 transition-all duration-300 hover:scale-105"
                  title={dashboardExpandido === dashboardId ? "Contraer dashboard" : "Expandir dashboard a pantalla completa"}
                >
                  <div className="relative z-10">
                    {dashboardExpandido === dashboardId ? (
                      <Minimize2 className="w-5 h-5 text-white group-hover:scale-110 transition-transform" />
                    ) : (
                      <Maximize2 className="w-5 h-5 text-white group-hover:scale-110 transition-transform" />
                    )}
                  </div>
                  <div className="absolute inset-0 bg-white/20 rounded-xl scale-0 group-hover:scale-100 transition-transform duration-200"></div>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Tabla del Dashboard con altura fija y scroll */}
        <div className={`overflow-auto border-t border-gray-200 dark:border-gray-600 scrollbar-thin scrollbar-thumb-bolivar-400 scrollbar-track-gray-200 hover:scrollbar-thumb-bolivar-500 ${conceptos.length > 8 ? 'max-h-[450px]' : 'max-h-fit'}`}>
          <table className="w-full border-collapse">
            <thead className="sticky top-0 z-30">
              {/* Header con las columnas específicas */}
              <tr className="bg-gray-50 dark:bg-gray-700 shadow-sm">
                <th className="sticky left-0 z-40 bg-gray-50 dark:bg-gray-700 border-r-2 border-gray-300 dark:border-gray-600 px-3 py-2 text-left text-xs font-bold text-gray-900 dark:text-white uppercase tracking-wider min-w-[200px]">
                  CONCEPTO
                </th>
                {columnasDashboard.map((columna, index) => (
                  <th key={index} className="bg-gray-50 dark:bg-gray-700 px-2 py-2 text-center border-l border-gray-200 dark:border-gray-600 min-w-[110px]">
                    <div className="flex flex-col items-center gap-1">
                      <span className="text-[10px] font-bold text-gray-800 dark:text-gray-200 leading-tight text-center uppercase tracking-wide">
                        {columna.empresa}
                      </span>
                      {columna.tipo && (
                        <span className="text-[8px] font-medium text-gray-600 dark:text-gray-400 uppercase">
                          {columna.tipo}
                        </span>
                      )}
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold shadow-sm border ${
                        columna.moneda === 'USD' ? 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/40 dark:text-green-300 dark:border-green-600' : 
                        columna.moneda === 'EUR' ? 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-600' :
                        'bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-900/40 dark:text-orange-300 dark:border-orange-600'
                      }`}>
                        {columna.moneda}
                      </span>
                    </div>
                  </th>
                ))}
                <th className="bg-green-50 dark:bg-green-900/20 px-4 py-3 text-center text-xs font-bold text-green-700 dark:text-green-400 uppercase tracking-wider border-l-2 border-green-300 dark:border-green-600">
                  Total
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {conceptos.map((concepto, index) => {
                const isEven = index % 2 === 0;
                const rowBg = isEven ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-750';
                
                // Calcular montos por columna según el área
                const montosPorColumna = columnasDashboard.map((_, colIndex) => 
                  calcularMontoCeldaParaDashboard(concepto.id, colIndex, dashboardId)
                );
                
                // Calcular total del concepto sumando todas las columnas
                const totalConcepto = montosPorColumna.reduce((sum, monto) => sum + monto, 0);

                return (
                  <tr key={concepto.id} className={`${rowBg} hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors`}>
                    <td className={`sticky left-0 z-10 ${rowBg} border-r-2 border-gray-300 dark:border-gray-600 px-3 py-2 min-w-[200px]`}>
                      <div className="flex items-center">
                        <div className={`w-1.5 h-1.5 rounded-full mr-2 ${concepto.activo !== false ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span className="text-xs font-medium text-gray-900 dark:text-white">
                          {concepto.nombre}
                        </span>
                      </div>
                    </td>
                    {columnasDashboard.map((columna, colIndex) => {
                      // Usar la lógica específica para este dashboard
                      const monto = calcularMontoCeldaParaDashboard(concepto.id, colIndex, dashboardId);
                      
                      return (
                        <td key={colIndex} className="px-2 py-2 text-center text-xs border-l border-gray-200 dark:border-gray-600 min-w-[110px]">
                          <span className={`font-semibold ${
                            monto > 0 ? 'text-green-600 dark:text-green-400' :
                            monto < 0 ? 'text-red-600 dark:text-red-400' :
                            'text-gray-500 dark:text-gray-400'
                          }`}>
                            {monto !== 0 ? (
                              columna.moneda === 'USD' ? 
                                `$${monto.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}` :
                              columna.moneda === 'EUR' ? 
                                `€${monto.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}` :
                                `$${monto.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
                            ) : '—'}
                          </span>
                        </td>
                      );
                    })}
                    <td className="px-4 py-3 text-center bg-green-50 dark:bg-green-900/20 border-l-2 border-green-300 dark:border-green-600">
                      <span className="text-sm font-bold text-green-700 dark:text-green-400">
                        {totalConcepto !== 0 ? formatearMonto(totalConcepto) : '—'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Footer del Dashboard */}
        <div className="px-4 py-2 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          <div className="flex justify-between items-center text-xs">
            <div className="flex items-center gap-3">
              <span className="text-gray-600 dark:text-gray-400">
                📋 Total de registros: <span className="font-semibold">{conceptos.length}</span>
              </span>
              {conceptos.length > 10 && (
                <span className="text-[10px] text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded">
                  ↕️ Desplázate para ver más
                </span>
              )}
            </div>
            <span className="text-gray-600 dark:text-gray-400">
              📅 {formatearPeriodo(informeConsolidado.periodo.nombre_mes, informeConsolidado.periodo.año)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  // Si hay un dashboard expandido, renderizar solo ese dashboard en pantalla completa
  if (dashboardExpandido && informeConsolidado) {
    const esTesoreria = dashboardExpandido === 'tesoreria';
    const conceptosExpandidos = esTesoreria 
      ? informeConsolidado.metadata.conceptos_tesoreria 
      : informeConsolidado.metadata.conceptos_pagaduria;
    
    return (
      <div className="fixed inset-0 z-50 bg-gray-900/95 backdrop-blur-sm">
        <div className="h-screen flex flex-col">
          {/* Header funcional de pantalla completa */}
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-bolivar-600 to-bolivar-700 shadow-lg">
            <div className="flex items-center gap-4">
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  <span>{esTesoreria ? '🏦' : '👥'}</span>
                  {esTesoreria ? 'Dashboard Tesorería' : 'Dashboard Pagaduría'}
                </h1>
                <p className="text-bolivar-100 text-sm">
                  {formatearPeriodo(informeConsolidado.periodo.nombre_mes, informeConsolidado.periodo.año)} - Vista Expandida
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Controles funcionales */}
              <div className="flex items-center gap-2 text-bolivar-100 text-sm">
                <Calendar className="w-4 h-4" />
                <select
                  value={mes}
                  onChange={(e) => setMes(Number(e.target.value))}
                  className="px-2 py-1 rounded bg-white/20 text-white border border-white/30 focus:ring-2 focus:ring-white/50 focus:border-transparent text-sm"
                >
                  {meses.map(m => (
                    <option key={m.value} value={m.value} className="text-gray-900">{m.label}</option>
                  ))}
                </select>
                
                <select
                  value={año}
                  onChange={(e) => setAño(Number(e.target.value))}
                  className="px-2 py-1 rounded bg-white/20 text-white border border-white/30 focus:ring-2 focus:ring-white/50 focus:border-transparent text-sm"
                >
                  {años.map(a => (
                    <option key={a} value={a} className="text-gray-900">{a}</option>
                  ))}
                </select>
              </div>
              
              <button
                onClick={cargarDatos}
                disabled={cargando}
                className="px-3 py-1 bg-white/20 hover:bg-white/30 text-white rounded transition-colors duration-200 text-sm flex items-center gap-1"
              >
                <RefreshCw className={`w-3 h-3 ${cargando ? 'animate-spin' : ''}`} />
                {cargando ? 'Cargando...' : 'Actualizar'}
              </button>
              
              <button
                onClick={() => setDashboardExpandido(null)}
                className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 transition-colors duration-200 group"
                title="Cerrar pantalla completa"
              >
                <X className="w-5 h-5 text-white group-hover:scale-110 transition-transform" />
              </button>
            </div>
          </div>
          
          {/* Dashboard expandido con altura completa */}
          <div className="flex-1 overflow-hidden p-6">
            <div className="h-full bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              {/* Header del dashboard interno */}
              <div className="p-4 bg-gradient-to-r from-bolivar-500 to-bolivar-600 border-b border-bolivar-400">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                      <span>{esTesoreria ? '🏦' : '👥'}</span>
                      {esTesoreria ? 'Dashboard Tesorería' : 'Dashboard Pagaduría'}
                    </h2>
                    <p className="text-bolivar-100 text-sm mt-1">
                      Análisis Detallado - {informeConsolidado.periodo.nombre_mes} {informeConsolidado.periodo.año}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-bolivar-100 text-sm">
                      Total Conceptos: {conceptosExpandidos.length}
                    </p>
                    <p className="text-bolivar-200 text-xs">
                      Activos: {conceptosExpandidos.filter(c => (c as any).activo !== false).length}
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Tabla expandida con altura completa */}
              <div className="h-[calc(100%-120px)] overflow-auto">
                <table className="w-full border-collapse">
                  <thead className="sticky top-0 z-30">
                    <tr className="bg-gray-50 dark:bg-gray-700 shadow-sm">
                      <th className="sticky left-0 z-40 bg-gray-50 dark:bg-gray-700 border-r-2 border-gray-300 dark:border-gray-600 px-4 py-3 text-left text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider min-w-[250px]">
                        CONCEPTO
                      </th>
                      {columnasEspecificas.map((columna, index) => (
                        <th key={index} className="bg-gray-50 dark:bg-gray-700 px-4 py-3 text-center border-l border-gray-200 dark:border-gray-600 min-w-[140px]">
                          <div className="flex flex-col items-center gap-2">
                            <span className="text-xs font-bold text-gray-800 dark:text-gray-200 leading-tight text-center uppercase tracking-wide">
                              {columna.empresa}
                            </span>
                            {columna.tipo && (
                              <span className="text-[10px] font-medium text-gray-600 dark:text-gray-400 uppercase">
                                {columna.tipo}
                              </span>
                            )}
                            <span className={`px-3 py-1 rounded-full text-xs font-bold shadow-sm border ${
                              columna.moneda === 'USD' ? 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/40 dark:text-green-300 dark:border-green-600' : 
                              columna.moneda === 'EUR' ? 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-600' :
                              'bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-900/40 dark:text-orange-300 dark:border-orange-600'
                            }`}>
                              {columna.moneda}
                            </span>
                          </div>
                        </th>
                      ))}
                      <th className="bg-green-50 dark:bg-green-900/20 px-4 py-3 text-center text-sm font-bold text-green-700 dark:text-green-400 uppercase tracking-wider border-l-2 border-green-300 dark:border-green-600 min-w-[120px]">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {conceptosExpandidos.map((concepto, index) => {
                      const isEven = index % 2 === 0;
                      const rowBg = isEven ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-750';
                      
                      // Calcular montos por columna para la vista expandida
                      const montosPorColumna = columnasEspecificas.map((_, colIndex) => 
                        calcularMontoCelda(concepto.id, colIndex)
                      );
                      
                      // Calcular total del concepto sumando todas las columnas
                      const totalConcepto = montosPorColumna.reduce((sum, monto) => sum + monto, 0);

                      return (
                        <tr key={concepto.id} className={`${rowBg} hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors`}>
                          <td className={`sticky left-0 z-10 ${rowBg} border-r-2 border-gray-300 dark:border-gray-600 px-4 py-3 min-w-[250px]`}>
                            <div className="flex items-center">
                              <div className={`w-2 h-2 rounded-full mr-3 ${(concepto as any).activo !== false ? 'bg-green-500' : 'bg-red-500'}`}></div>
                              <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {concepto.nombre}
                              </span>
                            </div>
                          </td>
                          {columnasEspecificas.map((columna, colIndex) => {
                            const monto = montosPorColumna[colIndex];
                            return (
                              <td key={colIndex} className="px-4 py-3 text-center text-sm border-l border-gray-200 dark:border-gray-600 min-w-[140px]">
                                <span className={`font-semibold ${
                                  monto > 0 ? 'text-green-600 dark:text-green-400' :
                                  monto < 0 ? 'text-red-600 dark:text-red-400' :
                                  'text-gray-500 dark:text-gray-400'
                                }`}>
                                  {monto !== 0 ? (
                                    columna.moneda === 'USD' ? 
                                      `$${monto.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}` :
                                    columna.moneda === 'EUR' ? 
                                      `€${monto.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}` :
                                      `$${monto.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
                                  ) : '—'}
                                </span>
                              </td>
                            );
                          })}
                          <td className="px-4 py-3 text-center bg-green-50 dark:bg-green-900/20 border-l-2 border-green-300 dark:border-green-600">
                            <span className="text-sm font-bold text-green-700 dark:text-green-400">
                              {totalConcepto !== 0 ? formatearMonto(totalConcepto) : '—'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Principal */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                📊 Consolidado
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Análisis consolidado por conceptos de Tesorería y Pagaduría
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-500" />
                <select
                  value={mes}
                  onChange={(e) => setMes(Number(e.target.value))}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {meses.map(m => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
                
                <select
                  value={año}
                  onChange={(e) => setAño(Number(e.target.value))}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {años.map(a => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>
              
              <button
                onClick={cargarDatos}
                disabled={cargando}
                className="inline-flex items-center px-4 py-2 bg-bolivar-600 text-white rounded-lg hover:bg-bolivar-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${cargando ? 'animate-spin' : ''}`} />
                {cargando ? 'Cargando...' : 'Actualizar'}
              </button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <p className="text-red-700 dark:text-red-300">{error}</p>
            </div>
          </div>
        )}

        {/* Loading */}
        {cargando && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-bolivar-600"></div>
            <span className="ml-2 text-gray-600 dark:text-gray-400">Cargando datos...</span>
          </div>
        )}

        {/* Dashboards */}
        {!cargando && informeConsolidado && (
          <div className="space-y-8">
            {/* Dashboard Tesorería */}
            {renderDashboard(
              'Dashboard Tesorería',
              '🏦',
              informeConsolidado.metadata.conceptos_tesoreria,
              'tesoreria'
            )}

            {/* Dashboard Pagaduría */}
            {renderDashboard(
              'Dashboard Pagaduría',
              '👥',
              informeConsolidado.metadata.conceptos_pagaduria,
              'pagaduria'
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;