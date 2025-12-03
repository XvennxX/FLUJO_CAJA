import React, { useState } from 'react';
import { Calendar, Filter, Download, TrendingUp, TrendingDown, BarChart3, LineChart } from 'lucide-react';
import { 
  LineChart as RechartsLineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { useMonthlyFlow } from '../hooks/useMonthlyFlow';

const MonthlyFlow: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');
  const [selectedDateRange] = useState({
    start: new Date(2025, 0, 1), // 1 enero 2025
    end: new Date(2025, 11, 31)  // 31 diciembre 2025
  });
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>(['CAPITALIZADORA', 'BOLÍVAR', 'COMERCIALES']);
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('line');

  // Usar el hook personalizado
  const { data: chartData, accountsData, metrics, loading, error, exportData } = useMonthlyFlow(selectedPeriod, selectedDateRange);

  const colors = {
    'CAPITALIZADORA': '#22d3ee',
    'BOLÍVAR': '#0ea5e9',
    'COMERCIALES': '#fbbf24'
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-800 dark:text-gray-200 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.dataKey}: {formatCurrency(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {selectedCompanies.map((company) => (
              <Area
                key={company}
                type="monotone"
                dataKey={company}
                stackId="1"
                stroke={colors[company as keyof typeof colors]}
                fill={colors[company as keyof typeof colors]}
                fillOpacity={0.6}
              />
            ))}
          </AreaChart>
        );
      
      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {selectedCompanies.map((company) => (
              <Bar
                key={company}
                dataKey={company}
                fill={colors[company as keyof typeof colors]}
              />
            ))}
          </BarChart>
        );
      
      default:
        return (
          <RechartsLineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {selectedCompanies.map((company) => (
              <Line
                key={company}
                type="monotone"
                dataKey={company}
                stroke={colors[company as keyof typeof colors]}
                strokeWidth={3}
                dot={{ fill: colors[company as keyof typeof colors], strokeWidth: 2, r: 4 }}
              />
            ))}
          </RechartsLineChart>
        );
    }
  };

  const pieData = Object.entries(accountsData).flatMap(([company, accounts]) =>
    Object.entries(accounts).map(([account, data]) => ({
      name: `${company} - ${account.split(' - ')[1]}`,
      value: data.saldo,
      company
    }))
  );

  const totalIngresos = metrics.totalIngresos;
  const totalEgresos = metrics.totalEgresos;
  const totalSaldo = metrics.totalSaldo;

  if (loading) {
    return (
      <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-bolivar-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando datos del flujo...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen flex items-center justify-center">
        <div className="text-center text-red-600">
          <p className="text-lg font-semibold mb-2">Error al cargar los datos</p>
          <p className="text-gray-600 dark:text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-2">Flujo Mensual</h1>
        <p className="text-gray-600 dark:text-gray-400">Análisis de ingresos y gastos por mes</p>
      </div>

      {/* Controles de filtro */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4 items-center">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Período de tiempo</label>
              <div className="flex gap-2">
                {[
                  { value: 'week', label: 'Semanal' },
                  { value: 'month', label: 'Mensual' },
                  { value: 'year', label: 'Anual' }
                ].map((period) => (
                  <button
                    key={period.value}
                    onClick={() => setSelectedPeriod(period.value as 'week' | 'month' | 'year')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      selectedPeriod === period.value
                        ? 'bg-bolivar-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    {period.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tipo de gráfica</label>
              <div className="flex gap-2">
                {[
                  { value: 'line', icon: LineChart, label: 'Línea' },
                  { value: 'area', icon: BarChart3, label: 'Área' },
                  { value: 'bar', icon: BarChart3, label: 'Barras' }
                ].map((type) => (
                  <button
                    key={type.value}
                    onClick={() => setChartType(type.value as 'line' | 'area' | 'bar')}
                    className={`p-2 rounded-lg transition-colors ${
                      chartType === type.value
                        ? 'bg-bolivar-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200'
                    }`}
                    title={type.label}
                  >
                    <type.icon className="w-4 h-4" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <button 
              onClick={() => exportData('csv')}
              className="flex items-center gap-2 px-4 py-2 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors"
            >
              <Download className="w-4 h-4" />
              Exportar
            </button>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Empresas</label>
          <div className="flex gap-4">
            {Object.keys(colors).map((company) => (
              <label key={company} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedCompanies.includes(company)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedCompanies([...selectedCompanies, company]);
                    } else {
                      setSelectedCompanies(selectedCompanies.filter(c => c !== company));
                    }
                  }}
                  className="rounded border-gray-300 dark:border-gray-600"
                />
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: colors[company as keyof typeof colors] }}
                ></div>
                <span className="text-sm text-gray-700 dark:text-gray-300">{company}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Ingresos</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(totalIngresos)}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Egresos</p>
              <p className="text-2xl font-bold text-red-600">{formatCurrency(totalEgresos)}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-full">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Saldo Neto</p>
              <p className={`text-2xl font-bold ${totalSaldo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(totalSaldo)}
              </p>
            </div>
            <div className={`p-3 rounded-full ${totalSaldo >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
              <BarChart3 className={`w-6 h-6 ${totalSaldo >= 0 ? 'text-green-600' : 'text-red-600'}`} />
            </div>
          </div>
        </div>
      </div>

      {/* Gráfica principal */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Flujo de Caja por {selectedPeriod === 'week' ? 'Semana' : selectedPeriod === 'month' ? 'Mes' : 'Trimestre'}
          </h2>
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Calendar className="w-4 h-4" />
            {format(selectedDateRange.start, 'MMM yyyy', { locale: es })} - {format(selectedDateRange.end, 'MMM yyyy', { locale: es })}
          </div>
        </div>
        
        <div style={{ width: '100%', height: '400px' }}>
          <ResponsiveContainer>
            {renderChart()}
          </ResponsiveContainer>
        </div>
      </div>

      {/* Gráficas adicionales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribución por cuentas */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Distribución por Cuentas</h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ percent }) => `${(percent && percent > 5) ? `${(percent * 100).toFixed(0)}%` : ''}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[entry.company as keyof typeof colors]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => [formatCurrency(value), 'Saldo']}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Comparativo Ingresos vs Egresos */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">Ingresos vs Egresos</h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar dataKey="ingresos" fill="#22c55e" name="Ingresos" />
                <Bar dataKey="egresos" fill="#ef4444" name="Egresos" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonthlyFlow;

