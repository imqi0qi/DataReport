CREATE TABLE `graphs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `graph_id` varchar(64) DEFAULT NULL,
  `rep_id` varchar(64) DEFAULT NULL,
  `title` varchar(256) DEFAULT NULL,
  `sub_title` varchar(256) DEFAULT NULL,
  `graph_type` varchar(32) DEFAULT NULL,
  `sql_query` mediumtext,
  `sql_host` varchar(16) DEFAULT NULL,
  `sql_user` varchar(64) DEFAULT NULL,
  `sql_passwd` varchar(64) DEFAULT NULL,
  `url_img` varchar(64) DEFAULT NULL,
  `cre_time` datetime DEFAULT NULL,
  `mod_time` datetime DEFAULT NULL,
  `ins_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

CREATE TABLE `reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rep_id` varchar(64) DEFAULT NULL,
  `rep_name` varchar(64) DEFAULT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `header` varchar(256) DEFAULT NULL,
  `sub_header` varchar(256) DEFAULT NULL,
  `is_up` int(11) DEFAULT NULL,
  `send_mail` varchar(256) DEFAULT NULL,
  `rec_mail` varchar(256) DEFAULT NULL,
  `cc_mail` varchar(256) DEFAULT NULL,
  `mod_time` datetime DEFAULT NULL,
  `cre_time` datetime DEFAULT NULL,
  `run_time` varchar(32) DEFAULT NULL,
  `ins_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rep_id` (`rep_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

CREATE TABLE `runreports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `log_id` varchar(64) DEFAULT NULL,
  `rep_id` varchar(64) DEFAULT NULL,
  `status` varchar(32) DEFAULT NULL,
  `beg_run_time` datetime DEFAULT NULL,
  `end_run_time` datetime DEFAULT NULL,
  `diff_run_time` varchar(32) DEFAULT NULL,
  `ins_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(64) DEFAULT NULL,
  `user_nick` varchar(64) DEFAULT NULL,
  `user_name` varchar(64) DEFAULT NULL,
  `user_passwd` varchar(64) DEFAULT NULL,
  `is_admin` int(11) DEFAULT '0',
  `ins_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;