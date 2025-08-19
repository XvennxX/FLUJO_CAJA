import { useState, useEffect } from 'react';
import { Calendar, Filter, Upload } from 'lucide-react';
import DatePicker from '../Calendar/DatePicker';
import { useAuditoria } from '../../hooks/useAuditoria';

interface CashFlowData {
  [date: string]: {
    [concept: string]: {
      [company: string]: {
        [account: string]: number;
      };
    };
  };
}

const cashFlowData: CashFlowData = {
  '2025-01-22': {
    'SALDO DIA ANTERIOR': {
      'CAPITALIZADORAPP': {
        'BANCO DAVIVIENDA - 482800001265': 2850000.00,
        'BANCO DAVIVIENDA - 482800001273': 1750000.00,
        'BANCO DAVIVIENDA - 482800002024': 950000.00,
        'BANCO DAVIVIENDA - 482800007882': 1200000.00,
        'BANCO DAVIVIENDA - 482800007908': 850000.00,
        'BANCO DAVIVIENDA - 482800007890': 2100000.00,
        'BANCO DAVIVIENDA - 482800010001': 3200000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': 5200000.00,
        'BANCO DAVIVIENDA - 482800007882': 4100000.00,
        'BANCO DAVIVIENDA - 482800007908': 3200000.00,
        'BANCO DAVIVIENDA - 482800007890': 2800000.00,
        'BANCO DAVIVIENDA - 482800010001': 6800000.00,
        'BANCO DAVIVIENDA - 482800010019': 2400000.00,
        'BANCO DAVIVIENDA - 482800010027': 3900000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800001257': 3600000.00,
        'BANCO DAVIVIENDA - 482800007882': 2900000.00,
        'BANCO DAVIVIENDA - 482800007908': 1800000.00,
        'BANCO DAVIVIENDA - 482800007890': 2200000.00,
        'BANCO DAVIVIENDA - 482800010001': 4700000.00,
        'BANCO DAVIVIENDA - 482800010019': 1250000.00,
        'BANCO DAVIVIENDA - 482800010027': 3400000.00
      },
      'GRUPO BOLIVAR': {
        'DAVIVIENDA INT - 867614010': 15200000.00,
        'DAVIVIENDA - 010002000127': 8900000.00,
        'BANCO DE BOGOTA - 000977280': 5600000.00
      },
      'SEISA': {
        'DAVIVIENDA INT - 010003000003': 2500000.00
      },
      'RIBI': {
        'DAVIVIENDA INT - 010003000003': 1800000.00
      }
    },
    'CONSUMO': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800001265': -85000.00,
        'BANCO DAVIVIENDA - 482800001273': -45000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': -320000.00,
        'BANCO DAVIVIENDA - 482800007882': -180000.00,
        'BANCO DAVIVIENDA - 482800007908': -95000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800001257': -150000.00,
        'BANCO DAVIVIENDA - 482800007882': -120000.00,
        'BANCO DAVIVIENDA - 482800007908': -78000.00
      }
    },
    'VENTANILLA': {
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': -280000.00,
        'BANCO DAVIVIENDA - 482800007882': -165000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800001257': -195000.00,
        'BANCO DAVIVIENDA - 482800007882': -125000.00
      }
    },
    'SALDO NETO INICIAL PAGADURÍA': {
      'GRUPO BOLIVAR': {
        'DAVIVIENDA - 010002000127': 1250000.00,
        'BANCO DE BOGOTA - 000977280': 850000.00
      }
    },
    'PAGOS INTERCOMPAÑIAS': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800001265': -150000.00,
        'BANCO DAVIVIENDA - 482800001273': -85000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': -320000.00,
        'BANCO DAVIVIENDA - 482800007882': -180000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800001257': -95000.00,
        'BANCO DAVIVIENDA - 482800007882': -120000.00
      }
    },
    'INGRESOS INTERESES': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800010001': 45000.00,
        'BANCO DAVIVIENDA - 482800010019': 38000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800010001': 125000.00,
        'BANCO DAVIVIENDA - 482800010019': 78000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800010001': 85000.00,
        'BANCO DAVIVIENDA - 482800010019': 62000.00
      }
    },
    'INGRESO REDENCIÓN TÍTULOS': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800002024': 850000.00,
        'BANCO DAVIVIENDA - 482800002032': 420000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800002024': 320000.00,
        'BANCO DAVIVIENDA - 482800002032': 180000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800002024': 280000.00,
        'BANCO DAVIVIENDA - 482800002032': 150000.00
      }
    },
    'APERTURA ACTIVO FINANCIERO': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800003024': -2500000.00,
        'BANCO DAVIVIENDA - 482800003032': -1800000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800003024': -4200000.00,
        'BANCO DAVIVIENDA - 482800003032': -3100000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800003024': -1900000.00,
        'BANCO DAVIVIENDA - 482800003032': -1400000.00
      }
    },
    'CANCELACIÓN ACTIVO FINANCIERO': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800003024': 1200000.00,
        'BANCO DAVIVIENDA - 482800003032': 900000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800003024': 1800000.00,
        'BANCO DAVIVIENDA - 482800003032': 1300000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800003024': 950000.00,
        'BANCO DAVIVIENDA - 482800003032': 720000.00
      }
    },
    'INTERESES ACTIVO FINANCIERO': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800003024': 120000.00,
        'BANCO DAVIVIENDA - 482800003032': 95000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800003024': 180000.00,
        'BANCO DAVIVIENDA - 482800003032': 125000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800003024': 85000.00,
        'BANCO DAVIVIENDA - 482800003032': 65000.00
      }
    },
    'CANCELACIÓN KW': {
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800004024': -85000.00,
        'BANCO DAVIVIENDA - 482800004032': -55000.00
      }
    },
    'PAGO INTERESES KW': {
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800004024': -25000.00,
        'BANCO DAVIVIENDA - 482800004032': -18000.00
      }
    },
    'COMPRA TÍTULOS': {
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800005024': -450000.00,
        'BANCO DAVIVIENDA - 482800005032': -320000.00
      }
    },
    'COMPRA SIMULTÁNEA ACTIVA': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800006024': -1250000.00
      }
    },
    'REDENCIÓN SIMULTÁNEA PASIVA': {
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800006032': 750000.00
      }
    }
  },
  '2025-01-21': {
    'SALDO DIA ANTERIOR': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800001265': 2650000.00,
        'BANCO DAVIVIENDA - 482800001273': 1650000.00,
        'BANCO DAVIVIENDA - 482800002024': 1150000.00,
        'BANCO DAVIVIENDA - 482800002032': 800000.00,
        'BANCO DAVIVIENDA - 482800010001': 3100000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': 5000000.00,
        'BANCO DAVIVIENDA - 482800007882': 3900000.00,
        'BANCO DAVIVIENDA - 482800001265': 6500000.00,
        'BANCO DAVIVIENDA - 482800001273': 2200000.00,
        'BANCO DAVIVIENDA - 482800010001': 8200000.00,
        'BANCO DAVIVIENDA - 482800002024': 1750000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800001257': 3400000.00,
        'BANCO DAVIVIENDA - 482800007882': 2700000.00,
        'BANCO DAVIVIENDA - 482800002024': 1700000.00,
        'BANCO DAVIVIENDA - 482800010001': 4500000.00,
        'BANCO DAVIVIENDA - 482800001265': 3200000.00
      },
      'GRUPO BOLIVAR': {
        'DAVIVIENDA INT - 867614010': 14800000.00,
        'DAVIVIENDA - 010002000127': 8500000.00
      }
    },
    'CONSUMO': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800001265': -75000.00,
        'BANCO DAVIVIENDA - 482800001273': -42000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': -290000.00,
        'BANCO DAVIVIENDA - 482800007882': -165000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800001257': -120000.00,
        'BANCO DAVIVIENDA - 482800007882': -85000.00
      }
    },
    'PAGOS INTERCOMPAÑIAS': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800001265': -125000.00,
        'CITIBANK COMP - 36203301': -75000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': -280000.00,
        'BANCO REPUBLICA - 62250774-0': -150000.00
      }
    },
    'INGRESOS INTERESES': {
      'CAPITALIZADORA': {
        'DAVIVIENDA INT - 865784010': 42000.00,
        'JP MORGAN - 36203301': 35000.00
      },
      'SEGUROS BOLÍVAR': {
        'DAVIVIENDA INT - 865804010': 115000.00,
        'CITIBANK COMP - 36203328': 72000.00
      }
    }
  },
  '2025-01-20': {
    'SALDO DIA ANTERIOR': {
      'CAPITALIZADORA': {
        'BANCO DAVIVIENDA - 482800001265': 2500000.00,
        'BANCO DAVIVIENDA - 482800001273': 1580000.00,
        'BANCO DAVIVIENDA - 482800002024': 1100000.00,
        'BANCO DAVIVIENDA - 482800002032': 750000.00
      },
      'SEGUROS BOLÍVAR': {
        'BANCO DAVIVIENDA - 482800001257': 4800000.00,
        'BANCO DAVIVIENDA - 482800007882': 6200000.00,
        'BANCO DAVIVIENDA - 482800001265': 2100000.00,
        'BANCO DAVIVIENDA - 482800010001': 8000000.00
      },
      'COMERCIALES': {
        'BANCO DAVIVIENDA - 482800001257': 3200000.00,
        'BANCO DAVIVIENDA - 482800007882': 2500000.00,
        'BANCO DAVIVIENDA - 482800002024': 1600000.00,
        'BANCO DAVIVIENDA - 482800001265': 3000000.00
      },
      'GRUPO BOLIVAR': {
        'DAVIVIENDA INT - 867614010': 14200000.00,
        'DAVIVIENDA - 010002000127': 8200000.00
      }
    }
  }
};

const companies = ['CAPITALIZADORA', 'SEGUROS BOLÍVAR', 'COMERCIALES', 'GRUPO BOLIVAR', 'SEISA', 'RIBI', 'INVERSORAS', 'SALUD EPS BOLIVAR', 'SALUD IPS BOLIVAR', 'SERVICIOS BOLIVAR'];
export default function Dashboard() {
  // Asegurar que siempre inicie con el 22 de enero
  const [selectedDate, setSelectedDate] = useState('2025-01-22');
  const { logCashFlowChange, logImportAction } = useAuditoria();
  
  // Verificar que la fecha inicial sea válida y forzar actualización si es necesaria
  const handleDateChange = async (newDate: string) => {
    const oldDate = selectedDate;
    setSelectedDate(newDate);
    
    // Registrar cambio de fecha en auditoría
    await logCashFlowChange(
      newDate,
      `Consultó el flujo de caja del ${new Date(newDate).toLocaleDateString('es-CO')}`,
      { fechaAnterior: oldDate },
      { fechaNueva: newDate }
    );
  };

  const handleImport = async () => {
    // Registrar acción de importar en auditoría
    await logImportAction(
      `Solicitó importar datos de flujo de caja para la fecha ${new Date(selectedDate).toLocaleDateString('es-CO')}`,
      selectedDate
    );
    
    // Aquí iría la lógica real de importación
    alert('Funcionalidad de importar en desarrollo');
  };

  // Efecto para asegurar que se inicialice correctamente
  useEffect(() => {
    if (selectedDate !== '2025-01-22') {
      setSelectedDate('2025-01-22');
    }
  }, []);
  
  const [showCompany, setShowCompany] = useState({
    CAPITALIZADORA: true,
    'SEGUROS BOLÍVAR': true,
    COMERCIALES: true,
    'GRUPO BOLIVAR': true,
    SEISA: true,
    RIBI: true,
    INVERSORAS: true,
    'SALUD EPS BOLIVAR': true,
    'SALUD IPS BOLIVAR': true,
    'SERVICIOS BOLIVAR': true
  });

  const availableDates = Object.keys(cashFlowData).sort().reverse();
  const currentData = cashFlowData[selectedDate] || {};

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const getCompanyAbbreviation = (company: string) => {
    const abbreviations: { [key: string]: string } = {
      'CAPITALIZADORA': 'CA',
      'SEGUROS BOLÍVAR': 'SB',
      'COMERCIALES': 'CO',
      'GRUPO BOLIVAR': 'GB',
      'SEISA': 'SE',
      'RIBI': 'RI',
      'INVERSORAS': 'IN',
      'SALUD EPS BOLIVAR': 'SEB',
      'SALUD IPS BOLIVAR': 'SIB',
      'SERVICIOS BOLIVAR': 'SVB'
    };
    return abbreviations[company] || company.substring(0, 2).toUpperCase();
  };

  const getVisibleCompanies = () => {
    return companies.filter(company => showCompany[company as keyof typeof showCompany]);
  };

  const getAllAccounts = () => {
    const accounts: { [key: string]: string[] } = {};
    Object.values(currentData).forEach(conceptData => {
      Object.entries(conceptData).forEach(([company, companyData]) => {
        if (!accounts[company]) accounts[company] = [];
        Object.keys(companyData).forEach(account => {
          if (!accounts[company].includes(account)) {
            accounts[company].push(account);
          }
        });
      });
    });
    return accounts;
  };

  const calculateCompanyTotal = (company: string) => {
    let total = 0;
    Object.values(currentData).forEach(conceptData => {
      if (conceptData[company]) {
        Object.values(conceptData[company]).forEach(amount => {
          total += amount;
        });
      }
    });
    return total;
  };

  const allAccounts = getAllAccounts();
  const visibleCompanies = getVisibleCompanies();

  return (
    <div className="space-y-6">
      {/* Header con controles de fecha */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Flujo de Caja Diario</h1>
          </div>
          
          <DatePicker 
            selectedDate={selectedDate}
            onDateChange={handleDateChange}
            availableDates={availableDates}
          />
        </div>

        {/* Filtros */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filtros:</span>
            </div>
            
            {/* Filtro de empresas - Diseño compacto */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Empresas:</span>
                <div className="flex items-center space-x-1">
                  <span className="text-xs bg-bolivar-100 text-bolivar-700 px-2 py-1 rounded-full">
                    {Object.values(showCompany).filter(v => v).length} de {companies.length}
                  </span>
                  <button
                    onClick={() => {
                      const allVisible = Object.values(showCompany).every(v => v);
                      const newState = Object.keys(showCompany).reduce((acc, key) => {
                        acc[key as keyof typeof showCompany] = !allVisible;
                        return acc;
                      }, {} as typeof showCompany);
                      setShowCompany(newState);
                    }}
                    className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded border text-gray-600 dark:text-gray-300 transition-colors"
                  >
                    {Object.values(showCompany).every(v => v) ? 'Limpiar' : 'Todas'}
                  </button>
                </div>
              </div>
            </div>
            
            {/* Grid compacto de empresas */}
            <div className="flex flex-col items-start">
              <div className="grid grid-cols-5 gap-1 mb-1">
                {companies.map(company => {
                  const isSelected = showCompany[company as keyof typeof showCompany];
                  const shortName = getCompanyAbbreviation(company);
                  
                  return (
                    <button
                      key={company}
                      onClick={() => setShowCompany(prev => ({ ...prev, [company]: !prev[company as keyof typeof prev] }))}
                      className={`w-10 h-8 text-xs font-bold rounded transition-all duration-200 border ${
                        isSelected
                          ? 'bg-bolivar-500 text-white border-bolivar-600 shadow-sm' 
                          : 'bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                      }`}
                      title={company}
                    >
                      {shortName}
                    </button>
                  );
                })}
              </div>
              <div className="text-xs text-gray-400">
                Hover para ver nombre completo
              </div>
            </div>
          </div>
          
          <button 
            onClick={handleImport}
            className="flex items-center space-x-2 px-4 py-2 bg-bolivar-600 text-white rounded-lg hover:bg-bolivar-700 transition-colors"
          >
            <Upload className="w-4 h-4" />
            <span>Importar</span>
          </button>
        </div>
      </div>

      {/* Tabla principal */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-bolivar-600 text-white">
                <th className="sticky left-0 bg-bolivar-600 px-4 py-3 text-left text-sm font-semibold min-w-[200px] z-10">
                  CONCEPTO
                </th>
                {visibleCompanies.map(company => {
                  const accounts = allAccounts[company] || [];
                  return accounts.map(account => (
                    <th key={`${company}-${account}`} className="px-4 py-3 text-center text-sm font-semibold min-w-[150px] border-l border-bolivar-500">
                      <div className="space-y-1">
                        <div className="font-bold text-gold-400">{company}</div>
                        <div className="text-xs opacity-90">{account.split(' - ')[0]}</div>
                        <div className="text-xs opacity-75">{account.split(' - ')[1]}</div>
                      </div>
                    </th>
                  ));
                })}
                <th className="px-4 py-3 text-center text-sm font-semibold min-w-[120px] border-l-2 border-gold-400 bg-bolivar-700">
                  TOTAL
                </th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(currentData).map(([concept, conceptData], conceptIndex) => (
                <tr key={concept} className={`${conceptIndex % 2 === 0 ? 'bg-gray-50 dark:bg-gray-700' : 'bg-white dark:bg-gray-800'} hover:bg-bolivar-50 dark:hover:bg-bolivar-900/20 transition-colors`}>
                  <td className="sticky left-0 bg-inherit px-4 py-3 font-medium text-gray-900 dark:text-white border-r border-gray-200 dark:border-gray-600 z-10">
                    <div className="flex items-center space-x-2">
                      {concept.includes('INGRESO') && <div className="w-3 h-3 bg-green-500 rounded-full"></div>}
                      {concept.includes('EGRESO') && <div className="w-3 h-3 bg-red-500 rounded-full"></div>}
                      {concept.includes('SALDO') && <div className="w-3 h-3 bg-blue-500 rounded-full"></div>}
                      <span className="text-sm">{concept}</span>
                    </div>
                  </td>
                  {visibleCompanies.map(company => {
                    const accounts = allAccounts[company] || [];
                    return accounts.map(account => {
                      const amount = conceptData[company]?.[account] || 0;
                      return (
                        <td key={`${company}-${account}`} className="px-4 py-3 text-right text-sm border-l border-gray-200 dark:border-gray-700">
                          <span className={`${
                            amount > 0 ? 'text-green-600' : 
                            amount < 0 ? 'text-red-600' : 
                            'text-gray-500 dark:text-gray-400'
                          } font-mono`}>
                            {amount !== 0 ? formatCurrency(amount) : '-'}
                          </span>
                        </td>
                      );
                    });
                  })}
                  <td className="px-4 py-3 text-right text-sm font-semibold border-l-2 border-gold-400 bg-gray-100 dark:bg-gray-700">
                    {(() => {
                      const total = Object.values(conceptData).reduce((sum, companyData) => {
                        return sum + Object.values(companyData).reduce((companySum, amount) => companySum + amount, 0);
                      }, 0);
                      return (
                        <span className={`${
                          total > 0 ? 'text-green-600' : 
                          total < 0 ? 'text-red-600' : 
                          'text-gray-500 dark:text-gray-400'
                        } font-mono`}>
                          {formatCurrency(total)}
                        </span>
                      );
                    })()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resumen por empresa */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {visibleCompanies.map(company => {
          const total = calculateCompanyTotal(company);
          const accounts = allAccounts[company] || [];
          
          return (
            <div key={company} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{company}</h3>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  total > 0 ? 'bg-green-100 text-green-700' : 
                  total < 0 ? 'bg-red-100 text-red-700' : 
                  'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}>
                  {formatCurrency(total)}
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  <span className="font-medium">{accounts.length}</span> cuentas activas
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Última actualización: {new Date().toLocaleTimeString('es-CO')}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Estado vacío */}
      {Object.keys(currentData).length === 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No hay datos disponibles</h3>
          <p className="text-gray-500 dark:text-gray-400">No se encontraron movimientos para la fecha seleccionada.</p>
        </div>
      )}
    </div>
  );
}

