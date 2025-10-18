-- Script para agregar campos relacionados con golpes y afecciones dentales específicas
-- Este script se ejecutará cuando esté listo el odontograma interactivo
-- Ejecutar este script en la base de datos clinicaodontologica

USE clinicaodontologica;

-- Agregar campos relacionados con golpes y afecciones dentales específicas
ALTER TABLE historiaclinica 
ADD COLUMN golpe_como VARCHAR(255) DEFAULT NULL COMMENT 'Cómo fue el golpe',
ADD COLUMN golpe_recibio_tratamiento BOOLEAN DEFAULT FALSE COMMENT 'Si recibió tratamiento por el golpe',
ADD COLUMN sangrado_encias BOOLEAN DEFAULT FALSE COMMENT 'Sangrado de encías',
ADD COLUMN movilidad_dentaria BOOLEAN DEFAULT FALSE COMMENT 'Movilidad dentaria',
ADD COLUMN calculo_detalle TEXT DEFAULT NULL COMMENT 'Detalles sobre presencia de cálculo',
ADD COLUMN enfermedad_periodontal_detalle TEXT DEFAULT NULL COMMENT 'Detalles sobre enfermedad periodontal',
ADD COLUMN observaciones_dentales TEXT DEFAULT NULL COMMENT 'Observaciones sobre el estado dental',
ADD COLUMN cantidad_dientes INT DEFAULT NULL COMMENT 'Cantidad de dientes existentes';

-- Mostrar la estructura actualizada de la tabla
DESCRIBE historiaclinica;
