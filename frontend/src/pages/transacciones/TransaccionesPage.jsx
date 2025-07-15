import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { Calendar, Search, Filter, Plus, Edit, Trash2, Download } from 'lucide-react'

function TransaccionesPage() {
  const { user } = useAuthStore()
  const [transacciones, setTransacciones] = useState([])
  const [filtros, setFiltros] = useState({
    fechaInicio: '',
    fechaFin: '',
    categoria: '',
    tipo: '',
    busqueda: ''
  })
  const [mostrarModal, setMostrarModal] = useState(false)

  // Datos de ejemplo
  useEffect(() => {
    setTransacciones([
      {
        id: 1,
        fecha: '2025-01-15',
        concepto: 'Pago Nómina Enero',
        categoria: 'Gastos Operacionales',
        tipo: 'egreso',
        valor: 15000000,
        saldoAnterior: 125000000,
        saldoPosterior: 110000000,
        usuario: 'Ana García'
      },
      {
        id: 2,
        fecha: '2025-01-15',
        concepto: 'Recaudo Ventas',
        categoria: 'Ingresos Operacionales',
        tipo: 'ingreso',
        valor: 8500000,
        saldoAnterior: 110000000,
        saldoPosterior: 118500000,
        usuario: 'Carlos Ruiz'
      },
      {
        id: 3,
        fecha: '2025-01-14',
        concepto: 'Pago Proveedores',
        categoria: 'Gastos Operacionales',
        tipo: 'egreso',
        valor: 4200000,
        saldoAnterior: 122500000,
        saldoPosterior: 118300000,
        usuario: 'Ana García'
      },
      {
        id: 4,
        fecha: '2025-01-14',
        concepto: 'Ingresos por Servicios',
        categoria: 'Ingresos por Servicios',
        tipo: 'ingreso',
        valor: 6800000,
        saldoAnterior: 118300000,
        saldoPosterior: 125100000,
        usuario: 'Miguel Torres'
      }
    ])
  }, [])

  const puedeEditar = user?.rol === 'tesoreria' || 
                      (user?.rol === 'pagaduria' && user?.permisos?.includes('transacciones_egresos'))

  const transaccionesFiltradas = transacciones.filter(t => {
    const cumpleFecha = !filtros.fechaInicio || !filtros.fechaFin || 
                        (t.fecha >= filtros.fechaInicio && t.fecha <= filtros.fechaFin)
    const cumpleCategoria = !filtros.categoria || t.categoria.includes(filtros.categoria)
    const cumpleTipo = !filtros.tipo || t.tipo === filtros.tipo
    const cumpleBusqueda = !filtros.busqueda || 
                           t.concepto.toLowerCase().includes(filtros.busqueda.toLowerCase())
    
    return cumpleFecha && cumpleCategoria && cumpleTipo && cumpleBusqueda
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-200 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Transacciones</h1>
          <p className="text-gray-600 mt-2">Gestión de movimientos de efectivo</p>
        </div>
        {puedeEditar && (
          <button 
            onClick={() => setMostrarModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Nueva Transacción</span>
          </button>
        )}
      </div>

      {/* Filtros */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filtros
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fecha Inicio
              </label>
              <input
                type="date"
                value={filtros.fechaInicio}
                onChange={(e) => setFiltros({...filtros, fechaInicio: e.target.value})}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fecha Fin
              </label>
              <input
                type="date"
                value={filtros.fechaFin}
                onChange={(e) => setFiltros({...filtros, fechaFin: e.target.value})}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Categoría
              </label>
              <select
                value={filtros.categoria}
                onChange={(e) => setFiltros({...filtros, categoria: e.target.value})}
                className="input-field"
              >
                <option value="">Todas</option>
                <option value="Operacionales">Gastos Operacionales</option>
                <option value="Servicios">Ingresos por Servicios</option>
                <option value="Ventas">Ingresos por Ventas</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo
              </label>
              <select
                value={filtros.tipo}
                onChange={(e) => setFiltros({...filtros, tipo: e.target.value})}
                className="input-field"
              >
                <option value="">Todos</option>
                <option value="ingreso">Ingresos</option>
                <option value="egreso">Egresos</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Buscar
              </label>
              <div className="relative">
                <Search className="h-4 w-4 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar concepto..."
                  value={filtros.busqueda}
                  onChange={(e) => setFiltros({...filtros, busqueda: e.target.value})}
                  className="input-field pl-10"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabla de transacciones */}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h3 className="text-lg font-medium">
            Transacciones ({transaccionesFiltradas.length})
          </h3>
          <button className="btn-secondary flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Exportar</span>
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Concepto
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Categoría
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Valor
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Saldo Posterior
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                {puedeEditar && (
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                )}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transaccionesFiltradas.map((transaccion) => (
                <tr key={transaccion.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(transaccion.fecha).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {transaccion.concepto}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {transaccion.categoria}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      transaccion.tipo === 'ingreso' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {transaccion.tipo === 'ingreso' ? 'Ingreso' : 'Egreso'}
                    </span>
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${
                    transaccion.tipo === 'ingreso' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaccion.tipo === 'ingreso' ? '+' : '-'}${transaccion.valor.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 font-medium">
                    ${transaccion.saldoPosterior.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {transaccion.usuario}
                  </td>
                  {puedeEditar && (
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <div className="flex justify-center space-x-2">
                        <button className="text-indigo-600 hover:text-indigo-900">
                          <Edit className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-900">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mensaje si no hay permisos */}
      {!puedeEditar && (
        <div className="card bg-blue-50 border-blue-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Calendar className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-blue-800">Modo Solo Lectura</h3>
                <p className="text-blue-700 mt-1">
                  Tu rol actual ({user?.rol === 'mesa_dinero' ? 'Mesa de Dinero' : user?.rol}) 
                  solo permite visualizar las transacciones.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TransaccionesPage
