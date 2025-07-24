import React, { useMemo } from 'react';
import { Calendar, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { useCashFlow } from '../../hooks/useCashFlow';
import { formatCurrency } from '../../utils/formatters';
import { MonthlyReport } from '../../types';

const MonthlyFlow: React.FC = () => {
  const { transactions } = useCashFlow();

  const monthlyData: MonthlyReport[] = useMemo(() => {
    const monthlyMap = new Map<string, { income: number; expenses: number }>();

    transactions.forEach(transaction => {
      const date = new Date(transaction.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthlyMap.has(monthKey)) {
        monthlyMap.set(monthKey, { income: 0, expenses: 0 });
      }

      const monthData = monthlyMap.get(monthKey)!;
      if (transaction.type === 'income') {
        monthData.income += transaction.amount;
      } else {
        monthData.expenses += transaction.amount;
      }
    });

    return Array.from(monthlyMap.entries())
      .map(([monthKey, data]) => ({
        month: new Date(monthKey + '-01').toLocaleDateString('es-CO', { 
          year: 'numeric', 
          month: 'long' 
        }),
        income: data.income,
        expenses: data.expenses,
        balance: data.income - data.expenses,
      }))
      .sort((a, b) => new Date(b.month).getTime() - new Date(a.month).getTime())
      .slice(0, 12);
  }, [transactions]);

  const currentMonth = monthlyData[0] || { month: '', income: 0, expenses: 0, balance: 0 };

  return (
    <div className="space-y-6">
      {/* Current Month Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Ingresos del Mes</p>
            <p className="text-2xl font-bold text-green-600">
              {formatCurrency(currentMonth.income)}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-red-500 to-rose-500">
              <TrendingDown className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Gastos del Mes</p>
            <p className="text-2xl font-bold text-red-600">
              {formatCurrency(currentMonth.expenses)}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-lg bg-gradient-to-r ${
              currentMonth.balance >= 0 ? 'from-blue-500 to-indigo-500' : 'from-orange-500 to-red-500'
            }`}>
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Balance del Mes</p>
            <p className={`text-2xl font-bold ${
              currentMonth.balance >= 0 ? 'text-blue-600' : 'text-orange-600'
            }`}>
              {formatCurrency(currentMonth.balance)}
            </p>
          </div>
        </div>
      </div>

      {/* Monthly History */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Calendar className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Historial Mensual</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mes
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ingresos
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Gastos
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Balance
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tendencia
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {monthlyData.map((month, index) => {
                const maxAmount = Math.max(month.income, month.expenses);
                const incomePercentage = maxAmount > 0 ? (month.income / maxAmount) * 100 : 0;
                const expensePercentage = maxAmount > 0 ? (month.expenses / maxAmount) * 100 : 0;

                return (
                  <tr key={month.month} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-gray-900 capitalize">
                        {month.month}
                      </p>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="space-y-1">
                        <p className="text-sm font-semibold text-green-600">
                          {formatCurrency(month.income)}
                        </p>
                        <div className="w-20 h-1 bg-gray-200 rounded-full ml-auto">
                          <div
                            className="h-1 bg-green-500 rounded-full transition-all duration-500"
                            style={{ width: `${incomePercentage}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="space-y-1">
                        <p className="text-sm font-semibold text-red-600">
                          {formatCurrency(month.expenses)}
                        </p>
                        <div className="w-20 h-1 bg-gray-200 rounded-full ml-auto">
                          <div
                            className="h-1 bg-red-500 rounded-full transition-all duration-500"
                            style={{ width: `${expensePercentage}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <p className={`text-sm font-bold ${
                        month.balance >= 0 ? 'text-blue-600' : 'text-orange-600'
                      }`}>
                        {formatCurrency(month.balance)}
                      </p>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        month.balance >= 0 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {month.balance >= 0 ? (
                          <>
                            <TrendingUp className="h-3 w-3 mr-1" />
                            Positivo
                          </>
                        ) : (
                          <>
                            <TrendingDown className="h-3 w-3 mr-1" />
                            Negativo
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MonthlyFlow;