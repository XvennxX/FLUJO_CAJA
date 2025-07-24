import React, { useState, useMemo } from 'react';
import { Download, Filter, Eye, EyeOff, Calculator, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { bankAccounts, dailyCashFlowData, BankAccount, CashFlowEntry } from '../../data/cashFlowData';
import { formatCurrency } from '../../utils/formatters';

const Dashboard: React.FC = () => {
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>(['CAPITALIZADORA', 'BOLÍVAR', 'COMERCIALES']);
  const [showUSD, setShowUSD] = useState(true);
  const [showCOP, setShowCOP] = useState(true);
  const [selectedDate, setSelectedDate] = useState('2025-01-22');

  const companies = ['CAPITALIZADORA', 'BOLÍVAR', 'COMERCIALES', 'CAPITALIZADORA AHO', 'BOLÍVAR AHO', 'BOLÍVAR ARL', 'COMERCIALES AHO'];

  const currentDayData = useMemo(() => {
    return dailyCashFlowData.find(day => day.date === selectedDate);
  }, [selectedDate]);

  const cashFlowEntries = currentDayData?.entries || [];

  const availableDates = dailyCashFlowData.map(day => day.date).sort().reverse();

  const filteredAccounts = useMemo(() => {
    return bankAccounts.filter(account => 
      selectedCompanies.includes(account.company) &&
      ((showUSD && account.currency === 'USD') || (showCOP && account.currency === 'COP'))
    );
  }, [selectedCompanies, showUSD, showCOP]);

  const getAccountBalance = (accountId: string) => {
    return cashFlowEntries.reduce((total, entry) => {
      const amount = entry.accounts[accountId] || 0;
      return entry.type === 'I' ? total + amount : total - amount;
    }, 0);
  };

  const getTotalByCompany = (company: string) => {
    const companyAccounts = filteredAccounts.filter(acc => acc.company === company);
    return companyAccounts.reduce((total, account) => total + getAccountBalance(account.id), 0);
  };

  const getRowTotal = (entry: CashFlowEntry) => {
    return filteredAccounts.reduce((total, account) => {
      const amount = entry.accounts[account.id] || 0;
      return total + amount;
    }, 0);
  };

  const getGrandTotal = () => {
    return filteredAccounts.reduce((total, account) => total + getAccountBalance(account.id), 0);
  };

  const toggleCompany = (company: string) => {
    setSelectedCompanies(prev => 
      prev.includes(company) 
        ? prev.filter(c => c !== company)
        : [...prev, company]
    );
  };

  const navigateDate = (direction: 'prev' | 'next') => {
    const currentIndex = availableDates.indexOf(selectedDate);
    if (direction === 'prev' && currentIndex < availableDates.length - 1) {
      setSelectedDate(availableDates[currentIndex + 1]);
    } else if (direction === 'next' && currentIndex > 0) {
      setSelectedDate(availableDates[currentIndex - 1]);
    }
  };

  const formatDateDisplay = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Flujo de Caja Consolidado</h3>
            <p className="text-sm text-gray-600 capitalize">{formatDateDisplay(selectedDate)}</p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3">
            {/* Date Navigation */}
            <div className="flex items-center space-x-2 bg-gray-50 rounded-lg p-2">
              <button
                onClick={() => navigateDate('prev')}
                disabled={availableDates.indexOf(selectedDate) === availableDates.length - 1}
                className="p-1 text-gray-600 hover:text-blue-600 disabled:text-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <div className="flex items-center space-x-2 px-3 py-1">
                <Calendar className="h-4 w-4 text-gray-600" />
                <select
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="bg-transparent border-none text-sm font-medium text-gray-900 focus:outline-none cursor-pointer"
                >
                  {availableDates.map(date => (
                    <option key={date} value={date}>
                      {new Date(date).toLocaleDateString('es-CO')}
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={() => navigateDate('next')}
                disabled={availableDates.indexOf(selectedDate) === 0}
                className="p-1 text-gray-600 hover:text-blue-600 disabled:text-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>

            {/* Currency Filters */}
            <div className="flex items-center space-x-2 bg-gray-50 rounded-lg p-2">
              <button
                onClick={() => setShowCOP(!showCOP)}
                className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  showCOP ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                {showCOP ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                <span>COP</span>
              </button>
              <button
                onClick={() => setShowUSD(!showUSD)}
                className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  showUSD ? 'bg-green-500 text-white' : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                {showUSD ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                <span>USD</span>
              </button>
            </div>

            <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all">
              <Download className="h-4 w-4" />
              <span>Exportar</span>
            </button>
          </div>
        </div>

        {/* Company Filters */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {companies.map(company => (
              <button
                key={company}
                onClick={() => toggleCompany(company)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  selectedCompanies.includes(company)
                    ? 'bg-blue-100 text-blue-800 border border-blue-200'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {company}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Date Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <Calendar className="h-5 w-5 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Flujo de Caja del Día</h4>
              <p className="text-sm text-gray-600 capitalize">{formatDateDisplay(selectedDate)}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Total Movimientos</p>
            <p className="text-lg font-bold text-blue-600">{cashFlowEntries.length}</p>
          </div>
        </div>
      </div>

      {/* Cash Flow Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {cashFlowEntries.length === 0 ? (
          <div className="p-12 text-center">
            <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay datos para esta fecha</h3>
            <p className="text-gray-500">Selecciona una fecha diferente para ver el flujo de caja</p>
          </div>
        ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            {/* Header */}
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="sticky left-0 bg-gray-50 px-4 py-3 text-left font-medium text-gray-700 border-r border-gray-200 min-w-[200px]">
                  CONCEPTO
                </th>
                {filteredAccounts.map(account => (
                  <th key={account.id} className="px-3 py-3 text-center font-medium text-gray-700 border-r border-gray-200 min-w-[120px]">
                    <div className="space-y-1">
                      <div className="text-xs font-bold text-blue-600">{account.company}</div>
                      <div className="text-xs text-gray-500">{account.bank}</div>
                      <div className="text-xs font-mono text-gray-600">{account.accountNumber}</div>
                      <div className={`text-xs font-bold ${account.currency === 'USD' ? 'text-green-600' : 'text-blue-600'}`}>
                        {account.currency}
                      </div>
                    </div>
                  </th>
                ))}
                <th className="px-4 py-3 text-center font-medium text-gray-700 bg-yellow-50 min-w-[120px]">
                  TOTAL
                </th>
              </tr>
            </thead>

            {/* Body */}
            <tbody>
              {cashFlowEntries.map((entry, index) => {
                const rowTotal = getRowTotal(entry);
                const isPositive = entry.type === 'I';
                
                return (
                  <tr key={entry.id} className={`border-b border-gray-100 hover:bg-gray-50 ${
                    index % 2 === 0 ? 'bg-white' : 'bg-gray-25'
                  }`}>
                    <td className="sticky left-0 bg-inherit px-4 py-3 font-medium text-gray-900 border-r border-gray-200">
                      <div className="flex items-center space-x-2">
                        <span className={`w-2 h-2 rounded-full ${
                          isPositive ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                        <span>{entry.concept}</span>
                      </div>
                    </td>
                    {filteredAccounts.map(account => {
                      const amount = entry.accounts[account.id] || 0;
                      const hasValue = amount !== 0;
                      
                      return (
                        <td key={account.id} className={`px-3 py-3 text-right border-r border-gray-200 ${
                          hasValue ? (amount > 0 ? 'bg-green-50' : 'bg-red-50') : ''
                        }`}>
                          {hasValue && (
                            <span className={`font-medium ${
                              amount > 0 ? 'text-green-700' : 'text-red-700'
                            }`}>
                              {formatCurrency(Math.abs(amount))}
                            </span>
                          )}
                        </td>
                      );
                    })}
                    <td className={`px-4 py-3 text-right font-bold bg-yellow-50 ${
                      rowTotal > 0 ? 'text-green-700' : rowTotal < 0 ? 'text-red-700' : 'text-gray-700'
                    }`}>
                      {rowTotal !== 0 && formatCurrency(Math.abs(rowTotal))}
                    </td>
                  </tr>
                );
              })}

              {/* Subtotals */}
              <tr className="bg-blue-50 border-t-2 border-blue-200">
                <td className="sticky left-0 bg-blue-50 px-4 py-3 font-bold text-blue-900 border-r border-gray-200">
                  SUBTOTAL MOVIMIENTO PAGADURIA
                </td>
                {filteredAccounts.map(account => {
                  const subtotal = cashFlowEntries
                    .filter(entry => ['ingreso_1', 'consumo_nacional', 'ingreso_cta_pagaduria'].includes(entry.id))
                    .reduce((total, entry) => {
                      const amount = entry.accounts[account.id] || 0;
                      return entry.type === 'I' ? total + amount : total - amount;
                    }, 0);
                  
                  return (
                    <td key={account.id} className={`px-3 py-3 text-right font-bold border-r border-gray-200 ${
                      subtotal > 0 ? 'text-green-700' : subtotal < 0 ? 'text-red-700' : 'text-gray-700'
                    }`}>
                      {subtotal !== 0 && formatCurrency(Math.abs(subtotal))}
                    </td>
                  );
                })}
                <td className="px-4 py-3 text-right font-bold bg-blue-100 text-blue-900">
                  {formatCurrency(Math.abs(filteredAccounts.reduce((total, account) => {
                    const subtotal = cashFlowEntries
                      .filter(entry => ['ingreso_1', 'consumo_nacional', 'ingreso_cta_pagaduria'].includes(entry.id))
                      .reduce((sum, entry) => {
                        const amount = entry.accounts[account.id] || 0;
                        return entry.type === 'I' ? sum + amount : sum - amount;
                      }, 0);
                    return total + subtotal;
                  }, 0)))}
                </td>
              </tr>

              {/* Movement Tesoreria */}
              <tr className="bg-cyan-50 border-t border-cyan-200">
                <td className="sticky left-0 bg-cyan-50 px-4 py-3 font-bold text-cyan-900 border-r border-gray-200">
                  MOVIMIENTO TESORERIA
                </td>
                {filteredAccounts.map(account => (
                  <td key={account.id} className="px-3 py-3 text-right font-bold text-cyan-700 border-r border-gray-200">
                    7.000,00
                  </td>
                ))}
                <td className="px-4 py-3 text-right font-bold bg-cyan-100 text-cyan-900">
                  {formatCurrency(7000 * filteredAccounts.length)}
                </td>
              </tr>

              {/* Final Balance */}
              <tr className="bg-green-50 border-t-2 border-green-200">
                <td className="sticky left-0 bg-green-50 px-4 py-3 font-bold text-green-900 border-r border-gray-200">
                  SALDO TOTAL EN BANCOS
                </td>
                {filteredAccounts.map(account => {
                  const balance = getAccountBalance(account.id);
                  return (
                    <td key={account.id} className={`px-3 py-3 text-right font-bold border-r border-gray-200 ${
                      balance > 0 ? 'text-green-700' : balance < 0 ? 'text-red-700' : 'text-gray-700'
                    }`}>
                      {balance !== 0 && formatCurrency(Math.abs(balance))}
                    </td>
                  );
                })}
                <td className={`px-4 py-3 text-right font-bold text-lg bg-green-100 ${
                  getGrandTotal() > 0 ? 'text-green-700' : 'text-red-700'
                }`}>
                  {formatCurrency(Math.abs(getGrandTotal()))}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {selectedCompanies.slice(0, 4).map(company => {
          const total = getTotalByCompany(company);
          return (
            <div key={company} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${
                  total > 0 ? 'bg-gradient-to-r from-green-500 to-emerald-500' : 'bg-gradient-to-r from-red-500 to-rose-500'
                }`}>
                  <Calculator className="h-6 w-6 text-white" />
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">{company}</p>
                <p className={`text-xl font-bold ${
                  total > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(Math.abs(total))}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {bankAccounts.filter(acc => acc.company === company && selectedCompanies.includes(acc.company)).length} cuentas
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Dashboard;