-- Migración: notificaciones in-app (campana estilo red social)
-- Ejecutada en producción el 2026-08-23 (por el usuario).
CREATE TABLE IF NOT EXISTS `notificaciones` (
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
