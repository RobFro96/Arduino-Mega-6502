const uint8_t PROTOCOL_START_BYTE = 0xFF;     //!> Value of the start byte
const uint8_t PROTOCOL_MESSAGE_EXTRA_LEN = 3; //!> Length of the total message = PROTOCOL_MESSAGE_EXTRA_LEN + Payload Length
const uint8_t PROTOCOL_COMMAND = 1;           //!> Index of the command byte
const uint8_t PROTOCOL_PAYLOAD_LEN = 2;       //!> Index of the payload length
const uint8_t PROTOCOL_DATA = 3;              //!> Index of the first data byte

const uint8_t PROTOCOL_WHOIAM_VALUE = 0x2f;
const uint8_t PROTOCOL_VERSION = 1;

typedef enum
{
    CMD_WHOIAM_VERSION = 1,
    CMD_PEEK_PINS = 2,
    CMD_SINGLE_STEP = 3,
    CMD_MEM_REQUEST = 4,
    CMD_MEM_WRITE = 5
} protocol_cmd_t;

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
    case CMD_PEEK_PINS:
        cmd_peek_pins();
        break;
    case CMD_SINGLE_STEP:
        cmd_single_step();
        break;
    case CMD_MEM_REQUEST:
        cmd_mem_request();
        break;
    case CMD_MEM_WRITE:
        cmd_mem_write();
        break;
    }
}

static void cmd_whoiam_version()
{
    char response[5] = {PROTOCOL_START_BYTE, CMD_WHOIAM_VERSION, 2, PROTOCOL_WHOIAM_VALUE, PROTOCOL_VERSION};
    Serial.write(response, 5);
}

static void cmd_peek_pins()
{
    char response[7] = {
        PROTOCOL_START_BYTE,
        CMD_PEEK_PINS,
        4,
        pins_get_cbus(),
        pins_get_dbus(),
        pins_get_abus_low_byte(),
        pins_get_abus_high_byte()};
    Serial.write(response, 7);
}

static void cmd_single_step()
{
    if (rx_buffer[PROTOCOL_PAYLOAD_LEN] != 3)
    {
        char response[3] = {PROTOCOL_START_BYTE, CMD_SINGLE_STEP, 0};
        Serial.write(response, 3);
        return;
    }

    cycle_single(rx_buffer[PROTOCOL_DATA], rx_buffer[PROTOCOL_DATA + 1],
                 rx_buffer[PROTOCOL_DATA + 2]);

    char response[7] = {
        PROTOCOL_START_BYTE,
        CMD_SINGLE_STEP,
        4,
        pins_get_cbus(),
        pins_get_dbus(),
        pins_get_abus_low_byte(),
        pins_get_abus_high_byte()};
    Serial.write(response, 7);
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
    for (uint8_t i = 0; i < length; i++)
    {
        uint8_t data = memory_read(memory_pointer);
        Serial.write(&data, 1);
        memory_pointer++;
    }
}

static void cmd_mem_write()
{
    uint8_t length = rx_buffer[PROTOCOL_PAYLOAD_LEN];

    for (uint8_t i = 0; i < length; i++)
    {
        memory_write_all(memory_pointer, rx_buffer[PROTOCOL_DATA + (uint16_t)i]);
        memory_pointer++;
    }

    char response[3] = {PROTOCOL_START_BYTE, CMD_MEM_WRITE, 0};
    Serial.write(response, 3);
}