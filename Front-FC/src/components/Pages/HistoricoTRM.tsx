import React, { useState, useEffect } from 'react';
import { Calendar, Download, RefreshCw, TrendingUp, TrendingDown, Minus, Search, Filter } from 'lucide-react';
import { useTRM } from '../../hooks/useTRM';

interface TRMHistorico {
  fecha: string;
  valor: number;
  fecha_creacion: string;
}

const HistoricoTRM: React.FC = () => {
  const { trm: currentTRM } = useTRM();
  const [trmData, setTrmData] = useState<TRMHistorico[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMonth, setSelectedMonth] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<string>(new Date().getFullYear().toString());
  const [dateRange] = useState<{start: string, end: string}>({
    start: '',
    end: ''
  });

  // Construye una serie continua día a día entre start y end, rellenando con la última TRM conocida
  const buildContinuousSeries = (
    rows: TRMHistorico[],
    start?: string,
    end?: string
  ): TRMHistorico[] => {
    if (!rows || rows.length === 0) return [];
    // Parseo que respeta la fecha sin conversión de zona horaria
    const parse = (s: string) => {
      const [y, m, d] = s.split('-').map(Number);
      return new Date(y, m - 1, d);
    };
    const fmt = (d: Date) => {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${y}-${m}-${day}`;
    };

    // Ordenar ascendente por fecha para construir hacia adelante
    const sortedAsc = [...rows].sort((a, b) => (a.fecha > b.fecha ? 1 : a.fecha < b.fecha ? -1 : 0));
    const minDate = parse(sortedAsc[0].fecha);
    const maxDate = parse(sortedAsc[sortedAsc.length - 1].fecha);
    const startDate = start ? parse(start) : minDate;
    const endDate = end ? parse(end) : maxDate;

    // Crear mapa rápido por fecha
    const map = new Map<string, TRMHistorico>();
    for (const r of rows) map.set(r.fecha, r);

    const outAsc: TRMHistorico[] = [];
    let lastKnown: TRMHistorico | null = null;
    // Recorremos de start a end (ascendente) y luego invertimos para presentar descendente
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      const key = fmt(d);
      const hit = map.get(key);
      if (hit) {
        outAsc.push(hit);
        lastKnown = hit;
      } else if (lastKnown) {
        outAsc.push({ fecha: key, valor: lastKnown.valor, fecha_creacion: new Date().toISOString() });
      }
    }
    return outAsc.reverse();
  };

  // Función para obtener el rango de TRM
  const fetchTRMData = async () => {
    try {
      setLoading(true);
      
      let startDate = dateRange.start;
      let endDate = dateRange.end;
      const today = new Date().toISOString().split('T')[0];
      
      // Si se selecciona mes/año específico, calcular rango
      if (selectedMonth && selectedYear) {
        const year = parseInt(selectedYear);
        const month = parseInt(selectedMonth);
        startDate = `${year}-${month.toString().padStart(2, '0')}-01`;
        const lastDay = new Date(year, month, 0).getDate();
        endDate = `${year}-${month.toString().padStart(2, '0')}-${lastDay}`;
      }
      
      // Usar fetch directo como el hook lo hace internamente
      const token = localStorage.getItem('access_token');
      const timestamp = new Date().getTime();
      let url = `http://localhost:8000/api/v1/trm/range?limit=100&_t=${timestamp}`;
      
      if (startDate) {
        url += `&fecha_inicio=${startDate}`;
      }
      
      // Siempre traer hasta hoy si no hay fin explícito
      url += `&fecha_fin=${endDate || today}`;
      
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      };
      
      const response = await fetch(url, { headers });
      if (!response.ok) {
        throw new Error('Error al obtener rango de TRM');
      }
      
      const data: TRMHistorico[] = await response.json();
      // Densificar serie para mostrar días faltantes con última TRM conocida
      const continuous = buildContinuousSeries(
        data,
        startDate || undefined,
        (endDate || today)
      );
      setTrmData(continuous);
    } catch (err) {
      console.error('Error fetching TRM data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTRMData();
  }, [selectedMonth, selectedYear, dateRange]);

  // Si cambia la TRM actual (p. ej. después de una verificación/backfill), refrescar el histórico
  useEffect(() => {
    if (currentTRM?.fecha) {
      fetchTRMData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTRM?.fecha]);

  // Filtrar datos por término de búsqueda
  const filteredData = trmData.filter(item => {
    const searchLower = searchTerm.toLowerCase();
    const [y, m, d] = item.fecha.split('-').map(Number);
    const dateStr = new Date(y, m - 1, d).toLocaleDateString('es-CO');
    return (
      item.fecha.includes(searchLower) ||
      item.valor.toString().includes(searchLower) ||
      dateStr.includes(searchLower)
    );
  });

  // Calcular estadísticas
  const stats = {
    total: filteredData.length,
    promedio: filteredData.length > 0 ? filteredData.reduce((sum, item) => sum + item.valor, 0) / filteredData.length : 0,
    maximo: filteredData.length > 0 ? Math.max(...filteredData.map(item => item.valor)) : 0,
    minimo: filteredData.length > 0 ? Math.min(...filteredData.map(item => item.valor)) : 0
  };

  // Función para obtener la tendencia
  const getTrend = (current: number, previous: number) => {
    if (current > previous) return { icon: TrendingUp, color: 'text-green-600', text: 'Subió' };
    if (current < previous) return { icon: TrendingDown, color: 'text-red-600', text: 'Bajó' };
    return { icon: Minus, color: 'text-gray-600', text: 'Igual' };
  };

  // Función para exportar a CSV
  const exportToCSV = () => {
    const headers = ['Fecha Vigencia', 'Valor TRM', 'Fecha Creación'];
    const csvData = [
      headers.join(','),
      ...filteredData.map(item => {
        const [y, m, d] = item.fecha.split('-').map(Number);
        const fechaFormateada = new Date(y, m - 1, d).toLocaleDateString('es-CO');
        return [
          fechaFormateada,
          item.valor.toString(),
          new Date(item.fecha_creacion).toLocaleDateString('es-CO')
        ].join(',');
      })
    ].join('\\n');

    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `historico_trm_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Generar opciones de años (últimos 5 años)
  const yearOptions = Array.from({ length: 5 }, (_, i) => {
    const year = new Date().getFullYear() - i;
    return year.toString();
  });

  const monthOptions = [
    { value: '', label: 'Todos los meses' },
    { value: '1', label: 'Enero' },
    { value: '2', label: 'Febrero' },
    { value: '3', label: 'Marzo' },
    { value: '4', label: 'Abril' },
    { value: '5', label: 'Mayo' },
    { value: '6', label: 'Junio' },
    { value: '7', label: 'Julio' },
    { value: '8', label: 'Agosto' },
    { value: '9', label: 'Septiembre' },
    { value: '10', label: 'Octubre' },
    { value: '11', label: 'Noviembre' },
    { value: '12', label: 'Diciembre' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando histórico de TRM...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Histórico de TRM
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Consulta el histórico de la Tasa Representativa del Mercado
          </p>
        </div>
        <div className="flex items-center space-x-3 mt-4 sm:mt-0">
          <button
            onClick={fetchTRMData}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Actualizar</span>
          </button>
          <button
            onClick={exportToCSV}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Exportar</span>
          </button>
        </div>
      </div>

      {/* TRM Actual */}
      {currentTRM && (
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">TRM Actual</h3>
              <p className="text-blue-100">Última tasa registrada</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">
                ${currentTRM.valor.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="text-blue-100">
                {new Date(currentTRM.fecha).toLocaleDateString('es-CO', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Registros</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Promedio</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${stats.promedio.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Máximo</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${stats.maximo.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
              <TrendingDown className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Mínimo</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${stats.minimo.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Buscar
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar por fecha o valor..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Año
            </label>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {yearOptions.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Mes
            </label>
            <select
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {monthOptions.map(month => (
                <option key={month.value} value={month.value}>{month.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Rango personalizado
            </label>
            <button
              onClick={() => {
                setSelectedMonth('');
                setSelectedYear(new Date().getFullYear().toString());
              }}
              className="w-full px-3 py-2 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-500 transition-colors flex items-center justify-center space-x-2"
            >
              <Filter className="w-4 h-4" />
              <span>Limpiar</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabla de histórico */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Fecha Vigencia
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Valor TRM
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Tendencia
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Variación
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Fecha Registro
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredData.map((item, index) => {
                const previousValue = index < filteredData.length - 1 ? filteredData[index + 1].valor : item.valor;
                const trend = getTrend(item.valor, previousValue);
                const variation = item.valor - previousValue;
                const variationPercent = previousValue !== 0 ? (variation / previousValue) * 100 : 0;

                return (
                  <tr key={item.fecha} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {(() => {
                              const [y, m, d] = item.fecha.split('-').map(Number);
                              return new Date(y, m - 1, d).toLocaleDateString('es-CO');
                            })()}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {(() => {
                              const [y, m, d] = item.fecha.split('-').map(Number);
                              return new Date(y, m - 1, d).toLocaleDateString('es-CO', { weekday: 'long' });
                            })()}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-gray-900 dark:text-white">
                        ${item.valor.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`flex items-center ${trend.color}`}>
                        <trend.icon className="w-4 h-4 mr-1" />
                        <span className="text-sm font-medium">{trend.text}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {variation !== 0 && (
                        <div className={`text-sm ${variation > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                          <div className="font-medium">
                            {variation > 0 ? '+' : ''}${Math.abs(variation).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </div>
                          <div className="text-xs">
                            ({variation > 0 ? '+' : ''}{variationPercent.toFixed(2)}%)
                          </div>
                        </div>
                      )}
                      {variation === 0 && (
                        <span className="text-sm text-gray-500 dark:text-gray-400">Sin cambio</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(item.fecha_creacion).toLocaleDateString('es-CO', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          
          {filteredData.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 dark:text-gray-500 text-lg mb-2">
                No se encontraron registros de TRM
              </div>
              <p className="text-gray-500 dark:text-gray-400">
                {searchTerm || selectedMonth 
                  ? 'Intenta ajustar los filtros de búsqueda'
                  : 'No hay datos disponibles para mostrar'
                }
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoricoTRM;