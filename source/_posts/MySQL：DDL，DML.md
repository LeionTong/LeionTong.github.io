---
title: MySQL
date: 2017-04-16T09:00:00.000Z
tags: null
---

# SQL：DDL，DML

## DDL：Data Defination Language `mysql> HELP Data Definition`

```
CREATE, ALTER, DROP
    DATABASE, TABLE
    INDEX, VIEW, USER
    FUNCTION, FUNCTION UDF, PROCEDURE, TABLESPACE, TRIGGER, SERVER
```

## DML: Data Manipulation Language `mysql> HELP Data Manipulation`

<!-- more -->
```
INSERT/REPLACE, DELETE, SELECT, UPDATE
```

## 数据库：

> 对于MySQL而言，每个数据库（DATABASE）其实就是对应数据目录（datadir）下的一个目录（db_name），用于规定一个项目或者方案的集合，因此DATABASE也被称为SCHEMA；

```
CREATE {DATABASE | SCHEMA} [IF NOT EXISTS] db_name CHARACTER SET [=] charset_name  COLLATE [=] collation_name
ALTER {DATABASE | SCHEMA} [db_name] CHARACTER SET [=] charset_name  COLLATE [=] collation_name
DROP {DATABASE | SCHEMA} [IF EXISTS] db_name
```


### #

**示例：** 显示当前已存在的所有数据库;

```
MariaDB [(none)]> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| test               |
+--------------------+
4 rows in set (0.00 sec)
```

**创建一个数据库 CREATE DATABASE;**

```
MariaDB [(none)]> CREATE DATABASE mydb;
Query OK, 1 row affected (0.00 sec)
```

如果要创建的数据库已存在，就会报错；如果此时是一个sql脚本的话执行到这里就中断了；

```
MariaDB [(none)]> CREATE DATABASE mydb;
ERROR 1007 (HY000): Can't create database 'mydb'; database exists
```

创建数据库时可以加上条件判断 IF NOT EXISTS ；这样只会出现警告，而不会报错中断操作；可以使用命令 SHOW WARNINGS 查看；

```
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS mydb;
Query OK, 1 row affected, 1 warning (0.00 sec)

MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS mydb;
Query OK, 1 row affected, 1 warning (0.00 sec)

MariaDB [(none)]> SHOW WARNINGS;
+-------+------+-----------------------------------------------+
| Level | Code | Message                                       |
+-------+------+-----------------------------------------------+
| Note  | 1007 | Can't create database 'mydb'; database exists |
+-------+------+-----------------------------------------------+
1 row in set (0.00 sec)
```

创建数据库时可以指定默认字符集 CHARATER SET；

```
MariaDB [(none)]> CREATE DATABASE IF NOT EXISTS testdb CHARACTER SET utf8;
Query OK, 1 row affected (0.00 sec)
```

**如果要创建数据库时忘记指定字符集，可以使用ALTER DATABASE 修改；**

```
MariaDB [(none)]> ALTER DATABASE mydb CHARATER SET utf8;
Query OK, 1 row affected (0.00 sec)
```

**删除一个数据库 DROP DATABASE;**

```
MariaDB [(none)]> DROP DATABASE testdb;
Query OK, 0 rows affected (0.00 sec)
```

同样，如果要删除的数据库不存在，就会报错；可以加上条件判断IF EXISTS 以避免报错；

```
MariaDB [(none)]> DROP DATABASE testdb;
ERROR 1008 (HY000): Can't drop database 'testdb'; database doesn't exist

MariaDB [(none)]> DROP DATABASE IF EXISTS testdb;
Query OK, 0 rows affected, 1 warning (0.00 sec)
```

### #

## 表：

> 表名是否区分大小写取决于文件系统，强烈建议不要使用仅仅大小写不同的表名；

### CREATE：

#### 语法1

```
CREATE [TEMPORARY] TABLE [IF NOT EXISTS] tbl_name
    (create_definition,...)
    [table_options]
    [partition_options]
```

#### 语法2

```
CREATE [TEMPORARY] TABLE [IF NOT EXISTS] tbl_name
    [(create_definition,...)]
    [table_options]
    [partition_options]
    select_statement
```

> 通过查询语句来创建表，直接将查询语句的结果插入到新创建的表中；只能复制字段名和类型，不能复制字段定义；

#### 语法3

```
CREATE [TEMPORARY] TABLE [IF NOT EXISTS] tbl_name
    { LIKE old_tbl_name | (LIKE old_tbl_name) }
```

> 复制某存在的表的结构来创建新的空表；

#### 选项

```
create_definition:
    col_name column_definition
```

```
column_definition:
    data_type [NOT NULL | NULL] [DEFAULT default_value]
      [AUTO_INCREMENT] [UNIQUE [KEY] | [PRIMARY] KEY]
      [COMMENT 'string']
      [COLUMN_FORMAT {FIXED|DYNAMIC|DEFAULT}]
```

```
table_options：
    ENGINE [=] engine_name
```

查看支持的所有存储引擎： `mysql> SHOW ENGINES;` 查看指定表的存储引擎： `mysql> SHOW TABLE STATUS LIKE clause;` 查看使用指定存储引擎的表： `mysql> SHOW TABLE STATUS WHERE Engine='InnoDB'\G`

### DROP:

```
DROP [TEMPORARY] TABLE [IF EXISTS] tbl_name [, tbl_name];
```

### ALTER：

```
ALTER  TABLE tbl_name
    [alter_specification [, alter_specification] ...]
```

可修改内容：

```
* table_options
* 添加定义：ADD
    - 字段、字段集合、索引、约束
* 修改字段：
    - CHANGE [COLUMN] old_col_name new_col_name column_definition [FIRST|AFTER col_name]
    - MODIFY [COLUMN] col_name column_definition [FIRST | AFTER col_name]
* 删除操作：DROP
    - 字段、索引、约束
```

表重命名： `RENAME [TO|AS] new_tbl_name`

### 查看表结构定义：

```
DESC tbl_name；
```

### 查看表定义：

```
SHOW CREATE TABLE tbl_name
```

### 查看表属性信息：

```
    SHOW TABLE STATUS [{FROM | IN} db_name] [LIKE 'pattern' | WHERE expr]
```

#### #

**示例：** **创建一张表**

```
CREATE TABLE tbl1;`
```

创建表tbl2，指定字段列数据类型、主键等信息；

```
MariaDB [(none)]> USE mydb;
Database changed
MariaDB [mydb]> CREATE TABLE tbl2(id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, name CHAR(20));
Query OK, 0 rows affected (0.00 sec)

MariaDB [mydb]> DESC tbl2;
+-------+---------------------+------+-----+---------+----------------+
| Field | Type                | Null | Key | Default | Extra          |
+-------+---------------------+------+-----+---------+----------------+
| id    | tinyint(3) unsigned | NO   | PRI | NULL    | auto_increment |
| name  | char(20)            | YES  |     | NULL    |                |
+-------+---------------------+------+-----+---------+----------------+
2 rows in set (0.00 sec)
```

创建表tbl3，单独指定主键

```
MariaDB [mydb]> CREATE TABLE tbl3(id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT, name CHAR(20), PRIMARY KEY(id));
Query OK, 0 rows affected (0.01 sec)

MariaDB [mydb]> DESC tbl3;
+-------+---------------------+------+-----+---------+----------------+
| Field | Type                | Null | Key | Default | Extra          |
+-------+---------------------+------+-----+---------+----------------+
| id    | tinyint(3) unsigned | NO   | PRI | NULL    | auto_increment |
| name  | char(20)            | YES  |     | NULL    |                |
+-------+---------------------+------+-----+---------+----------------+
2 rows in set (0.00 sec)
```

创建表tbl4，同时给指定字段创建索引；

```
MariaDB [mydb]> CREATE TABLE tbl4(id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT, name CHAR(20), age TINYINT UNSIGNED, PRIMARY KEY(id), index(name));
MariaDB [mydb]> DESC tbl4;
+-------+---------------------+------+-----+---------+----------------+
| Field | Type                | Null | Key | Default | Extra          |
+-------+---------------------+------+-----+---------+----------------+
| id    | tinyint(3) unsigned | NO   | PRI | NULL    | auto_increment |
| name  | char(20)            | YES  | MUL | NULL    |                |
| age   | tinyint(3) unsigned | YES  |     | NULL    |                |
+-------+---------------------+------+-----+---------+----------------+
3 rows in set (0.00 sec)
```

查看表tbl4的索引信息;注意到，这里有两行，第一行是主键索引 PRIMARY 针对 id 字段，第二行是自定义索引 name 针对 name 字段；由于自定义的索引未指定索引名，因此默认索引名与字段名一样；

```
MariaDB [mydb]> SHOW INDEXES FROM tbl4;
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| tbl4  |          0 | PRIMARY  |            1 | id          | A         |           0 |     NULL | NULL   |      | BTREE      |         |               |
| tbl4  |          1 | name     |            1 | name        | A         |           0 |     NULL | NULL   | YES  | BTREE      |         |               |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
2 rows in set (0.00 sec)

MariaDB [mydb]> SHOW INDEXES FROM tbl4\G
*************************** 1\. row ***************************
        Table: tbl4
   Non_unique: 0
     Key_name: PRIMARY
 Seq_in_index: 1
  Column_name: id
    Collation: A
  Cardinality: 0
     Sub_part: NULL
       Packed: NULL
         Null:
   Index_type: BTREE
      Comment:
Index_comment:
*************************** 2\. row ***************************
        Table: tbl4
   Non_unique: 1
     Key_name: name
 Seq_in_index: 1
  Column_name: name
    Collation: A
  Cardinality: 0
     Sub_part: NULL
       Packed: NULL
         Null: YES
   Index_type: BTREE
      Comment:
Index_comment:
2 rows in set (0.00 sec)
```

查看表的索引信息；

```
MariaDB [mydb]> show table status;
+------+--------+---------+------------+------+----------------+-------------+-----------------+--------------+-----------+----------------+---------------------+-------------+------------+-----------------+----------+----------------+---------+
| Name | Engine | Version | Row_format | Rows | Avg_row_length | Data_length | Max_data_length | Index_length | Data_free | Auto_increment | Create_time         | Update_time | Check_time | Collation       | Checksum | Create_options | Comment |
+------+--------+---------+------------+------+----------------+-------------+-----------------+--------------+-----------+----------------+---------------------+-------------+------------+-----------------+----------+----------------+---------+
| tbl2 | InnoDB |      10 | Compact    |    0 |              0 |       16384 |               0 |            0 |   9437184 |              1 | 2017-06-03 22:24:47 | NULL        | NULL       | utf8_general_ci |     NULL |                |         |
| tbl3 | InnoDB |      10 | Compact    |    0 |              0 |       16384 |               0 |            0 |   9437184 |              1 | 2017-06-03 22:29:15 | NULL        | NULL       | utf8_general_ci |     NULL |                |         |
| tbl4 | InnoDB |      10 | Compact    |    0 |              0 |       16384 |               0 |        16384 |   9437184 |              1 | 2017-06-03 22:51:45 | NULL        | NULL       | utf8_general_ci |     NULL |                |         |
+------+--------+---------+------------+------+----------------+-------------+-----------------+--------------+-----------+----------------+---------------------+-------------+------------+-----------------+----------+----------------+---------+
3 rows in set (0.00 sec)

MariaDB [mydb]> SHOW TABLE STATUS\G
*************************** 1\. row ***************************
           Name: tbl2
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 0
 Avg_row_length: 0
    Data_length: 16384
Max_data_length: 0
   Index_length: 0
      Data_free: 9437184
 Auto_increment: 1
    Create_time: 2017-06-03 22:24:47
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
*************************** 2\. row ***************************
           Name: tbl3
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 0
 Avg_row_length: 0
    Data_length: 16384
Max_data_length: 0
   Index_length: 0
      Data_free: 9437184
 Auto_increment: 1
    Create_time: 2017-06-03 22:29:15
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
*************************** 3\. row ***************************
           Name: tbl4
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 0
 Avg_row_length: 0
    Data_length: 16384
Max_data_length: 0
   Index_length: 16384
      Data_free: 9437184
 Auto_increment: 1
    Create_time: 2017-06-03 22:51:45
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
3 rows in set (0.01 sec)

MariaDB [mydb]> SHOW TABLE STATUS LIKE 'tbl4'\G
*************************** 1\. row ***************************
           Name: tbl4
         Engine: InnoDB
        Version: 10
     Row_format: Compact
           Rows: 0
 Avg_row_length: 0
    Data_length: 16384
Max_data_length: 0
   Index_length: 16384
      Data_free: 9437184
 Auto_increment: 1
    Create_time: 2017-06-03 22:51:45
    Update_time: NULL
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
1 row in set (0.00 sec)
```

创建表tbl5，表选项 table_options 指定存储引擎 ENGINE ；

```
MariaDB [mydb]>  CREATE TABLE tbl5(id INT) ENGINE MyISAM;
Query OK, 0 rows affected (0.00 sec)

MariaDB [mydb]> DESC tbl5;
+-------+---------+------+-----+---------+-------+
| Field | Type    | Null | Key | Default | Extra |
+-------+---------+------+-----+---------+-------+
| id    | int(11) | YES  |     | NULL    |       |
+-------+---------+------+-----+---------+-------+
1 row in set (0.01 sec)

MariaDB [mydb]> SHOW TABLE STATUS WHERE ENGINE='MyISAM'\G
*************************** 1\. row ***************************
           Name: tbl5
         Engine: MyISAM
        Version: 10
     Row_format: Fixed
           Rows: 0
 Avg_row_length: 0
    Data_length: 0
Max_data_length: 1970324836974591
   Index_length: 1024
      Data_free: 0
 Auto_increment: NULL
    Create_time: 2017-06-03 23:26:08
    Update_time: 2017-06-03 23:26:08
     Check_time: NULL
      Collation: utf8_general_ci
       Checksum: NULL
 Create_options:
        Comment:
1 row in set (0.00 sec)
```

使用SELECT语句查询获取的数据创建表tbl6；

```
MariaDB [mydb]> CREATE TABLE tbl6 SELECT Host,User,Password From mysql.user;
Query OK, 8 rows affected (0.02 sec)
Records: 8  Duplicates: 0  Warnings: 0

MariaDB [mydb]> DESC tbl6;
+----------+----------+------+-----+---------+-------+
| Field    | Type     | Null | Key | Default | Extra |
+----------+----------+------+-----+---------+-------+
| Host     | char(60) | NO   |     |         |       |
| User     | char(16) | NO   |     |         |       |
| Password | char(41) | NO   |     |         |       |
+----------+----------+------+-----+---------+-------+
3 rows in set (0.00 sec)

MariaDB [mydb]> SELECT * FROM tbl6;
+-----------+------+-------------------------------------------+
| Host      | User | Password                                  |
+-----------+------+-------------------------------------------+
| localhost | root |                                           |
| centos7   | root |                                           |
| 127.0.0.1 | root |                                           |
| ::1       | root |                                           |
| localhost |      |                                           |
| centos7   |      |                                           |
| %         | test | *00E247AC5F9AF26AE0194B41E1E769DEE1429A29 |
| localhost | test | *00E247AC5F9AF26AE0194B41E1E769DEE1429A29 |
+-----------+------+-------------------------------------------+
8 rows in set (0.00 sec)
```

复制表结构；

```
MariaDB [mydb]> CREATE TABLE tbl7 like mysql.user;
Query OK, 0 rows affected (0.02 sec)

MariaDB [mydb]> DESC tbl7;
+------------------------+-----------------------------------+------+-----+----------+-------+
| Field                  | Type                              | Null | Key | Default  | Extra |
+------------------------+-----------------------------------+------+-----+----------+-------+
| Host                   | char(60)                          | NO   | PRI |          |       |
| User                   | char(80)                          | NO   | PRI |          |       |
| Password               | char(41)                          | NO   |     |          |       |
| Select_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Insert_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Update_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Delete_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Create_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Drop_priv              | enum('N','Y')                     | NO   |     | N        |       |
| Reload_priv            | enum('N','Y')                     | NO   |     | N        |       |
| Shutdown_priv          | enum('N','Y')                     | NO   |     | N        |       |
| Process_priv           | enum('N','Y')                     | NO   |     | N        |       |
| File_priv              | enum('N','Y')                     | NO   |     | N        |       |
| Grant_priv             | enum('N','Y')                     | NO   |     | N        |       |
| References_priv        | enum('N','Y')                     | NO   |     | N        |       |
| Index_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Alter_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Show_db_priv           | enum('N','Y')                     | NO   |     | N        |       |
| Super_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Create_tmp_table_priv  | enum('N','Y')                     | NO   |     | N        |       |
| Lock_tables_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Execute_priv           | enum('N','Y')                     | NO   |     | N        |       |
| Repl_slave_priv        | enum('N','Y')                     | NO   |     | N        |       |
| Repl_client_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Create_view_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Show_view_priv         | enum('N','Y')                     | NO   |     | N        |       |
| Create_routine_priv    | enum('N','Y')                     | NO   |     | N        |       |
| Alter_routine_priv     | enum('N','Y')                     | NO   |     | N        |       |
| Create_user_priv       | enum('N','Y')                     | NO   |     | N        |       |
| Event_priv             | enum('N','Y')                     | NO   |     | N        |       |
| Trigger_priv           | enum('N','Y')                     | NO   |     | N        |       |
| Create_tablespace_priv | enum('N','Y')                     | NO   |     | N        |       |
| ssl_type               | enum('','ANY','X509','SPECIFIED') | NO   |     |          |       |
| ssl_cipher             | blob                              | NO   |     | NULL     |       |
| x509_issuer            | blob                              | NO   |     | NULL     |       |
| x509_subject           | blob                              | NO   |     | NULL     |       |
| max_questions          | int(11) unsigned                  | NO   |     | 0        |       |
| max_updates            | int(11) unsigned                  | NO   |     | 0        |       |
| max_connections        | int(11) unsigned                  | NO   |     | 0        |       |
| max_user_connections   | int(11)                           | NO   |     | 0        |       |
| plugin                 | char(64)                          | NO   |     |          |       |
| authentication_string  | text                              | NO   |     | NULL     |       |
| password_expired       | enum('N','Y')                     | NO   |     | N        |       |
| is_role                | enum('N','Y')                     | NO   |     | N        |       |
| default_role           | char(80)                          | NO   |     |          |       |
| max_statement_time     | decimal(12,6)                     | NO   |     | 0.000000 |       |
+------------------------+-----------------------------------+------+-----+----------+-------+
46 rows in set (0.02 sec)
```

#### #
