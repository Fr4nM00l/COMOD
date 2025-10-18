-- Script para actualizar la tabla historiaclinica con campos del formulario real
-- EXCLUYE campos relacionados con golpes y afecciones dentales específicas (se implementarán con el odontograma)
-- Ejecutar este script en la base de datos clinicaodontologica

USE clinicaodontologica;

-- Agregar campos faltantes a la tabla historiaclinica (versión simplificada)
ALTER TABLE historiaclinica 
ADD COLUMN domicilio VARCHAR(255) DEFAULT NULL COMMENT 'Dirección del paciente',
ADD COLUMN edad INT DEFAULT NULL COMMENT 'Edad del paciente',
ADD COLUMN tratamiento_odontologico BOOLEAN DEFAULT FALSE COMMENT 'Si estuvo bajo tratamiento odontológico',
ADD COLUMN tratamiento_odontologico_detalle TEXT DEFAULT NULL COMMENT 'Detalles del tratamiento odontológico',
ADD COLUMN colageno BOOLEAN DEFAULT FALSE COMMENT 'Problemas de colágeno (hiperlaxitud)',
ADD COLUMN fiebre_reumatica BOOLEAN DEFAULT FALSE COMMENT 'Fiebre reumática',
ADD COLUMN diabetes BOOLEAN DEFAULT FALSE COMMENT 'Diabetes',
ADD COLUMN cardiaco BOOLEAN DEFAULT FALSE COMMENT 'Problema cardíaco',
ADD COLUMN hipertension BOOLEAN DEFAULT FALSE COMMENT 'Hipertensión arterial',
ADD COLUMN sifilis BOOLEAN DEFAULT FALSE COMMENT 'Sífilis o gonorrea',
ADD COLUMN transfusiones BOOLEAN DEFAULT FALSE COMMENT 'Transfusiones',
ADD COLUMN embarazada BOOLEAN DEFAULT FALSE COMMENT 'Embarazada',
ADD COLUMN meses_embarazo VARCHAR(50) DEFAULT NULL COMMENT 'Meses de embarazo',
ADD COLUMN chagas BOOLEAN DEFAULT FALSE COMMENT 'Chagas',
ADD COLUMN hepatitis BOOLEAN DEFAULT FALSE COMMENT 'Hepatitis',
ADD COLUMN renales BOOLEAN DEFAULT FALSE COMMENT 'Problemas renales',
ADD COLUMN ulcera BOOLEAN DEFAULT FALSE COMMENT 'Úlcera gástrica',
ADD COLUMN convulsiones BOOLEAN DEFAULT FALSE COMMENT 'Convulsiones',
ADD COLUMN tiempo_fumando VARCHAR(100) DEFAULT NULL COMMENT 'Tiempo fumando',
ADD COLUMN otras_enfermedades TEXT DEFAULT NULL COMMENT 'Otras enfermedades o recomendaciones médicas',
ADD COLUMN tomo_medicamento BOOLEAN DEFAULT FALSE COMMENT 'Si tomó medicamento',
ADD COLUMN medicamento_detalle VARCHAR(255) DEFAULT NULL COMMENT 'Detalles del medicamento tomado',
ADD COLUMN dolor_tipo ENUM('continuo', 'intermitente', 'provocado') DEFAULT NULL COMMENT 'Tipo de dolor',
ADD COLUMN dolor_localizacion ENUM('localizado', 'irradiado') DEFAULT NULL COMMENT 'Localización del dolor',
ADD COLUMN dificultades_funcionales TEXT DEFAULT NULL COMMENT 'Dificultades para hablar, tragar, abrir la boca',
ADD COLUMN examen_tejidos_blandos TEXT DEFAULT NULL COMMENT 'Resultados del examen de tejidos blandos',
ADD COLUMN firma_paciente VARCHAR(255) DEFAULT NULL COMMENT 'Firma del paciente',
ADD COLUMN firma_profesional VARCHAR(255) DEFAULT NULL COMMENT 'Firma y sello del profesional',
ADD COLUMN motivo_consulta TEXT NOT NULL COMMENT 'Motivo de consulta',
ADD COLUMN diagnostico_presuntivo TEXT DEFAULT NULL COMMENT 'Diagnóstico presuntivo',
ADD COLUMN plan_tratamiento TEXT DEFAULT NULL COMMENT 'Plan de tratamiento';

-- NOTA: Los siguientes campos se implementarán cuando esté listo el odontograma:
-- - golpe_como, golpe_recibio_tratamiento (relacionados con golpes)
-- - sangrado_encias, movilidad_dentaria, calculo_detalle, enfermedad_periodontal_detalle
-- - observaciones_dentales, cantidad_dientes (relacionados con afecciones dentales específicas)

-- Actualizar comentarios de campos existentes para mayor claridad
ALTER TABLE historiaclinica 
MODIFY COLUMN ObraSocial VARCHAR(100) DEFAULT NULL COMMENT 'Obra social del paciente',
MODIFY COLUMN NumAfiliado VARCHAR(50) DEFAULT NULL COMMENT 'Número de afiliado',
MODIFY COLUMN Alergias TEXT DEFAULT NULL COMMENT 'Alergias del paciente',
MODIFY COLUMN Enfermedades TEXT DEFAULT NULL COMMENT 'Enfermedades del paciente',
MODIFY COLUMN Fuma BOOLEAN DEFAULT FALSE COMMENT 'Si fuma',
MODIFY COLUMN Drogas TEXT DEFAULT NULL COMMENT 'Consumo de drogas',
MODIFY COLUMN Medicamentos TEXT DEFAULT NULL COMMENT 'Medicamentos que consume actualmente',
MODIFY COLUMN NivelDeDolor TINYINT(4) DEFAULT NULL COMMENT 'Nivel de dolor (1=suave, 2=moderado, 3=intenso)',
MODIFY COLUMN Calmante VARCHAR(100) DEFAULT NULL COMMENT 'Qué puede calmar el dolor',
MODIFY COLUMN GolpeEnDientes BOOLEAN DEFAULT FALSE COMMENT 'Si sufrió un golpe en los dientes',
MODIFY COLUMN FechaGolpe DATE DEFAULT NULL COMMENT 'Fecha del golpe en los dientes';

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_historiaclinica_paciente_fecha ON historiaclinica(Paciente_id, Fecha);
CREATE INDEX idx_historiaclinica_fecha ON historiaclinica(Fecha);

-- Mostrar la estructura actualizada de la tabla
DESCRIBE historiaclinica;
