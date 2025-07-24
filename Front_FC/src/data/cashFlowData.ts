export interface BankAccount {
  id: string;
  company: string;
  bank: string;
  accountNumber: string;
  currency: 'COP' | 'USD';
  type: 'NORMAL' | 'AHORRO' | 'ARL';
}

export interface CashFlowEntry {
  id: string;
  concept: string;
  type: 'I' | 'E'; // Ingreso o Egreso
  date: string; // Fecha del movimiento
  accounts: Record<string, number>; // accountId -> amount
}

export interface DailyCashFlow {
  date: string;
  entries: CashFlowEntry[];
}

export const bankAccounts: BankAccount[] = [
  // CAPITALIZADORA
  { id: 'cap_dav_1', company: 'CAPITALIZADORA', bank: 'BANCO DAVIVIENDA', accountNumber: '006069999420', currency: 'COP', type: 'NORMAL' },
  { id: 'cap_rep_1', company: 'CAPITALIZADORA', bank: 'BANCO REPUBLICA', accountNumber: '62250766-0', currency: 'COP', type: 'NORMAL' },
  { id: 'cap_citi_usd', company: 'CAPITALIZADORA', bank: 'CITIBANK COMP', accountNumber: '36203301', currency: 'USD', type: 'NORMAL' },
  { id: 'cap_citi_cop', company: 'CAPITALIZADORA', bank: 'CITIBANK COMP', accountNumber: '36203301', currency: 'COP', type: 'NORMAL' },
  { id: 'cap_jp_usd', company: 'CAPITALIZADORA', bank: 'JP MORGAN', accountNumber: '', currency: 'USD', type: 'NORMAL' },
  { id: 'cap_jp_cop', company: 'CAPITALIZADORA', bank: 'JP MORGAN', accountNumber: '', currency: 'COP', type: 'NORMAL' },
  { id: 'cap_dav_int_usd', company: 'CAPITALIZADORA', bank: 'DAVIVIENDA INT', accountNumber: '865784010', currency: 'USD', type: 'NORMAL' },
  { id: 'cap_dav_int_cop', company: 'CAPITALIZADORA', bank: 'DAVIVIENDA INT', accountNumber: '865784010', currency: 'COP', type: 'NORMAL' },
  
  // BOLÍVAR
  { id: 'bol_dav_1', company: 'BOLÍVAR', bank: 'BANCO DAVIVIENDA', accountNumber: '006069999412', currency: 'COP', type: 'NORMAL' },
  { id: 'bol_rep_1', company: 'BOLÍVAR', bank: 'BANCO REPUBLICA', accountNumber: '62250774-0', currency: 'COP', type: 'NORMAL' },
  { id: 'bol_citi_usd', company: 'BOLÍVAR', bank: 'CITIBANK COMP', accountNumber: '36203328', currency: 'USD', type: 'NORMAL' },
  { id: 'bol_citi_cop', company: 'BOLÍVAR', bank: 'CITIBANK COMP', accountNumber: '36203328', currency: 'COP', type: 'NORMAL' },
  { id: 'bol_dav_int_usd', company: 'BOLÍVAR', bank: 'DAVIVIENDA INT', accountNumber: '865804010', currency: 'USD', type: 'NORMAL' },
  { id: 'bol_dav_int_cop', company: 'BOLÍVAR', bank: 'DAVIVIENDA INT', accountNumber: '865804010', currency: 'COP', type: 'NORMAL' },
  
  // COMERCIALES
  { id: 'com_dav_1', company: 'COMERCIALES', bank: 'BANCO DAVIVIENDA', accountNumber: '006069999404', currency: 'COP', type: 'NORMAL' },
  { id: 'com_rep_1', company: 'COMERCIALES', bank: 'BANCO REPUBLICA', accountNumber: '62250782-0', currency: 'COP', type: 'NORMAL' },
  { id: 'com_citi_usd', company: 'COMERCIALES', bank: 'CITIBANK COMP', accountNumber: '36025015', currency: 'USD', type: 'NORMAL' },
  { id: 'com_citi_cop', company: 'COMERCIALES', bank: 'CITIBANK COMP', accountNumber: '36025015', currency: 'COP', type: 'NORMAL' },
  { id: 'com_dav_int_usd', company: 'COMERCIALES', bank: 'DAVIVIENDA INT', accountNumber: '865794010', currency: 'USD', type: 'NORMAL' },
  { id: 'com_dav_int_cop', company: 'COMERCIALES', bank: 'DAVIVIENDA INT', accountNumber: '865794010', currency: 'COP', type: 'NORMAL' },
  
  // AHORRO ACCOUNTS
  { id: 'cap_aho_dav', company: 'CAPITALIZADORA AHO', bank: 'BANCO DAVIVIENDA', accountNumber: '482800001265', currency: 'COP', type: 'AHORRO' },
  { id: 'bol_aho_dav', company: 'BOLÍVAR AHO', bank: 'BANCO DAVIVIENDA', accountNumber: '482800001273', currency: 'COP', type: 'AHORRO' },
  { id: 'bol_arl_dav', company: 'BOLÍVAR ARL', bank: 'BANCO DAVIVIENDA', accountNumber: '482800002024', currency: 'COP', type: 'ARL' },
  { id: 'com_aho_dav', company: 'COMERCIALES AHO', bank: 'BANCO DAVIVIENDA', accountNumber: '482800001257', currency: 'COP', type: 'AHORRO' },
];

// Datos de ejemplo para múltiples días
export const dailyCashFlowData: DailyCashFlow[] = [
  {
    date: '2025-01-22',
    entries: [
      {
        id: 'saldo_anterior',
        concept: 'SALDO DIA ANTERIOR',
        type: 'I',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 0,
          'bol_dav_1': 0,
          'com_dav_1': 0,
        }
      },
      {
        id: 'ingreso_1',
        concept: 'INGRESO',
        type: 'I',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 30150.00,
          'bol_dav_1': 14021764.91,
          'com_dav_1': 7807589.11,
        }
      },
      {
        id: 'egreso_1',
        concept: 'EGRESO',
        type: 'E',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 0,
          'bol_dav_1': 0,
          'com_dav_1': 0,
        }
      },
      {
        id: 'consumo_nacional',
        concept: 'CONSUMO NACIONAL',
        type: 'E',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 1367.78,
          'bol_dav_1': -184532.99,
          'com_dav_1': 15468.87,
        }
      },
      {
        id: 'ingreso_cta_pagaduria',
        concept: 'INGRESO CTA PAGADURIA',
        type: 'I',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 1971.00,
          'bol_dav_1': 0,
          'com_dav_1': 0,
        }
      },
      {
        id: 'recaudos_libertador',
        concept: 'RECAUDOS LIBERTADOR',
        type: 'I',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 0,
          'bol_dav_1': 0,
          'com_dav_1': 193685.22,
        }
      },
      {
        id: 'otros_pagos',
        concept: 'OTROS PAGOS',
        type: 'E',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 6.27,
          'bol_dav_1': 0,
          'com_dav_1': 18.23,
        }
      },
      {
        id: 'ventan_proveedores',
        concept: 'VENTAN PROVEEDORES',
        type: 'E',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 35247.82,
          'bol_dav_1': 0,
          'com_dav_1': 2023902.76,
        }
      },
      {
        id: 'nomina_administrativa',
        concept: 'NOMINA ADMINISTRATIVA',
        type: 'E',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 150.00,
          'bol_dav_1': 237.93,
          'com_dav_1': 7315.60,
        }
      },
      {
        id: 'nomina_pensiones',
        concept: 'NOMINA PENSIONES',
        type: 'E',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 0,
          'bol_dav_1': 22271218.01,
          'com_dav_1': 0,
        }
      },
      {
        id: 'otros_imptos',
        concept: 'OTROS IMPTOS',
        type: 'E',
        date: '2025-01-22',
        accounts: {
          'cap_dav_1': 0,
          'bol_dav_1': 0,
          'com_dav_1': 4557.60,
        }
      },
    ]
  },
  {
    date: '2025-01-21',
    entries: [
      {
        id: 'saldo_anterior',
        concept: 'SALDO DIA ANTERIOR',
        type: 'I',
        date: '2025-01-21',
        accounts: {
          'cap_dav_1': 15000.00,
          'bol_dav_1': 8500000.00,
          'com_dav_1': 3200000.00,
        }
      },
      {
        id: 'ingreso_1',
        concept: 'INGRESO',
        type: 'I',
        date: '2025-01-21',
        accounts: {
          'cap_dav_1': 25000.00,
          'bol_dav_1': 12000000.00,
          'com_dav_1': 6500000.00,
        }
      },
      {
        id: 'consumo_nacional',
        concept: 'CONSUMO NACIONAL',
        type: 'E',
        date: '2025-01-21',
        accounts: {
          'cap_dav_1': 800.00,
          'bol_dav_1': 150000.00,
          'com_dav_1': 12000.00,
        }
      },
      {
        id: 'otros_pagos',
        concept: 'OTROS PAGOS',
        type: 'E',
        date: '2025-01-21',
        accounts: {
          'cap_dav_1': 5.50,
          'bol_dav_1': 0,
          'com_dav_1': 15.75,
        }
      },
    ]
  },
  {
    date: '2025-01-20',
    entries: [
      {
        id: 'saldo_anterior',
        concept: 'SALDO DIA ANTERIOR',
        type: 'I',
        date: '2025-01-20',
        accounts: {
          'cap_dav_1': 12000.00,
          'bol_dav_1': 7800000.00,
          'com_dav_1': 2900000.00,
        }
      },
      {
        id: 'ingreso_1',
        concept: 'INGRESO',
        type: 'I',
        date: '2025-01-20',
        accounts: {
          'cap_dav_1': 18000.00,
          'bol_dav_1': 9500000.00,
          'com_dav_1': 5200000.00,
        }
      },
      {
        id: 'consumo_nacional',
        concept: 'CONSUMO NACIONAL',
        type: 'E',
        date: '2025-01-20',
        accounts: {
          'cap_dav_1': 1200.00,
          'bol_dav_1': 180000.00,
          'com_dav_1': 8500.00,
        }
      },
    ]
  }
];