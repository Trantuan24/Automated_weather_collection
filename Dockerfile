# Sử dụng image chính thức của Apache Airflow
FROM apache/airflow:2.9.2

# Cài đặt các thư viện bổ sung từ requirements.txt
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt


# Thiết lập thư mục làm việc
WORKDIR /opt/airflow

# Copy DAGs và các file cấu hình vào container
COPY dags/ /opt/airflow/dags/
COPY config/ /opt/airflow/config/

# Thiết lập quyền truy cập
RUN chown -R airflow:airflow /opt/airflow

# Chạy entrypoint mặc định của Airflow
ENTRYPOINT ["/entrypoint"]
CMD ["webserver"]
