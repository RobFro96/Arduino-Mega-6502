#include <OneButton.h>
#include "defines.h"
#include <EEPROM.h>

OneButton btn_halt_step(40, true, true);
bool single_stepping = false;

void setup()
{
    pins_init();
    Serial.begin(115200);

    pinMode(13, 1);
    digitalWrite(13, 0);

    Serial.write(0);

    btn_halt_step.attachClick(on_btn_halt_step_clicked);
    btn_halt_step.attachLongPressStart(on_btn_halt_step_long_press);

    single_stepping = EEPROM.read(0);
    p_halt_led_set(single_stepping);

    p_reset_h();
    delay(10);
}

void loop()
{
    if (!single_stepping)
    {
        while (!(PING & (1 << 1)))
            ;
        delay(50);

        run_free();

        set_single_stepping_state(true);
    }

    btn_halt_step.tick();

    if (Serial.available())
    {
        protocol_on_rxd();
    }

    // Reset auto-hold
    if (!p_reset_val())
    {
        p_reset_l();
    }
}

void set_single_stepping_state(bool state)
{
    single_stepping = state;
    p_halt_led_set(state);
    EEPROM.write(0, state);
}

void on_btn_halt_step_clicked()
{
    if (single_stepping)
    {
        single_step();
    }
}

void on_btn_halt_step_long_press()
{
    if (single_stepping)
    {
        set_single_stepping_state(false);
        p_cbus_vectors_set(0);
    }
}

void single_step()
{
    p_phi2_l();
    p_dbus_input();
    __asm__ __volatile__("nop");
    p_phi2_h();

    char response[7] = {
        PROTOCOL_START_BYTE,
        CMD_BUS_ACTION,
        4,
        p_cbus_val(),
        p_dbus_val(),
        p_abus_val_l(),
        p_abus_val_h()};
    Serial.write(response, 7);

    p_cbus_vectors_set(0);
}
