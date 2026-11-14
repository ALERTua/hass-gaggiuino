# Unsupported fields

The integration leaves out these fields of the machine on purpose.

| Field | Reason |
|---|---|
| `lcd_sleep` | The documentation of the firmware gives no range of the values, and a number entity without a range can write a bad value. |
| `lcd_go_home` | The documentation of the firmware gives no range of the values, and a number entity without a range can write a bad value. |
| `lcd_close_on_brew_off` | It changes what `lcd_go_home` does, so it stays out together with that field. |
| `pcb_v2` | It is a service value with no use in an automation. |
| `debug_logging_enabled` | It is a service value with no use in an automation. |
| `energy_tracked_seconds` | It is a service value with no use in an automation. |
| `session_energy_tracked_seconds` | It is a service value with no use in an automation. |
