import React, { useState } from 'react';
import { Tag, Plus, Edit, Trash2, TrendingUp, TrendingDown } from 'lucide-react';
import { useCashFlow } from '../../hooks/useCashFlow';
import { formatCurrency } from '../../utils/formatters';

const Categories: React.FC = () => {
  const { categories, getCategoryData } = useCashFlow();
  const [filterType, setFilterType] = useState<'all' | 'income' | 'expense'>('all');
  
  const categoryData = getCategoryData();
  const filteredCategories = filterType === 'all' 
    ? categoryData 
    : categoryData.filter(c => c.type === filterType);

  const incomeCategories = categoryData.filter(c => c.type === 'income');
  const expenseCategories = categoryData.filter(c => c.type === 'expense');

  const totalIncome = incomeCategories.reduce((sum, c) => sum + c.total, 0);
  const totalExpenses = expenseCategories.reduce((sum, c) => sum + c.total, 0);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Categorías de Ingresos</p>
            <p className="text-2xl font-bold text-green-600">{incomeCategories.length}</p>
            <p className="text-sm text-gray-500 mt-1">
              Total: {formatCurrency(totalIncome)}
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
            <p className="text-sm font-medium text-gray-600">Categorías de Gastos</p>
            <p className="text-2xl font-bold text-red-600">{expenseCategories.length}</p>
            <p className="text-sm text-gray-500 mt-1">
              Total: {formatCurrency(totalExpenses)}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-500">
              <Tag className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600">Total Categorías</p>
            <p className="text-2xl font-bold text-blue-600">{categories.length}</p>
            <p className="text-sm text-gray-500 mt-1">
              Activas: {categoryData.length}
            </p>
          </div>
        </div>
      </div>

      {/* Categories Management */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
          <h3 className="text-lg font-semibold text-gray-900">Gestión de Categorías</h3>
          <div className="flex items-center space-x-3">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as 'all' | 'income' | 'expense')}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todas las categorías</option>
              <option value="income">Solo ingresos</option>
              <option value="expense">Solo gastos</option>
            </select>
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all flex items-center space-x-2">
              <Plus className="h-4 w-4" />
              <span>Nueva Categoría</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCategories.map((category) => (
            <div
              key={category.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: category.color }}
                  />
                  <span className="font-medium text-gray-900">{category.name}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <button className="p-1 text-gray-400 hover:text-blue-600 transition-colors">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-red-600 transition-colors">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    category.type === 'income' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {category.type === 'income' ? 'Ingreso' : 'Gasto'}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    {formatCurrency(category.total)}
                  </span>
                </div>
                
                {category.total > 0 && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-500"
                      style={{
                        backgroundColor: category.color,
                        width: `${(category.total / Math.max(...filteredCategories.map(c => c.total))) * 100}%`,
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredCategories.length === 0 && (
          <div className="text-center py-12">
            <Tag className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500">No hay categorías para mostrar</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Categories;