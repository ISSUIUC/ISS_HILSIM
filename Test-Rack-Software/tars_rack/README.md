## HILSIM Data Streamer - TARS

This is the directory storing the code for the TARS data-streaming module to be used with the Kamaji service.

> [!IMPORTANT]
> This avionics stack type **DOES NOT** support power cycling

> [!IMPORTANT]
> This avionics stack is susceptible to **LOCKING** (Non-recoverable errors)

#### Differences in the Avionics Interface
`detect_avionics`
Usually you would want to detect avionics by reading their output and confirming that the information they're giving you is consistent with that av stack. This interface doesn't need to be as sophisticated (as **TARS** does not have any peripherals). The interface will treat the first non-server port taken up as the avionics target port.

> [!WARNING]
> When using this avionics interface, do **not** plug in other peripherals into the datastreamer computer, as this may cause a mismatch between the platformio target and the datastreamer av target.


