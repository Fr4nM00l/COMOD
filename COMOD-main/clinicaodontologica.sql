-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 19-08-2025 a las 19:55:40
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `clinicaodontologica`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `afeccion`
--

CREATE TABLE `afeccion` (
  `id` int(11) NOT NULL,
  `CodigoSNOMED` varchar(50) DEFAULT NULL,
  `NombreAfeccion` varchar(100) DEFAULT NULL,
  `Descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `afeccion`
--

INSERT INTO `afeccion` (`id`, `CodigoSNOMED`, `NombreAfeccion`, `Descripcion`) VALUES
(1, '234620007', 'Caries dental', 'Lesión en la estructura del diente causada por procesos de desmineralización.'),
(2, '30281000119102', 'Gingivitis', 'Inflamación de las encías, con enrojecimiento y sangrado.'),
(3, '426492004', 'Periodontitis', 'Enfermedad inflamatoria crónica que afecta al tejido de soporte del diente.'),
(4, '44054006', 'Diente fracturado', 'Rotura parcial o completa de la corona o raíz del diente.'),
(5, '56942006', 'Diente impactado', 'Diente que no ha erupcionado completamente debido a obstrucción.'),
(6, '233603009', 'Absceso dental', 'Acumulación de pus en la zona periapical o periodontal debido a infección.'),
(7, '16886004', 'Diente retenido', 'Diente que permanece dentro del hueso o encía sin erupcionar.'),
(8, '109987003', 'Bruxismo', 'Ajuste involuntario y continuo de los dientes que produce desgaste.'),
(9, '65363002', 'Mordida cruzada', 'Maloclusión en la que el diente superior encaja por dentro del inferior.'),
(10, '264588007', 'Hipoplasia de esmalte', 'Defecto de desarrollo que ocasiona reducción de grosor de esmalte.');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalleafeccion`
--

CREATE TABLE `detalleafeccion` (
  `id` int(11) NOT NULL,
  `DetalleDiente_id` int(11) NOT NULL,
  `Afeccion_id` int(11) NOT NULL,
  `ZonaDiente` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `detalleafeccion`
--

INSERT INTO `detalleafeccion` (`id`, `DetalleDiente_id`, `Afeccion_id`, `ZonaDiente`) VALUES
(1, 1, 1, 'Oclusal'),
(2, 2, 2, 'Vestibular'),
(3, 5, 6, 'Periapical'),
(4, 6, 4, 'Vestibular'),
(5, 9, 10, 'Oclusal'),
(6, 10, 1, 'Distal');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detallediente`
--

CREATE TABLE `detallediente` (
  `id` int(11) NOT NULL,
  `Odontograma_id` int(11) NOT NULL,
  `NumDiente` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `detallediente`
--

INSERT INTO `detallediente` (`id`, `Odontograma_id`, `NumDiente`) VALUES
(1, 1, 11),
(2, 1, 12),
(3, 1, 21),
(4, 1, 22),
(5, 2, 11),
(6, 2, 12),
(7, 2, 21),
(8, 2, 22),
(9, 3, 11),
(10, 3, 12),
(11, 3, 21),
(12, 3, 22);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalleturno`
--

CREATE TABLE `detalleturno` (
  `id` int(11) NOT NULL,
  `Odontologo_id` int(11) NOT NULL,
  `Paciente_id` int(11) NOT NULL,
  `FechaTurno` date NOT NULL,
  `HoraTurno` time NOT NULL,
  `tipo_consulta` varchar(100) DEFAULT NULL,
  `duracion` int(11) DEFAULT 30,
  `observaciones` text DEFAULT NULL,
  `estado` enum('pendiente','en_curso','completado','cancelado') DEFAULT 'pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historiaclinica`
--

CREATE TABLE `historiaclinica` (
  `id` int(11) NOT NULL,
  `Fecha` date NOT NULL,
  `Paciente_id` int(11) NOT NULL,
  `ObraSocial` varchar(100) DEFAULT NULL,
  `NumAfiliado` varchar(50) DEFAULT NULL,
  `Alergias` text DEFAULT NULL,
  `Enfermedades` text DEFAULT NULL,
  `Fuma` tinyint(1) DEFAULT 0,
  `Drogas` text DEFAULT NULL,
  `Medicamentos` text DEFAULT NULL,
  `NivelDeDolor` tinyint(4) DEFAULT NULL,
  `Calmante` varchar(100) DEFAULT NULL,
  `GolpeEnDientes` tinyint(1) DEFAULT 0,
  `FechaGolpe` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `historiaclinica`
--

INSERT INTO `historiaclinica` (`id`, `Fecha`, `Paciente_id`, `ObraSocial`, `NumAfiliado`, `Alergias`, `Enfermedades`, `Fuma`, `Drogas`, `Medicamentos`, `NivelDeDolor`, `Calmante`, `GolpeEnDientes`, `FechaGolpe`) VALUES
(1, '2025-05-10', 1, 'Galeno', 'G-1001', 'Ninguna', 'Ninguna', 0, NULL, NULL, 1, 'Ibuprofeno', 0, NULL),
(2, '2025-05-11', 2, 'OSDE', 'O-2002', 'Penicilina', 'Hipertensión', 1, NULL, 'Losartan', 2, 'Paracetamol', 1, '2025-04-15'),
(3, '2025-05-12', 3, 'Swiss Medical', 'S-3003', 'Gluten', 'Ninguna', 0, NULL, NULL, 3, 'Diclofenac', 0, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `odontograma`
--

CREATE TABLE `odontograma` (
  `id` int(11) NOT NULL,
  `Fecha` date NOT NULL,
  `HistoriaClinica_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `odontograma`
--

INSERT INTO `odontograma` (`id`, `Fecha`, `HistoriaClinica_id`) VALUES
(1, '2025-05-10', 1),
(2, '2025-05-11', 2),
(3, '2025-05-12', 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `odontologo`
--

CREATE TABLE `odontologo` (
  `id` int(11) NOT NULL,
  `Nombre` varchar(100) NOT NULL,
  `FechaNacimiento` date DEFAULT NULL,
  `DNI` varchar(15) DEFAULT NULL,
  `Usuario` varchar(50) DEFAULT NULL,
  `Contraseña` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `odontologo`
--

INSERT INTO `odontologo` (`id`, `Nombre`, `FechaNacimiento`, `DNI`, `Usuario`, `Contraseña`) VALUES
(1, 'Dr. Juan Pérez', '1978-03-15', '28333444', 'juanp', 'odo123'),
(2, 'Dra. María López', '1982-06-22', '29222333', 'marial', 'odo456');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `paciente`
--

CREATE TABLE `paciente` (
  `id` int(11) NOT NULL,
  `Nombre` varchar(100) NOT NULL,
  `FechaNacimiento` date DEFAULT NULL,
  `DNI` varchar(15) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `direccion` text DEFAULT NULL,
  `contacto_emergencia` varchar(100) DEFAULT NULL,
  `telefono_emergencia` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `paciente`
--

INSERT INTO `paciente` (`id`, `Nombre`, `FechaNacimiento`, `DNI`) VALUES
(1, 'Sofía Ruiz', '1992-07-19', '40123456'),
(2, 'Diego Ramírez', '1985-02-02', '38987654'),
(3, 'María Estévez', '2001-12-05', '38223344');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `secretario`
--

CREATE TABLE `secretario` (
  `id` int(11) NOT NULL,
  `Nombre` varchar(100) NOT NULL,
  `FechaNacimiento` date DEFAULT NULL,
  `DNI` varchar(15) DEFAULT NULL,
  `Usuario` varchar(50) DEFAULT NULL,
  `Contraseña` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `secretario`
--

INSERT INTO `secretario` (`id`, `Nombre`, `FechaNacimiento`, `DNI`, `Usuario`, `Contraseña`) VALUES
(1, 'Laura Martínez', '1985-04-12', '30123456', 'lauram', 'sec123'),
(2, 'Verónica Gómez', '1990-08-25', '31234567', 'verog', 'sec456');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `procedimientos`
-- Catálogo de procedimientos dentales posibles de aplicar a un diente
--

CREATE TABLE `procedimientos` (
  `id` int(11) NOT NULL,
  `CodigoSNOMED` varchar(50) DEFAULT NULL,
  `NombreProcedimiento` varchar(100) NOT NULL,
  `Descripcion` text DEFAULT NULL,
  `DuracionMinutos` smallint(6) DEFAULT NULL,
  `Costo` decimal(10,2) DEFAULT NULL,
  `Activo` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `procedimientos`
--
INSERT INTO `procedimientos` (`id`, `CodigoSNOMED`, `NombreProcedimiento`, `Descripcion`, `DuracionMinutos`, `Costo`, `Activo`) VALUES
(1, '234849007', 'Obturación (empaste) resina', 'Restauración de caries con resina compuesta', 45, 12000.00, 1),
(2, '234936006', 'Tratamiento de conducto', 'Endodoncia de diente afectado', 90, 45000.00, 1),
(3, '234952009', 'Extracción simple', 'Extracción no quirúrgica de pieza dentaria', 30, 18000.00, 1),
(4, '310627008', 'Limpieza profesional', 'Profilaxis y remoción de sarro', 30, 10000.00, 1),
(5, '234965007', 'Corona provisoria', 'Colocación de corona temporal', 60, 30000.00, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalleprocedimiento`
-- Relación de procedimientos planificados/realizados por diente
--

CREATE TABLE `detalleprocedimiento` (
  `id` int(11) NOT NULL,
  `DetalleDiente_id` int(11) NOT NULL,
  `Procedimiento_id` int(11) NOT NULL,
  `Odontologo_id` int(11) DEFAULT NULL,
  `Fecha` date DEFAULT NULL,
  `ZonaDiente` varchar(50) DEFAULT NULL,
  `Estado` enum('pendiente','realizado','cancelado') DEFAULT 'pendiente',
  `Observaciones` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `afeccion`
--
ALTER TABLE `afeccion`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `CodigoSNOMED` (`CodigoSNOMED`);

--
-- Indices de la tabla `detalleafeccion`
--
ALTER TABLE `detalleafeccion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `DetalleDiente_id` (`DetalleDiente_id`),
  ADD KEY `Afeccion_id` (`Afeccion_id`);

--
-- Indices de la tabla `detallediente`
--
ALTER TABLE `detallediente`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Odontograma_id` (`Odontograma_id`);

--
-- Indices de la tabla `detalleturno`
--
ALTER TABLE `detalleturno`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Odontologo_id` (`Odontologo_id`),
  ADD KEY `Paciente_id` (`Paciente_id`);

--
-- Indices de la tabla `historiaclinica`
--
ALTER TABLE `historiaclinica`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Paciente_id` (`Paciente_id`);

--
-- Indices de la tabla `odontograma`
--
ALTER TABLE `odontograma`
  ADD PRIMARY KEY (`id`),
  ADD KEY `HistoriaClinica_id` (`HistoriaClinica_id`);

--
-- Indices de la tabla `odontologo`
--
ALTER TABLE `odontologo`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `DNI` (`DNI`),
  ADD UNIQUE KEY `Usuario` (`Usuario`);

--
-- Indices de la tabla `paciente`
--
ALTER TABLE `paciente`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `DNI` (`DNI`);

--
-- Indices de la tabla `secretario`
--
ALTER TABLE `secretario`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `DNI` (`DNI`),
  ADD UNIQUE KEY `Usuario` (`Usuario`);

--
-- Indices de la tabla `procedimientos`
--
ALTER TABLE `procedimientos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `CodigoSNOMED` (`CodigoSNOMED`),
  ADD UNIQUE KEY `NombreProcedimiento` (`NombreProcedimiento`);

--
-- Indices de la tabla `detalleprocedimiento`
--
ALTER TABLE `detalleprocedimiento`
  ADD PRIMARY KEY (`id`),
  ADD KEY `DetalleDiente_id` (`DetalleDiente_id`),
  ADD KEY `Procedimiento_id` (`Procedimiento_id`),
  ADD KEY `Odontologo_id` (`Odontologo_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `afeccion`
--
ALTER TABLE `afeccion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `detalleafeccion`
--
ALTER TABLE `detalleafeccion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `detallediente`
--
ALTER TABLE `detallediente`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `detalleturno`
--
ALTER TABLE `detalleturno`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `historiaclinica`
--
ALTER TABLE `historiaclinica`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `odontograma`
--
ALTER TABLE `odontograma`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `odontologo`
--
ALTER TABLE `odontologo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `paciente`
--
ALTER TABLE `paciente`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `secretario`
--
ALTER TABLE `secretario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `procedimientos`
--
ALTER TABLE `procedimientos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `detalleprocedimiento`
--
ALTER TABLE `detalleprocedimiento`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `detalleafeccion`
--
ALTER TABLE `detalleafeccion`
  ADD CONSTRAINT `detalleafeccion_ibfk_1` FOREIGN KEY (`DetalleDiente_id`) REFERENCES `detallediente` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalleafeccion_ibfk_2` FOREIGN KEY (`Afeccion_id`) REFERENCES `afeccion` (`id`);

--
-- Filtros para la tabla `detallediente`
--
ALTER TABLE `detallediente`
  ADD CONSTRAINT `detallediente_ibfk_1` FOREIGN KEY (`Odontograma_id`) REFERENCES `odontograma` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `detalleturno`
--
ALTER TABLE `detalleturno`
  ADD CONSTRAINT `detalleturno_ibfk_1` FOREIGN KEY (`Odontologo_id`) REFERENCES `odontologo` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalleturno_ibfk_2` FOREIGN KEY (`Paciente_id`) REFERENCES `paciente` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `historiaclinica`
--
ALTER TABLE `historiaclinica`
  ADD CONSTRAINT `historiaclinica_ibfk_1` FOREIGN KEY (`Paciente_id`) REFERENCES `paciente` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `odontograma`
--
ALTER TABLE `odontograma`
  ADD CONSTRAINT `odontograma_ibfk_1` FOREIGN KEY (`HistoriaClinica_id`) REFERENCES `historiaclinica` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `detalleprocedimiento`
--
ALTER TABLE `detalleprocedimiento`
  ADD CONSTRAINT `detalleprocedimiento_ibfk_1` FOREIGN KEY (`DetalleDiente_id`) REFERENCES `detallediente` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalleprocedimiento_ibfk_2` FOREIGN KEY (`Procedimiento_id`) REFERENCES `procedimientos` (`id`),
  ADD CONSTRAINT `detalleprocedimiento_ibfk_3` FOREIGN KEY (`Odontologo_id`) REFERENCES `odontologo` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
