import pandas as pd
import pymysql

# 数据库配置信息
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'db_evcharger_0707'
}

# 1. 读取CSV文件，指定数据类型并设置 low_memory=False
dtype_spec = {
    'city_id': 'int64',
    'station_name': 'object',
    'connector_id': 'int64',
    'coordinates_x': 'float64',
    'coordinates_y': 'float64',
    'tariff_amount': 'float64',
    'tariff_connectionfee': 'float64',
    'max_chargerate': 'int64',
    'plug_type_ccs': 'float64',
    'plug_type_chademo': 'float64',
    'plug_type_type_2_plug': 'float64',
    'connector_type_AC': 'float64',
    'connector_type_AC Controller/Receiver': 'float64',
    'connector_type_Rapid': 'float64',
    'connector_type_Ultra-Rapid': 'float64',
    'connector_type_iCharging': 'float64',
    'connector_avg_usage': 'float64',
    'station_avg_usage': 'float64',
    'distance_to_center': 'float64',
    'city_station_density': 'float64',
    'station_connector_count': 'int64',
    'station_avg_max_chargerate': 'float64',
    'station_density_10km': 'int64',
    'station_density_1km': 'int64',
    'station_density_20km': 'int64'
}

df = pd.read_csv('cleaned_charging_station_data.csv', dtype=dtype_spec, low_memory=False)

# 2. 重命名列名以去除特殊字符
df = df.rename(columns={
    'connector_type_AC Controller/Receiver': 'connector_type_AC_Controller_Receiver'
})

# 3. 删除不需要的特征
columns_to_drop = [
    'is_weekend', 'time_of_day', 'is_holiday', 'is_work_hour',
    'connector_unique_id', 'usage_last_24h', 'usage_last_7d',
    'city_density_level', 'availability_24h_ago',
    'availability_1week_ago', 'availability_change', 'relative_days',
    'is_available'
]
df = df.drop(columns=columns_to_drop)

# 4. 保留的特征列表
features_to_keep = [
    'city_id', 'station_name', 'connector_id', 'coordinates_x', 'coordinates_y',
    'tariff_amount', 'tariff_connectionfee', 'max_chargerate', 'plug_type_ccs',
    'plug_type_chademo', 'plug_type_type_2_plug', 'connector_type_AC',
    'connector_type_AC_Controller_Receiver', 'connector_type_Rapid',
    'connector_type_Ultra-Rapid', 'connector_type_iCharging',
    'connector_avg_usage', 'station_avg_usage', 'distance_to_center',
    'city_station_density', 'station_connector_count', 'station_avg_max_chargerate',
    'station_density_10km', 'station_density_1km', 'station_density_20km'
]

# 5. 聚合数据
grouped_df = df.groupby(['station_name', 'connector_id']).first().reset_index()

# 6. 检查聚合后数据的一致性
consistent_df = grouped_df[features_to_keep]

# 7. 创建数据库连接
connection = pymysql.connect(
    host=db_config['host'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['database']
)

# 8. 创建表（如果不存在）
create_table_query = """
CREATE TABLE IF NOT EXISTS PredictionInput (
    city_id INT,
    station_name VARCHAR(255) NOT NULL,
    connector_id INT NOT NULL,
    coordinates_x FLOAT,
    coordinates_y FLOAT,
    tariff_amount FLOAT,
    tariff_connectionfee FLOAT,
    max_chargerate INT,
    plug_type_ccs FLOAT,
    plug_type_chademo FLOAT,
    plug_type_type_2_plug FLOAT,
    connector_type_AC FLOAT,
    connector_type_AC_Controller_Receiver FLOAT,
    connector_type_Rapid FLOAT,
    connector_type_Ultra_Rapid FLOAT,
    connector_type_iCharging FLOAT,
    connector_avg_usage FLOAT,
    station_avg_usage FLOAT,
    distance_to_center FLOAT,
    city_station_density FLOAT,
    station_connector_count INT,
    station_avg_max_chargerate FLOAT,
    station_density_10km INT,
    station_density_1km INT,
    station_density_20km INT,
    PRIMARY KEY (station_name, connector_id)
)
"""

with connection.cursor() as cursor:
    cursor.execute(create_table_query)
connection.commit()

# 9. 将数据插入数据库
insert_query = """
INSERT INTO PredictionInput (
    city_id, station_name, connector_id, coordinates_x, coordinates_y,
    tariff_amount, tariff_connectionfee, max_chargerate, plug_type_ccs,
    plug_type_chademo, plug_type_type_2_plug, connector_type_AC,
    connector_type_AC_Controller_Receiver, connector_type_Rapid,
    connector_type_Ultra_Rapid, connector_type_iCharging,
    connector_avg_usage, station_avg_usage, distance_to_center,
    city_station_density, station_connector_count, station_avg_max_chargerate,
    station_density_10km, station_density_1km, station_density_20km
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
) ON DUPLICATE KEY UPDATE
    coordinates_x = VALUES(coordinates_x),
    coordinates_y = VALUES(coordinates_y),
    tariff_amount = VALUES(tariff_amount),
    tariff_connectionfee = VALUES(tariff_connectionfee),
    max_chargerate = VALUES(max_chargerate),
    plug_type_ccs = VALUES(plug_type_ccs),
    plug_type_chademo = VALUES(plug_type_chademo),
    plug_type_type_2_plug = VALUES(plug_type_type_2_plug),
    connector_type_AC = VALUES(connector_type_AC),
    connector_type_AC_Controller_Receiver = VALUES(connector_type_AC_Controller_Receiver),
    connector_type_Rapid = VALUES(connector_type_Rapid),
    connector_type_Ultra_Rapid = VALUES(connector_type_Ultra_Rapid),
    connector_type_iCharging = VALUES(connector_type_iCharging),
    connector_avg_usage = VALUES(connector_avg_usage),
    station_avg_usage = VALUES(station_avg_usage),
    distance_to_center = VALUES(distance_to_center),
    city_station_density = VALUES(city_station_density),
    station_connector_count = VALUES(station_connector_count),
    station_avg_max_chargerate = VALUES(station_avg_max_chargerate),
    station_density_10km = VALUES(station_density_10km),
    station_density_1km = VALUES(station_density_1km),
    station_density_20km = VALUES(station_density_20km)
"""

with connection.cursor() as cursor:
    for index, row in consistent_df.iterrows():
        cursor.execute(insert_query, (
            row['city_id'], row['station_name'], row['connector_id'], row['coordinates_x'], row['coordinates_y'],
            row['tariff_amount'], row['tariff_connectionfee'], row['max_chargerate'], row['plug_type_ccs'],
            row['plug_type_chademo'], row['plug_type_type_2_plug'], row['connector_type_AC'],
            row['connector_type_AC_Controller_Receiver'], row['connector_type_Rapid'],
            row['connector_type_Ultra-Rapid'], row['connector_type_iCharging'],
            row['connector_avg_usage'], row['station_avg_usage'], row['distance_to_center'],
            row['city_station_density'], row['station_connector_count'], row['station_avg_max_chargerate'],
            row['station_density_10km'], row['station_density_1km'], row['station_density_20km']
        ))
    connection.commit()

# 10. 关闭数据库连接
connection.close()
