#define MEM_RAM_START (0x0000)
#define MEM_RAM_SIZE (0x0800)
#define MEM_RAM_VALUE (0x00)
#define MEM_EEPROM_START (0x8000)
#define MEM_EEPROM_SIZE (0x1000)
#define MEM_RESET_VECTOR_START (0xFFFA)
#define MEM_RESET_VECTOR_SIZE (0x0006)
#define MEM_EEPROM_VALUE (0x00)
#define MEM_READ_VALUE (0x00)

uint8_t ram[MEM_RAM_SIZE];
uint8_t eeprom[MEM_EEPROM_SIZE];
uint8_t reset_vector[MEM_RESET_VECTOR_SIZE];

void memory_init()
{
    for (uint16_t i = 0; i < MEM_RAM_SIZE; i++)
    {
        ram[i] = MEM_RAM_VALUE;
    }
    for (uint16_t i = 0; i < MEM_EEPROM_SIZE; i++)
    {
        eeprom[i] = MEM_EEPROM_VALUE;
    }
    for (uint16_t i = 0; i < MEM_RESET_VECTOR_SIZE; i++)
    {
        reset_vector[i] = MEM_EEPROM_VALUE;
    }

    reset_vector[1] = 0x80;
    reset_vector[3] = 0x80;
    reset_vector[5] = 0x80;
}

uint8_t memory_is_valid(uint16_t addr)
{
    if (addr >= MEM_RAM_START && addr <= MEM_RAM_START + MEM_RAM_SIZE - 1)
        return 1;
    else if (addr >= MEM_EEPROM_START && addr <= MEM_EEPROM_START + MEM_EEPROM_SIZE - 1)
        return 1;
    else if (addr >= MEM_RESET_VECTOR_START && addr <= MEM_RESET_VECTOR_START + MEM_RESET_VECTOR_SIZE - 1)
        return 1;
    else
        return 0;
}

uint8_t memory_read(uint16_t addr)
{
    if (addr >= MEM_RAM_START && addr <= MEM_RAM_START + MEM_RAM_SIZE - 1)
        return ram[addr - MEM_RAM_START];
    else if (addr >= MEM_EEPROM_START && addr <= MEM_EEPROM_START + MEM_EEPROM_SIZE - 1)
        return eeprom[addr - MEM_EEPROM_START];
    else if (addr >= MEM_RESET_VECTOR_START && addr <= MEM_RESET_VECTOR_START + MEM_RESET_VECTOR_SIZE - 1)
        return reset_vector[addr - MEM_RESET_VECTOR_START];
    else
        return MEM_READ_VALUE;
}

void memory_write_ram(uint16_t addr, uint8_t value)
{
    if (addr >= MEM_RAM_START && addr < MEM_RAM_START + MEM_RAM_SIZE)
        ram[addr - MEM_RAM_START] = value;
}

uint8_t memory_write_all(uint16_t addr, uint8_t value)
{
    if (addr >= MEM_RAM_START && addr <= MEM_RAM_START + MEM_RAM_SIZE - 1)
        ram[addr - MEM_RAM_START] = value;
    else if (addr >= MEM_EEPROM_START && addr <= MEM_EEPROM_START + MEM_EEPROM_SIZE - 1)
        eeprom[addr - MEM_EEPROM_START] = value;
    else if (addr >= MEM_RESET_VECTOR_START && addr <= MEM_RESET_VECTOR_START + MEM_RESET_VECTOR_SIZE - 1)
        reset_vector[addr - MEM_RESET_VECTOR_START] = value;
}