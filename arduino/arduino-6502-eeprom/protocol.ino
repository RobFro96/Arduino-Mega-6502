static uint8_t rx_buffer_index = 0;
static uint8_t rx_payload_len;
uint8_t rx_buffer[257];
static uint16_t memory_pointer = 0;

void protocol_on_rxd()
{
    uint8_t c = Serial.read();

    // Storing the current byte in the buffer
    if (((c == PROTOCOL_START_BYTE) && (rx_buffer_index == 0)) || (rx_buffer_index > 0))
    {
        rx_buffer[rx_buffer_index] = c;
        rx_buffer_index++;
    }

    // reading the payload length
    if (rx_buffer_index == PROTOCOL_PAYLOAD_LEN + 1)
    {
        rx_payload_len = c;
    }

    // end of the message
    if (rx_buffer_index == rx_payload_len + PROTOCOL_MESSAGE_EXTRA_LEN)
    {
        rx_buffer_index = 0;
        message_decode();
    }
}

static void message_decode()
{
    switch (rx_buffer[PROTOCOL_COMMAND])
    {
    case CMD_WHOIAM_VERSION:
        cmd_whoiam_version();
        break;
    case CMD_MEM_REQUEST:
        cmd_mem_request();
        break;
    case CMD_MEM_WRITE:
        cmd_mem_write();
        break;
    case CMD_MEM_PAGE_WRITE:
        cmd_mem_page_write();
        break;
    case CMD_API_ACTIONS:
        cmd_api_actions();
        break;
    }
}

static void cmd_whoiam_version()
{
    char response[5] = {PROTOCOL_START_BYTE, CMD_WHOIAM_VERSION, 2, PROTOCOL_WHOIAM_VALUE, PROTOCOL_VERSION};
    Serial.write(response, 5);

    phi_halt();
}

static void cmd_mem_request()
{
    if (rx_buffer[PROTOCOL_PAYLOAD_LEN] != 3)
    {
        char response[3] = {PROTOCOL_START_BYTE, CMD_MEM_REQUEST, 0};
        Serial.write(response, 3);
        return;
    }

    memory_pointer = rx_buffer[PROTOCOL_DATA] + ((uint16_t)rx_buffer[PROTOCOL_DATA + 1] << 8);
    uint8_t length = rx_buffer[PROTOCOL_DATA + 2];

    char response[3] = {
        PROTOCOL_START_BYTE,
        CMD_MEM_REQUEST,
        length};
    Serial.write(response, 3);

    p_rdy_be_l();
    p_abus_output();

    for (uint8_t i = 0; i < length; i++)
    {
        p_abus_set(memory_pointer);
        delayMicroseconds(10);
        uint8_t data = p_dbus_val();
        Serial.write(&data, 1);
        memory_pointer++;
    }

    p_abus_input();
    p_rdy_be_h();
}

static void cmd_mem_write()
{
    uint8_t length = rx_buffer[PROTOCOL_PAYLOAD_LEN];

    p_rdy_be_l();
    p_eeprom_oe_h();
    p_abus_set(0x0000);
    p_abus_output();
    p_dbus_output();

    for (uint8_t i = 0; i < length; i++)
    {
        p_abus_set((memory_pointer & 0x7FFF) + 0x8000);
        p_dbus_set(rx_buffer[PROTOCOL_DATA + (uint16_t)i]);

        p_eeprom_we_l();
        delayMicroseconds(1);
        p_eeprom_we_h();
        delay(10);

        memory_pointer++;
    }

    p_dbus_input();
    p_abus_input();
    p_eeprom_oe_l();
    p_rdy_be_h();

    char response[3] = {PROTOCOL_START_BYTE, CMD_MEM_WRITE, 0};
    Serial.write(response, 3);
}

// Test: ff0442000000112233445566778899aabbccddeeff102132435465768798a9bacbdcedfe0f2031425364758697a8b9cadbecfd0e1f30415263748596a7b8c9daebfc0d1e2f
// ff0203000040
static void cmd_mem_page_write()
{
    uint8_t length = rx_buffer[PROTOCOL_PAYLOAD_LEN];

    if (length != 66)
    {
        char response[3] = {PROTOCOL_START_BYTE, CMD_MEM_PAGE_WRITE, 0};
        Serial.write(response, 3);
        return;
    }

    memory_pointer = rx_buffer[PROTOCOL_DATA] + ((uint16_t)rx_buffer[PROTOCOL_DATA + 1] << 8);
    memory_pointer = (memory_pointer & 0xFFC0) | 0x8000;

    p_rdy_be_l();
    p_eeprom_oe_h();
    p_abus_set(0x0000);
    p_abus_output();
    p_dbus_output();

    for (uint8_t i = 0; i < 64; i++)
    {
        p_abus_set(memory_pointer);
        p_dbus_set(rx_buffer[PROTOCOL_DATA + (uint16_t)i + 2]);

        p_eeprom_we_l();
        delayMicroseconds(1);
        p_eeprom_we_h();
        delayMicroseconds(1);

        memory_pointer++;
    }

    p_dbus_input();
    p_abus_input();
    p_eeprom_oe_l();
    p_rdy_be_h();

    char response[3] = {PROTOCOL_START_BYTE, CMD_MEM_PAGE_WRITE, 0};
    Serial.write(response, 3);
}

static void cmd_api_actions()
{
    if (rx_buffer[PROTOCOL_PAYLOAD_LEN] != 1)
    {
        char response[3] = {PROTOCOL_START_BYTE, CMD_API_ACTIONS, 0};
        Serial.write(response, 3);
        return;
    }

    uint8_t actions = rx_buffer[PROTOCOL_DATA];

    char response[3] = {PROTOCOL_START_BYTE, CMD_API_ACTIONS, 0};
    Serial.write(response, 3);

    if (actions & CMD_API_ACTION_IRQ)
    {
        p_irq_l();
    }
    if (actions & CMD_API_ACTION_NMI)
    {
        p_nmi_l();
    }
    if (actions & CMD_API_ACTION_RESET)
    {
        p_reset_l();
    }
    if (actions & CMD_API_ACTION_SINGLE_STEP)
    {
        if (!single_stepping)
        {
            phi_halt();
        }
        single_step();
    }
    if (actions & CMD_API_ACTION_RUN)
    {
        phi_run();
    }
    if (actions & CMD_API_ACTION_AUTO_RESET)
    {
        phi_halt();
        p_reset_l();
        for (uint8_t i = 0; i < 10; i++)
        {
            single_step();
        }
    }
}