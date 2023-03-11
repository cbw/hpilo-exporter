from prometheus_client import Gauge, Info
from prometheus_client import REGISTRY

registry = REGISTRY

hpilo_ip_address = Info('hpilo_ip_address', 'HP iLO IP address', ["product_name", "server_name"])
hpilo_firmware_version = Info('hpilo_firmware_version', 'HP iLO firmware version', ["product_name", "server_name"])

hpilo_vrm_gauge = Gauge('hpilo_vrm', 'HP iLO vrm status', ["product_name", "server_name"])
hpilo_drive_gauge = Gauge('hpilo_drive', 'HP iLO drive status', ["product_name", "server_name"])
hpilo_battery_gauge = Gauge('hpilo_battery', 'HP iLO battery status', ["product_name", "server_name"])
hpilo_storage_gauge = Gauge('hpilo_storage', 'HP iLO storage status', ["product_name", "server_name"])
hpilo_fans_gauge = Gauge('hpilo_fans', 'HP iLO fans status', ["product_name", "server_name"])
hpilo_bios_hardware_gauge = Gauge('hpilo_bios_hardware', 'HP iLO bios_hardware status', ["product_name", "server_name"])
hpilo_memory_gauge = Gauge('hpilo_memory', 'HP iLO memory status', ["product_name", "server_name"])
hpilo_power_supplies_gauge = Gauge('hpilo_power_supplies', 'HP iLO power_supplies status', ["product_name",
                                                                                            "server_name"])
hpilo_processor_gauge = Gauge('hpilo_processor', 'HP iLO processor status', ["product_name", "server_name"])
hpilo_network_gauge = Gauge('hpilo_network', 'HP iLO network status', ["product_name", "server_name"])
hpilo_temperature_gauge = Gauge('hpilo_temperature', 'HP iLO temperature status', ["product_name", "server_name"])
hpilo_host_power_gauge = Gauge('hpilo_host_power', 'HP iLO host power status', ["product_name", "server_name"])
hpilo_host_uptime_gauge = Gauge('hpilo_host_uptime', 'HP iLO minutes host has been powered on', ["product_name", "server_name"])

hpilo_nic_status_gauge = Gauge('hpilo_nic_status', 'HP iLO NIC status', ["product_name", "server_name", "nic_name", "ip_address"])

hpilo_fan_status_gauge = Gauge('hpilo_fan_status', 'HP iLO fan status', ["product_name", "server_name", "fan_name"])
hpilo_fan_speed_gauge = Gauge('hpilo_fan_speed', 'HP iLO fan speed', ["product_name", "server_name", "fan_name"])

hpilo_temp_gauge = Gauge('hpilo_temp', 'HP iLO temperature', ["product_name", "server_name", "thermometer_name"])
hpilo_temp_status_gauge = Gauge('hpilo_temp_status', 'HP iLO thermometer status', ["product_name", "server_name", "thermometer_name"])
hpilo_temp_caution_gauge = Gauge('hpilo_temp_caution', 'HP iLO temperature caution point', ["product_name", "server_name", "thermometer_name"])
hpilo_temp_critical_gauge = Gauge('hpilo_temp_critical', 'HP iLO temperature critical point', ["product_name", "server_name", "thermometer_name"])

infos = {
    'hpilo_ip_address': hpilo_ip_address,
    'hpilo_firmware_version': hpilo_firmware_version,
}

gauges = {
    'hpilo_vrm_gauge': hpilo_vrm_gauge,
    'hpilo_drive_gauge': hpilo_drive_gauge,
    'hpilo_battery_gauge': hpilo_battery_gauge,
    'hpilo_storage_gauge': hpilo_storage_gauge,
    'hpilo_fans_gauge': hpilo_fans_gauge,
    'hpilo_bios_hardware_gauge': hpilo_bios_hardware_gauge,
    'hpilo_memory_gauge': hpilo_memory_gauge,
    'hpilo_power_supplies_gauge': hpilo_power_supplies_gauge,
    'hpilo_processor_gauge': hpilo_processor_gauge,
    'hpilo_network_gauge': hpilo_network_gauge,
    'hpilo_temperature_gauge': hpilo_temperature_gauge,
    'hpilo_host_power:gauge': hpilo_host_power_gauge,
    'hpilo_host_uptime_gauge': hpilo_host_uptime_gauge,
    'hpilo_nic_status_gauge': hpilo_nic_status_gauge,
    'hpilo_fan_status_gauge': hpilo_fan_status_gauge,
    'hpilo_fan_speed_gauge': hpilo_fan_speed_gauge,
    'hpilo_temp_gauge': hpilo_temp_gauge,
    'hpilo_temp_status_gauge': hpilo_temp_status_gauge,
    'hpilo_temp_caution_gauge': hpilo_temp_caution_gauge,
    'hpilo_temp_critical_gauge': hpilo_temp_critical_gauge,
}
