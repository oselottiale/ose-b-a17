import uasyncio as asyncio #v1 käytä sivua dev.oseale.com/ohjain/index2.html ohjaimena
from machine import Pin, PWM
import aioble
import bluetooth

BLE_SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
BLE_CHAR_UUID    = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

palvelu = aioble.Service(BLE_SERVICE_UUID)
komento_char = aioble.Characteristic(
    palvelu, BLE_CHAR_UUID,
    read=True, write=True
)

aioble.register_services(palvelu)

# -----------------------------
# Moottorien pinnit
# -----------------------------
moottoriA_pwm = PWM(Pin(16))
moottoriB_pwm = PWM(Pin(18))

moottoriA_ohjausA = Pin(15, Pin.OUT)
moottoriA_ohjausB = Pin(14, Pin.OUT)

moottoriB_ohjausA = Pin(13, Pin.OUT)
moottoriB_ohjausB = Pin(12, Pin.OUT)

moottoriA_pwm.freq(1000)
moottoriB_pwm.freq(1000)

def pysayta():
    moottoriA_pwm.duty_u16(0)
    moottoriB_pwm.duty_u16(0)
    moottoriA_ohjausA.low()
    moottoriA_ohjausB.low()
    moottoriB_ohjausA.low()
    moottoriB_ohjausB.low()

def eteen():
    moottoriA_ohjausA.high()
    moottoriA_ohjausB.low()
    moottoriB_ohjausA.high()
    moottoriB_ohjausB.low()
    moottoriA_pwm.duty_u16(50000)
    moottoriB_pwm.duty_u16(50000)

def taakse():
    moottoriA_ohjausA.low()
    moottoriA_ohjausB.high()
    moottoriB_ohjausA.low()
    moottoriB_ohjausB.high()
    moottoriA_pwm.duty_u16(50000)
    moottoriB_pwm.duty_u16(50000)

async def ble_loop():
    while True:
        print("Odotetaan BLE-yhteyttä...")
        conn = await aioble.advertise(
            100_000,
            name="Ratikka",
            services=[BLE_SERVICE_UUID]
        )

        print("Yhdistetty!")
        await asyncio.sleep(0.2)

        while conn.is_connected():
            event = await komento_char.written()

            data = komento_char.read()
            komento = data.decode().strip()

            print("Komento:", komento)

            if komento == "eteen":
                eteen()
            elif komento == "taakse":
                taakse()
            elif komento == "stop":
                pysayta()

            await asyncio.sleep(0.01)

        print("Yhteys katkaistu")
        pysayta()

asyncio.run(ble_loop())

