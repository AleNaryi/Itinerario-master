-- Migracion: relojes de verdad del modulo EN VIVO
-- Autorizada por el usuario (feature operativa; excepcion puntual a la regla NO-backend)
-- 1) guiones.inicio_show        -> cuándo se dio Iniciar al guion (NULL tras Finalizar)
-- 2) elementos_guion.inicio_curso -> cuándo ese elemento entró a en_curso (NULL fuera de en_curso;
--                                    se renueva en cada reingreso, p.ej. al reiniciar un evento)

ALTER TABLE `guiones` ADD COLUMN `inicio_show` DATETIME NULL DEFAULT NULL COMMENT 'Momento de Iniciar del show en vivo' AFTER `estado`;
ALTER TABLE `elementos_guion` ADD COLUMN `inicio_curso` DATETIME NULL DEFAULT NULL COMMENT 'Momento de entrada a en_curso' AFTER `estado`;
