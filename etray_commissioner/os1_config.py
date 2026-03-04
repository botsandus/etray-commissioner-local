"""Configuration settings for OS1 devices."""

SENSOR_TYPES = {
    "OS1": {
        "base_config": {
            "accel_fsr": "NORMAL",
            "azimuth_window": [0, 360000],
            "columns_per_packet": 16,
            "gyro_fsr": "NORMAL",
            "lidar_mode": "2048x10",
            "min_range_threshold_cm": 50,
            "multipurpose_io_mode": "OFF",
            "nmea_baud_rate": "BAUD_9600",
            "nmea_ignore_valid_char": 0,
            "nmea_in_polarity": "ACTIVE_HIGH",
            "nmea_leap_seconds": 0,
            "operating_mode": "NORMAL",
            "phase_lock_enable": False,
            "phase_lock_offset": 0,
            "return_order": "STRONGEST_TO_WEAKEST",
            "signal_multiplier": 1,
            "sync_pulse_in_polarity": "ACTIVE_HIGH",
            "sync_pulse_out_angle": 360,
            "sync_pulse_out_frequency": 1,
            "sync_pulse_out_polarity": "ACTIVE_HIGH",
            "sync_pulse_out_pulse_width": 10,
            "timestamp_mode": "TIME_FROM_PTP_1588",
            "udp_dest": "172.16.0.1",
            "udp_profile_imu": "LEGACY",
            "udp_profile_lidar": "RNG19_RFL8_SIG16_NIR16",
        },
        "individual_config": {
            "Pick-face": {
                "target_ip": "172.16.0.25",
                "udp_port_imu": 7503,
                "udp_port_lidar": 7502,
            },
            "Block-stack": {
                "target_ip": "172.16.0.26",
                "udp_port_imu": 7505,
                "udp_port_lidar": 7504,
            },
        },
        "target_url": "/api/v1/sensor/config",
    }
}
