import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, PieChart } from 'lucide-react';
import { CashFlowSummary } from '../types';
import { formatCurrency } from '../utils/formatters';

interface SummaryCardsProps {
  summary: CashFlowSummary;
}

const SummaryCards: React.FC<SummaryCardsProps> = ({ summary }) => {
  const cards = [
    {
      title: 'Balance Total',
      value: summary.balance,
      icon: DollarSign,
      color: summary.balance >= 0 ? 'bg-gradient-to-r from-green-500 to-emerald-500' : 'bg-gradient-to-r from-red-500 to-rose-500',
      textColor: summary.balance >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: summary.balance >= 0 ? 'bg-green-50' : 'bg-red-50',
    },
    {
      title: 'Ingresos del Mes',
      value: summary.monthlyIncome,
      icon: TrendingUp,
      color: 'bg-gradient-to-r from-green-500 to-emerald-500',
      textColor: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Gastos del Mes',
      value: summary.monthlyExpenses,
      icon: TrendingDown,
      color: 'bg-gradient-to-r from-red-500 to-rose-500',
      textColor: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Balance Mensual',
      value: summary.monthlyIncome - summary.monthlyExpenses,
      icon: PieChart,
      color: (summary.monthlyIncome - summary.monthlyExpenses) >= 0 
        ? 'bg-gradient-to-r from-blue-500 to-indigo-500' 
        : 'bg-gradient-to-r from-orange-500 to-red-500',
      textColor: (summary.monthlyIncome - summary.monthlyExpenses) >= 0 ? 'text-blue-600' : 'text-orange-600',
      bgColor: (summary.monthlyIncome - summary.monthlyExpenses) >= 0 ? 'bg-blue-50' : 'bg-orange-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div
            key={index}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${card.color} shadow-lg`}>
                <Icon className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-600">{card.title}</p>
              <p className={`text-2xl font-bold ${card.textColor}`}>
                {formatCurrency(card.value)}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SummaryCards;