import { useState, useEffect } from 'react'
import { useAuthStore } from '../../store/authStore'
import { Plus, Edit, Trash2, Tag } from 'lucide-react'

function CategoriasPage() {
  const { user } = useAuthStore()
  const [categorias, setCategorias] = useState([])
  const [mostrarModal, setMostrarModal] = useState(false)
  const [categoriaEditando, setCategoriaEditando] = useState(null)

  // Datos de ejemplo
  useEffect(() => {
    setCategorias([
      {
        id: 1,
        nombre: 'Ingresos Operacionales',
        tipo: 'ingreso',
        descripcion: 'Ingresos por actividades principales del negocio',
        activa: true,
        subcategorias: [
          { id: 11, nombre: 'Recaudo Ventas', padre: 1 },
          { id: 12, nombre: 'Ingresos por Servicios', padre: 1 },
          { id: 13, nombre: 'Otros Ingresos Operacionales', padre: 1 }
        ]
      },
      {
        id: 2,
        nombre: 'Ingresos No Operacionales',
        tipo: 'ingreso',
        descripcion: 'Ingresos por actividades secundarias',
        activa: true,
        subcategorias: [
          { id: 21, nombre: 'Rendimientos Financieros', padre: 2 },
          { id: 22, nombre: 'Ingresos Extraordinarios', padre: 2 }
        ]
      },
      {
        id: 3,
        nombre: 'Gastos Operacionales',
        tipo: 'egreso',
        descripcion: 'Gastos necesarios para la operación',
        activa: true,
        subcategorias: [
          { id: 31, nombre: 'Pago Nómina', padre: 3 },
          { id: 32, nombre: 'Pago Proveedores', padre: 3 },
          { id: 33, nombre: 'Servicios Públicos', padre: 3 },
          { id: 34, nombre: 'Gastos Administrativos', padre: 3 }
        ]
      },
      {
        id: 4,
        nombre: 'Gastos No Operacionales',
        tipo: 'egreso',
        descripcion: 'Gastos financieros y extraordinarios',
        activa: true,
        subcategorias: [
          { id: 41, nombre: 'Gastos Financieros', padre: 4 },
          { id: 42, nombre: 'Gastos Extraordinarios', padre: 4 }
        ]
      }
    ])
  }, [])

  const puedeEditar = user?.rol === 'tesoreria'

  const categoriasPorTipo = {
    ingreso: categorias.filter(c => c.tipo === 'ingreso'),
    egreso: categorias.filter(c => c.tipo === 'egreso')
  }

  const editarCategoria = (categoria) => {
    setCategoriaEditando(categoria)
    setMostrarModal(true)
  }

  const eliminarCategoria = (id) => {
    if (confirm('¿Está seguro de eliminar esta categoría?')) {
      setCategorias(categorias.filter(c => c.id !== id))
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-200 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Categorías</h1>
          <p className="text-gray-600 mt-2">Gestión de categorías de ingresos y egresos</p>
        </div>
        {puedeEditar && (
          <button 
            onClick={() => setMostrarModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Nueva Categoría</span>
          </button>
        )}
      </div>

      {/* Categorías de Ingresos */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-green-800 flex items-center">
            <div className="p-2 bg-green-100 rounded-lg mr-3">
              <Tag className="h-5 w-5 text-green-600" />
            </div>
            Categorías de Ingresos
          </h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {categoriasPorTipo.ingreso.map((categoria) => (
              <div key={categoria.id} className="border border-green-200 rounded-lg p-4 bg-green-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h4 className="text-lg font-semibold text-green-900">{categoria.nombre}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        categoria.activa 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {categoria.activa ? 'Activa' : 'Inactiva'}
                      </span>
                    </div>
                    <p className="text-green-700 mt-1">{categoria.descripcion}</p>
                    
                    {/* Subcategorías */}
                    {categoria.subcategorias && categoria.subcategorias.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-green-800 mb-2">Subcategorías:</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                          {categoria.subcategorias.map((sub) => (
                            <div key={sub.id} className="bg-white border border-green-200 rounded px-3 py-2">
                              <span className="text-sm text-green-800">{sub.nombre}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {puedeEditar && (
                    <div className="flex space-x-2 ml-4">
                      <button 
                        onClick={() => editarCategoria(categoria)}
                        className="text-indigo-600 hover:text-indigo-900 p-2"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button 
                        onClick={() => eliminarCategoria(categoria.id)}
                        className="text-red-600 hover:text-red-900 p-2"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Categorías de Egresos */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-red-800 flex items-center">
            <div className="p-2 bg-red-100 rounded-lg mr-3">
              <Tag className="h-5 w-5 text-red-600" />
            </div>
            Categorías de Egresos
          </h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {categoriasPorTipo.egreso.map((categoria) => (
              <div key={categoria.id} className="border border-red-200 rounded-lg p-4 bg-red-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h4 className="text-lg font-semibold text-red-900">{categoria.nombre}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        categoria.activa 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {categoria.activa ? 'Activa' : 'Inactiva'}
                      </span>
                    </div>
                    <p className="text-red-700 mt-1">{categoria.descripcion}</p>
                    
                    {/* Subcategorías */}
                    {categoria.subcategorias && categoria.subcategorias.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium text-red-800 mb-2">Subcategorías:</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                          {categoria.subcategorias.map((sub) => (
                            <div key={sub.id} className="bg-white border border-red-200 rounded px-3 py-2">
                              <span className="text-sm text-red-800">{sub.nombre}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {puedeEditar && (
                    <div className="flex space-x-2 ml-4">
                      <button 
                        onClick={() => editarCategoria(categoria)}
                        className="text-indigo-600 hover:text-indigo-900 p-2"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button 
                        onClick={() => eliminarCategoria(categoria.id)}
                        className="text-red-600 hover:text-red-900 p-2"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-green-50 border-green-200">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-green-600">
              {categoriasPorTipo.ingreso.length}
            </div>
            <div className="text-green-800 font-medium">Categorías de Ingresos</div>
          </div>
        </div>

        <div className="card bg-red-50 border-red-200">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-red-600">
              {categoriasPorTipo.egreso.length}
            </div>
            <div className="text-red-800 font-medium">Categorías de Egresos</div>
          </div>
        </div>

        <div className="card bg-blue-50 border-blue-200">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-blue-600">
              {categorias.reduce((total, cat) => total + (cat.subcategorias?.length || 0), 0)}
            </div>
            <div className="text-blue-800 font-medium">Total Subcategorías</div>
          </div>
        </div>
      </div>

      {/* Mensaje si no hay permisos */}
      {!puedeEditar && (
        <div className="card bg-blue-50 border-blue-200">
          <div className="card-body">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Tag className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-blue-800">Modo Solo Lectura</h3>
                <p className="text-blue-700 mt-1">
                  Solo los usuarios con rol de Tesorería pueden crear y modificar categorías.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CategoriasPage
