#!/bin/sh

USER='root'
PASSWORD='rplinux'
SOCKET=/tmp/maria_10.6.sock
MYSQL_HOME=/maria/maria_10.6
OSINFO_LOG=/maria/maria_log/status_log_2
CONFIG=/etc/my.cnf_10.6
DB_PROCESS_NAME='mariadbd'


echo "===================== hostname =====================" >> $OSINFO_LOG/os_info.log
hostname >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== OS Version =====================" >> $OSINFO_LOG/os_info.log
cat /etc/redhat-release >> $OSINFO_LOG/os_info.log
cat /etc/issue >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== ip =====================" >> $OSINFO_LOG/os_info.log
ip a >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== cpu =====================" >> $OSINFO_LOG/os_info.log
cat /proc/cpuinfo >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== db used memeory  =====================" >> $OSINFO_LOG/os_info.log
ps awxuf |grep $DB_PROCESS_NAME >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== memory =====================" >> $OSINFO_LOG/os_info.log
cat /proc/meminfo >> $OSINFO_LOG/os_info.log
echo "===================== memory free =====================" >> $OSINFO_LOG/os_info.log
free >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== disk =====================" >> $OSINFO_LOG/os_info.log
df -h >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== db process =====================" >> $OSINFO_LOG/os_info.log
ps -ef | grep mysql >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== my.cnf =====================" >> $OSINFO_LOG/os_info.log
cat $CONFIG >> $OSINFO_LOG/os_info.log
echo ""

echo "===================== global variables =====================" >> $OSINFO_LOG/os_info.log
$MYSQL_HOME/bin/mysqladmin -u$USER -p$PASSWORD -S$SOCKET variables >> $OSINFO_LOG/os_info.log
echo ""



# Add DB INFO
echo "===================== 3.5.5.2 스키마별 테이블 사이즈 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "SELECT table_schema, table_name, size FROM ( SELECT table_schema,table_name,TRUNCATE((data_length + index_length) / 1024 / 1024 / 1024, 2) AS size,ROW_NUMBER() OVER (PARTITION BY table_schema ORDER BY (data_length + index_length) DESC) AS rn FROM information_schema.tables WHERE table_schema NOT IN ('sys','performance_schema','mysql','information_schema')) AS ranked WHERE rn <= 5 ORDER BY table_schema, size DESC;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log 
echo ""

echo "===================== 3.5.5.3 스토리지 엔진별 테이블 개수 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "SELECT table_schema, engine, COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema NOT IN ('sys', 'performance_schema', 'mysql', 'information_schema') GROUP BY table_schema, engine ORDER BY table_schema, engine;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.1 미사용DB계정 확인 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "SELECT DISTINCT m_u.user, m_u.host FROM mysql.user m_u LEFT JOIN performance_schema.accounts ps_a ON m_u.user = ps_a.user AND ps_a.host = m_u.host LEFT JOIN information_schema.views is_v ON is_v.definer = CONCAT(m_u.User, '@', m_u.Host) AND is_v.security_type = 'DEFINER' LEFT JOIN information_schema.routines is_r ON is_r.definer = CONCAT(m_u.User, '@', m_u.Host) AND is_r.security_type = 'DEFINER' LEFT JOIN information_schema.events is_e ON is_e.definer = CONCAT(m_u.user, '@', m_u.host) LEFT JOIN information_schema.triggers is_t ON is_t.definer = CONCAT(m_u.user, '@', m_u.host) WHERE ps_a.user IS NULL AND is_v.definer IS NULL AND is_r.definer IS NULL AND is_e.definer IS NULL AND is_t.definer IS NULL order by m_u.user, m_u.host;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.2.1 미사용 인덱스 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "SELECT * FROM sys.schema_unused_indexes;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.2.2 중복 인덱스 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "SELECT table_schema,table_name,redundant_index_name,redundant_index_columns,dominant_index_name,dominant_index_columns FROM sys. schema_redundant_indexes;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.2.3 분포도 낮은 인덱스 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "SELECT t.TABLE_SCHEMA AS 'Db', t.TABLE_NAME AS 'Table', s.INDEX_NAME AS 'Index_Name', s.COLUMN_NAME AS 'Field_Name', s.SEQ_IN_INDEX AS Seq_In_Index,s2.max_columns AS 'Max_Cols',s.CARDINALITY AS 'Card',t.TABLE_ROWS AS 'Est_rows', ROUND( ( (s.CARDINALITY / IFNULL(t.TABLE_ROWS, 0.01)) * 100), 2) AS 'Sel %' FROM INFORMATION_SCHEMA.STATISTICS s INNER JOIN INFORMATION_SCHEMA.TABLES t ON s.TABLE_SCHEMA = t.TABLE_SCHEMA AND s.TABLE_NAME = t.TABLE_NAME INNER JOIN ( SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, MAX(SEQ_IN_INDEX) AS max_columns FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA not in('mysql','information_schema','sys','performance_schema') GROUP BY TABLE_SCHEMA, TABLE_NAME, INDEX_NAME ) AS s2 ON s.TABLE_SCHEMA = s2.TABLE_SCHEMA AND s.TABLE_NAME = s2.TABLE_NAME AND s.INDEX_NAME = s2.INDEX_NAME WHERE t.TABLE_SCHEMA != 'mysql' AND s.CARDINALITY != 0 ORDER BY 'Sel %' ASC;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.3 변경 없는 테이블 진단 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "select t.table_schema, t.table_name, t.table_rows, tio.count_read, tio.count_write from information_schema.tables as t join performance_schema.table_io_waits_summary_by_table as tio on tio.object_schema = t.table_schema and tio.object_name = t.table_name where t.table_schema not in ('mysql','performance_schema','sys') and tio.count_write = 0 order by t.table_schema, t.table_name;"`
echo -e "\n$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.4.1 Full Table Scan SQL =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e 'select db, query, exec_count, sys.format_time(total_latency) as "formatted_total_latency",rows_sent_avg, rows_examined_avg, last_seen from sys.x$statements_with_full_table_scans order by total_latency desc;'`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.4.2 임시테이블 사용 SQL =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "select db,query,exec_count,total_latency,tmp_tables_to_disk_pct from sys.statements_with_temp_tables order by tmp_tables_to_disk_pct DESC;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""

echo "===================== 5.5 PK/UK 누락 테이블 =====================" >> $OSINFO_LOG/add_db_info.log
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "SELECT t.TABLE_SCHEMA, t.TABLE_NAME FROM information_schema.TABLES AS t LEFT JOIN information_schema.KEY_COLUMN_USAGE AS c ON t.TABLE_SCHEMA = c.CONSTRAINT_SCHEMA AND t.TABLE_NAME = c.TABLE_NAME AND c.CONSTRAINT_NAME = 'PRIMARY' WHERE t.TABLE_SCHEMA NOT IN('information_schema', 'performance_schema', 'mysql', 'sys') AND t.TABLE_TYPE NOT IN('SEQUENCE', 'VIEW') AND c.CONSTRAINT_NAME IS NULL;"`
echo -e "$SQL" >> $OSINFO_LOG/add_db_info.log
echo ""



