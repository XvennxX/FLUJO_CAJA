import { useState, useEffect } from 'react';

export interface Company {
  id: number;
  nombre: string;
}

export interface CompanyForm {
  nombre: string;
}

export const useCompanies = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Obtener token del localStorage
  const getToken = () => {
    return localStorage.getItem('access_token');
  };

  // Headers para las peticiones API
  const getHeaders = () => {
    const token = getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  };

  // Cargar compañías desde el API
  const fetchCompanies = async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = getHeaders();
      console.log('Fetching companies with headers:', headers);
      
      const response = await fetch('http://localhost:8000/api/v1/companies/test', {
        headers: headers
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('No tienes autorización para ver las compañías. Por favor, inicia sesión.');
        }
        if (response.status === 401) {
          throw new Error('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.');
        }
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Companies data:', data);
      setCompanies(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error fetching companies:', err);
    } finally {
      setLoading(false);
    }
  };

  // Agregar nueva compañía
  const addCompany = async (companyData: CompanyForm): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/companies/test', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(companyData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear la compañía');
      }

      const newCompany = await response.json();
      setCompanies(prev => [...prev, newCompany]);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error adding company:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Actualizar compañía
  const updateCompany = async (id: number, companyData: CompanyForm): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/companies/test/${id}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(companyData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al actualizar la compañía');
      }

      const updatedCompany = await response.json();
      setCompanies(prev => prev.map(company => 
        company.id === id ? updatedCompany : company
      ));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error updating company:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Eliminar compañía
  const deleteCompany = async (id: number): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/companies/test/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al eliminar la compañía');
      }

      setCompanies(prev => prev.filter(company => company.id !== id));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error deleting company:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Cargar compañías al montar el componente
  useEffect(() => {
    fetchCompanies();
  }, []);

  return {
    companies,
    loading,
    error,
    addCompany,
    updateCompany,
    deleteCompany,
    refetch: fetchCompanies
  };
};
