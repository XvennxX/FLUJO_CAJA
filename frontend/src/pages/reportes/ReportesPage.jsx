import { useState } from 'react'
import { useAuthStore } from '../../store/authStore'
import { BarChart3, FileText, Calendar, Download, TrendingUp, TrendingDown, PieChart } from 'lucide-react'

function ReportesPage() {
  const { user } = useAuthStore()
  const [filtros, setFiltros] = useState({
    fechaInicio: '',
    fechaFin: '',
    tipoReporte: 'flujo_mensual'
  })
  const [reporteGenerado, setReporteGenerado] = useState(null)

  const tiposReporte = [
    { 
      id: 'flujo_mensual', 
      nombre: 'Flujo de Caja Mensual', 
      descripcion: 'Resumen de ingresos y egresos por mes',
      icono: BarChart3
    },
    { 
      id: 'comparativo_periodos', 
      nombre: 'Comparativo entre Períodos', 
      descripcion: 'Comparación de flujos entre diferentes meses',
      icono: TrendingUp
    },
    { 
      id: 'categorias_detalle', 
      nombre: 'Análisis por Categorías', 
      descripcion: 'Desglose detallado por categorías de ingresos y egresos',
      icono: PieChart
    },
    { 
      id: 'proyeccion_flujo', 
      nombre: 'Proyección de Flujo', 
      descripcion: 'Proyección basada en tendencias históricas',
      icono: TrendingDown
    }
  ]

  const generarReporte = () => {
    // Simulación de generación de reporte
    const reporteEjemplo = {
      tipo: filtros.tipoReporte,
      periodo: `${filtros.fechaInicio} - ${filtros.fechaFin}`,
      resumen: {
        totalIngresos: 145200000,
        totalEgresos: 128300000,
        flujoNeto: 16900000,
        diasAnalizados: 31
      },
      categorias: [
        { nombre: 'Recaudo Ventas', ingresos: 85000000, participacion: 58.5 },
        { nombre: 'Ingresos por Servicios', ingresos: 45000000, participacion: 31.0 },
        { nombre: 'Otros Ingresos', ingresos: 15200000, participacion: 10.5 },
        { nombre: 'Pago Nómina', egresos: 45000000, participacion: 35.1 },
        { nombre: 'Pago Proveedores', egresos: 38000000, participacion: 29.6 },
        { nombre: 'Servicios Públicos', egresos: 25000000, participacion: 19.5 },
        { nombre: 'Gastos Administrativos', egresos: 20300000, participacion: 15.8 }
      ],
      tendencias: {
        crecimientoIngresos: 12.5,
        variacionEgresos: -3.2,
        eficienciaOperacional: 88.4
      }
    }
    
    setReporteGenerado(reporteEjemplo)
  }

  const exportarReporte = (formato) => {
    alert(`Exportando reporte en formato ${formato.toUpperCase()}...`)
  }

  const tipoSeleccionado = tiposReporte.find(t => t.id === filtros.tipoReporte)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Reportes y Análisis</h1>
        <p className="text-gray-600 mt-2">Generación de reportes y análisis del flujo de caja</p>
      </div>

      {/* Selección de tipo de reporte */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium">Tipo de Reporte</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tiposReporte.map((tipo) => {
              const IconoComponent = tipo.icono
              return (
                <div
                  key={tipo.id}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    filtros.tipoReporte === tipo.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setFiltros({...filtros, tipoReporte: tipo.id})}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${
                      filtros.tipoReporte === tipo.id ? 'bg-blue-100' : 'bg-gray-100'
                    }`}>
                      <IconoComponent className={`h-6 w-6 ${
                        filtros.tipoReporte === tipo.id ? 'text-blue-600' : 'text-gray-600'
                      }`} />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{tipo.nombre}</h4>
                      <p className="text-sm text-gray-500 mt-1">{tipo.descripcion}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Configuración del reporte */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium">Configuración</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
            <div className="flex items-end">
              <button
                onClick={generarReporte}
                disabled={!filtros.fechaInicio || !filtros.fechaFin}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                <FileText className="h-4 w-4" />
                <span>Generar Reporte</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Resultado del reporte */}
      {reporteGenerado && (
        <div className="space-y-6">
          {/* Header del reporte */}
          <div className="card">
            <div className="card-header flex justify-between items-center">
              <div>
                <h3 className="text-lg font-medium">{tipoSeleccionado?.nombre}</h3>
                <p className="text-sm text-gray-500">
                  Período: {reporteGenerado.periodo} | Generado el {new Date().toLocaleDateString()}
                </p>
              </div>
              <div className="flex space-x-2">
                <button 
                  onClick={() => exportarReporte('pdf')}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Download className="h-4 w-4" />
                  <span>PDF</span>
                </button>
                <button 
                  onClick={() => exportarReporte('excel')}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Download className="h-4 w-4" />
                  <span>Excel</span>
                </button>
              </div>
            </div>
          </div>

          {/* Resumen ejecutivo */}
          <div className="card">
            <div className="card-header">
              <h4 className="text-lg font-medium">Resumen Ejecutivo</h4>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ${reporteGenerado.resumen.totalIngresos.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Ingresos</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    ${reporteGenerado.resumen.totalEgresos.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Total Egresos</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    ${reporteGenerado.resumen.flujoNeto.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Flujo Neto</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600">
                    {reporteGenerado.resumen.diasAnalizados}
                  </div>
                  <div className="text-sm text-gray-600">Días Analizados</div>
                </div>
              </div>
            </div>
          </div>

          {/* Análisis por categorías */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Ingresos por categoría */}
            <div className="card">
              <div className="card-header">
                <h4 className="text-lg font-medium text-green-800">Ingresos por Categoría</h4>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  {reporteGenerado.categorias
                    .filter(c => c.ingresos)
                    .map((categoria, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <div>
                        <div className="font-medium">{categoria.nombre}</div>
                        <div className="text-sm text-gray-500">{categoria.participacion}%</div>
                      </div>
                      <div className="text-green-600 font-semibold">
                        ${categoria.ingresos.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Egresos por categoría */}
            <div className="card">
              <div className="card-header">
                <h4 className="text-lg font-medium text-red-800">Egresos por Categoría</h4>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  {reporteGenerado.categorias
                    .filter(c => c.egresos)
                    .map((categoria, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <div>
                        <div className="font-medium">{categoria.nombre}</div>
                        <div className="text-sm text-gray-500">{categoria.participacion}%</div>
                      </div>
                      <div className="text-red-600 font-semibold">
                        ${categoria.egresos.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Indicadores de tendencia */}
          <div className="card">
            <div className="card-header">
              <h4 className="text-lg font-medium">Indicadores de Tendencia</h4>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    +{reporteGenerado.tendencias.crecimientoIngresos}%
                  </div>
                  <div className="text-sm text-gray-600">Crecimiento Ingresos</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {reporteGenerado.tendencias.variacionEgresos}%
                  </div>
                  <div className="text-sm text-gray-600">Variación Egresos</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {reporteGenerado.tendencias.eficienciaOperacional}%
                  </div>
                  <div className="text-sm text-gray-600">Eficiencia Operacional</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Información adicional */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="card-body">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-blue-800">📊 Sistema de Reportes</h3>
              <p className="text-blue-700 mt-1">
                Los reportes se generan en tiempo real basados en los datos del sistema. 
                Los datos mostrados son de ejemplo. Próximamente se agregarán gráficos interactivos.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportesPage
