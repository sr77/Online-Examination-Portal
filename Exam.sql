CREATE TABLE IF NOT EXISTS `Exam`.`Stud` (
  `fname` VARCHAR(20) NOT NULL,
  `lname` VARCHAR(20) NULL,
  `username` VARCHAR(10) NOT NULL,
  `passwd` VARCHAR(5000) NOT NULL,
  `email` VARCHAR(50) NULL,
  `sem` INT NOT NULL,
  `department` VARCHAR(45) NOT NULL,
  `mob_no` VARCHAR(15) NULL,
  `dob` DATE NULL,
  `guardian` VARCHAR(45) NULL,
  `img` BLOB NULL,
  `about` VARCHAR(45) NULL,
  PRIMARY KEY (`username`))
ENGINE=MyISAM;



CREATE TABLE IF NOT EXISTS `Exam`.`faculti` (
  `username` VARCHAR(20) NOT NULL,
  `passwd` VARCHAR(5000) NOT NULL,
  `fname` VARCHAR(20) NOT NULL,
  `lname` VARCHAR(20) NULL,
  `email` VARCHAR(45) NULL,
  `mob_no` VARCHAR(15) NULL,
  `department` VARCHAR(45) NULL,
  `subj_taught` VARCHAR(500) NULL,
  `img` BLOB NULL,
  `about` VARCHAR(45) NULL,
  PRIMARY KEY (`username`))
ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `Exam`.`QBank` (
  `ques_id` VARCHAR(50) NOT NULL,
  `username` VARCHAR(20) NULL,
  `question` LONGTEXT NOT NULL,
  `q_img` BLOB NULL,
  `opt_A` MEDIUMTEXT NOT NULL,
  `opt_A_img` BLOB NULL,
  `opt_B` MEDIUMTEXT NOT NULL,
  `opt_B_img` BLOB NULL,
  `opt_C` MEDIUMTEXT NOT NULL,
  `opt_C_img` BLOB NULL,
  `opt_D` MEDIUMTEXT NOT NULL,
  `opt_D_img` BLOB NULL,
  `sol_id` INT(11) NOT NULL,
  `q_tags` VARCHAR(45) NULL,
  `q_marks` INT(11) NULL,
  PRIMARY KEY (`ques_id`),
  INDEX `username_idx` (`username` ASC),
  CONSTRAINT `username`
    FOREIGN KEY (`username`)
    REFERENCES `mydb`.`faculti` (`username`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE=MyISAM;



CREATE TABLE IF NOT EXISTS `Exam`.`soltest` (
  `test_id` VARCHAR(50) NOT NULL,
  `sol_id` INT(11) NOT NULL,
  `explanation` VARCHAR(500) NOT NULL,
  PRIMARY KEY (`test_id`, `explanation`),
  INDEX `sol_id_idx` (`sol_id` ASC),
  CONSTRAINT `sol_id`
    FOREIGN KEY (`sol_id`)
    REFERENCES `mydb`.`QBank` (`sol_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE=MyISAM;



CREATE TABLE IF NOT EXISTS `Exam`.`Response` (
  `username` VARCHAR(10) NOT NULL,
  `test_id` VARCHAR(50) NULL,
  `ques_id` VARCHAR(50) NULL,
  `sol_id` INT(11) NULL,
  PRIMARY KEY (`username`),
  INDEX `test_id_idx` (`test_id` ASC),
  INDEX `sol_id_idx` (`sol_id` ASC),
  INDEX `ques_id_idx` (`ques_id` ASC),
  CONSTRAINT `username`
    FOREIGN KEY (`username`)
    REFERENCES `mydb`.`Stud` (`username`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `test_id`
    FOREIGN KEY (`test_id`)
    REFERENCES `mydb`.`Test` (`test_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `sol_id`
    FOREIGN KEY (`sol_id`)
    REFERENCES `mydb`.`QBank` (`sol_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ques_id`
    FOREIGN KEY (`ques_id`)
    REFERENCES `mydb`.`QBank` (`ques_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `Exam`.`Results` (
  `username` VARCHAR(10) NOT NULL,
  `test_id` VARCHAR(50) NULL,
  `marks_obtained` INT(11) NULL,
  PRIMARY KEY (`username`),
  INDEX `test_id_idx` (`test_id` ASC),
  CONSTRAINT `username`
    FOREIGN KEY (`username`)
    REFERENCES `mydb`.`Stud` (`username`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `test_id`
    FOREIGN KEY (`test_id`)
    REFERENCES `mydb`.`Test` (`test_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE=MyISAM;



