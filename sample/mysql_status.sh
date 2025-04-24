#!/bin/sh

TODAY=`date +%Y%m%d`
NOW=`date +%Y%m%d%H%M`
USER='root'
PASSWORD='rplinux'
SOCKET=/tmp/maria_10.6.sock
MYSQL_HOME=/maria/maria_10.6
MYSQL_LOG=/maria/maria_log/status_log_2
DB_PROCESS_NAME='mariadbd'

mkdir -p $MYSQL_LOG/global_status/$TODAY
mkdir -p $MYSQL_LOG/processlist/$TODAY
mkdir -p $MYSQL_LOG/innodb_st/$TODAY
mkdir -p $MYSQL_LOG/size,rate/$TODAY
mkdir -p $MYSQL_LOG/memory_used/$TODAY
mkdir -p $MYSQL_LOG/vmstat/$TODAY
mkdir -p $MYSQL_LOG/disk_info/$TODAY

$MYSQL_HOME/bin/mysqladmin -u$USER -p$PASSWORD -S$SOCKET extended-status > $MYSQL_LOG/global_status/$TODAY/global_status.$NOW
$MYSQL_HOME/bin/mysqladmin -u$USER -p$PASSWORD -S$SOCKET processlist > $MYSQL_LOG/processlist/$TODAY/processlist.$NOW && $MYSQL_HOME/bin/mysql -uroot -p$PASSWORD -S$SOCKET -e 'show processlist' | grep -v 'Id' | grep -v '-' | wc -l >> $MYSQL_LOG/processlist/$TODAY/processlist.$NOW
$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e "show engine innodb status\G" > $MYSQL_LOG/innodb_st/$TODAY/innodb_st.$NOW

# DATA SIZE
SQL=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e 'SELECT SUM(data_length + index_length)/1024/1024/1024 FROM information_schema.TABLES;' | awk 'NR==2'`
echo "DATA SIZE:$SQL GB" >> $MYSQL_LOG/size,rate/$TODAY/size_rate.$NOW
echo ""

# TMP RATE
CTDT=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e'show global status' | grep Created_tmp_disk |  awk '{print $2}'`
CTT=`$MYSQL_HOME/bin/mysql -u$USER -p$PASSWORD -S$SOCKET -e 'show global status' | grep Created_tmp_tables |  awk '{print $2}'`
TMP_RESULT=`echo "($CTDT/($CTDT+$CTT))*100" | bc -l`
echo "TMP DISK RATE:$TMP_RESULT" >> $MYSQL_LOG/size,rate/$TODAY/size_rate.$NOW
echo ""
ps awxuf |grep $DB_PROCESS_NAME |grep -v grep |grep -v safe |awk '{print $4}' > $MYSQL_LOG/memory_used/$TODAY/memory_used.$NOW
vmstat 1 20 > $MYSQL_LOG/vmstat/$TODAY/vmstat_st.$NOW

# DISK INFO
df -h > $MYSQL_LOG/disk_info/$TODAY/disk_info.$NOW




#status log delete
#mdate1=`date +%Y%m%d --date '6days ago'`

#rm -rf ${MYSQL_LOG}/global_status/${mdate1}
#rm -rf ${MYSQL_LOG}/processlist/${mdate1}
#rm -rf ${MYSQL_LOG}/innodb_st/${mdate1}
#rm -rf ${MYSQL_LOG}/memory_used/${mdate1}
#rm -rf ${MYSQL_LOG}/vmstat/${mdate1}
#rm -rf ${MYSQL_LOG}/disk_info/${mdate1}

