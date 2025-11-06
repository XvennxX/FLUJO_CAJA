import React, { useState } from 'react';
import { 
  HelpCircle, 
  Search, 
  Book, 
  MessageCircle, 
  Phone, 
  Mail, 
  FileText, 
  Video,
  ChevronDown,
  ChevronRight,
  Send,
  Download,
  ExternalLink
} from 'lucide-react';

const Help: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState('faq');
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const [supportForm, setSupportForm] = useState({
    subject: '',
    category: 'general',
    priority: 'normal',
    description: '',
    email: '',
    phone: ''
  });

  const categories = [
    { id: 'faq', label: 'Preguntas Frecuentes', icon: HelpCircle },
    { id: 'guides', label: 'Guías y Tutoriales', icon: Book },
    { id: 'videos', label: 'Videos de Ayuda', icon: Video },
    { id: 'contact', label: 'Contactar Soporte', icon: MessageCircle },
    { id: 'resources', label: 'Recursos', icon: FileText }
  ];

  const faqs = [
    {
      question: '¿Cómo accedo a los diferentes módulos del sistema?',
      answer: 'Puedes navegar entre módulos usando el menú lateral izquierdo. Los módulos disponibles dependen de tu rol de usuario. Administradores tienen acceso completo, mientras que otros roles tienen permisos específicos.',
      category: 'navegacion'
    },
    {
      question: '¿Cómo genero un reporte de flujo de caja?',
      answer: 'Ve al módulo de Informes, selecciona el tipo de reporte "Flujo de Caja", define el rango de fechas y las compañías que deseas incluir, luego haz clic en "Generar Reporte".',
      category: 'reportes'
    },
    {
      question: '¿Puedo exportar los datos a Excel?',
      answer: 'Sí, la mayoría de reportes y listados tienen la opción de exportar a Excel. Busca el botón "Exportar" o el ícono de descarga en las páginas de reportes.',
      category: 'exportacion'
    },
    {
      question: '¿Cómo cambio mi contraseña?',
      answer: 'Ve a "Mi Perfil" desde el menú de usuario (esquina superior derecha), luego a la sección "Seguridad" donde podrás cambiar tu contraseña.',
      category: 'seguridad'
    },
    {
      question: '¿Qué significa cada estado en la conciliación?',
      answer: 'Los estados son: Pendiente (sin revisar), Evaluado (revisado pero no confirmado), Confirmado (aprobado para cierre), Cerrado (proceso completado).',
      category: 'conciliacion'
    },
    {
      question: '¿Cómo agrego una nueva compañía al sistema?',
      answer: 'Ve al módulo "Compañías", haz clic en "Nueva Compañía", completa el formulario con el nombre de la compañía y guarda. Luego podrás agregar cuentas bancarias a esa compañía.',
      category: 'companias'
    }
  ];

  const guides = [
    {
      title: 'Guía de Inicio Rápido',
      description: 'Aprende los conceptos básicos de SIFCO en 10 minutos',
      duration: '10 min',
      difficulty: 'Principiante',
      type: 'PDF'
    },
    {
      title: 'Manual de Usuario Completo',
      description: 'Documentación detallada de todas las funcionalidades',
      duration: '45 min',
      difficulty: 'Intermedio',
      type: 'PDF'
    },
    {
      title: 'Gestión de Conciliaciones',
      description: 'Proceso paso a paso para realizar conciliaciones',
      duration: '20 min',
      difficulty: 'Intermedio',
      type: 'Video'
    },
    {
      title: 'Generación de Reportes',
      description: 'Cómo crear y personalizar reportes financieros',
      duration: '15 min',
      difficulty: 'Principiante',
      type: 'Video'
    }
  ];

  const videos = [
    {
      title: 'Introducción a SIFCO',
      description: 'Conoce la interfaz y navegación básica',
      duration: '5:30',
      thumbnail: '🎥',
      url: '#'
    },
    {
      title: 'Creando tu Primera Conciliación',
      description: 'Tutorial paso a paso del proceso de conciliación',
      duration: '12:45',
      thumbnail: '🎥',
      url: '#'
    },
    {
      title: 'Gestión de Compañías y Cuentas',
      description: 'Aprende a administrar empresas y cuentas bancarias',
      duration: '8:20',
      thumbnail: '🎥',
      url: '#'
    },
    {
      title: 'Reportes Avanzados',
      description: 'Técnicas avanzadas para análisis financiero',
      duration: '18:15',
      thumbnail: '🎥',
      url: '#'
    }
  ];

  const handleSupportSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Ticket de soporte enviado:', supportForm);
    // Aquí iría la lógica para enviar el ticket
    alert('Tu solicitud ha sido enviada. Te contactaremos pronto.');
    setSupportForm({
      subject: '',
      category: 'general',
      priority: 'normal',
      description: '',
      email: '',
      phone: ''
    });
  };

  const filteredFaqs = faqs.filter(faq => 
    faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
    faq.answer.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderFaqSection = () => (
    <div className="space-y-6">
      {/* Búsqueda */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <input
          type="text"
          placeholder="Buscar en preguntas frecuentes..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
        />
      </div>

      {/* FAQs */}
      <div className="space-y-4">
        {filteredFaqs.map((faq, index) => (
          <div key={index} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
            <button
              onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 dark:bg-gray-900 transition-colors"
            >
              <span className="font-medium text-gray-900 dark:text-white pr-4">{faq.question}</span>
              {expandedFaq === index ? (
                <ChevronDown className="h-5 w-5 text-gray-500 dark:text-gray-400 flex-shrink-0" />
              ) : (
                <ChevronRight className="h-5 w-5 text-gray-500 dark:text-gray-400 flex-shrink-0" />
              )}
            </button>
            {expandedFaq === index && (
              <div className="px-4 pb-4 border-t border-gray-100">
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed pt-3">{faq.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderGuidesSection = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {guides.map((guide, index) => (
        <div key={index} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between mb-3">
            <h3 className="font-semibold text-gray-900 dark:text-white text-lg">{guide.title}</h3>
            <span className={`px-2 py-1 text-xs rounded-full ${
              guide.type === 'PDF' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {guide.type}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{guide.description}</p>
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
            <span>⏱️ {guide.duration}</span>
            <span className={`px-2 py-1 rounded-full ${
              guide.difficulty === 'Principiante' 
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {guide.difficulty}
            </span>
          </div>
          <div className="flex space-x-2">
            <button className="flex items-center space-x-2 px-4 py-2 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors flex-1">
              <Download size={16} />
              <span>Descargar</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors">
              <ExternalLink size={16} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  const renderVideosSection = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {videos.map((video, index) => (
        <div key={index} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
          <div className="aspect-video bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-4xl">
            {video.thumbnail}
          </div>
          <div className="p-4">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{video.title}</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">{video.description}</p>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500 dark:text-gray-400">⏱️ {video.duration}</span>
              <button className="px-3 py-1 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors text-sm">
                Ver Video
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderContactSection = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Información de Contacto */}
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Información de Contacto</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
              <Phone className="h-6 w-6 text-blue-600" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Teléfono</p>
                <p className="text-gray-600 dark:text-gray-400">+57 (1) 423-9000</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Lun - Vie: 8:00 AM - 6:00 PM</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
              <Mail className="h-6 w-6 text-green-600" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Correo Electrónico</p>
                <p className="text-gray-600 dark:text-gray-400">soporte.sifco@bolivar.com</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Respuesta en menos de 2 horas</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-4 bg-purple-50 rounded-lg">
              <MessageCircle className="h-6 w-6 text-purple-600" />
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Chat en Línea</p>
                <p className="text-gray-600 dark:text-gray-400">Disponible 24/7</p>
                <button className="text-sm text-purple-600 hover:text-purple-800 font-medium">
                  Iniciar Chat →
                </button>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Horarios de Atención</h3>
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Lunes - Viernes:</span>
                <span className="font-medium">8:00 AM - 6:00 PM</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Sábados:</span>
                <span className="font-medium">9:00 AM - 1:00 PM</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Domingos:</span>
                <span className="font-medium">Cerrado</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-400">Soporte Crítico:</span>
                <span className="font-medium text-red-600">24/7</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Formulario de Soporte */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Enviar Solicitud de Soporte</h3>
        <form onSubmit={handleSupportSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Asunto</label>
            <input
              type="text"
              required
              value={supportForm.subject}
              onChange={(e) => setSupportForm({ ...supportForm, subject: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
              placeholder="Describe brevemente el problema"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Categoría</label>
              <select
                value={supportForm.category}
                onChange={(e) => setSupportForm({ ...supportForm, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
              >
                <option value="general">General</option>
                <option value="tecnico">Técnico</option>
                <option value="acceso">Acceso</option>
                <option value="reportes">Reportes</option>
                <option value="conciliacion">Conciliación</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Prioridad</label>
              <select
                value={supportForm.priority}
                onChange={(e) => setSupportForm({ ...supportForm, priority: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
              >
                <option value="baja">Baja</option>
                <option value="normal">Normal</option>
                <option value="alta">Alta</option>
                <option value="critica">Crítica</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Descripción del Problema</label>
            <textarea
              required
              rows={4}
              value={supportForm.description}
              onChange={(e) => setSupportForm({ ...supportForm, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
              placeholder="Describe el problema con el mayor detalle posible..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Correo de Contacto</label>
              <input
                type="email"
                required
                value={supportForm.email}
                onChange={(e) => setSupportForm({ ...supportForm, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Teléfono (Opcional)</label>
              <input
                type="tel"
                value={supportForm.phone}
                onChange={(e) => setSupportForm({ ...supportForm, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-bolivar-500 focus:border-bolivar-500"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-bolivar-500 text-white rounded-lg hover:bg-bolivar-600 transition-colors font-medium"
          >
            <Send size={16} />
            <span>Enviar Solicitud</span>
          </button>
        </form>
      </div>
    </div>
  );

  const renderResourcesSection = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[
        { 
          title: 'API Documentation', 
          description: 'Documentación técnica para desarrolladores',
          type: 'Técnico',
          icon: '📘'
        },
        { 
          title: 'Notas de Versión', 
          description: 'Últimas actualizaciones y mejoras',
          type: 'General',
          icon: '📋'
        },
        { 
          title: 'Mejores Prácticas', 
          description: 'Recomendaciones para uso óptimo',
          type: 'Guía',
          icon: '⭐'
        },
        { 
          title: 'Plantillas Excel', 
          description: 'Formatos predefinidos para importación',
          type: 'Recurso',
          icon: '📊'
        },
        { 
          title: 'Políticas de Seguridad', 
          description: 'Normativas y procedimientos de seguridad',
          type: 'Político',
          icon: '🔒'
        },
        { 
          title: 'Glosario de Términos', 
          description: 'Definiciones de conceptos financieros',
          type: 'Referencia',
          icon: '📚'
        }
      ].map((resource, index) => (
        <div key={index} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-md transition-shadow">
          <div className="text-3xl mb-3">{resource.icon}</div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{resource.title}</h3>
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">{resource.description}</p>
          <div className="flex items-center justify-between">
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs rounded-full">
              {resource.type}
            </span>
            <button className="text-bolivar-600 hover:text-bolivar-800 text-sm font-medium">
              Ver más →
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  const renderContent = () => {
    switch (activeCategory) {
      case 'faq':
        return renderFaqSection();
      case 'guides':
        return renderGuidesSection();
      case 'videos':
        return renderVideosSection();
      case 'contact':
        return renderContactSection();
      case 'resources':
        return renderResourcesSection();
      default:
        return renderFaqSection();
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-bolivar-500 to-bolivar-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Ayuda y Soporte</h1>
        <p className="text-bolivar-100">Encuentra respuestas y obtén asistencia para usar SIFCO</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar de Categorías */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <nav className="space-y-2">
              {categories.map((category) => {
                const Icon = category.icon;
                return (
                  <button
                    key={category.id}
                    onClick={() => setActiveCategory(category.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors text-left ${
                      activeCategory === category.id
                        ? 'bg-bolivar-100 text-bolivar-700 border-l-4 border-bolivar-600'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    <Icon size={18} />
                    <span className="font-medium">{category.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Contenido Principal */}
        <div className="lg:col-span-3">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help;


