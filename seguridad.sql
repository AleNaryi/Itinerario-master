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
-- Base de datos: `seguridad`
--
CREATE DATABASE IF NOT EXISTS `seguridad` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `seguridad`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `actividad_usuario`
--

CREATE TABLE `actividad_usuario` (
  `id` int(11) NOT NULL,
  `sesion_id` int(11) DEFAULT NULL,
  `usuario_id` int(11) NOT NULL,
  `tipo_accion` varchar(30) NOT NULL,
  `modulo` varchar(50) NOT NULL,
  `accion` text DEFAULT NULL,
  `detalle` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`detalle`)),
  `pagina` varchar(200) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cambios_por_modulo`
--

CREATE TABLE `cambios_por_modulo` (
  `id` int(11) NOT NULL,
  `actividad_id` int(11) NOT NULL,
  `tabla_afectada` varchar(50) NOT NULL,
  `registro_id` int(11) DEFAULT NULL,
  `campo` varchar(100) NOT NULL,
  `valor_anterior` text DEFAULT NULL,
  `valor_nuevo` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dashboard_visibilidad`
--

CREATE TABLE `dashboard_visibilidad` (
  `id` int(11) NOT NULL,
  `rol_id` int(11) NOT NULL,
  `modulo_key` varchar(50) NOT NULL,
  `visible` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Datos para la tabla `dashboard_visibilidad`
--

INSERT INTO `dashboard_visibilidad` (`id`, `rol_id`, `modulo_key`, `visible`) VALUES
(1, 2, 'guion', 1),
(2, 2, 'mantenimiento', 1),
(3, 2, 'premio', 1),
(4, 2, 'contrato', 1),
(5, 2, 'balance', 1),
(6, 2, 'tarea', 1),
(7, 2, 'patrocinador', 1),
(8, 2, 'usuario', 1),
(45, 1, 'guion', 1),
(46, 1, 'mantenimiento', 1),
(47, 1, 'premio', 1),
(48, 1, 'contrato', 1),
(49, 1, 'balance', 1),
(50, 1, 'tarea', 1),
(51, 1, 'patrocinador', 1),
(52, 1, 'usuario', 1),
(53, 1, 'actividad', 1),
(54, 1, 'enlinea', 1),
(65, 3, 'guion', 1),
(66, 3, 'mantenimiento', 0),
(67, 3, 'premio', 0),
(68, 3, 'contrato', 0),
(69, 3, 'balance', 0),
(70, 3, 'tarea', 1),
(71, 3, 'patrocinador', 0),
(72, 3, 'usuario', 0),
(73, 3, 'actividad', 0),
(74, 3, 'enlinea', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `errores_aplicacion`
--

CREATE TABLE `errores_aplicacion` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  `tipo_error` varchar(50) DEFAULT NULL,
  `mensaje` text DEFAULT NULL,
  `traceback` text DEFAULT NULL,
  `pagina` varchar(200) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `permisos`
--

CREATE TABLE `permisos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `codigo` varchar(100) NOT NULL,
  `modulo` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Datos para la tabla `permisos`
--

INSERT INTO `permisos` (`id`, `nombre`, `codigo`, `modulo`, `descripcion`) VALUES
(1, 'Ver panel principal', 'dashboard.view', 'Dashboard', NULL),
(2, 'Ver lista de usuarios', 'usuario.view', 'Usuarios', NULL),
(3, 'Crear usuarios', 'usuario.create', 'Usuarios', NULL),
(4, 'Editar usuarios', 'usuario.edit', 'Usuarios', NULL),
(5, 'Eliminar usuarios', 'usuario.delete', 'Usuarios', NULL),
(6, 'Ver perfil propio', 'usuario.perfil', 'Usuarios', NULL),
(7, 'Ver guiones', 'guion.view', 'Guión', NULL),
(8, 'Crear guiones', 'guion.create', 'Guión', NULL),
(9, 'Editar guiones', 'guion.edit', 'Guión', NULL),
(10, 'Eliminar guiones', 'guion.delete', 'Guión', NULL),
(11, 'Publicar guiones', 'guion.publish', 'Guión', NULL),
(12, 'Previsualizar guiones', 'guion.preview', 'Guión', NULL),
(13, 'Ver pantalla en vivo', 'envivo.view', 'En Vivo', NULL),
(14, 'Controlar elementos en vivo', 'envivo.control', 'En Vivo', NULL),
(15, 'Ver premios', 'premio.view', 'Premios', NULL),
(16, 'Crear premios', 'premio.create', 'Premios', NULL),
(17, 'Editar premios', 'premio.edit', 'Premios', NULL),
(18, 'Eliminar premios', 'premio.delete', 'Premios', NULL),
(19, 'Entregar premios', 'premio.entregar', 'Premios', NULL),
(20, 'Ver mantenimiento', 'mantenimiento.view', 'Mantenimiento', NULL),
(21, 'Crear recursos', 'mantenimiento.create', 'Mantenimiento', NULL),
(22, 'Editar recursos', 'mantenimiento.edit', 'Mantenimiento', NULL),
(23, 'Eliminar recursos', 'mantenimiento.delete', 'Mantenimiento', NULL),
(24, 'Ver roles y permisos', 'rol.view', 'Roles', NULL),
(25, 'Editar permisos de usuarios', 'rol.edit', 'Roles', NULL),
(26, 'Ver tareas', 'gestion_tarea.view', 'Tareas', ''),
(27, 'Crear tareas', 'gestion_tarea.create', 'Tareas', ''),
(28, 'Editar tareas', 'gestion_tarea.edit', 'Tareas', ''),
(29, 'Eliminar tareas', 'gestion_tarea.delete', 'Tareas', ''),
(30, 'Completar tareas propias', 'gestion_tarea.complete', 'Tareas', ''),
(31, 'Ver patrocinadores', 'patrocinador.view', 'Patrocinadores', ''),
(32, 'Crear patrocinadores', 'patrocinador.create', 'Patrocinadores', ''),
(33, 'Editar patrocinadores', 'patrocinador.edit', 'Patrocinadores', ''),
(34, 'Eliminar patrocinadores', 'patrocinador.delete', 'Patrocinadores', ''),
(35, 'Ver contratos', 'contrato.view', 'Contratos', ''),
(36, 'Crear contratos', 'contrato.create', 'Contratos', ''),
(37, 'Editar contratos', 'contrato.edit', 'Contratos', ''),
(38, 'Eliminar contratos', 'contrato.delete', 'Contratos', ''),
(39, 'Ver balance', 'balance.view', 'Balance', ''),
(40, 'Registrar pagos', 'balance.create', 'Balance', ''),
(41, 'Editar pagos', 'balance.edit', 'Balance', ''),
(42, 'Eliminar pagos', 'balance.delete', 'Balance', ''),
(43, 'Ver inventario de recursos', 'inventario.view', 'Inventario', ''),
(44, 'Crear recursos', 'inventario.create', 'Inventario', ''),
(45, 'Editar recursos', 'inventario.edit', 'Inventario', ''),
(46, 'Eliminar recursos', 'inventario.delete', 'Inventario', ''),
(47, 'Asignar y devolver recursos', 'inventario.assign', 'Inventario', ''),
(48, 'Ver reels', 'reels.view', 'Reels', ''),
(49, 'Crear reels', 'reels.create', 'Reels', ''),
(50, 'Editar reels', 'reels.edit', 'Reels', ''),
(51, 'Eliminar reels', 'reels.delete', 'Reels', ''),
(52, 'Supervisar tareas de todos los usuarios', 'gestion_tarea.supervisar', 'Tareas', '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reportes_generados`
--

CREATE TABLE `reportes_generados` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `modulo` varchar(50) NOT NULL,
  `tipo_reporte` varchar(100) NOT NULL,
  `filtros` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`filtros`)),
  `archivo_ruta` varchar(300) NOT NULL,
  `archivo_nombre` varchar(200) NOT NULL,
  `archivo_tamano` int(11) DEFAULT 0,
  `creado_en` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Datos para la tabla `roles`
--

INSERT INTO `roles` (`id`, `nombre`, `descripcion`) VALUES
(1, 'Superadmin', 'Acceso total al sistema'),
(2, 'Administrador', 'Acceso administrativo excepto roles'),
(3, 'Usuario', 'Acceso básico de lectura');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol_permiso`
--

CREATE TABLE `rol_permiso` (
  `id` int(11) NOT NULL,
  `rol_id` int(11) NOT NULL,
  `permiso_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Datos para la tabla `rol_permiso`
--

INSERT INTO `rol_permiso` (`id`, `rol_id`, `permiso_id`) VALUES
(434, 1, 1),
(475, 1, 2),
(472, 1, 3),
(473, 1, 4),
(474, 1, 5),
(476, 1, 6),
(442, 1, 7),
(437, 1, 8),
(438, 1, 9),
(439, 1, 10),
(441, 1, 11),
(440, 1, 12),
(436, 1, 13),
(435, 1, 14),
(460, 1, 15),
(456, 1, 16),
(457, 1, 17),
(458, 1, 18),
(459, 1, 19),
(451, 1, 20),
(448, 1, 21),
(449, 1, 22),
(450, 1, 23),
(466, 1, 24),
(465, 1, 25),
(471, 1, 26),
(468, 1, 27),
(469, 1, 28),
(470, 1, 29),
(467, 1, 30),
(455, 1, 31),
(452, 1, 32),
(453, 1, 33),
(454, 1, 34),
(433, 1, 35),
(430, 1, 36),
(431, 1, 37),
(432, 1, 38),
(429, 1, 39),
(428, 1, 40),
(426, 1, 41),
(427, 1, 42),
(447, 1, 43),
(444, 1, 44),
(445, 1, 45),
(446, 1, 46),
(443, 1, 47),
(464, 1, 48),
(461, 1, 49),
(462, 1, 50),
(463, 1, 51),
(534, 1, 52),
(485, 2, 1),
(525, 2, 2),
(522, 2, 3),
(523, 2, 4),
(524, 2, 5),
(526, 2, 6),
(493, 2, 7),
(488, 2, 8),
(489, 2, 9),
(490, 2, 10),
(492, 2, 11),
(491, 2, 12),
(487, 2, 13),
(486, 2, 14),
(511, 2, 15),
(507, 2, 16),
(508, 2, 17),
(509, 2, 18),
(510, 2, 19),
(502, 2, 20),
(499, 2, 21),
(500, 2, 22),
(501, 2, 23),
(516, 2, 24),
(521, 2, 26),
(518, 2, 27),
(519, 2, 28),
(520, 2, 29),
(517, 2, 30),
(506, 2, 31),
(503, 2, 32),
(504, 2, 33),
(505, 2, 34),
(484, 2, 35),
(481, 2, 36),
(482, 2, 37),
(483, 2, 38),
(480, 2, 39),
(479, 2, 40),
(477, 2, 41),
(478, 2, 42),
(498, 2, 43),
(495, 2, 44),
(496, 2, 45),
(497, 2, 46),
(494, 2, 47),
(515, 2, 48),
(512, 2, 49),
(513, 2, 50),
(514, 2, 51),
(533, 2, 52),
(535, 3, 1),
(541, 3, 6),
(536, 3, 13),
(537, 3, 15),
(540, 3, 26),
(539, 3, 30),
(538, 3, 48);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sesiones_usuario`
--

CREATE TABLE `sesiones_usuario` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `inicio_sesion` datetime DEFAULT NULL,
  `fin_sesion` datetime DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(500) DEFAULT NULL,
  `duracion_segundos` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sincronizaciones`
--

CREATE TABLE `sincronizaciones` (
  `id` int(11) NOT NULL,
  `guion_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `fecha_sincronizacion` date NOT NULL,
  `hora_sincronizacion` time NOT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `cedula` varchar(20) NOT NULL,
  `rol` varchar(20) DEFAULT 'Usuario',
  `departamento` varchar(50) DEFAULT 'Medios',
  `telefono` varchar(20) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `fecha_registro` datetime DEFAULT NULL,
  `ultimo_acceso` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `email`, `password_hash`, `cedula`, `rol`, `departamento`, `telefono`, `activo`, `fecha_registro`, `ultimo_acceso`) VALUES
(3, 'Admin', 'admin@admin.com', 'scrypt:32768:8:1$VImiJ1cWMig3OJN6$66e6543200f85e636bf90eb21b174b6d22ceea892b52ecb277a9d878b41447879ad382b1e29418e473d6df392a991d827e214a96d411f0b3ae71f3ec7642dc11', '12345678', 'Superadmin', 'Palco de Operaciones', '0422345981', 1, '2026-05-05 21:34:59', '2026-07-07 21:25:15'),
(4, 'keiver', 'keiberzamudia14@gmail.com', 'scrypt:32768:8:1$Ja5EZ2d8z6RDtluV$21bbb2479653cb8914c283ba440713c18a32ad731791dd2a2187af34dac22370e55e2f85e8b92688f1587b59b009e003ee65ee62d42928dca52b0da2a2771ef0', '25469224', 'Superadmin', 'Medios', '0412344590', 1, '2026-05-05 23:44:26', '2026-07-09 16:05:12'),
(5, 'Genesis', 'gene@admin.com', 'scrypt:32768:8:1$coTXZEDqTjuXvG0Q$4b3453edd3c49f45f11e728ffa2565b9b34d8b52d7ab2b25fb2a8c8a626c3b7a8210c3b85da9362f95f5a0ccd86338bb6920bf1b7351cea6c4dd39184019ce22', '26357326', 'Administrador', 'Palco de Operaciones', '04243455566', 1, '2026-05-05 23:49:50', '2026-07-09 17:18:29'),
(6, 'naryi', 'naryi@admin.com', 'scrypt:32768:8:1$msjmk9hpl7gJNoQR$548780bb655c20abc0f30e5957b3168cb67fdd9c34c8d7999c1c9b07e0ea5de9e559caf6b101b35d8308e04dcec589bfc0b8112f047ca66b96f9e7c6f9b193b2', '14598999', 'Administrador', 'Medios', '04123455564', 1, '2026-05-06 19:58:32', '2026-06-27 16:24:17'),
(18, 'Yolianna', 'yolianna14@gmail.com', 'scrypt:32768:8:1$sLUimNcvv03AGwJE$739949399a6360649d2e7916a6aff4416b1757db6c36dc78eb5b6c77e86ccf615a177d850b8ffbd776d4aac2fa1129ca5906a584b219de7b2ee7b661b95997b1', '25894881', 'Usuario', 'Medios', '02512661166', 1, '2026-05-31 18:02:46', '2026-06-22 00:49:48'),
(24, 'Maria Alvarez', 'maria@admin.com', 'scrypt:32768:8:1$JwKu9i5KXzJhB0YR$36d209fbd8c9d500e4536163f86ccc815d637dff1bd28802ee0ed9778ecefbaa851fdf2856a7f02d460833ba6d36de616746f951ab6fed559475ca285a244733', '26480334', 'Usuario', 'Medios', '6776367376', 1, '2026-06-27 10:13:29', '2026-06-27 16:24:33');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_dashboard_vis`
--

CREATE TABLE `usuario_dashboard_vis` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `modulo_key` varchar(50) NOT NULL,
  `visible` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Datos para la tabla `usuario_dashboard_vis`
--

INSERT INTO `usuario_dashboard_vis` (`id`, `usuario_id`, `modulo_key`, `visible`) VALUES
(1, 4, 'guion', 0),
(2, 4, 'mantenimiento', 0),
(3, 4, 'premio', 0),
(4, 4, 'contrato', 0),
(5, 4, 'balance', 0),
(6, 4, 'tarea', 0),
(7, 4, 'patrocinador', 0),
(8, 4, 'usuario', 0),
(9, 4, 'actividad', 1),
(10, 4, 'enlinea', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_permiso`
--

CREATE TABLE `usuario_permiso` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `permiso_id` int(11) NOT NULL,
  `fecha_asignacion` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Datos para la tabla `usuario_permiso`
--

INSERT INTO `usuario_permiso` (`id`, `usuario_id`, `permiso_id`, `fecha_asignacion`) VALUES
(1, 4, 25, '2026-06-03 12:31:56'),
(2, 4, 26, '2026-06-03 12:31:56'),
(3, 4, 27, '2026-06-03 12:31:56'),
(4, 4, 28, '2026-06-03 12:31:56'),
(5, 4, 29, '2026-06-03 12:31:56'),
(6, 4, 30, '2026-06-03 12:31:56'),
(7, 4, 31, '2026-06-03 12:31:56'),
(8, 4, 32, '2026-06-03 12:31:56'),
(9, 4, 33, '2026-06-03 12:31:56'),
(10, 4, 34, '2026-06-03 12:31:56'),
(11, 4, 35, '2026-06-03 12:31:56'),
(12, 4, 36, '2026-06-03 12:31:56'),
(13, 4, 37, '2026-06-03 12:31:56'),
(14, 4, 38, '2026-06-03 12:31:56'),
(15, 4, 39, '2026-06-03 12:31:56'),
(16, 4, 40, '2026-06-03 12:31:56'),
(17, 4, 41, '2026-06-03 12:31:56'),
(18, 4, 42, '2026-06-03 12:31:56'),
(19, 4, 43, '2026-06-03 12:31:56'),
(20, 4, 44, '2026-06-03 12:31:56'),
(21, 4, 45, '2026-06-03 12:31:56'),
(22, 4, 46, '2026-06-03 12:31:56'),
(23, 4, 47, '2026-06-03 12:31:56'),
(24, 4, 48, '2026-06-03 12:31:56'),
(25, 4, 49, '2026-06-03 12:31:56'),
(26, 4, 50, '2026-06-03 12:31:57'),
(27, 4, 51, '2026-06-03 12:31:57');

-- --------------------------------------------------------

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `actividad_usuario`
--
ALTER TABLE `actividad_usuario`
  ADD PRIMARY KEY (`id`),
  ADD KEY `au_fk_sesion` (`sesion_id`),
  ADD KEY `au_fk_usuario` (`usuario_id`);

--
-- Indices de la tabla `cambios_por_modulo`
--
ALTER TABLE `cambios_por_modulo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cm_fk_actividad` (`actividad_id`);

--
-- Indices de la tabla `dashboard_visibilidad`
--
ALTER TABLE `dashboard_visibilidad`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_rol_modulo` (`rol_id`,`modulo_key`);

--
-- Indices de la tabla `errores_aplicacion`
--
ALTER TABLE `errores_aplicacion`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ea_fk_usuario` (`usuario_id`);

--
-- Indices de la tabla `permisos`
--
ALTER TABLE `permisos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `reportes_generados`
--
ALTER TABLE `reportes_generados`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_usuario` (`usuario_id`),
  ADD KEY `idx_modulo` (`modulo`),
  ADD KEY `idx_creado` (`creado_en`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `rol_permiso`
--
ALTER TABLE `rol_permiso`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `rol_permiso_unique` (`rol_id`,`permiso_id`),
  ADD KEY `rp_fk_permiso` (`permiso_id`);

--
-- Indices de la tabla `sesiones_usuario`
--
ALTER TABLE `sesiones_usuario`
  ADD PRIMARY KEY (`id`),
  ADD KEY `su_fk_usuario` (`usuario_id`);

--
-- Indices de la tabla `sincronizaciones`
--
ALTER TABLE `sincronizaciones`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `cedula` (`cedula`);

--
-- Indices de la tabla `usuario_dashboard_vis`
--
ALTER TABLE `usuario_dashboard_vis`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_user_modulo` (`usuario_id`,`modulo_key`);

--
-- Indices de la tabla `usuario_permiso`
--
ALTER TABLE `usuario_permiso`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario_permiso_unique` (`usuario_id`,`permiso_id`),
  ADD KEY `up_fk_permiso` (`permiso_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `actividad_usuario`
--
ALTER TABLE `actividad_usuario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cambios_por_modulo`
--
ALTER TABLE `cambios_por_modulo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `dashboard_visibilidad`
--
ALTER TABLE `dashboard_visibilidad`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=75;

--
-- AUTO_INCREMENT de la tabla `errores_aplicacion`
--
ALTER TABLE `errores_aplicacion`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `permisos`
--
ALTER TABLE `permisos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `reportes_generados`
--
ALTER TABLE `reportes_generados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `rol_permiso`
--
ALTER TABLE `rol_permiso`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=542;

--
-- AUTO_INCREMENT de la tabla `sesiones_usuario`
--
ALTER TABLE `sesiones_usuario`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sincronizaciones`
--
ALTER TABLE `sincronizaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de la tabla `usuario_dashboard_vis`
--
ALTER TABLE `usuario_dashboard_vis`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `usuario_permiso`
--
ALTER TABLE `usuario_permiso`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `actividad_usuario`
--
ALTER TABLE `actividad_usuario`
  ADD CONSTRAINT `au_fk_sesion` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_usuario` (`id`),
  ADD CONSTRAINT `au_fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Estructura de tabla para la tabla `password_reset_tokens`
--

CREATE TABLE `password_reset_tokens` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `token` varchar(64) NOT NULL,
  `expires_at` datetime NOT NULL,
  `used` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `password_reset_tokens`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `prt_fk_usuario` (`usuario_id`);

ALTER TABLE `password_reset_tokens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Filtros para la tabla `cambios_por_modulo`
--
ALTER TABLE `cambios_por_modulo`
  ADD CONSTRAINT `cm_fk_actividad` FOREIGN KEY (`actividad_id`) REFERENCES `actividad_usuario` (`id`);

--
-- Filtros para la tabla `errores_aplicacion`
--
ALTER TABLE `errores_aplicacion`
  ADD CONSTRAINT `ea_fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `rol_permiso`
--
ALTER TABLE `rol_permiso`
  ADD CONSTRAINT `rp_fk_permiso` FOREIGN KEY (`permiso_id`) REFERENCES `permisos` (`id`),
  ADD CONSTRAINT `rp_fk_rol` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`);

--
-- Filtros para la tabla `sesiones_usuario`
--
ALTER TABLE `sesiones_usuario`
  ADD CONSTRAINT `su_fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `usuario_permiso`
--
ALTER TABLE `usuario_permiso`
  ADD CONSTRAINT `up_fk_permiso` FOREIGN KEY (`permiso_id`) REFERENCES `permisos` (`id`),
  ADD CONSTRAINT `up_fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Estructura de tabla para la tabla `notificaciones`
--
CREATE TABLE `notificaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `tipo` varchar(40) NOT NULL DEFAULT 'tarea_asignada',
  `titulo` varchar(120) NOT NULL,
  `mensaje` varchar(255) NOT NULL,
  `url` varchar(200) DEFAULT NULL,
  `leida` tinyint(1) DEFAULT 0,
  `fecha_creacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_usuario_leida` (`usuario_id`, `leida`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Filtros para la tabla `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD CONSTRAINT `prt_fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
