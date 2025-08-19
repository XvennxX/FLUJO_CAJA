import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';

interface DatePickerProps {
  selectedDate: string;
  onDateChange: (date: string) => void;
  availableDates?: string[];
}

const DatePicker: React.FC<DatePickerProps> = ({ 
  selectedDate, 
  onDateChange, 
  availableDates = [] 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(() => {
    // Inicializar con enero 2025 para mostrar las fechas disponibles
    const dateParts = selectedDate.split('-');
    const year = parseInt(dateParts[0]);
    const month = parseInt(dateParts[1]) - 1; // Mes base 0
    return new Date(year, month, 1);
  });

  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Días del mes anterior
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const prevDate = new Date(year, month, -i);
      days.push({
        date: prevDate,
        isCurrentMonth: false,
        isToday: false,
        isSelected: false,
        hasData: false
      });
    }

    // Días del mes actual
    for (let day = 1; day <= daysInMonth; day++) {
      const currentDate = new Date(year, month, day);
      const dateString = formatDateToString(currentDate);
      const today = new Date();
      
      days.push({
        date: currentDate,
        isCurrentMonth: true,
        isToday: currentDate.toDateString() === today.toDateString(),
        isSelected: dateString === selectedDate,
        hasData: availableDates.includes(dateString)
      });
    }

    // Días del mes siguiente para completar la grilla
    const remainingDays = 42 - days.length; // 6 semanas × 7 días
    for (let day = 1; day <= remainingDays; day++) {
      const nextDate = new Date(year, month + 1, day);
      days.push({
        date: nextDate,
        isCurrentMonth: false,
        isToday: false,
        isSelected: false,
        hasData: false
      });
    }

    return days;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      if (direction === 'prev') {
        newMonth.setMonth(prev.getMonth() - 1);
      } else {
        newMonth.setMonth(prev.getMonth() + 1);
      }
      return newMonth;
    });
  };

  const navigateYear = (direction: 'prev' | 'next') => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      if (direction === 'prev') {
        newMonth.setFullYear(prev.getFullYear() - 1);
      } else {
        newMonth.setFullYear(prev.getFullYear() + 1);
      }
      return newMonth;
    });
  };

  const formatDateToString = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const handleDateClick = (date: Date) => {
    const dateString = formatDateToString(date);
    onDateChange(dateString);
    setIsOpen(false);
  };

  const goToToday = () => {
    const today = new Date();
    const todayString = formatDateToString(today);
    onDateChange(todayString);
    setCurrentMonth(new Date(today.getFullYear(), today.getMonth(), 1));
    setIsOpen(false);
  };

  const days = getDaysInMonth(currentMonth);
  
  // Crear objeto Date de manera más segura
  const selectedDateParts = selectedDate.split('-');
  const selectedDateObj = new Date(
    parseInt(selectedDateParts[0]), 
    parseInt(selectedDateParts[1]) - 1, 
    parseInt(selectedDateParts[2])
  );

  return (
    <div className="relative">
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 hover:bg-gray-50 dark:bg-gray-900 transition-colors"
      >
        <Calendar className="w-5 h-5 text-bolivar-600" />
        <div className="text-left">
          <div className="text-sm font-medium text-gray-900 dark:text-white">
            {selectedDateObj.toLocaleDateString('es-CO', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Seleccionar fecha
          </div>
        </div>
      </button>

      {/* Calendar Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 p-4 w-80">
          {/* Header with navigation */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateYear('prev')}
                className="p-1 hover:bg-gray-100 dark:bg-gray-700 rounded transition-colors"
                title="Año anterior"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => navigateMonth('prev')}
                className="p-1 hover:bg-gray-100 dark:bg-gray-700 rounded transition-colors"
                title="Mes anterior"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateMonth('next')}
                className="p-1 hover:bg-gray-100 dark:bg-gray-700 rounded transition-colors"
                title="Mes siguiente"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => navigateYear('next')}
                className="p-1 hover:bg-gray-100 dark:bg-gray-700 rounded transition-colors"
                title="Año siguiente"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick actions */}
          <div className="flex justify-center mb-4">
            <button
              onClick={goToToday}
              className="text-sm px-3 py-1 bg-bolivar-100 text-bolivar-700 rounded-full hover:bg-bolivar-200 transition-colors"
            >
              Ir a hoy
            </button>
          </div>

          {/* Days of week header */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {dayNames.map(day => (
              <div key={day} className="text-center text-xs font-medium text-gray-500 dark:text-gray-400 py-2">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-1">
            {days.map((day, index) => {
              const isClickable = day.isCurrentMonth;
              
              return (
                <button
                  key={index}
                  onClick={() => isClickable && handleDateClick(day.date)}
                  disabled={!isClickable}
                  className={`
                    relative p-2 text-sm rounded transition-colors
                    ${!day.isCurrentMonth 
                      ? 'text-gray-300 cursor-not-allowed' 
                      : 'text-gray-700 hover:bg-gray-100 dark:bg-gray-700'
                    }
                    ${day.isSelected 
                      ? 'bg-bolivar-500 text-white hover:bg-bolivar-600' 
                      : ''
                    }
                    ${day.isToday && !day.isSelected 
                      ? 'bg-bolivar-100 text-bolivar-700 font-semibold' 
                      : ''
                    }
                  `}
                >
                  {day.date.getDate()}
                  {day.hasData && (
                    <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-gold-500 rounded-full"></div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-center space-x-4 text-xs text-gray-600 dark:text-gray-400">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-bolivar-500 rounded-full"></div>
                <span>Seleccionado</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-gold-500 rounded-full"></div>
                <span>Con datos</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-bolivar-100 rounded-full"></div>
                <span>Hoy</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Overlay to close calendar */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default DatePicker;
