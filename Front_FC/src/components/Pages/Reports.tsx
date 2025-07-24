import React, { useMemo } from 'react';
import { BarChart3, PieChart, TrendingUp, Download, Calendar } from 'lucide-react';
import { useCashFlow } from '../../hooks/useCashFlow';
import { formatCurrency } from '../../utils/formatters';

const Reports: React.FC = () => {
  const { transactions, summary, getCategoryData } = useCashFlow();
  const categoryData = getCategoryData();

  const monthlyTrends = useMemo(() => {
    const last6Months = [];
    const now = new Date();
    
    for (let i = 5; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      const monthTransactions = transactions.filter(t => {
        const tDate = new Date(t.date);
        return tDate.getFullYear() === date.getFullYear() && 
               tDate.getMonth() === date.getMonth();
      });

      const income = monthTransactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
      
      const expenses = monthTransactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);

      last6Months.push({
        month: date.toLocaleDateString('es-CO', { month: 'short', year: 'numeric' }),
        income,
        expenses,
        balance: income - expenses,
      });
    }
    
    return last6Months;
  }, [transactions]);

  const maxAmount = Math.max(...monthlyTrends.flatMap(m => [m.income, m.expenses]));

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Informes Financieros</h3>
            <p className="text-sm text-gray-600">
              Análisis detallado del período actual
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Calendar className="h-4 w-4" />
              <span>Período</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all">
              <Download className="h-4 w-4" />
              <span>Exportar</span>
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Promedio Mensual Ingresos</p>
            <p className="text-xl font-bold text-green-600">
              {formatCurrency(monthlyTrends.reduce((sum, m) => sum + m.income, 0) / monthlyTrends.length)}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-red-500 to-rose-500">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Promedio Mensual Gastos</p>
            <p className="text-xl font-bold text-red-600">
              {formatCurrency(monthlyTrends.reduce((sum, m) => sum + m.expenses, 0) / monthlyTrends.length)}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-500">
              <PieChart className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Tasa de Ahorro</p>
            <p className="text-xl font-bold text-blue-600">
              {summary.totalIncome > 0 
                ? `${((summary.balance / summary.totalIncome) * 100).toFixed(1)}%`
                : '0%'
              }
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Total Transacciones</p>
            <p className="text-xl font-bold text-purple-600">{transactions.length}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Trends Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Tendencias Mensuales</h3>
          <div className="space-y-4">
            {monthlyTrends.map((month, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {month.month}
                  </span>
                  <span className={`text-sm font-semibold ${
                    month.balance >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(month.balance)}
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className="w-16 text-xs text-gray-500">Ingresos</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 bg-green-500 rounded-full transition-all duration-500"
                        style={{ width: `${maxAmount > 0 ? (month.income / maxAmount) * 100 : 0}%` }}
                      />
                    </div>
                    <div className="w-20 text-xs text-right text-green-600 font-medium">
                      {formatCurrency(month.income)}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 text-xs text-gray-500">Gastos</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 bg-red-500 rounded-full transition-all duration-500"
                        style={{ width: `${maxAmount > 0 ? (month.expenses / maxAmount) * 100 : 0}%` }}
                      />
                    </div>
                    <div className="w-20 text-xs text-right text-red-600 font-medium">
                      {formatCurrency(month.expenses)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Category Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Distribución por Categorías</h3>
          <div className="space-y-4">
            {categoryData.slice(0, 8).map((category) => {
              const percentage = categoryData.length > 0 
                ? (category.total / categoryData.reduce((sum, c) => sum + c.total, 0)) * 100 
                : 0;
              
              return (
                <div key={category.id} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: category.color }}
                      />
                      <span className="text-sm font-medium text-gray-700">
                        {category.name}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {formatCurrency(category.total)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {percentage.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-500"
                      style={{
                        backgroundColor: category.color,
                        width: `${percentage}%`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;