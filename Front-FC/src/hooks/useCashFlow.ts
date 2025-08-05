import { useState, useMemo } from 'react';
import { Transaction, Category, CashFlowSummary } from '../types';

const defaultCategories: Category[] = [
  { id: '1', name: 'Salario', type: 'income', color: '#10B981' },
  { id: '2', name: 'Ventas', type: 'income', color: '#059669' },
  { id: '3', name: 'Inversiones', type: 'income', color: '#047857' },
  { id: '4', name: 'Otros Ingresos', type: 'income', color: '#065F46' },
  { id: '5', name: 'Alimentación', type: 'expense', color: '#EF4444' },
  { id: '6', name: 'Transporte', type: 'expense', color: '#DC2626' },
  { id: '7', name: 'Servicios', type: 'expense', color: '#B91C1C' },
  { id: '8', name: 'Entretenimiento', type: 'expense', color: '#991B1B' },
  { id: '9', name: 'Salud', type: 'expense', color: '#7F1D1D' },
  { id: '10', name: 'Otros Gastos', type: 'expense', color: '#6B1B1B' },
];

const initialTransactions: Transaction[] = [
  {
    id: '1',
    description: 'Salario mensual',
    amount: 3500,
    category: 'Salario',
    type: 'income',
    date: '2025-01-15',
    createdAt: new Date('2025-01-15'),
    userId: '1',
  },
  {
    id: '2',
    description: 'Supermercado',
    amount: 150,
    category: 'Alimentación',
    type: 'expense',
    date: '2025-01-14',
    createdAt: new Date('2025-01-14'),
    userId: '1',
  },
  {
    id: '3',
    description: 'Gasolina',
    amount: 80,
    category: 'Transporte',
    type: 'expense',
    date: '2025-01-13',
    createdAt: new Date('2025-01-13'),
    userId: '1',
  },
];

export const useCashFlow = () => {
  const [transactions, setTransactions] = useState<Transaction[]>(initialTransactions);
  const [categories] = useState<Category[]>(defaultCategories);

  const addTransaction = (transaction: Omit<Transaction, 'id' | 'createdAt'>) => {
    const newTransaction: Transaction = {
      ...transaction,
      id: Date.now().toString(),
      createdAt: new Date(),
      userId: '1', // En una app real, esto vendría del contexto de autenticación
    };
    setTransactions(prev => [newTransaction, ...prev]);
  };

  const deleteTransaction = (id: string) => {
    setTransactions(prev => prev.filter(t => t.id !== id));
  };

  const updateTransaction = (id: string, updates: Partial<Transaction>) => {
    setTransactions(prev =>
      prev.map(t => (t.id === id ? { ...t, ...updates } : t))
    );
  };

  const summary: CashFlowSummary = useMemo(() => {
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    const totalIncome = transactions
      .filter(t => t.type === 'income')
      .reduce((sum, t) => sum + t.amount, 0);

    const totalExpenses = transactions
      .filter(t => t.type === 'expense')
      .reduce((sum, t) => sum + t.amount, 0);

    const monthlyIncome = transactions
      .filter(t => {
        const transactionDate = new Date(t.date);
        return (
          t.type === 'income' &&
          transactionDate.getMonth() === currentMonth &&
          transactionDate.getFullYear() === currentYear
        );
      })
      .reduce((sum, t) => sum + t.amount, 0);

    const monthlyExpenses = transactions
      .filter(t => {
        const transactionDate = new Date(t.date);
        return (
          t.type === 'expense' &&
          transactionDate.getMonth() === currentMonth &&
          transactionDate.getFullYear() === currentYear
        );
      })
      .reduce((sum, t) => sum + t.amount, 0);

    return {
      totalIncome,
      totalExpenses,
      balance: totalIncome - totalExpenses,
      monthlyIncome,
      monthlyExpenses,
    };
  }, [transactions]);

  const getCategoryData = () => {
    const categoryTotals = categories.map(category => {
      const total = transactions
        .filter(t => t.category === category.name)
        .reduce((sum, t) => sum + t.amount, 0);
      return { ...category, total };
    });

    return categoryTotals.filter(c => c.total > 0);
  };

  return {
    transactions,
    categories,
    summary,
    addTransaction,
    deleteTransaction,
    updateTransaction,
    getCategoryData,
  };
};