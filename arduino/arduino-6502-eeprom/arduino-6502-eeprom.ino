#include <OneButton.h>
#include "defines.h"

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
    p_halt_led_set(single_stepping);

    p_reset_h();
    delay(10);
}

void loop()
{
    btn_halt_step.tick();

    if (Serial.available())
    {
        protocol_on_rxd();
    }

    // Vector auto-hold
    if (single_stepping && !p_reset_val())
    {
        p_reset_l();
    }

    if (!single_stepping)
    {
        p_phi2_l();
        delayMicroseconds(1);
        p_phi2_h();
    }
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
        phi_run();
    }
    else
    {
        phi_halt();
    }
}

void phi_run()
{
    single_stepping = false;
    p_halt_led_set(single_stepping);
    p_cbus_vectors_set(0);
}

void phi_halt()
{
    single_stepping = true;
    p_halt_led_set(single_stepping);
}

void single_step()
{
    p_phi2_l();
    delayMicroseconds(1);
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