import { useState, useEffect, useMemo } from 'react';

export interface Company {
  id: number;
  nombre: string;
  fechaCreacion: Date;
  estado: boolean;
}

export interface Account {
  id: number;
  banco: string;
  numeroCuenta: string;
  companyId: number;
  fechaCreacion: Date;
  estado: boolean;
}

export interface CompanyForm {
  nombre: string;
}

export interface AccountForm {
  banco: string;
  numeroCuenta: string;
  companyId: number;
}

export const useCompanies = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Datos simulados iniciales
  const mockCompanies: Company[] = useMemo(() => [
    {
      id: 1,
      nombre: 'CAPITALIZADORA',
      fechaCreacion: new Date('2024-01-15'),
      estado: true
    },
    {
      id: 2,
      nombre: 'SEGUROS BOLÍVAR',
      fechaCreacion: new Date('2024-02-20'),
      estado: true
    },
    {
      id: 3,
      nombre: 'COMERCIALES',
      fechaCreacion: new Date('2024-03-10'),
      estado: true
    },
    {
      id: 4,
      nombre: 'GRUPO BOLIVAR',
      fechaCreacion: new Date('2024-04-05'),
      estado: true
    },
    {
      id: 5,
      nombre: 'SEISA',
      fechaCreacion: new Date('2024-05-12'),
      estado: true
    },
    {
      id: 6,
      nombre: 'RIBI',
      fechaCreacion: new Date('2024-06-18'),
      estado: true
    },
    {
      id: 7,
      nombre: 'INVERSORAS',
      fechaCreacion: new Date('2024-07-22'),
      estado: true
    },
    {
      id: 8,
      nombre: 'SALUD EPS BOLIVAR',
      fechaCreacion: new Date('2024-08-14'),
      estado: true
    },
    {
      id: 9,
      nombre: 'SALUD IPS BOLIVAR',
      fechaCreacion: new Date('2024-09-25'),
      estado: true
    },
    {
      id: 10,
      nombre: 'SERVICIOS BOLIVAR',
      fechaCreacion: new Date('2024-10-30'),
      estado: true
    }
  ], []);

  const mockAccounts: Account[] = useMemo(() => [
    // CAPITALIZADORA
    {
      id: 1,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800001265',
      companyId: 1,
      fechaCreacion: new Date('2024-01-16'),
      estado: true
    },
    {
      id: 2,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800001273',
      companyId: 1,
      fechaCreacion: new Date('2024-01-17'),
      estado: true
    },
    {
      id: 3,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800002024',
      companyId: 1,
      fechaCreacion: new Date('2024-01-18'),
      estado: true
    },
    {
      id: 4,
      banco: 'BANCO REPUBLICA',
      numeroCuenta: '62250766-0',
      companyId: 1,
      fechaCreacion: new Date('2024-01-20'),
      estado: true
    },
    {
      id: 5,
      banco: 'CITIBANK COMP',
      numeroCuenta: '36203301',
      companyId: 1,
      fechaCreacion: new Date('2024-01-22'),
      estado: true
    },
    {
      id: 6,
      banco: 'JP MORGAN',
      numeroCuenta: '36203301',
      companyId: 1,
      fechaCreacion: new Date('2024-01-24'),
      estado: true
    },
    {
      id: 7,
      banco: 'DAVIVIENDA INT',
      numeroCuenta: '865784010',
      companyId: 1,
      fechaCreacion: new Date('2024-01-26'),
      estado: true
    },
    // SEGUROS BOLÍVAR
    {
      id: 8,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800001257',
      companyId: 2,
      fechaCreacion: new Date('2024-02-21'),
      estado: true
    },
    {
      id: 9,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800007882',
      companyId: 2,
      fechaCreacion: new Date('2024-02-22'),
      estado: true
    },
    {
      id: 10,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800007908',
      companyId: 2,
      fechaCreacion: new Date('2024-02-23'),
      estado: true
    },
    {
      id: 11,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800007890',
      companyId: 2,
      fechaCreacion: new Date('2024-02-24'),
      estado: true
    },
    {
      id: 12,
      banco: 'BANCO REPUBLICA',
      numeroCuenta: '62250774-0',
      companyId: 2,
      fechaCreacion: new Date('2024-02-25'),
      estado: true
    },
    {
      id: 13,
      banco: 'CITIBANK COMP',
      numeroCuenta: '36203328',
      companyId: 2,
      fechaCreacion: new Date('2024-02-26'),
      estado: true
    },
    {
      id: 14,
      banco: 'JP MORGAN',
      numeroCuenta: '36203328',
      companyId: 2,
      fechaCreacion: new Date('2024-02-27'),
      estado: true
    },
    {
      id: 15,
      banco: 'DAVIVIENDA INT',
      numeroCuenta: '865804010',
      companyId: 2,
      fechaCreacion: new Date('2024-02-28'),
      estado: true
    },
    {
      id: 16,
      banco: 'BANCO DE BOGOTA',
      numeroCuenta: '000977298',
      companyId: 2,
      fechaCreacion: new Date('2024-03-01'),
      estado: true
    },
    {
      id: 17,
      banco: 'ITAÚ',
      numeroCuenta: '005597176',
      companyId: 2,
      fechaCreacion: new Date('2024-03-02'),
      estado: true
    },
    {
      id: 18,
      banco: 'CORFIDIARIO',
      numeroCuenta: '2113700',
      companyId: 2,
      fechaCreacion: new Date('2024-03-03'),
      estado: true
    },
    // COMERCIALES
    {
      id: 19,
      banco: 'BANCO DAVIVIENDA',
      numeroCuenta: '482800001257',
      companyId: 3,
      fechaCreacion: new Date('2024-03-11'),
      estado: true
    },
    {
      id: 20,
      banco: 'BANCO REPUBLICA',
      numeroCuenta: '62250782-0',
      companyId: 3,
      fechaCreacion: new Date('2024-03-15'),
      estado: true
    },
    {
      id: 21,
      banco: 'CITIBANK COMP',
      numeroCuenta: '36025015',
      companyId: 3,
      fechaCreacion: new Date('2024-03-16'),
      estado: true
    },
    {
      id: 22,
      banco: 'JP MORGAN',
      numeroCuenta: '36025015',
      companyId: 3,
      fechaCreacion: new Date('2024-03-17'),
      estado: true
    },
    {
      id: 23,
      banco: 'DAVIVIENDA INT',
      numeroCuenta: '865794010',
      companyId: 3,
      fechaCreacion: new Date('2024-03-18'),
      estado: true
    },
    {
      id: 24,
      banco: 'BANCO DE BOGOTA',
      numeroCuenta: '036273662',
      companyId: 3,
      fechaCreacion: new Date('2024-03-19'),
      estado: true
    },
    {
      id: 25,
      banco: 'BANCOLOMBIA',
      numeroCuenta: '5300635932',
      companyId: 3,
      fechaCreacion: new Date('2024-03-20'),
      estado: true
    },
    {
      id: 26,
      banco: 'BANCO POPULAR',
      numeroCuenta: '40195224',
      companyId: 3,
      fechaCreacion: new Date('2024-03-21'),
      estado: true
    },
    {
      id: 27,
      banco: 'BBVA',
      numeroCuenta: '137017554',
      companyId: 3,
      fechaCreacion: new Date('2024-03-22'),
      estado: true
    },
    // GRUPO BOLIVAR
    {
      id: 28,
      banco: 'DAVIVIENDA INT',
      numeroCuenta: '867614010',
      companyId: 4,
      fechaCreacion: new Date('2024-04-06'),
      estado: true
    },
    {
      id: 29,
      banco: 'DAVIVIENDA',
      numeroCuenta: '010002000127',
      companyId: 4,
      fechaCreacion: new Date('2024-04-07'),
      estado: true
    },
    {
      id: 30,
      banco: 'BANCO DE BOGOTA',
      numeroCuenta: '000977280',
      companyId: 4,
      fechaCreacion: new Date('2024-04-08'),
      estado: true
    },
    // SEISA
    {
      id: 31,
      banco: 'DAVIVIENDA INT',
      numeroCuenta: '010003000003',
      companyId: 5,
      fechaCreacion: new Date('2024-05-13'),
      estado: true
    },
    // RIBI
    {
      id: 32,
      banco: 'DAVIVIENDA INT',
      numeroCuenta: '010003000003',
      companyId: 6,
      fechaCreacion: new Date('2024-06-19'),
      estado: true
    }
  ], []);

  // Inicializar datos
  useEffect(() => {
    setLoading(true);
    // Simular carga de datos
    setTimeout(() => {
      const savedCompanies = localStorage.getItem('companies');
      const savedAccounts = localStorage.getItem('accounts');
      
      if (savedCompanies) {
        const parsedCompanies = JSON.parse(savedCompanies);
        setCompanies(parsedCompanies.map((c: any) => ({
          ...c,
          fechaCreacion: new Date(c.fechaCreacion)
        })));
      } else {
        setCompanies(mockCompanies);
        localStorage.setItem('companies', JSON.stringify(mockCompanies));
      }
      
      if (savedAccounts) {
        const parsedAccounts = JSON.parse(savedAccounts);
        setAccounts(parsedAccounts.map((a: any) => ({
          ...a,
          fechaCreacion: new Date(a.fechaCreacion)
        })));
      } else {
        setAccounts(mockAccounts);
        localStorage.setItem('accounts', JSON.stringify(mockAccounts));
      }
      
      setLoading(false);
    }, 800);
  }, [mockCompanies, mockAccounts]);

  // Guardar en localStorage cuando cambien los datos
  useEffect(() => {
    if (companies.length > 0) {
      localStorage.setItem('companies', JSON.stringify(companies));
    }
  }, [companies]);

  useEffect(() => {
    if (accounts.length > 0) {
      localStorage.setItem('accounts', JSON.stringify(accounts));
    }
  }, [accounts]);

  // Funciones CRUD para Compañías
  const addCompany = async (companyData: CompanyForm): Promise<void> => {
    try {
      setLoading(true);
      // Simular llamada API
      await new Promise(resolve => setTimeout(resolve, 500));

      const newCompany: Company = {
        id: Math.max(...companies.map(c => c.id), 0) + 1,
        nombre: companyData.nombre,
        fechaCreacion: new Date(),
        estado: true
      };

      setCompanies(prev => [...prev, newCompany]);
      setLoading(false);
    } catch (err) {
      setError('Error al crear la compañía');
      setLoading(false);
      throw err;
    }
  };

  const updateCompany = async (id: number, companyData: CompanyForm): Promise<void> => {
    try {
      setLoading(true);
      // Simular llamada API
      await new Promise(resolve => setTimeout(resolve, 500));

      setCompanies(prev => prev.map(company => 
        company.id === id 
          ? { ...company, nombre: companyData.nombre }
          : company
      ));
      setLoading(false);
    } catch (err) {
      setError('Error al actualizar la compañía');
      setLoading(false);
      throw err;
    }
  };

  const deleteCompany = async (id: number): Promise<void> => {
    try {
      setLoading(true);
      // Simular llamada API
      await new Promise(resolve => setTimeout(resolve, 500));

      // Eliminar compañía y sus cuentas asociadas
      setCompanies(prev => prev.filter(company => company.id !== id));
      setAccounts(prev => prev.filter(account => account.companyId !== id));
      setLoading(false);
    } catch (err) {
      setError('Error al eliminar la compañía');
      setLoading(false);
      throw err;
    }
  };

  // Funciones CRUD para Cuentas
  const addAccount = async (accountData: AccountForm): Promise<void> => {
    try {
      setLoading(true);
      // Simular llamada API
      await new Promise(resolve => setTimeout(resolve, 500));

      const newAccount: Account = {
        id: Math.max(...accounts.map(a => a.id), 0) + 1,
        banco: accountData.banco,
        numeroCuenta: accountData.numeroCuenta,
        companyId: accountData.companyId,
        fechaCreacion: new Date(),
        estado: true
      };

      setAccounts(prev => [...prev, newAccount]);
      setLoading(false);
    } catch (err) {
      setError('Error al crear la cuenta');
      setLoading(false);
      throw err;
    }
  };

  const updateAccount = async (id: number, accountData: AccountForm): Promise<void> => {
    try {
      setLoading(true);
      // Simular llamada API
      await new Promise(resolve => setTimeout(resolve, 500));

      setAccounts(prev => prev.map(account => 
        account.id === id 
          ? { 
              ...account, 
              banco: accountData.banco,
              numeroCuenta: accountData.numeroCuenta,
              companyId: accountData.companyId
            }
          : account
      ));
      setLoading(false);
    } catch (err) {
      setError('Error al actualizar la cuenta');
      setLoading(false);
      throw err;
    }
  };

  const deleteAccount = async (id: number): Promise<void> => {
    try {
      setLoading(true);
      // Simular llamada API
      await new Promise(resolve => setTimeout(resolve, 500));

      setAccounts(prev => prev.filter(account => account.id !== id));
      setLoading(false);
    } catch (err) {
      setError('Error al eliminar la cuenta');
      setLoading(false);
      throw err;
    }
  };

  // Obtener cuentas por compañía
  const getAccountsByCompany = (companyId: number): Account[] => {
    return accounts.filter(account => account.companyId === companyId);
  };

  // Validar si existe una cuenta
  const accountExists = (banco: string, numeroCuenta: string, excludeId?: number): boolean => {
    return accounts.some(account => 
      account.banco === banco && 
      account.numeroCuenta === numeroCuenta &&
      account.id !== excludeId
    );
  };

  // Validar si existe una compañía
  const companyExists = (nombre: string, excludeId?: number): boolean => {
    return companies.some(company => 
      company.nombre.toLowerCase() === nombre.toLowerCase() &&
      company.id !== excludeId
    );
  };

  return {
    companies,
    accounts,
    loading,
    error,
    addCompany,
    updateCompany,
    deleteCompany,
    addAccount,
    updateAccount,
    deleteAccount,
    getAccountsByCompany,
    accountExists,
    companyExists
  };
};
