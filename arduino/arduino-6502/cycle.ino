void cycle_single(uint8_t cbus, uint8_t fixed_dbus, uint8_t dbus)
{
    // pulldown cbus signals
    pins_pulldown_cbus(cbus);

    pins_phi2_l();
    delayMicroseconds(10);

    uint16_t abus = pins_get_abus();
    uint8_t rwb = pins_get_cbus() & RWB;

    if (fixed_dbus)
    {
        pins_write_dbus(dbus);
    }
    else
    {
        if (rwb)
        {
            // read
            if (memory_is_valid(abus))
            {
                // set dbus
                pins_write_dbus(memory_read(abus));
            }
            else
            {
                // open bus
                pins_clear_dbus();
            }
        }
        else
        {
            // write
            pins_clear_dbus();
        }
    }

    pins_phi2_h();

    if (!fixed_dbus && !rwb)
    {
        // write
        uint8_t dbus = pins_get_dbus();
        memory_write_ram(abus, dbus);
    }

    delayMicroseconds(1);
}