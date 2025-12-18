import React, { useEffect, useState } from 'react';
import { 
  Calendar, 
  Save, 
  AlertCircle, 
  DollarSign, 
  Building2, 
  TrendingUp, 
  CheckCircle2,
  RefreshCw,
  Shield,
  Clock,
  Upload,
  FileSpreadsheet,
  X
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface CuentaBancaria {
  id: number;
  numero_cuenta: string;
  nombre: string;
  compania_id: number;
  compania_nombre: string;
  moneda: string;
  // Saldos diferenciados por tipo de moneda
  saldo_inicial_usd?: number;  // Para cuentas multi-moneda
  saldo_inicial_cop?: number;  // Para cuentas solo COP
  saldo_dia_anterior_usd?: number;
  saldo_dia_anterior_cop?: number;
}

interface SaldoModificacion {
  cuenta_id: number;
  moneda: string;  // Agregar info de moneda
  saldo_inicial_usd?: number;
  saldo_inicial_cop?: number;
  saldo_dia_anterior_usd?: number;
  saldo_dia_anterior_cop?: number;
}

interface TRM {
  valor: number;
  fecha: string;
}

const hoy = new Date();
const formatearFecha = (fecha: Date) => fecha.toISOString().slice(0, 10);

function CargueInicial() {
  const { user } = useAuth();
  const [cuentas, setCuentas] = useState<CuentaBancaria[]>([]);
  const [fecha, setFecha] = useState(() => {
    const ayer = new Date();
    ayer.setDate(ayer.getDate() - 1);
    return formatearFecha(ayer);
  });
  const [trm, setTrm] = useState<TRM | null>(null);
  const [loadingTrm, setLoadingTrm] = useState(false);
  const [saldosModificados, setSaldosModificados] = useState<Map<number, SaldoModificacion>>(new Map());
  const [loading, setLoading] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  
  // Estado para modal de importación
  const [modalImportarAbierto, setModalImportarAbierto] = useState(false);
  const [tipoCarga, setTipoCarga] = useState<'mes' | 'dia'>('mes');
  const [mesImportar, setMesImportar] = useState(() => {
    const hoy = new Date();
    return `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}`;
  });
  const [diaImportar, setDiaImportar] = useState('');
  const [sobrescribir, setSobrescribir] = useState(false);
  const [archivoExcel, setArchivoExcel] = useState<File | null>(null);
  const [importando, setImportando] = useState(false);
  const [resultadoImportacion, setResultadoImportacion] = useState<any>(null);

  // Control de acceso: solo admin
  if (!user || user.role !== 'administrador') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-red-500" />
          </div>
          <h2 className="text-xl font-bold text-center mb-2 text-gray-900 dark:text-white">Acceso Restringido</h2>
          <p className="text-center text-gray-600 dark:text-gray-400">
            Esta página es solo para administradores.
          </p>
        </div>
      </div>
    );
  }

  // Cargar TRM del día seleccionado
  const cargarTRM = async (fechaTRM: string) => {
    setLoadingTrm(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/trm/by-date/${fechaTRM}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        }
      });
      
      if (response.ok) {
        const trmData = await response.json();
        setTrm(trmData);
      } else {
        setTrm(null);
        setError('No se encontró TRM para la fecha seleccionada. Verifica que esté cargada.');
      }
    } catch (err) {
      console.error('Error cargando TRM:', err);
      setTrm(null);
    } finally {
      setLoadingTrm(false);
    }
  };

  // Función para calcular COP desde USD (dividido entre 1000 para mostrar cifras manejables)
  const calcularCOP = (usd: number): number => {
    if (!trm) return 0;
    return (usd * trm.valor) / 1000;
  };

  // Cargar cuentas bancarias
  const cargarCuentas = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('access_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      };

      // Cargar cuentas bancarias
      const response = await fetch('http://localhost:8000/api/v1/bank-accounts/todas-las-cuentas', { headers });
      if (!response.ok) throw new Error('Error al cargar cuentas bancarias');
      
      const cuentasData = await response.json();
      
      // Cargar saldos existentes para la fecha seleccionada
      const saldosResponse = await fetch(`http://localhost:8000/api/v1/saldo-inicial/obtener-saldos?fecha=${fecha}`, { headers });
      const saldosData = saldosResponse.ok ? await saldosResponse.json() : [];

      // Filtrar cuentas: mostrar solo USD para multi-moneda, COP para cuentas solo pesos
      const cuentasFiltradas = cuentasData.filter((cuenta: any) => {
        // Si es USD, mostrar (es la editable para multi-moneda)
        if (cuenta.moneda === 'USD') return true;
        
        // Si es COP, verificar si existe una versión USD de la misma cuenta
        if (cuenta.moneda === 'COP') {
          const tieneVersionUSD = cuentasData.some((c: any) => 
            c.cuenta_bancaria_id === cuenta.cuenta_bancaria_id && c.moneda === 'USD'
          );
          // Solo mostrar COP si NO tiene versión USD (es decir, es cuenta solo pesos)
          return !tieneVersionUSD;
        }
        
        return false;
      });

      // Combinar datos
      const cuentasConSaldos = cuentasFiltradas.map((cuenta: any) => {
        const saldoExistente = saldosData.find((s: any) => s.cuenta_id === cuenta.id);
        const esMultiMoneda = cuenta.moneda === 'USD'; // Las cuentas USD son multi-moneda
        
        if (esMultiMoneda) {
          return {
            ...cuenta,
            saldo_inicial_usd: saldoExistente?.saldo_inicial || 0,
            saldo_dia_anterior_usd: saldoExistente?.saldo_dia_anterior || 0
          };
        } else {
          return {
            ...cuenta,
            saldo_inicial_cop: saldoExistente?.saldo_inicial || 0,
            saldo_dia_anterior_cop: saldoExistente?.saldo_dia_anterior || 0
          };
        }
      });

      setCuentas(cuentasConSaldos);
      
      // Cargar TRM del día
      await cargarTRM(fecha);
    } catch (err: any) {
      setError(err.message || 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCuentas();
  }, [fecha]);

  // Validar fecha (solo días anteriores)
  const handleFechaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const nuevaFecha = e.target.value;
    const fechaSeleccionada = new Date(nuevaFecha);
    
    if (fechaSeleccionada >= hoy) {
      setError('Solo puedes seleccionar días anteriores al actual.');
      return;
    }
    
    setError('');
    setFecha(nuevaFecha);
    setSaldosModificados(new Map()); // Limpiar modificaciones
  };

  // Manejar cambio de saldos (USD para multi-moneda, COP para cuentas solo pesos)
  const handleSaldoChange = (cuentaId: number, tipo: 'tesoreria' | 'pagaduria', valor: string) => {
    const valorNumerico = parseFloat(valor) || 0;
    const cuenta = cuentas.find(c => c.id === cuentaId);
    if (!cuenta) return;
    
    const esMultiMoneda = cuenta.moneda === 'USD';
    
    setSaldosModificados(prev => {
      const nuevo = new Map(prev);
      const existente = nuevo.get(cuentaId) || { cuenta_id: cuentaId, moneda: cuenta.moneda };
      
      if (tipo === 'tesoreria') {
        if (esMultiMoneda) {
          existente.saldo_inicial_usd = valorNumerico;
        } else {
          existente.saldo_inicial_cop = valorNumerico;
        }
      } else {
        if (esMultiMoneda) {
          existente.saldo_dia_anterior_usd = valorNumerico;
        } else {
          existente.saldo_dia_anterior_cop = valorNumerico;
        }
      }
      
      nuevo.set(cuentaId, existente);
      return nuevo;
    });

    // Actualizar también el estado local para reflejar el cambio en UI
    setCuentas(prev => prev.map(c => 
      c.id === cuentaId 
        ? {
            ...c,
            ...(tipo === 'tesoreria' 
              ? (esMultiMoneda 
                  ? { saldo_inicial_usd: valorNumerico }
                  : { saldo_inicial_cop: valorNumerico }
                )
              : (esMultiMoneda 
                  ? { saldo_dia_anterior_usd: valorNumerico }
                  : { saldo_dia_anterior_cop: valorNumerico }
                )
            )
          }
        : c
    ));
  };

  // Guardar cambios
  const handleGuardar = async () => {
    if (saldosModificados.size === 0) {
      setError('No hay cambios para guardar.');
      return;
    }

    setGuardando(true);
    setError('');
    setMensaje('');

    try {
      const token = localStorage.getItem('access_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      };

      // Procesar modificaciones según el tipo de moneda
      const modificaciones = Array.from(saldosModificados.values()).map(mod => {
        const esMultiMoneda = mod.moneda === 'USD';
        
        if (esMultiMoneda) {
          // Para cuentas multi-moneda (USD), enviar valores USD originales (SIN conversión)
          return {
            cuenta_id: mod.cuenta_id,
            saldo_inicial: mod.saldo_inicial_usd, // Enviar USD original
            saldo_dia_anterior: mod.saldo_dia_anterior_usd // Enviar USD original
          };
        } else {
          // Para cuentas solo COP, usar directamente los valores en pesos
          return {
            cuenta_id: mod.cuenta_id,
            saldo_inicial: mod.saldo_inicial_cop,
            saldo_dia_anterior: mod.saldo_dia_anterior_cop
          };
        }
      });

      const response = await fetch('http://localhost:8000/api/v1/saldo-inicial/guardar-cargue-inicial', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          fecha,
          modificaciones
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al guardar');
      }

      const resultado = await response.json();
      setMensaje(`✅ Cargue inicial guardado correctamente. ${resultado.transacciones_creadas || 0} registros procesados.`);
      setSaldosModificados(new Map()); // Limpiar modificaciones
      
      // Recargar datos para mostrar el estado actual
      setTimeout(() => cargarCuentas(), 500);

    } catch (err: any) {
      setError(err.message || 'Error al guardar los cambios.');
    } finally {
      setGuardando(false);
    }
  };

  // Manejar importación desde Excel
  const handleImportarExcel = async () => {
    if (!archivoExcel) {
      setError('Debe seleccionar el archivo Excel');
      return;
    }

    if (tipoCarga === 'dia' && !diaImportar) {
      setError('Debe seleccionar un día específico cuando tipo de carga es "Día"');
      return;
    }

    setImportando(true);
    setError('');
    setResultadoImportacion(null);

    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('tipo_carga', tipoCarga);
      formData.append('mes', mesImportar);
      if (tipoCarga === 'dia' && diaImportar) {
        formData.append('dia', diaImportar);
      }
      formData.append('sobrescribir', sobrescribir.toString());
      formData.append('archivo_excel', archivoExcel);

      const response = await fetch('http://localhost:8000/api/v1/saldo-inicial/importar-saldos', {
        method: 'POST',
        headers: {
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: formData
      });

      if (response.ok) {
        const resultado = await response.json();
        setResultadoImportacion(resultado);
        setMensaje(`Importación exitosa: ${resultado.cuentas_tesoreria} transacciones tesorería, ${resultado.cuentas_pagaduria} transacciones pagaduría`);
        
        // Recargar cuentas después de importación exitosa
        await cargarCuentas();
        
        // Cerrar modal después de 2 segundos
        setTimeout(() => {
          setModalImportarAbierto(false);
          setResultadoImportacion(null);
        }, 2000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error en la importación');
      }
    } catch (err) {
      console.error('Error importando:', err);
      setError('Error al importar archivos Excel');
    } finally {
      setImportando(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Cargue Inicial de Saldos</h1>
                <p className="text-gray-600 dark:text-gray-400">Configura saldos iniciales para días anteriores - Solo Administradores</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setModalImportarAbierto(true)}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>Importar desde Excel</span>
              </button>
              <Shield className="w-5 h-5 text-green-500" />
              <span className="text-sm text-green-600 font-medium">Admin</span>
            </div>
          </div>
        </div>

        {/* Selector de Fecha */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center space-x-4">
            <Calendar className="w-5 h-5 text-gray-500" />
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Fecha para Cargue Inicial
              </label>
              <input
                type="date"
                value={fecha}
                max={formatearFecha(new Date(hoy.getTime() - 86400000))}
                onChange={handleFechaChange}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Solo se pueden seleccionar días anteriores al actual
              </p>
              {trm && (
                <p className="text-xs text-green-600 dark:text-green-400 mt-1 font-medium">
                  TRM del día: ${trm.valor.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              )}
              {loadingTrm && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Cargando TRM...
                </p>
              )}
            </div>
            <button
              onClick={cargarCuentas}
              disabled={loading}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Recargar</span>
            </button>
          </div>
        </div>

        {/* Mensajes */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-700 dark:text-red-400">{error}</span>
            </div>
          </div>
        )}

        {mensaje && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <CheckCircle2 className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-green-700 dark:text-green-400">{mensaje}</span>
            </div>
          </div>
        )}

        {/* Tabla de Cuentas */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <Building2 className="w-5 h-5 mr-2" />
              Cuentas Bancarias - Saldos Editables
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Cuenta Bancaria
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Compañía
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Saldo Inicial Tesorería
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Equivalente COP
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Saldo Día Anterior Pagaduría  
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Equivalente COP
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center">
                        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                        <span>Cargando cuentas...</span>
                      </div>
                    </td>
                  </tr>
                ) : cuentas.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      No hay cuentas bancarias configuradas
                    </td>
                  </tr>
                ) : (
                  cuentas.map(cuenta => (
                    <tr key={cuenta.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <Building2 className="w-4 h-4 text-gray-400 mr-2" />
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {cuenta.numero_cuenta}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {cuenta.nombre} ({cuenta.moneda})
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-900 dark:text-white">
                          {cuenta.compania_nombre}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex items-center justify-center">
                          <DollarSign className={`w-4 h-4 mr-1 ${
                            cuenta.moneda === 'USD' ? 'text-green-500' : 'text-yellow-600'
                          }`} />
                          <input
                            type="number"
                            step="0.01"
                            value={cuenta.moneda === 'USD' 
                              ? (cuenta.saldo_inicial_usd || '') 
                              : (cuenta.saldo_inicial_cop || '')
                            }
                            onChange={(e) => handleSaldoChange(cuenta.id, 'tesoreria', e.target.value)}
                            className="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-center"
                            placeholder="0.00"
                            disabled={cuenta.moneda === 'USD' && !trm}
                          />
                          <span className="ml-1 text-xs font-medium text-gray-500">
                            {cuenta.moneda}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {cuenta.moneda === 'USD' 
                            ? `$${calcularCOP(cuenta.saldo_inicial_usd || 0).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                            : `$${(cuenta.saldo_inicial_cop || 0).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                          } COP
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex items-center justify-center">
                          <TrendingUp className={`w-4 h-4 mr-1 ${
                            cuenta.moneda === 'USD' ? 'text-blue-500' : 'text-purple-600'
                          }`} />
                          <input
                            type="number"
                            step="0.01"
                            value={cuenta.moneda === 'USD' 
                              ? (cuenta.saldo_dia_anterior_usd || '') 
                              : (cuenta.saldo_dia_anterior_cop || '')
                            }
                            onChange={(e) => handleSaldoChange(cuenta.id, 'pagaduria', e.target.value)}
                            className="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-center"
                            placeholder="0.00"
                            disabled={cuenta.moneda === 'USD' && !trm}
                          />
                          <span className="ml-1 text-xs font-medium text-gray-500">
                            {cuenta.moneda}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {cuenta.moneda === 'USD' 
                            ? `$${calcularCOP(cuenta.saldo_dia_anterior_usd || 0).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                            : `$${(cuenta.saldo_dia_anterior_cop || 0).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                          } COP
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Acciones */}
        <div className="mt-6 flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <Clock className="w-4 h-4 mr-2" />
            <span>
              {saldosModificados.size > 0 
                ? `${saldosModificados.size} cuenta(s) modificada(s)`
                : 'Sin cambios pendientes'
              }
            </span>
          </div>
          
          <button
            onClick={handleGuardar}
            disabled={guardando || saldosModificados.size === 0 || !trm}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
          >
            {guardando ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Guardando...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Guardar Cargue Inicial</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Modal de Importación desde Excel */}
      {modalImportarAbierto && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <FileSpreadsheet className="w-6 h-6 text-green-600" />
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    Importar Saldos desde Excel
                  </h2>
                </div>
                <button
                  onClick={() => setModalImportarAbierto(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Tipo de Carga */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tipo de Carga
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="mes"
                      checked={tipoCarga === 'mes'}
                      onChange={(e) => setTipoCarga(e.target.value as 'mes' | 'dia')}
                      className="mr-2"
                    />
                    <span className="text-gray-900 dark:text-white">Mes Completo</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="dia"
                      checked={tipoCarga === 'dia'}
                      onChange={(e) => setTipoCarga(e.target.value as 'mes' | 'dia')}
                      className="mr-2"
                    />
                    <span className="text-gray-900 dark:text-white">Día Específico</span>
                  </label>
                </div>
              </div>

              {/* Selección de Mes */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Mes a Importar
                </label>
                <input
                  type="month"
                  value={mesImportar}
                  onChange={(e) => setMesImportar(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Selección de Día (solo si tipo_carga === 'dia') */}
              {tipoCarga === 'dia' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Día Específico
                  </label>
                  <input
                    type="date"
                    value={diaImportar}
                    onChange={(e) => setDiaImportar(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              )}

              {/* Archivo Excel */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Archivo Excel (SALDO INICIAL)
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  El archivo debe tener hojas numeradas (1, 2, 3...) con campo "SALDO INICIAL"
                </p>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={(e) => setArchivoExcel(e.target.files?.[0] || null)}
                  className="w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 dark:file:bg-green-900/20 dark:file:text-green-400"
                />
                {archivoExcel && (
                  <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                    ✓ {archivoExcel.name}
                  </p>
                )}
              </div>

              {/* Sobrescribir */}
              <div className="mb-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={sobrescribir}
                    onChange={(e) => setSobrescribir(e.target.checked)}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Sobrescribir transacciones existentes
                  </span>
                </label>
              </div>

              {/* Resultado de Importación */}
              {resultadoImportacion && (
                <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <h3 className="font-bold text-green-800 dark:text-green-300 mb-2">Importación Completada</h3>
                  <div className="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <p>• Días procesados: {resultadoImportacion.dias_procesados}</p>
                    <p>• Transacciones Tesorería: {resultadoImportacion.cuentas_tesoreria}</p>
                    <p>• Transacciones Pagaduría: {resultadoImportacion.cuentas_pagaduria}</p>
                    {resultadoImportacion.dias_sin_trm?.length > 0 && (
                      <p className="text-yellow-600 dark:text-yellow-400">
                        ⚠ Días sin TRM: {resultadoImportacion.dias_sin_trm.join(', ')}
                      </p>
                    )}
                    {resultadoImportacion.cuentas_sin_match?.length > 0 && (
                      <p className="text-yellow-600 dark:text-yellow-400">
                        ⚠ Cuentas no encontradas: {resultadoImportacion.cuentas_sin_match.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Botones */}
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setModalImportarAbierto(false)}
                  disabled={importando}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleImportarExcel}
                  disabled={importando || !archivoExcel}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
                >
                  {importando ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Importando...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      <span>Importar</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CargueInicial;
