import React from 'react';
import { Category } from '../types';
import { formatCurrency } from '../utils/formatters';

interface CategoryChartProps {
  categoryData: (Category & { total: number })[];
  type: 'income' | 'expense';
}

const CategoryChart: React.FC<CategoryChartProps> = ({ categoryData, type }) => {
  const filteredData = categoryData.filter(c => c.type === type);
  const maxAmount = Math.max(...filteredData.map(c => c.total), 1);
  const title = type === 'income' ? 'Ingresos por Categoría' : 'Gastos por Categoría';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">{title}</h3>
      {filteredData.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No hay datos para mostrar</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredData.map((category) => {
            const percentage = (category.total / maxAmount) * 100;
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
                  <span className="text-sm font-semibold text-gray-900">
                    {formatCurrency(category.total)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-500 ease-out"
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
      )}
    </div>
  );
};

export default CategoryChart;