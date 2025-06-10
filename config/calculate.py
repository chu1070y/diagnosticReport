## 리스트 ---- 여기 곡 넣어줘야 계산식을 인식합니다!!
calculate_params_list = ['Innodb_buffer_hit_ratio', 'Tmp_disk_rate', 'Qps']


### 주의! 파라미터 이름 틀리면 에러 남!!!
## 계산식
calculate_params = {
    'Innodb_buffer_hit_ratio': '100 - (Innodb_buffer_pool_reads/Innodb_buffer_pool_read_requests) * 100',
    'Tmp_disk_rate': 'Created_tmp_disk_tables/(Created_tmp_disk_tables+Created_tmp_tables) * 100',
    'Qps': 'Questions/Uptime'
}



