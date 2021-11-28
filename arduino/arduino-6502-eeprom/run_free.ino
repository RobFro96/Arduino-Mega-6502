
void run_free()
{
    Serial.flush();

    while (PING & (1 << 1))
    {
        p_phi2_l();
        p_dbus_input();
        __asm__ __volatile__("nop");
        if (p_abus_val_h() == 0xD0)
        {
            apple_io_bus_check();
        }
        p_phi2_h();
    }
}

inline void apple_io_bus_check()
{
    // Apple IO
    uint8_t abus_l = p_abus_val_l() & 0x0F;

    if (p_cbus_val() & RWB)
    {
        // Read
        switch (abus_l)
        {
        case 0:
            // Request Keyboard input
            p_dbus_set(map_to_ascii(Serial.read()) | 0x80);
            p_dbus_output();
            break;
        case 1:
            //Request Keyboard pressed
            if (Serial.available())
            {
                p_dbus_set(0xFF);
            }
            else
            {
                p_dbus_set(0);
            }
            p_dbus_output();
            break;
        case 2:
            // Request Display Ready
            p_dbus_set(0);
            p_dbus_output();
            break;
        default:
            break;
        }
    }
    else
    {
        // Write
        switch (abus_l)
        {
        case 0:
            break;
        case 1:
            break;
        case 2:
            // Output Display
            p_phi2_h();
            __asm__ __volatile__("nop");
            __asm__ __volatile__("nop");
            __asm__ __volatile__("nop");
            char c = p_dbus_val() & 0x7F;
            switch (c)
            {
            case 0:
                break;
            // case 0x0d:
            //     Serial.println();
            //     break;
            case 0x5f:
                Serial.write(8);
                Serial.write(' ');
                Serial.write(8);
                break;
            default:
                Serial.write(c);
                break;
            }
        default:
            break;
        }
    }
}

char map_to_ascii(int c)
{
    // Convert lowercase keys to UPPERCASE
    if (c > 96 && c < 123)
    {
        c -= 32;
    }

    // Backspace
    if (c == 8)
    {
        c = 0x5f;
    }

    return c;
}