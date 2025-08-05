import { useState, useMemo } from 'react';
import { format, eachWeekOfInterval, eachMonthOfInterval } from 'date-fns';
import { es } from 'date-fns/locale';

export interface FlowData {
  period: string;
  date: Date;
  CAPITALIZADORA: number;
  BOLÍVAR: number;
  COMERCIALES: number;
  total: number;
  ingresos: number;
  egresos: number;
}

export interface AccountData {
  [company: string]: {
    [account: string]: {
      ingresos: number;
      egresos: number;
      saldo: number;
    };
  };
}

export interface DateRange {
  start: Date;
  end: Date;
}

export const useMonthlyFlow = (
  period: 'week' | 'month' | 'year',
  dateRange: DateRange
) => {
  const [loading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Simular datos del backend
  const generateMockData = useMemo((): FlowData[] => {
    const data: FlowData[] = [];
    const { start, end } = dateRange;
    
    let intervals: Date[] = [];
    
    try {
      if (period === 'week') {
        intervals = eachWeekOfInterval({ start, end }, { weekStartsOn: 1 });
      } else if (period === 'month') {
        intervals = eachMonthOfInterval({ start, end });
      } else {
        // Para año, usar trimestres
        intervals = [
          new Date(2025, 0, 1),  // Q1
          new Date(2025, 3, 1),  // Q2
          new Date(2025, 6, 1),  // Q3
          new Date(2025, 9, 1)   // Q4
        ];
      }

      intervals.forEach((date, index) => {
        // Generar datos más realistas con tendencias
        const baseMultiplier = 1 + (index * 0.1); // Crecimiento gradual
        const seasonalFactor = 1 + Math.sin((index * Math.PI) / 6) * 0.2; // Variación estacional
        
        const cap = (Math.random() * 3000000 + 2000000) * baseMultiplier * seasonalFactor;
        const bolivar = (Math.random() * 8000000 + 12000000) * baseMultiplier * seasonalFactor;
        const comerciales = (Math.random() * 4000000 + 6000000) * baseMultiplier * seasonalFactor;
        
        const totalFlow = cap + bolivar + comerciales;
        const ingresos = totalFlow * (0.6 + Math.random() * 0.2);
        const egresos = totalFlow * (0.4 + Math.random() * 0.2);

        let periodLabel = '';
        if (period === 'week') {
          periodLabel = `Sem ${format(date, 'w', { locale: es })} - ${format(date, 'MMM', { locale: es })}`;
        } else if (period === 'month') {
          periodLabel = format(date, 'MMM yyyy', { locale: es });
        } else {
          periodLabel = `Q${Math.floor(index) + 1} 2025`;
        }

        data.push({
          period: periodLabel,
          date,
          CAPITALIZADORA: Math.round(cap),
          BOLÍVAR: Math.round(bolivar),
          COMERCIALES: Math.round(comerciales),
          total: Math.round(totalFlow),
          ingresos: Math.round(ingresos),
          egresos: Math.round(egresos)
        });
      });
    } catch (err) {
      console.error('Error generating data:', err);
      setError('Error al generar datos');
    }
    
    return data;
  }, [period, dateRange]);

  // Datos de cuentas por empresa
  const accountsData: AccountData = useMemo(() => ({
    'CAPITALIZADORA': {
      'BANCO DAVIVIENDA - 006069999420': { 
        ingresos: 3500000, 
        egresos: 2400000, 
        saldo: 1100000 
      },
      'BANCO REPUBLICA - 62250766-0': { 
        ingresos: 1800000, 
        egresos: 1200000, 
        saldo: 600000 
      }
    },
    'BOLÍVAR': {
      'BANCO DAVIVIENDA - 006069999412': { 
        ingresos: 15000000, 
        egresos: 10500000, 
        saldo: 4500000 
      },
      'BANCO REPUBLICA - 62250774-0': { 
        ingresos: 9500000, 
        egresos: 7200000, 
        saldo: 2300000 
      }
    },
    'COMERCIALES': {
      'BANCO DAVIVIENDA - 006069999404': { 
        ingresos: 8200000, 
        egresos: 5400000, 
        saldo: 2800000 
      },
      'BANCO REPUBLICA - 62250782-0': { 
        ingresos: 4100000, 
        egresos: 3200000, 
        saldo: 900000 
      }
    }
  }), []);

  // Calcular métricas totales
  const metrics = useMemo(() => {
    const totalIngresos = generateMockData.reduce((sum, item) => sum + item.ingresos, 0);
    const totalEgresos = generateMockData.reduce((sum, item) => sum + item.egresos, 0);
    const totalSaldo = totalIngresos - totalEgresos;
    
    const promedioIngresos = totalIngresos / generateMockData.length;
    const promedioEgresos = totalEgresos / generateMockData.length;

    return {
      totalIngresos,
      totalEgresos,
      totalSaldo,
      promedioIngresos,
      promedioEgresos,
      crecimientoMensual: generateMockData.length > 1 
        ? ((generateMockData[generateMockData.length - 1].total - generateMockData[0].total) / generateMockData[0].total) * 100
        : 0
    };
  }, [generateMockData]);

  // Función para exportar datos
  const exportData = (exportFormat: 'csv' | 'json' = 'csv') => {
    const currentDate = new Date();
    const dateStr = format(currentDate, 'yyyy-MM-dd');
    
    if (exportFormat === 'csv') {
      const headers = ['Período', 'Capitalizadora', 'Bolívar', 'Comerciales', 'Total', 'Ingresos', 'Egresos'];
      const csvContent = [
        headers.join(','),
        ...generateMockData.map(item => [
          item.period,
          item.CAPITALIZADORA,
          item.BOLÍVAR,
          item.COMERCIALES,
          item.total,
          item.ingresos,
          item.egresos
        ].join(','))
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      const fileName = `flujo_mensual_${period}_${dateStr}.csv`;
      link.setAttribute('download', fileName);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      const jsonContent = JSON.stringify({ data: generateMockData, metrics, accountsData }, null, 2);
      const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      const fileName = `flujo_mensual_${period}_${dateStr}.json`;
      link.setAttribute('download', fileName);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return {
    data: generateMockData,
    accountsData,
    metrics,
    loading,
    error,
    exportData
  };
};
