-- Migracion: tabla password_reset_tokens
-- Ejecutar en la base de datos `seguridad`

  CREATE TABLE IF NOT EXISTS `password_reset_tokens` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `usuario_id` int(11) NOT NULL,
    `token` varchar(64) NOT NULL,
    `expires_at` datetime NOT NULL,
    `used` tinyint(1) DEFAULT 0,
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `token` (`token`),
    KEY `prt_fk_usuario` (`usuario_id`),
    CONSTRAINT `prt_fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
