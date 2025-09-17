"""
Migración para crear tabla dias_festivos.

Revision ID: create_dias_festivos
Revises: 
Create Date: 2025-09-17 16:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import date

# revision identifiers
revision = 'create_dias_festivos'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """
    Crear tabla dias_festivos para gestionar días festivos de Colombia.
    """
    # Crear tabla
    op.create_table(
        'dias_festivos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tipo', sa.String(length=50), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices
    op.create_index('ix_dias_festivos_id', 'dias_festivos', ['id'], unique=False)
    op.create_index('ix_dias_festivos_fecha', 'dias_festivos', ['fecha'], unique=True)
    
    # Insertar festivos de Colombia 2025
    festivos_2025 = [
        ('2025-01-01', 'Año Nuevo', 'Celebración del primer día del año', 'civil'),
        ('2025-01-06', 'Reyes Magos', 'Epifanía del Señor', 'religioso'),
        ('2025-03-24', 'Día de San José', 'Festividad de San José', 'religioso'),
        ('2025-04-17', 'Jueves Santo', 'Jueves previo a la Pascua', 'religioso'),
        ('2025-04-18', 'Viernes Santo', 'Conmemoración de la crucifixión de Jesucristo', 'religioso'),
        ('2025-05-01', 'Día del Trabajo', 'Día Internacional del Trabajador', 'civil'),
        ('2025-06-02', 'Ascensión de Jesús', 'Ascensión del Señor', 'religioso'),
        ('2025-06-23', 'Corpus Christi', 'Festividad católica', 'religioso'),
        ('2025-06-30', 'Sagrado Corazón de Jesús', 'Festividad católica', 'religioso'),
        ('2025-06-30', 'San Pedro y San Pablo', 'Festividad de los apóstoles', 'religioso'),
        ('2025-07-20', 'Día de la Independencia', 'Independencia de Colombia', 'nacional'),
        ('2025-08-07', 'Batalla de Boyacá', 'Conmemoración de la Batalla de Boyacá', 'nacional'),
        ('2025-08-18', 'Asunción de la Virgen', 'Asunción de María', 'religioso'),
        ('2025-10-13', 'Día de la Raza', 'Día de la Hispanidad', 'nacional'),
        ('2025-11-03', 'Todos los Santos', 'Festividad católica', 'religioso'),
        ('2025-11-17', 'Independencia de Cartagena', 'Independencia de Cartagena', 'nacional'),
        ('2025-12-08', 'Inmaculada Concepción', 'Festividad católica', 'religioso'),
        ('2025-12-25', 'Navidad', 'Celebración del nacimiento de Jesucristo', 'religioso')
    ]
    
    # Insertar festivos de Colombia 2026 (fechas aproximadas según regulación)
    festivos_2026 = [
        ('2026-01-01', 'Año Nuevo', 'Celebración del primer día del año', 'civil'),
        ('2026-01-12', 'Reyes Magos', 'Epifanía del Señor (trasladado)', 'religioso'),
        ('2026-03-23', 'Día de San José', 'Festividad de San José (trasladado)', 'religioso'),
        ('2026-04-02', 'Jueves Santo', 'Jueves previo a la Pascua', 'religioso'),
        ('2026-04-03', 'Viernes Santo', 'Conmemoración de la crucifixión de Jesucristo', 'religioso'),
        ('2026-05-01', 'Día del Trabajo', 'Día Internacional del Trabajador', 'civil'),
        ('2026-05-18', 'Ascensión de Jesús', 'Ascensión del Señor (trasladado)', 'religioso'),
        ('2026-06-08', 'Corpus Christi', 'Festividad católica (trasladado)', 'religioso'),
        ('2026-06-15', 'Sagrado Corazón de Jesús', 'Festividad católica (trasladado)', 'religioso'),
        ('2026-06-29', 'San Pedro y San Pablo', 'Festividad de los apóstoles (trasladado)', 'religioso'),
        ('2026-07-20', 'Día de la Independencia', 'Independencia de Colombia', 'nacional'),
        ('2026-08-07', 'Batalla de Boyacá', 'Conmemoración de la Batalla de Boyacá', 'nacional'),
        ('2026-08-17', 'Asunción de la Virgen', 'Asunción de María (trasladado)', 'religioso'),
        ('2026-10-12', 'Día de la Raza', 'Día de la Hispanidad (trasladado)', 'nacional'),
        ('2026-11-02', 'Todos los Santos', 'Festividad católica (trasladado)', 'religioso'),
        ('2026-11-16', 'Independencia de Cartagena', 'Independencia de Cartagena (trasladado)', 'nacional'),
        ('2026-12-08', 'Inmaculada Concepción', 'Festividad católica', 'religioso'),
        ('2026-12-25', 'Navidad', 'Celebración del nacimiento de Jesucristo', 'religioso')
    ]
    
    # Combinar todos los festivos
    todos_festivos = festivos_2025 + festivos_2026
    
    # Insertar registros
    for fecha_str, nombre, descripcion, tipo in todos_festivos:
        op.execute(f"""
            INSERT INTO dias_festivos (fecha, nombre, descripcion, tipo, activo)
            VALUES ('{fecha_str}', '{nombre}', '{descripcion}', '{tipo}', true)
        """)

def downgrade():
    """
    Eliminar tabla dias_festivos.
    """
    op.drop_index('ix_dias_festivos_fecha', table_name='dias_festivos')
    op.drop_index('ix_dias_festivos_id', table_name='dias_festivos')
    op.drop_table('dias_festivos')