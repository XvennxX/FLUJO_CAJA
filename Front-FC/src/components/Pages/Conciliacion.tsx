import React, { useState } from 'react';
import { 
  Calculator, 
  Check, 
  X, 
  Building2, 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  FileText,
  Lock,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { useConciliacion } from '../../hooks/useConciliacion';
import { formatCurrency } from '../../utils/formatters';

const Conciliacion: React.FC = () => {
  const { 
    companyBalances, 
    updateCompanyStatus, 
    calculateTotals,
    evaluarTodas,
    confirmarTodas,
    cerrarTodas
  } = useConciliacion();
  
  const [selectedCompany, setSelectedCompany] = useState<string>('all');

  const filteredBalances = selectedCompany === 'all' 
    ? companyBalances 
    : companyBalances.filter(b => b.company === selectedCompany);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pendiente':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'evaluado':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'confirmado':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'cerrado':
        return <Lock className="h-5 w-5 text-gray-500 dark:text-gray-400" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'evaluado':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'confirmado':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cerrado':
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-200 dark:border-gray-700';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-200 dark:border-gray-700';
    }
  };

  const totales = calculateTotals(filteredBalances);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <Calculator className="h-8 w-8 text-bolivar-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Conciliación Contable</h1>
            <p className="text-gray-600 dark:text-gray-400">Resumen de cierres por compañía</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={selectedCompany}
            onChange={(e) => setSelectedCompany(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-bolivar-500 focus:border-transparent"
          >
            <option value="all">Todas las compañías</option>
            <option value="CAPITALIZADORA">CAPITALIZADORA</option>
            <option value="SEGUROS BOLÍVAR">SEGUROS BOLÍVAR</option>
            <option value="COMERCIALES">COMERCIALES</option>
          </select>
        </div>
      </div>

      {/* Resumen General */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-800">Pagaduría - Ingresos</span>
          </div>
          <p className="text-2xl font-bold text-blue-900 mt-2">
            {formatCurrency(totales.pagaduriaIngresos)}
          </p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <TrendingDown className="h-5 w-5 text-red-600" />
            <span className="text-sm font-medium text-red-800">Pagaduría - Egresos</span>
          </div>
          <p className="text-2xl font-bold text-red-900 mt-2">
            {formatCurrency(totales.pagaduriaEgresos)}
          </p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-green-800">Tesorería - Ingresos</span>
          </div>
          <p className="text-2xl font-bold text-green-900 mt-2">
            {formatCurrency(totales.tesoreriaIngresos)}
          </p>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <TrendingDown className="h-5 w-5 text-orange-600" />
            <span className="text-sm font-medium text-orange-800">Tesorería - Egresos</span>
          </div>
          <p className="text-2xl font-bold text-orange-900 mt-2">
            {formatCurrency(totales.tesoreriaEgresos)}
          </p>
        </div>

        <div className={`border rounded-lg p-4 ${totales.total >= 0 ? 'bg-bolivar-50 border-bolivar-200' : 'bg-red-50 border-red-200'}`}>
          <div className="flex items-center space-x-2">
            <DollarSign className={`h-5 w-5 ${totales.total >= 0 ? 'text-bolivar-600' : 'text-red-600'}`} />
            <span className={`text-sm font-medium ${totales.total >= 0 ? 'text-bolivar-800' : 'text-red-800'}`}>
              Total General
            </span>
          </div>
          <p className={`text-2xl font-bold mt-2 ${totales.total >= 0 ? 'text-bolivar-900' : 'text-red-900'}`}>
            {formatCurrency(totales.total)}
          </p>
        </div>
      </div>

      {/* Tabla de Balances por Compañía */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
            <Building2 className="h-5 w-5" />
            <span>Detalle por Compañía</span>
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Compañía
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Pagaduría
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Tesorería
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredBalances.map((balance) => (
                <tr key={balance.company} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-5 w-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {balance.company}
                      </span>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 text-center">
                    <div className="space-y-1">
                      <div className="text-xs text-green-600">
                        +{formatCurrency(balance.pagaduria.ingresos)}
                      </div>
                      <div className="text-xs text-red-600">
                        -{formatCurrency(balance.pagaduria.egresos)}
                      </div>
                      <div className={`text-sm font-semibold ${balance.pagaduria.saldo >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                        {formatCurrency(balance.pagaduria.saldo)}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 text-center">
                    <div className="space-y-1">
                      <div className="text-xs text-green-600">
                        +{formatCurrency(balance.tesoreria.ingresos)}
                      </div>
                      <div className="text-xs text-red-600">
                        -{formatCurrency(balance.tesoreria.egresos)}
                      </div>
                      <div className={`text-sm font-semibold ${balance.tesoreria.saldo >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                        {formatCurrency(balance.tesoreria.saldo)}
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 text-center">
                    <span className={`text-lg font-bold ${balance.total >= 0 ? 'text-bolivar-700' : 'text-red-700'}`}>
                      {formatCurrency(balance.total)}
                    </span>
                  </td>
                  
                  <td className="px-6 py-4 text-center">
                    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(balance.status)}`}>
                      {getStatusIcon(balance.status)}
                      <span className="capitalize">{balance.status}</span>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 text-center">
                    <div className="flex items-center justify-center space-x-2">
                      {/* Evaluar */}
                      {balance.status === 'pendiente' && (
                        <button
                          onClick={() => updateCompanyStatus(balance.company, 'evaluado')}
                          className="p-1 text-orange-600 hover:text-orange-800 hover:bg-orange-100 rounded"
                          title="Evaluar"
                        >
                          <FileText className="h-4 w-4" />
                        </button>
                      )}
                      
                      {/* Confirmar */}
                      {balance.status === 'evaluado' && (
                        <button
                          onClick={() => updateCompanyStatus(balance.company, 'confirmado')}
                          className="p-1 text-green-600 hover:text-green-800 hover:bg-green-100 rounded"
                          title="Confirmar"
                        >
                          <Check className="h-4 w-4" />
                        </button>
                      )}
                      
                      {/* Cerrar */}
                      {balance.status === 'confirmado' && (
                        <button
                          onClick={() => updateCompanyStatus(balance.company, 'cerrado')}
                          className="p-1 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
                          title="Cerrar"
                        >
                          <Lock className="h-4 w-4" />
                        </button>
                      )}
                      
                      {/* Retroceder un paso */}
                      {balance.status !== 'pendiente' && balance.status !== 'cerrado' && (
                        <button
                          onClick={() => {
                            const currentFlow = ['pendiente', 'evaluado', 'confirmado', 'cerrado'];
                            const currentIndex = currentFlow.indexOf(balance.status);
                            if (currentIndex > 0) {
                              updateCompanyStatus(balance.company, currentFlow[currentIndex - 1]);
                            }
                          }}
                          className="p-1 text-yellow-600 hover:text-yellow-800 hover:bg-yellow-100 rounded"
                          title="Retroceder"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Acciones Globales */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Acciones de Cierre</h3>
        <div className="flex flex-wrap gap-3">
          <button
            className="flex items-center space-x-2 px-4 py-2 bg-orange-100 text-orange-800 border border-orange-300 rounded-lg hover:bg-orange-200 transition-colors"
            onClick={evaluarTodas}
          >
            <FileText className="h-4 w-4" />
            <span>Evaluar Todas</span>
          </button>
          
          <button
            className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-800 border border-green-300 rounded-lg hover:bg-green-200 transition-colors"
            onClick={confirmarTodas}
          >
            <CheckCircle className="h-4 w-4" />
            <span>Confirmar Todas</span>
          </button>
          
          <button
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
            onClick={cerrarTodas}
          >
            <Lock className="h-4 w-4" />
            <span>Cerrar Todas</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Conciliacion;


