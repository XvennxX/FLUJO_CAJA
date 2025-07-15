import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { Calendar, ChevronLeft, ChevronRight, Download, RefreshCw } from 'lucide-react'

function FlujoMensualPage() {
  const { user } = useAuthStore()
  const [mesSeleccionado, setMesSeleccionado] = useState(new Date())
  const [datosFlujov, setDatosFlujov] = useState({})
  const [categorias, setCategorias] = useState([])

  // Generar datos de ejemplo que replican la estructura de Excel
  useEffect(() => {
    const diasDelMes = new Date(mesSeleccionado.getFullYear(), mesSeleccionado.getMonth() + 1, 0).getDate()
    
    // Categorías de ejemplo basadas en los Excel originales
    const categoriasEjemplo = [
      { id: 1, nombre: 'SALDO INICIAL', tipo: 'saldo', orden: 1 },
      { id: 2, nombre: 'INGRESOS OPERACIONALES', tipo: 'titulo', orden: 2 },
      { id: 3, nombre: 'Recaudo Ventas', tipo: 'ingreso', orden: 3, padre: 2 },
      { id: 4, nombre: 'Ingresos por Servicios', tipo: 'ingreso', orden: 4, padre: 2 },
      { id: 5, nombre: 'Otros Ingresos', tipo: 'ingreso', orden: 5, padre: 2 },
      { id: 6, nombre: 'TOTAL INGRESOS', tipo: 'subtotal', orden: 6 },
      { id: 7, nombre: 'EGRESOS OPERACIONALES', tipo: 'titulo', orden: 7 },
      { id: 8, nombre: 'Pago Nómina', tipo: 'egreso', orden: 8, padre: 7 },
      { id: 9, nombre: 'Pago Proveedores', tipo: 'egreso', orden: 9, padre: 7 },
      { id: 10, nombre: 'Servicios Públicos', tipo: 'egreso', orden: 10, padre: 7 },
      { id: 11, nombre: 'Gastos Administrativos', tipo: 'egreso', orden: 11, padre: 7 },
      { id: 12, nombre: 'TOTAL EGRESOS', tipo: 'subtotal', orden: 12 },
      { id: 13, nombre: 'FLUJO NETO DEL DÍA', tipo: 'flujo', orden: 13 },
      { id: 14, nombre: 'SALDO FINAL', tipo: 'saldo_final', orden: 14 }
    ]

    setCategorias(categoriasEjemplo)

    // Generar datos aleatorios para cada día
    const datos = {}
    for (let dia = 1; dia <= diasDelMes; dia++) {
      datos[dia] = {
        'SALDO INICIAL': dia === 1 ? 125000000 : (datos[dia - 1]?.['SALDO FINAL'] || 125000000),
        'Recaudo Ventas': Math.random() > 0.3 ? Math.floor(Math.random() * 8000000) + 2000000 : 0,
        'Ingresos por Servicios': Math.random() > 0.5 ? Math.floor(Math.random() * 5000000) + 1000000 : 0,
        'Otros Ingresos': Math.random() > 0.8 ? Math.floor(Math.random() * 3000000) + 500000 : 0,
        'Pago Nómina': dia === 15 || dia === 30 ? 15000000 : 0,
        'Pago Proveedores': Math.random() > 0.6 ? Math.floor(Math.random() * 6000000) + 1000000 : 0,
        'Servicios Públicos': dia === 5 ? 2500000 : 0,
        'Gastos Administrativos': Math.random() > 0.7 ? Math.floor(Math.random() * 2000000) + 300000 : 0
      }

      // Calcular totales
      const totalIngresos = datos[dia]['Recaudo Ventas'] + datos[dia]['Ingresos por Servicios'] + datos[dia]['Otros Ingresos']
      const totalEgresos = datos[dia]['Pago Nómina'] + datos[dia]['Pago Proveedores'] + datos[dia]['Servicios Públicos'] + datos[dia]['Gastos Administrativos']
      
      datos[dia]['TOTAL INGRESOS'] = totalIngresos
      datos[dia]['TOTAL EGRESOS'] = totalEgresos
      datos[dia]['FLUJO NETO DEL DÍA'] = totalIngresos - totalEgresos
      datos[dia]['SALDO FINAL'] = datos[dia]['SALDO INICIAL'] + datos[dia]['FLUJO NETO DEL DÍA']
    }

    setDatosFlujov(datos)
  }, [mesSeleccionado])

  const cambiarMes = (incremento) => {
    const nuevoMes = new Date(mesSeleccionado)
    nuevoMes.setMonth(nuevoMes.getMonth() + incremento)
    setMesSeleccionado(nuevoMes)
  }

  const obtenerValor = (categoria, dia) => {
    const valor = datosFlujov[dia]?.[categoria] || 0
    return valor
  }

  const obtenerEstiloCategoria = (categoria) => {
    if (categoria.tipo === 'titulo') return 'bg-blue-100 font-bold text-blue-900'
    if (categoria.tipo === 'subtotal') return 'bg-gray-100 font-bold'
    if (categoria.tipo === 'saldo' || categoria.tipo === 'saldo_final') return 'bg-green-100 font-semibold text-green-900'
    if (categoria.tipo === 'flujo') return 'bg-yellow-100 font-semibold text-yellow-900'
    return 'bg-white'
  }

  const formatearValor = (valor, tipo) => {
    if (!valor || valor === 0) return '-'
    
    const esNegativo = valor < 0
    const valorAbs = Math.abs(valor)
    const valorFormateado = valorAbs.toLocaleString()
    
    if (tipo === 'egreso' || tipo === 'subtotal' && valor > 0) {
      return `$${valorFormateado}`
    }
    
    return `${esNegativo ? '-' : ''}$${valorFormateado}`
  }

  const diasDelMes = new Date(mesSeleccionado.getFullYear(), mesSeleccionado.getMonth() + 1, 0).getDate()
  const nombreMes = mesSeleccionado.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-200 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Flujo Mensual</h1>
          <p className="text-gray-600 mt-2">Vista tipo Excel del flujo de caja diario</p>
        </div>
        <div className="flex items-center space-x-4">
          <button className="btn-secondary flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <span>Actualizar</span>
          </button>
          <button className="btn-secondary flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Exportar Excel</span>
          </button>
        </div>
      </div>

      {/* Navegación de mes */}
      <div className="flex items-center justify-center space-x-4 bg-white p-4 rounded-lg shadow">
        <button 
          onClick={() => cambiarMes(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <div className="flex items-center space-x-2">
          <Calendar className="h-5 w-5 text-gray-500" />
          <h2 className="text-xl font-semibold capitalize">{nombreMes}</h2>
        </div>
        <button 
          onClick={() => cambiarMes(1)}
          className="p-2 hover:bg-gray-100 rounded-lg"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>

      {/* Tabla principal estilo Excel */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-50">
                <th className="border border-gray-300 px-4 py-3 text-left font-semibold sticky left-0 bg-gray-50 z-10 min-w-[200px]">
                  CONCEPTO
                </th>
                {Array.from({ length: diasDelMes }, (_, i) => i + 1).map(dia => (
                  <th key={dia} className="border border-gray-300 px-2 py-3 text-center font-semibold min-w-[80px]">
                    {dia}
                  </th>
                ))}
                <th className="border border-gray-300 px-4 py-3 text-center font-semibold bg-gray-100 min-w-[120px]">
                  TOTAL MES
                </th>
              </tr>
            </thead>
            <tbody>
              {categorias.map((categoria) => {
                const totalMes = Array.from({ length: diasDelMes }, (_, i) => i + 1)
                  .reduce((suma, dia) => suma + obtenerValor(categoria.nombre, dia), 0)

                return (
                  <tr key={categoria.id} className={obtenerEstiloCategoria(categoria)}>
                    <td className="border border-gray-300 px-4 py-2 sticky left-0 z-10 bg-inherit font-medium">
                      {categoria.tipo === 'titulo' ? categoria.nombre : 
                       categoria.padre ? `  ${categoria.nombre}` : categoria.nombre}
                    </td>
                    {Array.from({ length: diasDelMes }, (_, i) => i + 1).map(dia => {
                      const valor = obtenerValor(categoria.nombre, dia)
                      return (
                        <td key={dia} className="border border-gray-300 px-2 py-2 text-right text-sm">
                          {categoria.tipo === 'titulo' ? '' : formatearValor(valor, categoria.tipo)}
                        </td>
                      )
                    })}
                    <td className="border border-gray-300 px-4 py-2 text-right font-semibold bg-gray-100">
                      {categoria.tipo === 'titulo' ? '' : formatearValor(totalMes, categoria.tipo)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Información adicional */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-green-50 border-green-200">
          <div className="card-body">
            <h3 className="text-lg font-medium text-green-800">Total Ingresos del Mes</h3>
            <p className="text-2xl font-bold text-green-600 mt-2">
              ${Object.values(datosFlujov).reduce((suma, dia) => suma + (dia['TOTAL INGRESOS'] || 0), 0).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="card bg-red-50 border-red-200">
          <div className="card-body">
            <h3 className="text-lg font-medium text-red-800">Total Egresos del Mes</h3>
            <p className="text-2xl font-bold text-red-600 mt-2">
              ${Object.values(datosFlujov).reduce((suma, dia) => suma + (dia['TOTAL EGRESOS'] || 0), 0).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="card bg-blue-50 border-blue-200">
          <div className="card-body">
            <h3 className="text-lg font-medium text-blue-800">Flujo Neto del Mes</h3>
            <p className="text-2xl font-bold text-blue-600 mt-2">
              ${Object.values(datosFlujov).reduce((suma, dia) => suma + (dia['FLUJO NETO DEL DÍA'] || 0), 0).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Nota explicativa */}
      <div className="card bg-yellow-50 border-yellow-200">
        <div className="card-body">
          <h3 className="text-lg font-medium text-yellow-800">📊 Vista Excel Digitalizada</h3>
          <p className="text-yellow-700 mt-1">
            Esta vista replica la estructura de los archivos Excel originales (CUADROFLUJOMAYO2025.xlsx, JUNIO2025.xlsx) 
            con cálculos automáticos y navegación por meses. Los datos mostrados son de ejemplo.
          </p>
        </div>
      </div>
    </div>
  )
}

export default FlujoMensualPage
