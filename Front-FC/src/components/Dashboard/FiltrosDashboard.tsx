import React, { useState } from 'react';
import { Building2, Landmark, X, ChevronDown, Filter } from 'lucide-react';

interface BankAccount {
  id: number;
  numero_cuenta: string;
  banco: {
    id: number;
    nombre: string;
  };
  monedas: string[];
  tipo_cuenta: string;
  compania: {
    id: number;
    nombre: string;
  };
}

interface FiltrosDashboardProps {
  bankAccounts: BankAccount[];
  companiasFiltradas: number[];
  bancosFiltrados: number[];
  onCompaniasChange: (companias: number[]) => void;
  onBancosChange: (bancos: number[]) => void;
  onLimpiarFiltros: () => void;
}

export const FiltrosDashboard: React.FC<FiltrosDashboardProps> = ({
  bankAccounts,
  companiasFiltradas,
  bancosFiltrados,
  onCompaniasChange,
  onBancosChange,
  onLimpiarFiltros
}) => {
  const [dropdownCompanias, setDropdownCompanias] = useState(false);
  const [dropdownBancos, setDropdownBancos] = useState(false);

  // Obtener lista única de compañías
  const companias = Array.from(
    new Map(
      bankAccounts.map(account => [
        account.compania.id,
        { id: account.compania.id, nombre: account.compania.nombre }
      ])
    ).values()
  ).sort((a, b) => a.nombre.localeCompare(b.nombre));

  // Obtener lista única de bancos
  const bancos = Array.from(
    new Map(
      bankAccounts.map(account => [
        account.banco.id,
        { id: account.banco.id, nombre: account.banco.nombre }
      ])
    ).values()
  ).sort((a, b) => a.nombre.localeCompare(b.nombre));

  const handleCompaniaToggle = (companiaId: number) => {
    const nuevasCompanias = companiasFiltradas.includes(companiaId)
      ? companiasFiltradas.filter(id => id !== companiaId)
      : [...companiasFiltradas, companiaId];
    onCompaniasChange(nuevasCompanias);
  };

  const handleBancoToggle = (bancoId: number) => {
    const nuevosBancos = bancosFiltrados.includes(bancoId)
      ? bancosFiltrados.filter(id => id !== bancoId)
      : [...bancosFiltrados, bancoId];
    onBancosChange(nuevosBancos);
  };

  const hayFiltrosActivos = companiasFiltradas.length > 0 || bancosFiltrados.length > 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 mb-4">
      <div className="flex items-center gap-4">
        {/* Icono de filtros */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Filtros:</span>
        </div>

        {/* Dropdown Compañías */}
        <div className="relative">
          <button
            onClick={() => setDropdownCompanias(!dropdownCompanias)}
            className={`flex items-center gap-2 px-3 py-1.5 text-sm border rounded-md transition-colors ${
              companiasFiltradas.length > 0 
                ? 'border-blue-300 bg-blue-50 text-blue-700' 
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Building2 className="w-4 h-4" />
            <span>
              {companiasFiltradas.length === 0 
                ? 'Compañías' 
                : companiasFiltradas.length === companias.length
                ? 'Todas las compañías'
                : `${companiasFiltradas.length} compañía${companiasFiltradas.length > 1 ? 's' : ''}`
              }
            </span>
            <ChevronDown className={`w-4 h-4 transition-transform ${dropdownCompanias ? 'rotate-180' : ''}`} />
          </button>

          {dropdownCompanias && (
            <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-md shadow-lg z-50">
              <div className="p-2 border-b border-gray-100">
                <button
                  onClick={() => {
                    onCompaniasChange(companiasFiltradas.length === companias.length ? [] : companias.map(c => c.id));
                  }}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  {companiasFiltradas.length === companias.length ? 'Deseleccionar todas' : 'Seleccionar todas'}
                </button>
              </div>
              <div className="max-h-48 overflow-y-auto">
                {companias.map((compania) => (
                  <label
                    key={compania.id}
                    className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={companiasFiltradas.includes(compania.id)}
                      onChange={() => handleCompaniaToggle(compania.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
                    />
                    <span className="text-sm text-gray-700">{compania.nombre}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Dropdown Bancos */}
        <div className="relative">
          <button
            onClick={() => setDropdownBancos(!dropdownBancos)}
            className={`flex items-center gap-2 px-3 py-1.5 text-sm border rounded-md transition-colors ${
              bancosFiltrados.length > 0 
                ? 'border-green-300 bg-green-50 text-green-700' 
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Landmark className="w-4 h-4" />
            <span>
              {bancosFiltrados.length === 0 
                ? 'Bancos' 
                : bancosFiltrados.length === bancos.length
                ? 'Todos los bancos'
                : `${bancosFiltrados.length} banco${bancosFiltrados.length > 1 ? 's' : ''}`
              }
            </span>
            <ChevronDown className={`w-4 h-4 transition-transform ${dropdownBancos ? 'rotate-180' : ''}`} />
          </button>

          {dropdownBancos && (
            <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-md shadow-lg z-50">
              <div className="p-2 border-b border-gray-100">
                <button
                  onClick={() => {
                    onBancosChange(bancosFiltrados.length === bancos.length ? [] : bancos.map(b => b.id));
                  }}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  {bancosFiltrados.length === bancos.length ? 'Deseleccionar todos' : 'Seleccionar todos'}
                </button>
              </div>
              <div className="max-h-48 overflow-y-auto">
                {bancos.map((banco) => (
                  <label
                    key={banco.id}
                    className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={bancosFiltrados.includes(banco.id)}
                      onChange={() => handleBancoToggle(banco.id)}
                      className="rounded border-gray-300 text-green-600 focus:ring-green-500 w-4 h-4"
                    />
                    <span className="text-sm text-gray-700">{banco.nombre}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Botón limpiar filtros */}
        {hayFiltrosActivos && (
          <button
            onClick={() => {
              onLimpiarFiltros();
              setDropdownCompanias(false);
              setDropdownBancos(false);
            }}
            className="flex items-center gap-1 px-2 py-1.5 text-xs text-red-600 hover:bg-red-50 rounded-md transition-colors border border-red-200"
          >
            <X className="w-3 h-3" />
            Limpiar
          </button>
        )}

        {/* Indicador de filtros activos */}
        {hayFiltrosActivos && (
          <div className="text-xs text-gray-500">
            {companiasFiltradas.length > 0 && bancosFiltrados.length > 0 && (
              <span>Filtros aplicados</span>
            )}
          </div>
        )}
      </div>

      {/* Cerrar dropdowns al hacer clic fuera */}
      {(dropdownCompanias || dropdownBancos) && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => {
            setDropdownCompanias(false);
            setDropdownBancos(false);
          }}
        />
      )}
    </div>
  );
};