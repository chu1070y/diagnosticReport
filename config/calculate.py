## 리스트
calculate_params_list = ['Innodb_buffer_hit_ratio', 'Tmp_disk_rate']


### 주의! 파라미터 이름 틀리면 에러 남!!!
## 계산식
Innodb_buffer_hit_ratio = '100 - (Innodb_buffer_pool_reads/Innodb_buffer_pool_read_requests) *100'
Tmp_disk_rate = 'Created_tmp_disk_tables/(Created_tmp_disk_tables+Created_tmp_tables)*100'
