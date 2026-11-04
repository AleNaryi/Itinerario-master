-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 10-07-2026

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `estadio_db`
--
CREATE DATABASE IF NOT EXISTS `estadio_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `estadio_db`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asignaciones_recursos`
--

CREATE TABLE `asignaciones_recursos` (
  `id` int(11) NOT NULL,
  `recurso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha_asignacion` datetime DEFAULT current_timestamp(),
  `fecha_devolucion_esperada` date DEFAULT NULL,
  `fecha_devolucion_real` datetime DEFAULT NULL,
  `estado_asignacion_id` int(11) DEFAULT 1,
  `notas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `contrato`
--

CREATE TABLE `contrato` (
  `id_contrato` int(11) NOT NULL,
  `id_patrocinador` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `estado` varchar(100) NOT NULL,
  `estatus` varchar(100) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `monto_total` decimal(12,2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `color` varchar(7) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `elementos_guion`
--

CREATE TABLE `elementos_guion` (
  `id` int(11) NOT NULL,
  `guion_id` int(11) NOT NULL,
  `fecha_id` int(11) DEFAULT NULL,
  `tipo` varchar(20) NOT NULL,
  `hora` time DEFAULT NULL,
  `inning` int(11) DEFAULT NULL,
  `medio_inning` varchar(10) DEFAULT NULL,
  `contenido` text NOT NULL,
  `duracion_estimada` int(11) NOT NULL,
  `encargado` varchar(100) NOT NULL,
  `orden` int(11) DEFAULT NULL,
  `creado_en` datetime DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `inicio_curso` datetime DEFAULT NULL COMMENT 'Momento de entrada a en_curso'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_asignacion`
--

CREATE TABLE `estado_asignacion` (
  `id` int(11) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Datos para la tabla `estado_asignacion`
--

INSERT INTO `estado_asignacion` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Pendiente', 'Asignación activa, pendiente de devolución'),
(2, 'Devuelto', 'Recurso devuelto exitosamente'),
(3, 'Vencido', 'Asignación vencida (no devuelto a tiempo)');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_recurso`
--

CREATE TABLE `estado_recurso` (
  `id` int(11) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Datos para la tabla `estado_recurso`
--

INSERT INTO `estado_recurso` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Disponible', 'Recurso disponible para uso o asignación'),
(2, 'Asignado', 'Recurso actualmente asignado a un usuario'),
(3, 'En Mantenimiento', 'Recurso en proceso de mantenimiento o reparación'),
(4, 'Dañado', 'Recurso reportado como dañado'),
(5, 'Baja', 'Recurso dado de baja del inventario');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `guiones`
--

CREATE TABLE `guiones` (
  `id` int(11) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `inicio_show` datetime DEFAULT NULL COMMENT 'Momento de Iniciar del show en vivo',
  `creado_en` datetime DEFAULT NULL,
  `modificado_en` datetime DEFAULT NULL,
  `tiempo_inning` int(11) DEFAULT NULL,
  `grupo_id` varchar(36) DEFAULT NULL,
  `status` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `guion_fechas`
--

CREATE TABLE `guion_fechas` (
  `id` int(11) NOT NULL,
  `guion_id` int(11) NOT NULL,
  `fecha` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_chat`
--

CREATE TABLE `historial_chat` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `mensaje_usuario` text NOT NULL,
  `respuesta_ia` text NOT NULL,
  `contexto` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`contexto`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_mantenimiento`
--

CREATE TABLE `historial_mantenimiento` (
  `id` int(11) NOT NULL,
  `mantenimiento_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `accion` varchar(50) NOT NULL,
  `descripcion` text NOT NULL,
  `creado_en` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mantenimientos`
--

CREATE TABLE `mantenimientos` (
  `id` int(11) NOT NULL,
  `recurso_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `estado` varchar(20) DEFAULT 'en_espera',
  `fecha_ingreso` date NOT NULL,
  `fecha_salida` date DEFAULT NULL,
  `diagnostico` text DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  `creado_en` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos`
--

CREATE TABLE `pagos` (
  `id_pago` int(11) NOT NULL,
  `id_contrato` int(11) NOT NULL,
  `monto` decimal(12,2) NOT NULL,
  `tipo_pago` varchar(20) NOT NULL,
  `referencia` varchar(100) DEFAULT NULL,
  `fecha_pago` date NOT NULL,
  `hora_pago` time NOT NULL,
  `registrado_por` int(11) DEFAULT NULL,
  `Descripcion` text DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `estado` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `patrocinadores`
--

CREATE TABLE `patrocinadores` (
  `id_patrocinador` int(11) NOT NULL,
  `nombre_empresa` varchar(100) NOT NULL,
  `rif` varchar(20) NOT NULL,
  `tipo_contrato` int(11) NOT NULL,
  `nombre_contacto` text NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `estado` int(11) NOT NULL,
  `encargado_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `premios`
--

CREATE TABLE `premios` (
  `id` int(11) NOT NULL,
  `id_patrocinador` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'pendiente',
  `fecha_creacion` date NOT NULL DEFAULT current_timestamp(),
  `fecha_entrega` datetime DEFAULT NULL,
  `entregado_por` int(11) DEFAULT NULL,
  `hora_creacion` time NOT NULL,
  `foto` varchar(200) DEFAULT 'default-premio.png',
  `cantidad` int(11) NOT NULL DEFAULT 1,
  `cantidad_entregada` int(11) NOT NULL DEFAULT 0,
  `estatus` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recursos`
--

CREATE TABLE `recursos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `tipo_id` int(11) NOT NULL,
  `estado_id` int(11) NOT NULL DEFAULT 1,
  `fecha_compra` date DEFAULT NULL,
  `costo` decimal(10,2) DEFAULT NULL,
  `eliminado` tinyint(1) NOT NULL DEFAULT 0,
  `creado_en` datetime DEFAULT current_timestamp(),
  `modificado_en` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reels`
--

CREATE TABLE `reels` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `id_patrocinador` int(11) DEFAULT NULL,
  `duracion_total` float DEFAULT 0,
  `creado_en` datetime DEFAULT current_timestamp(),
  `modificado_en` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tareas`
--

CREATE TABLE `tareas` (
  `id_tarea` int(11) NOT NULL,
  `Nombre_Tarea` varchar(255) NOT NULL,
  `Instruccion` varchar(255) NOT NULL,
  `id_usuario_creador` int(11) DEFAULT NULL,
  `Estatus` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tareas_asignadas`
--

CREATE TABLE `tareas_asignadas` (
  `id_asignacion` int(11) NOT NULL,
  `id_tarea` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `Estado` varchar(50) DEFAULT 'Pendiente',
  `fecha_asignacion_tarea` datetime DEFAULT NULL,
  `Estatus` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_recurso`
--

CREATE TABLE `tipo_recurso` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Datos para la tabla `tipo_recurso`
--

INSERT INTO `tipo_recurso` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Equipo de PC', 'Computadoras, laptops, tablets'),
(2, 'Equipo de Video', 'Cámaras, proyectores, monitores, pantallas LED'),
(3, 'Iluminación', 'Luces, reflectores, dimmers, mesas de luz'),
(4, 'Mobiliario', 'Mesas, sillas, stands, tarimas'),
(5, 'Instrumento', 'Instrumentos musicales, amplificadores'),
(6, 'Vehículo', 'Vehículos de producción y logística'),
(7, 'Otro', 'Otros tipos de recursos'),
(8, 'Microfono', 'Micrófonos inalámbricos y de solapa');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `videos`
--

CREATE TABLE `videos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `duracion_segundos` int(11) DEFAULT 0,
  `orden` int(11) DEFAULT NULL,
  `reel_id` int(11) NOT NULL,
  `id_patrocinador` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
--
-- VOLCADO DE DATOS
-- --------------------------------------------------------

--
-- Datos para la tabla `departamentos`
--

INSERT INTO `departamentos` (`id`, `nombre`, `descripcion`, `color`) VALUES
(1, 'Producción', 'Puesta en escena, guiones y transmisión', '#e74c3c'),
(2, 'Técnica', 'Soporte técnico, mantenimiento de equipos', '#3498db'),
(3, 'Comercial', 'Gestión de patrocinadores y contratos', '#2ecc71'),
(4, 'Administración', 'Gestión general del estadio', '#9b59b6'),
(5, 'Operaciones', 'Operaciones en vivo y palco', '#f39c12');

--
-- Datos para la tabla `patrocinadores`
--

INSERT INTO `patrocinadores` (`id_patrocinador`, `nombre_empresa`, `rif`, `tipo_contrato`, `nombre_contacto`, `telefono`, `email`, `estado`, `encargado_id`) VALUES
(1, 'Maltin Polar', 'J-00005820-9', 2, 'José Luis Rodríguez', '0212-4003000', 'jrodriguez@polar.com', 1, 3),
(2, 'Pepsi Venezuela', 'J-00028049-5', 2, 'María Fernanda López', '0212-5002000', 'mlopez@pepsi.com', 1, 4),
(3, 'Café Flor de Arauca', 'J-40206831-0', 1, 'Carlos Mendoza', '0251-2661100', 'cmendoza@cafeflor.com', 1, 5),
(4, 'Tubrica C.A', 'J-31028456-7', 1, 'Pedro Jiménez', '0241-8581000', 'p jimenez@tubrica.com', 1, 6),
(5, 'Banesco Banco Universal', 'J-00078321-3', 2, 'Ana Sofía Pérez', '0212-2064646', 'aperez@banesco.com', 1, 3),
(6, 'Movilnet C.A', 'J-30472189-0', 1, 'Roberto Díaz', '0212-3001000', 'rdiaz@movilnet.com', 1, 4),
(7, 'Alimentos Mary', 'J-29587314-6', 1, 'Luis Hernández', '0241-8782000', 'lhernandez@alimentosmary.com', 1, 5),
(8, 'Farmatodo C.A', 'J-00032815-8', 2, 'Gabriela Torres', '0212-7003000', 'gtorres@farmatodo.com', 1, 6),
(9, 'Cerveza Regional', 'J-40157623-8', 1, 'Manuel Castillo', '0261-7984000', 'mcastillo@regional.com', 1, 3);

--
-- Datos para la tabla `contrato`
--

INSERT INTO `contrato` (`id_contrato`, `id_patrocinador`, `fecha_inicio`, `fecha_fin`, `estado`, `estatus`, `tipo`, `monto_total`) VALUES
(1, 1, '2026-04-01', '2026-10-31', '1', 'Vigente', '2', 85000.00),
(2, 2, '2026-05-01', '2026-09-30', '1', 'Vigente', '2', 62000.00),
(3, 3, '2026-06-01', '2026-08-31', '1', 'Vigente', '1', 25000.00),
(4, 4, '2026-04-15', '2026-07-15', '0', 'Vencido', '1', 30000.00),
(5, 5, '2026-03-01', '2026-12-31', '1', 'Vigente', '3', 120000.00),
(6, 6, '2026-06-01', '2026-09-30', '1', 'Vigente', '1', 18000.00),
(7, 7, '2026-07-01', '2026-09-30', '1', 'Vigente', '1', 15000.00),
(8, 8, '2026-04-01', '2026-11-30', '1', 'Vigente', '2', 45000.00),
(9, 9, '2026-05-15', '2026-08-15', '1', 'Vigente', '1', 22000.00);

--
-- Datos para la tabla `recursos`
--

INSERT INTO `recursos` (`id`, `nombre`, `descripcion`, `tipo_id`, `estado_id`, `fecha_compra`, `costo`, `eliminado`) VALUES
(1, 'Sony PXW-Z150', 'Cámara 4K profesional para transmisión en vivo', 2, 1, '2025-03-15', 4500.00, 0),
(2, 'Pantalla LED 55"', 'Pantalla LED para sala de control y palco', 2, 1, '2025-06-20', 3200.00, 0),
(3, 'Yamaha TF3', 'Mezcladora digital 24 canales para audio en vivo', 8, 1, '2024-11-10', 5800.00, 0),
(4, 'Shure SM58 x4', 'Micrófonos dinámicos inalámbricos para presentadores', 8, 1, '2025-08-05', 1200.00, 0),
(5, 'Dell XPS 15', 'Laptop para control de guiones y presentaciones', 1, 1, '2025-09-01', 2100.00, 0),
(6, 'Epson EB-L615U', 'Proyector láser 6000 lúmenes para pantallas del estadio', 2, 1, '2025-01-20', 3800.00, 0),
(7, 'Mesa de iluminación DMX', 'Controlador de luces para escenario principal', 3, 1, '2024-12-05', 2600.00, 0),
(8, 'Sillas plegables x20', 'Set de sillas para área de producción', 4, 1, '2025-04-10', 400.00, 0),
(9, 'Bafle JBL PRX812W', 'Bafle inalámbrico 12" para zona de transmisión', 7, 1, '2025-07-15', 1800.00, 0),
(10, 'iPad Pro 12.9"', 'Tablet para control remoto de presentaciones', 1, 1, '2025-10-01', 1100.00, 0);

--
-- Datos para la tabla `tipo_recurso` (se insertan arriba)

--
-- Datos para la tabla `premios`
--

INSERT INTO `premios` (`id`, `id_patrocinador`, `nombre`, `descripcion`, `estado`, `fecha_creacion`, `fecha_entrega`, `entregado_por`, `hora_creacion`, `foto`, `cantidad`, `cantidad_entregada`, `estatus`) VALUES
(1, 1, '6 Pack Maltin Polar', 'Caja de 6 latas de Maltin Polar 350ml', 'entregado', '2026-06-15', '2026-06-18 19:30:00', 3, '10:00:00', 'default-premio.png', 50, 12, 0),
(2, 2, 'Pepsi Cola 2L x3', 'Tres botellas de Pepsi Cola 2 litros', 'entregado', '2026-06-15', '2026-06-18 20:15:00', 4, '10:30:00', 'default-premio.png', 30, 8, 0),
(3, 5, 'Tarjeta Banesco $50', 'Tarjeta de regalo Banesco por 50$', 'pendiente', '2026-07-01', NULL, NULL, '09:00:00', 'default-premio.png', 10, 0, 1),
(4, 3, 'Café Flor de Arauca 250g', 'Paquete de café premium tostado oscuro', 'entregado', '2026-06-20', '2026-06-22 18:45:00', 5, '11:00:00', 'default-premio.png', 20, 5, 0),
(5, 8, 'Kit Farmatodo', 'Kit de productos de higiene personal', 'pendiente', '2026-07-05', NULL, NULL, '14:00:00', 'default-premio.png', 40, 0, 1),
(6, 6, 'Camiseta Movilnet', 'Camiseta oficial Movilnet edición beisbol', 'entregado', '2026-06-10', '2026-06-12 19:00:00', 3, '08:30:00', 'default-premio.png', 100, 25, 0),
(7, 4, 'Combo Tubrica', 'Kit de herramientas básicas Tubrica', 'pendiente', '2026-07-08', NULL, NULL, '15:30:00', 'default-premio.png', 15, 0, 1),
(8, 9, 'Cerveza Regional 6 Pack', 'Caja de 6 latas de Cerveza Regional', 'pendiente', '2026-07-10', NULL, NULL, '12:00:00', 'default-premio.png', 25, 0, 1),
(9, 1, 'Polar Pina 1L x2', 'Dos botellas de Polar Pina 1 litro', 'entregado', '2026-06-25', '2026-06-28 20:00:00', 4, '09:30:00', 'default-premio.png', 40, 15, 0),
(10, 7, 'Caja Alimentos Mary', 'Caja de snacks y dulces variados', 'pendiente', '2026-07-12', NULL, NULL, '16:00:00', 'default-premio.png', 30, 0, 1);

--
-- Datos para la tabla `guiones`
--

INSERT INTO `guiones` (`id`, `nombre`, `estado`, `creado_en`, `modificado_en`, `tiempo_inning`, `grupo_id`, `status`) VALUES
(1, 'Cardenales vs Leones - 2026-07-10', 'publicado', '2026-07-08 09:00:00', '2026-07-09 14:30:00', 120, NULL, 1),
(2, 'Cardenales vs Tiburones - 2026-07-12', 'borrador', '2026-07-10 10:00:00', '2026-07-10 10:00:00', 120, NULL, 1),
(3, 'Cardenales vs Navegantes - 2026-07-15', 'borrador', '2026-07-10 11:00:00', '2026-07-10 11:00:00', 120, NULL, 1),
(4, 'Cardenales vs Tigres - 2026-07-18', 'borrador', '2026-07-10 12:00:00', '2026-07-10 12:00:00', 120, NULL, 1),
(5, 'Cardenales vs Águilas - 2026-07-20', 'borrador', '2026-07-10 13:00:00', '2026-07-10 13:00:00', 120, NULL, 1);

--
-- Datos para la tabla `guion_fechas`
--

INSERT INTO `guion_fechas` (`id`, `guion_id`, `fecha`) VALUES
(1, 1, '2026-07-10'),
(2, 2, '2026-07-12'),
(3, 3, '2026-07-15'),
(4, 4, '2026-07-18'),
(5, 5, '2026-07-20');

--
-- Datos para la tabla `elementos_guion`
--

INSERT INTO `elementos_guion` (`id`, `guion_id`, `fecha_id`, `tipo`, `hora`, `inning`, `medio_inning`, `contenido`, `duracion_estimada`, `encargado`, `orden`, `creado_en`, `estado`) VALUES
-- Guion 1: Cardenales vs Leones
(1, 1, 1, 'pregame', '17:00:00', NULL, NULL, 'Apertura de puertas y bienvenida', 300, 'keiver', 1, '2026-07-08 09:05:00', 'pendiente'),
(2, 1, 1, 'pregame', '17:30:00', NULL, NULL, 'Presentación de alineaciones por pantallas', 180, 'Genesis', 2, '2026-07-08 09:06:00', 'pendiente'),
(3, 1, 1, 'pregame', '18:00:00', NULL, NULL, 'Ceremonia de lanzamiento inaugural', 240, 'keiver', 3, '2026-07-08 09:07:00', 'pendiente'),
(4, 1, 1, 'pregame', '18:15:00', NULL, NULL, 'Himno Nacional - Orquesta del Estado', 180, 'Genesis', 4, '2026-07-08 09:08:00', 'pendiente'),
(5, 1, 1, 'pregame', '18:20:00', NULL, NULL, 'Video bienvenida patrocinadores', 60, 'keiver', 5, '2026-07-08 09:09:00', 'pendiente'),
(6, 1, 1, 'game', NULL, 1, 'baja', 'Publicidad Maltin Polar - Jumbotron', 30, 'keiver', 1, '2026-07-08 09:10:00', NULL),
(7, 1, 1, 'game', NULL, 1, 'alta', 'Publicidad Pepsi - Bafles del estadio', 30, 'Genesis', 2, '2026-07-08 09:11:00', NULL),
(8, 1, 1, 'game', NULL, 2, 'baja', 'Concurso Maltin Polar - Lanzamiento de pelota', 120, 'keiver', 3, '2026-07-08 09:12:00', NULL),
(9, 1, 1, 'game', NULL, 3, 'alta', 'Publicidad Banesco - Finanzas personales', 30, 'Genesis', 4, '2026-07-08 09:13:00', NULL),
(10, 1, 1, 'game', NULL, 4, 'baja', 'Reels Café Flor de Arauca', 25, 'keiver', 5, '2026-07-08 09:14:00', NULL),
(11, 1, 1, 'game', NULL, 5, 'alta', 'Publicidad Movilnet - Plan datos beisbol', 30, 'Genesis', 6, '2026-07-08 09:15:00', NULL),
(12, 1, 1, 'game', NULL, 6, 'baja', 'Ceremonia de premiación fan del juego', 180, 'keiver', 7, '2026-07-08 09:16:00', NULL),
(13, 1, 1, 'game', NULL, 7, 'alta', 'Publicidad Farmatodo - Salud y bienestar', 30, 'Genesis', 8, '2026-07-08 09:17:00', NULL),
(14, 1, 1, 'game', NULL, 8, 'baja', 'Reels Cerveza Regional', 25, 'keiver', 9, '2026-07-08 09:18:00', NULL),
(15, 1, 1, 'postgame', NULL, NULL, NULL, 'Entrega de premios a ganadores', 300, 'keiver', 1, '2026-07-08 09:19:00', NULL),
(16, 1, 1, 'postgame', NULL, NULL, NULL, 'Entrevistas post-juego y agradecimientos', 600, 'Genesis', 2, '2026-07-08 09:20:00', NULL),
-- Guion 2: Cardenales vs Tiburones
(17, 2, 2, 'pregame', '17:00:00', NULL, NULL, 'Apertura de puertas', 300, 'keiver', 1, '2026-07-10 10:05:00', 'pendiente'),
(18, 2, 2, 'pregame', '17:30:00', NULL, NULL, 'Presentación de alineaciones', 180, 'Genesis', 2, '2026-07-10 10:06:00', 'pendiente'),
(19, 2, 2, 'pregame', '18:00:00', NULL, NULL, 'Ceremonia de lanzamiento inaugural', 240, 'keiver', 3, '2026-07-10 10:07:00', 'pendiente'),
(20, 2, 2, 'pregame', '18:15:00', NULL, NULL, 'Himno Nacional', 180, 'Genesis', 4, '2026-07-10 10:08:00', 'pendiente'),
(21, 2, 2, 'game', NULL, 1, 'baja', 'Publicidad Maltin Polar', 30, 'keiver', 1, '2026-07-10 10:10:00', NULL),
(22, 2, 2, 'game', NULL, 2, 'baja', 'Concurso Alimentos Mary - Sabor del juego', 120, 'keiver', 2, '2026-07-10 10:11:00', NULL),
(23, 2, 2, 'game', NULL, 3, 'alta', 'Publicidad Tubrica', 30, 'Genesis', 3, '2026-07-10 10:12:00', NULL),
(24, 2, 2, 'game', NULL, 5, 'baja', 'Reels Banesco', 25, 'keiver', 4, '2026-07-10 10:13:00', NULL),
(25, 2, 2, 'game', NULL, 7, 'alta', 'Publicidad Pepsi', 30, 'Genesis', 5, '2026-07-10 10:14:00', NULL),
-- Guion 3: Cardenales vs Navegantes
(26, 3, 3, 'pregame', '18:00:00', NULL, NULL, 'Apertura de puertas y animación', 300, 'keiver', 1, '2026-07-10 11:05:00', 'pendiente'),
(27, 3, 3, 'pregame', '18:30:00', NULL, NULL, 'Himno Nacional y presentación', 240, 'Genesis', 2, '2026-07-10 11:06:00', 'pendiente'),
(28, 3, 3, 'game', NULL, 1, 'baja', 'Publicidad Movilnet', 30, 'keiver', 1, '2026-07-10 11:08:00', NULL),
(29, 3, 3, 'game', NULL, 3, 'baja', 'Concurso Café Flor de Arauca', 120, 'keiver', 2, '2026-07-10 11:09:00', NULL),
(30, 3, 3, 'game', NULL, 5, 'alta', 'Publicidad Farmatodo', 30, 'Genesis', 3, '2026-07-10 11:10:00', NULL),
(31, 3, 3, 'game', NULL, 7, 'baja', 'Reels Cerveza Regional', 25, 'keiver', 4, '2026-07-10 11:11:00', NULL);

--
-- Datos para la tabla `pagos`
--

INSERT INTO `pagos` (`id_pago`, `id_contrato`, `monto`, `tipo_pago`, `referencia`, `fecha_pago`, `hora_pago`, `registrado_por`, `Descripcion`, `fecha_registro`, `estado`) VALUES
(1, 1, 21250.00, 'Transferencia', 'TRF-2026-001', '2026-04-05', '10:00:00', 3, 'Pago inicial contrato Maltin Polar - 25%', '2026-04-05 10:05:00', 1),
(2, 1, 21250.00, 'Transferencia', 'TRF-2026-002', '2026-06-05', '10:00:00', 3, 'Segundo abono contrato Maltin Polar - 25%', '2026-06-05 10:05:00', 1),
(3, 2, 15500.00, 'Transferencia', 'TRF-2026-003', '2026-05-10', '11:00:00', 4, 'Pago inicial contrato Pepsi - 25%', '2026-05-10 11:05:00', 1),
(4, 5, 30000.00, 'Transferencia', 'TRF-2026-004', '2026-03-15', '09:30:00', 3, 'Pago inicial contrato Banesco - 25%', '2026-03-15 09:35:00', 1),
(5, 5, 30000.00, 'Transferencia', 'TRF-2026-005', '2026-06-15', '09:30:00', 3, 'Segundo abono contrato Banesco - 25%', '2026-06-15 09:35:00', 1),
(6, 8, 11250.00, 'Efectivo', 'EFE-2026-001', '2026-04-10', '14:00:00', 5, 'Pago inicial contrato Farmatodo - 25%', '2026-04-10 14:05:00', 1),
(7, 3, 6250.00, 'Efectivo', 'EFE-2026-002', '2026-06-10', '15:00:00', 5, 'Pago inicial contrato Café Flor - 50%', '2026-06-10 15:05:00', 1),
(8, 9, 5500.00, 'Transferencia', 'TRF-2026-006', '2026-05-20', '16:00:00', 6, 'Pago inicial contrato Cerveza Regional - 25%', '2026-05-20 16:05:00', 1);

--
-- Datos para la tabla `reels`
--

INSERT INTO `reels` (`id`, `nombre`, `id_patrocinador`, `duracion_total`, `creado_en`, `modificado_en`) VALUES
(1, 'Maltin Polar - Edición Verano', 1, 45.0, '2026-06-01 10:00:00', '2026-06-01 10:00:00'),
(2, 'Pepsi - Noche de Beisbol', 2, 30.0, '2026-06-05 11:00:00', '2026-06-05 11:00:00'),
(3, 'Banesco - Finanzas Familiares', 5, 35.0, '2026-06-10 09:00:00', '2026-06-10 09:00:00'),
(4, 'Café Flor de Arauca - Momento Café', 3, 25.0, '2026-06-15 14:00:00', '2026-06-15 14:00:00'),
(5, 'Movilnet - Conectados al Juego', 6, 20.0, '2026-06-20 10:00:00', '2026-06-20 10:00:00');

--
-- Datos para la tabla `videos`
--

INSERT INTO `videos` (`id`, `nombre`, `duracion_segundos`, `orden`, `reel_id`, `id_patrocinador`) VALUES
(1, 'Maltin Polar - Spot 15s', 15, 1, 1, 1),
(2, 'Maltin Polar - Behind the scenes', 15, 2, 1, 1),
(3, 'Maltin Polar - Testimonios fans', 15, 3, 1, 1),
(4, 'Pepsi - Spot principal', 15, 1, 2, 2),
(5, 'Pepsi - Momento refresh', 15, 2, 2, 2),
(6, 'Banesco - Consejos financieros', 20, 1, 3, 5),
(7, 'Banesco - Beneficios tarjeta', 15, 2, 3, 5),
(8, 'Café Flor - Tueste artesanal', 15, 1, 4, 3),
(9, 'Café Flor - Recetas', 10, 2, 4, 3),
(10, 'Movilnet - Plan beisbol', 10, 1, 5, 6),
(11, 'Movilnet - Conectividad', 10, 2, 5, 6);

--
-- Datos para la tabla `tareas`
--

INSERT INTO `tareas` (`id_tarea`, `Nombre_Tarea`, `Instruccion`, `id_usuario_creador`, `Estatus`) VALUES
(1, 'Verificar equipo de transmisión', 'Revisar estado de cámaras, mezcladora y pantallas antes del juego', 3, 1),
(2, 'Calibrar sonido del estadio', 'Ajustar niveles de audio en bafles principales y zonas secundarias', 3, 1),
(3, 'Preparar contenido Jumbotron', 'Cargar videos de patrocinadores y spots en el sistema de pantallas', 4, 1),
(4, 'Revisar iluminación del campo', 'Verificar focos principales, focos de juego y luz de emergencia', 5, 1),
(5, 'Entregar kits de premios', 'Preparar y entregar premios a zona de animación 2 horas antes del juego', 6, 1),
(6, 'Coordinar llegada de patrocinadores', 'Confirmar asistencia y asignar accesos a invitados especiales', 3, 1);

--
-- Datos para la tabla `tareas_asignadas`
--

INSERT INTO `tareas_asignadas` (`id_asignacion`, `id_tarea`, `id_usuario`, `Estado`, `fecha_asignacion_tarea`, `Estatus`) VALUES
(1, 1, 4, 'Completada', '2026-07-09 14:00:00', 1),
(2, 2, 5, 'Completada', '2026-07-09 14:30:00', 1),
(3, 3, 4, 'En Progreso', '2026-07-09 15:00:00', 1),
(4, 4, 6, 'Pendiente', '2026-07-10 08:00:00', 1),
(5, 5, 5, 'Pendiente', '2026-07-10 09:00:00', 1),
(6, 6, 3, 'Pendiente', '2026-07-10 10:00:00', 1);

-- --------------------------------------------------------

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `asignaciones_recursos`
--
ALTER TABLE `asignaciones_recursos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_asignaciones_recurso` (`recurso_id`),
  ADD KEY `idx_asignaciones_estado` (`estado_asignacion_id`);

--
-- Indices de la tabla `contrato`
--
ALTER TABLE `contrato`
  ADD PRIMARY KEY (`id_contrato`),
  ADD KEY `id_patrocinador` (`id_patrocinador`);

--
-- Indices de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `elementos_guion`
--
ALTER TABLE `elementos_guion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `guion_id` (`guion_id`),
  ADD KEY `fecha_id` (`fecha_id`);

--
-- Indices de la tabla `estado_asignacion`
--
ALTER TABLE `estado_asignacion`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `estado_recurso`
--
ALTER TABLE `estado_recurso`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `guiones`
--
ALTER TABLE `guiones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_grupo_id` (`grupo_id`);

--
-- Indices de la tabla `guion_fechas`
--
ALTER TABLE `guion_fechas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `guion_id` (`guion_id`);

--
-- Indices de la tabla `historial_chat`
--
ALTER TABLE `historial_chat`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `historial_mantenimiento`
--
ALTER TABLE `historial_mantenimiento`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `idx_historial_mantenimiento` (`mantenimiento_id`);

--
-- Indices de la tabla `mantenimientos`
--
ALTER TABLE `mantenimientos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `idx_mantenimientos_estado` (`estado`),
  ADD KEY `idx_mantenimientos_recurso` (`recurso_id`);

--
-- Indices de la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD PRIMARY KEY (`id_pago`),
  ADD KEY `id_contrato` (`id_contrato`);

--
-- Indices de la tabla `patrocinadores`
--
ALTER TABLE `patrocinadores`
  ADD PRIMARY KEY (`id_patrocinador`);

--
-- Indices de la tabla `premios`
--
ALTER TABLE `premios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_patrocinador` (`id_patrocinador`);

--
-- Indices de la tabla `recursos`
--
ALTER TABLE `recursos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_recursos_tipo` (`tipo_id`),
  ADD KEY `idx_recursos_estado` (`estado_id`);

--
-- Indices de la tabla `reels`
--
ALTER TABLE `reels`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_patrocinador` (`id_patrocinador`);

--
-- Indices de la tabla `tareas`
--
ALTER TABLE `tareas`
  ADD PRIMARY KEY (`id_tarea`);

--
-- Indices de la tabla `tareas_asignadas`
--
ALTER TABLE `tareas_asignadas`
  ADD PRIMARY KEY (`id_asignacion`),
  ADD KEY `id_tarea` (`id_tarea`);

--
-- Indices de la tabla `tipo_recurso`
--
ALTER TABLE `tipo_recurso`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `videos`
--
ALTER TABLE `videos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_videos_reel` (`reel_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `asignaciones_recursos`
--
ALTER TABLE `asignaciones_recursos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `contrato`
--
ALTER TABLE `contrato`
  MODIFY `id_contrato` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `elementos_guion`
--
ALTER TABLE `elementos_guion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT de la tabla `estado_asignacion`
--
ALTER TABLE `estado_asignacion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `estado_recurso`
--
ALTER TABLE `estado_recurso`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `guiones`
--
ALTER TABLE `guiones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `guion_fechas`
--
ALTER TABLE `guion_fechas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `historial_chat`
--
ALTER TABLE `historial_chat`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `historial_mantenimiento`
--
ALTER TABLE `historial_mantenimiento`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `mantenimientos`
--
ALTER TABLE `mantenimientos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pagos`
--
ALTER TABLE `pagos`
  MODIFY `id_pago` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `patrocinadores`
--
ALTER TABLE `patrocinadores`
  MODIFY `id_patrocinador` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `premios`
--
ALTER TABLE `premios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `recursos`
--
ALTER TABLE `recursos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `reels`
--
ALTER TABLE `reels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `tareas`
--
ALTER TABLE `tareas`
  MODIFY `id_tarea` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `tareas_asignadas`
--
ALTER TABLE `tareas_asignadas`
  MODIFY `id_asignacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `tipo_recurso`
--
ALTER TABLE `tipo_recurso`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `videos`
--
ALTER TABLE `videos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `asignaciones_recursos`
--
ALTER TABLE `asignaciones_recursos`
  ADD CONSTRAINT `fk_asignaciones_estado_asig` FOREIGN KEY (`estado_asignacion_id`) REFERENCES `estado_asignacion` (`id`),
  ADD CONSTRAINT `fk_asignaciones_recurso` FOREIGN KEY (`recurso_id`) REFERENCES `recursos` (`id`);

--
-- Filtros para la tabla `contrato`
--
ALTER TABLE `contrato`
  ADD CONSTRAINT `contrato_ibfk_1` FOREIGN KEY (`id_patrocinador`) REFERENCES `patrocinadores` (`id_patrocinador`);

--
-- Filtros para la tabla `elementos_guion`
--
ALTER TABLE `elementos_guion`
  ADD CONSTRAINT `elementos_guion_ibfk_1` FOREIGN KEY (`guion_id`) REFERENCES `guiones` (`id`),
  ADD CONSTRAINT `elementos_guion_ibfk_2` FOREIGN KEY (`fecha_id`) REFERENCES `guion_fechas` (`id`);

--
-- Filtros para la tabla `guion_fechas`
--
ALTER TABLE `guion_fechas`
  ADD CONSTRAINT `guion_fechas_ibfk_1` FOREIGN KEY (`guion_id`) REFERENCES `guiones` (`id`);

--
-- Filtros para la tabla `historial_mantenimiento`
--
ALTER TABLE `historial_mantenimiento`
  ADD CONSTRAINT `historial_mantenimiento_ibfk_1` FOREIGN KEY (`mantenimiento_id`) REFERENCES `mantenimientos` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`id_contrato`) REFERENCES `contrato` (`id_contrato`);

--
-- Filtros para la tabla `premios`
--
ALTER TABLE `premios`
  ADD CONSTRAINT `premios_ibfk_1` FOREIGN KEY (`id_patrocinador`) REFERENCES `patrocinadores` (`id_patrocinador`);

--
-- Filtros para la tabla `recursos`
--
ALTER TABLE `recursos`
  ADD CONSTRAINT `fk_recursos_estado` FOREIGN KEY (`estado_id`) REFERENCES `estado_recurso` (`id`),
  ADD CONSTRAINT `fk_recursos_tipo` FOREIGN KEY (`tipo_id`) REFERENCES `tipo_recurso` (`id`);

--
-- Filtros para la tabla `reels`
--
ALTER TABLE `reels`
  ADD CONSTRAINT `reels_ibfk_1` FOREIGN KEY (`id_patrocinador`) REFERENCES `patrocinadores` (`id_patrocinador`);

--
-- Filtros para la tabla `tareas_asignadas`
--
ALTER TABLE `tareas_asignadas`
  ADD CONSTRAINT `tareas_asignadas_ibfk_1` FOREIGN KEY (`id_tarea`) REFERENCES `tareas` (`id_tarea`);

--
-- Filtros para la tabla `videos`
--
ALTER TABLE `videos`
  ADD CONSTRAINT `fk_videos_reel` FOREIGN KEY (`reel_id`) REFERENCES `reels` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
