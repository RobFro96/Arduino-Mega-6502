const uint8_t PROTOCOL_START_BYTE = 0xFF;     //!> Value of the start byte
const uint8_t PROTOCOL_MESSAGE_EXTRA_LEN = 3; //!> Length of the total message = PROTOCOL_MESSAGE_EXTRA_LEN + Payload Length
const uint8_t PROTOCOL_COMMAND = 1;           //!> Index of the command byte
const uint8_t PROTOCOL_PAYLOAD_LEN = 2;       //!> Index of the payload length
const uint8_t PROTOCOL_DATA = 3;              //!> Index of the first data byte

const uint8_t PROTOCOL_WHOIAM_VALUE = 0xf2;
const uint8_t PROTOCOL_VERSION = 1;

const uint8_t CMD_API_ACTION_SINGLE_STEP = (1 << 0);
const uint8_t CMD_API_ACTION_RUN = (1 << 1);
const uint8_t CMD_API_ACTION_RESET = (1 << 2);
const uint8_t CMD_API_ACTION_NMI = (1 << 3);
const uint8_t CMD_API_ACTION_IRQ = (1 << 4);
const uint8_t CMD_API_ACTION_AUTO_RESET = (1 << 5);

typedef enum
{
    CMD_WHOIAM_VERSION = 1,
    CMD_MEM_REQUEST = 2,
    CMD_MEM_WRITE = 3,
    CMD_MEM_PAGE_WRITE = 4,
    CMD_BUS_ACTION = 5,
    CMD_API_ACTIONS = 6
} protocol_cmd_t;

// Control Bus PORTK
const uint8_t RDY_BE = (1 << 1);
const uint8_t RESB = (1 << 2);
const uint8_t PHI2 = (1 << 3);
const uint8_t RWB = (1 << 4);
const uint8_t IRQB = (1 << 5);
const uint8_t NMIB = (1 << 6);
const uint8_t SYNC = (1 << 7);

// Auxillary PORTG
const uint8_t HALT_LED = (1 << 0);
const uint8_t HALT_BTN = (1 << 1);
const uint8_t EEPROM_WE = (1 << 2);

// Auxiallary PORTD
const uint8_t EEPROM_OE = (1 << 7);

#define p_abus_val_l() (PINL)
#define p_abus_val_h() (PINC)

uint16_t p_abus_val()
{
    return (uint16_t)p_abus_val_l() + (((uint16_t)p_abus_val_h()) << 8);
}
#define p_abus_output() ({ DDRL = 0xFF; DDRC=0xFF; })
#define p_abus_input() ({ DDRL = 0x00; DDRC = 0x00; })
void p_abus_set(uint16_t abus)
{
    PORTL = abus;
    PORTC = abus >> 8;
}

#define p_dbus_val() (PINA)
#define p_dbus_output() ({ DDRA = 0xFF; })
#define p_dbus_input() ({ DDRA = 0x00; })
void p_dbus_set(uint8_t dbus)
{
    PORTA = dbus;
}

#define p_cbus_val() (PINK)
uint8_t p_cbus_vectors_set(uint8_t cbus)
{
    const uint8_t allowed_pulldown = IRQB + NMIB + RESB;
    DDRK = (cbus & allowed_pulldown) + (DDRK & ~allowed_pulldown);
}

#define p_reset_l() ({ DDRK |= RESB; })
#define p_reset_h() ({ DDRK &= ~RESB; })
#define p_reset_val() (PINK & RESB)

#define p_irq_l() ({ DDRK |= IRQB; })
#define p_nmi_l() ({ DDRK |= NMIB; })

#define p_phi2_l() ({ PORTK &= ~PHI2; })
#define p_phi2_h() ({ PORTK |= PHI2; })

#define p_rdy_be_l() ({ DDRK |= RDY_BE; })
#define p_rdy_be_h() ({ DDRK &= ~RDY_BE; })

#define p_eeprom_we_l() ({ PORTG &= ~EEPROM_WE; })
#define p_eeprom_we_h() ({ PORTG |= EEPROM_WE; })

#define p_eeprom_oe_l() ({ PORTD &= ~EEPROM_OE; })
#define p_eeprom_oe_h() ({ PORTD |= EEPROM_OE; })

void p_halt_led_set(uint8_t state)
{
    if (state)
        PORTG |= HALT_LED;
    else
        PORTG &= ~HALT_LED;
}