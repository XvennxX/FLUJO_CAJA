import { useState, useMemo } from 'react';
import { useCashFlow } from './useCashFlow';

interface CompanyBalance {
  company: string;
  pagaduria: {
    ingresos: number;
    egresos: number;
    saldo: number;
  };
  tesoreria: {
    ingresos: number;
    egresos: number;
    saldo: number;
  };
  total: number;
  status: 'pendiente' | 'evaluado' | 'confirmado' | 'cerrado';
}

interface ConciliationTotals {
  pagaduriaIngresos: number;
  pagaduriaEgresos: number;
  tesoreriaIngresos: number;
  tesoreriaEgresos: number;
  total: number;
}

export const useConciliacion = () => {
  const { transactions } = useCashFlow();
  
  const [conciliationStatus, setConciliationStatus] = useState<{[key: string]: string}>({
    'CAPITALIZADORA': 'pendiente',
    'SEGUROS BOLÍVAR': 'evaluado',
    'COMERCIALES': 'pendiente'
  });

  // Calcular balances por compañía
  const companyBalances = useMemo((): CompanyBalance[] => {
    const companies = ['CAPITALIZADORA', 'SEGUROS BOLÍVAR', 'COMERCIALES'];
    
    return companies.map(company => {
      // Filtrar transacciones por compañía
      const companyTransactions = transactions.filter(t => 
        t.description.toLowerCase().includes(company.toLowerCase()) ||
        t.category.toLowerCase().includes(company.toLowerCase())
      );

      // Separar por módulo (simulado basado en categorías o descripción)
      const pagaduriaTransactions = companyTransactions.filter(t => 
        t.category.toLowerCase().includes('nómina') ||
        t.category.toLowerCase().includes('payroll') ||
        t.category.toLowerCase().includes('pagaduría') ||
        t.description.toLowerCase().includes('nómina') ||
        t.category.toLowerCase().includes('salarios') ||
        t.category.toLowerCase().includes('personal')
      );

      const tesoreriaTransactions = companyTransactions.filter(t => 
        !pagaduriaTransactions.includes(t)
      );

      // Calcular totales para Pagaduría
      const pagaduriaIngresos = pagaduriaTransactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
      
      const pagaduriaEgresos = pagaduriaTransactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);

      // Calcular totales para Tesorería
      const tesoreriaIngresos = tesoreriaTransactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
      
      const tesoreriaEgresos = tesoreriaTransactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);

      const pagaduriaSaldo = pagaduriaIngresos - pagaduriaEgresos;
      const tesoreriaSaldo = tesoreriaIngresos - tesoreriaEgresos;
      const total = pagaduriaSaldo + tesoreriaSaldo;

      return {
        company,
        pagaduria: {
          ingresos: pagaduriaIngresos,
          egresos: pagaduriaEgresos,
          saldo: pagaduriaSaldo
        },
        tesoreria: {
          ingresos: tesoreriaIngresos,
          egresos: tesoreriaEgresos,
          saldo: tesoreriaSaldo
        },
        total,
        status: conciliationStatus[company] as 'pendiente' | 'evaluado' | 'confirmado' | 'cerrado'
      };
    });
  }, [transactions, conciliationStatus]);

  // Función para calcular totales generales
  const calculateTotals = (balances: CompanyBalance[]): ConciliationTotals => {
    return balances.reduce((acc, balance) => {
      acc.pagaduriaIngresos += balance.pagaduria.ingresos;
      acc.pagaduriaEgresos += balance.pagaduria.egresos;
      acc.tesoreriaIngresos += balance.tesoreria.ingresos;
      acc.tesoreriaEgresos += balance.tesoreria.egresos;
      acc.total += balance.total;
      return acc;
    }, {
      pagaduriaIngresos: 0,
      pagaduriaEgresos: 0,
      tesoreriaIngresos: 0,
      tesoreriaEgresos: 0,
      total: 0
    });
  };

  // Función para actualizar el estado de una compañía
  const updateCompanyStatus = (company: string, newStatus: string) => {
    setConciliationStatus(prev => ({
      ...prev,
      [company]: newStatus
    }));
  };

  // Función para evaluar todas las compañías pendientes
  const evaluarTodas = () => {
    const newStatus = { ...conciliationStatus };
    Object.keys(newStatus).forEach(company => {
      if (newStatus[company] === 'pendiente') {
        newStatus[company] = 'evaluado';
      }
    });
    setConciliationStatus(newStatus);
  };

  // Función para confirmar todas las compañías evaluadas
  const confirmarTodas = () => {
    const newStatus = { ...conciliationStatus };
    Object.keys(newStatus).forEach(company => {
      if (newStatus[company] === 'evaluado') {
        newStatus[company] = 'confirmado';
      }
    });
    setConciliationStatus(newStatus);
  };

  // Función para cerrar todas las compañías confirmadas
  const cerrarTodas = () => {
    const newStatus = { ...conciliationStatus };
    Object.keys(newStatus).forEach(company => {
      if (newStatus[company] === 'confirmado') {
        newStatus[company] = 'cerrado';
      }
    });
    setConciliationStatus(newStatus);
  };

  // Función para obtener el siguiente estado en el flujo
  const getNextStatus = (currentStatus: string): string | null => {
    const statusFlow = ['pendiente', 'evaluado', 'confirmado', 'cerrado'];
    const currentIndex = statusFlow.indexOf(currentStatus);
    return currentIndex < statusFlow.length - 1 ? statusFlow[currentIndex + 1] : null;
  };

  // Función para obtener el estado anterior en el flujo
  const getPreviousStatus = (currentStatus: string): string | null => {
    const statusFlow = ['pendiente', 'evaluado', 'confirmado', 'cerrado'];
    const currentIndex = statusFlow.indexOf(currentStatus);
    return currentIndex > 0 ? statusFlow[currentIndex - 1] : null;
  };

  // Función para verificar si se puede cambiar el estado
  const canChangeStatus = (currentStatus: string, newStatus: string): boolean => {
    const statusFlow = ['pendiente', 'evaluado', 'confirmado', 'cerrado'];
    const currentIndex = statusFlow.indexOf(currentStatus);
    const newIndex = statusFlow.indexOf(newStatus);
    
    // Solo permitir avanzar en el flujo o retroceder un paso
    return newIndex === currentIndex + 1 || newIndex === currentIndex - 1;
  };

  return {
    companyBalances,
    conciliationStatus,
    updateCompanyStatus,
    calculateTotals,
    evaluarTodas,
    confirmarTodas,
    cerrarTodas,
    getNextStatus,
    getPreviousStatus,
    canChangeStatus
  };
};
