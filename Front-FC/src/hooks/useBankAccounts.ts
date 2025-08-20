import { useState, useCallback } from 'react';

export interface BankAccount {
  id: number;
  numero_cuenta: string;
  compania_id: number;
  banco_id: number;
  monedas: ('COP' | 'USD' | 'EUR')[];
  tipo_cuenta: 'CORRIENTE' | 'AHORROS';
  banco_nombre?: string;
  compania_nombre?: string;
}

export interface Bank {
  id: number;
  nombre: string;
}

export interface CreateBankAccountData {
  numero_cuenta: string;
  banco_id: number;
  monedas: ('COP' | 'USD' | 'EUR')[];
  tipo_cuenta: 'CORRIENTE' | 'AHORROS';
}

export interface UpdateBankAccountData {
  numero_cuenta?: string;
  banco_id?: number;
  monedas?: ('COP' | 'USD' | 'EUR')[];
  tipo_cuenta?: 'CORRIENTE' | 'AHORROS';
}

export const useBankAccounts = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  };

  const getCompanyBankAccounts = useCallback(async (companyId: number): Promise<BankAccount[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/bank-accounts/test/companies/${companyId}`, {
        method: 'GET',
        headers: getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Error al obtener las cuentas bancarias');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createBankAccount = useCallback(async (companyId: number, accountData: CreateBankAccountData): Promise<BankAccount> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/bank-accounts/test/companies/${companyId}`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(accountData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear la cuenta bancaria');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateBankAccount = useCallback(async (accountId: number, accountData: UpdateBankAccountData): Promise<BankAccount> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/bank-accounts/${accountId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(accountData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al actualizar la cuenta bancaria');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteBankAccount = useCallback(async (accountId: number): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/bank-accounts/test/${accountId}`, {
        method: 'DELETE',
        headers: getHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al eliminar la cuenta bancaria');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getAllBanks = useCallback(async (): Promise<Bank[]> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/bank-accounts/test/banks`, {
        method: 'GET',
        headers: getHeaders(),
      });

      if (!response.ok) {
        throw new Error('Error al obtener los bancos');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getCompanyBankAccounts,
    createBankAccount,
    updateBankAccount,
    deleteBankAccount,
    getAllBanks,
  };
};
