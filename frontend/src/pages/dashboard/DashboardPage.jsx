import { useAuthStore } from '../../store/authStore'
import { DollarSign, TrendingUp, TrendingDown, Users } from 'lucide-react'

function DashboardPage() {
  const { user } = useAuthStore()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Bienvenido, {user?.nombre} - {user?.rol === 'tesoreria' ? 'Tesorería' : 
          user?.rol === 'pagaduria' ? 'Pagaduría' : 'Mesa de Dinero'}
        </p>
      </div>

      {/* Cards de métricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Saldo Actual</p>
                <p className="text-2xl font-bold text-gray-900">$125,400,000</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ingresos del Mes</p>
                <p className="text-2xl font-bold text-gray-900">$45,200,000</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <TrendingDown className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Egresos del Mes</p>
                <p className="text-2xl font-bold text-gray-900">$38,100,000</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Flujo Neto</p>
                <p className="text-2xl font-bold text-green-600">+$7,100,000</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resumen semanal */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium">Flujo de los Últimos 7 Días</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {[
                { dia: 'Lunes', ingresos: 5200000, egresos: 3800000 },
                { dia: 'Martes', ingresos: 4100000, egresos: 5200000 },
                { dia: 'Miércoles', ingresos: 6800000, egresos: 4100000 },
                { dia: 'Jueves', ingresos: 3900000, egresos: 4700000 },
                { dia: 'Viernes', ingresos: 7200000, egresos: 3900000 },
                { dia: 'Sábado', ingresos: 2100000, egresos: 1800000 },
                { dia: 'Domingo', ingresos: 1500000, egresos: 1200000 },
              ].map((item, index) => {
                const flujo = item.ingresos - item.egresos
                return (
                  <div key={index} className="flex items-center justify-between py-2">
                    <span className="text-sm font-medium text-gray-900">{item.dia}</span>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-green-600">
                        +${item.ingresos.toLocaleString()}
                      </span>
                      <span className="text-sm text-red-600">
                        -${item.egresos.toLocaleString()}
                      </span>
                      <span className={`text-sm font-medium ${flujo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {flujo >= 0 ? '+' : ''}${flujo.toLocaleString()}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Accesos rápidos */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium">Accesos Rápidos</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-2 gap-4">
              <button className="btn-primary">
                Nueva Transacción
              </button>
              <button className="btn-secondary">
                Ver Flujo Mensual
              </button>
              <button className="btn-secondary">
                Generar Reporte
              </button>
              <button className="btn-secondary">
                Exportar Excel
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Sistema en desarrollo */}
      <div className="card bg-yellow-50 border-yellow-200">
        <div className="card-body">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Users className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-yellow-800">🚧 Sistema en Desarrollo</h3>
              <p className="text-yellow-700 mt-1">
                Este es el dashboard principal del Sistema de Flujo de Caja. 
                Los datos mostrados son de ejemplo. Las funcionalidades se irán implementando progresivamente.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
