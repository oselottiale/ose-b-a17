import uasyncio as asyncio
import aioble, bluetooth
from machine import Pin, PWM


BLE_SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
BLE_CHAR_UUID    = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

palvelu = aioble.Service(BLE_SERVICE_UUID)
komento_char = aioble.Characteristic(
    palvelu, BLE_CHAR_UUID,
    read=True, write=True
)

aioble.register_services(palvelu)

# -----------------------------
# variablet
# -----------------------------

# freq = moottorien taajuus, 0-65535
freq1=65535
freq2=1000
# lepo = loopin lepoaika, sekunneissa
lepo1=0.2
lepo2=0.01
# led = ledeihn liittyvä variable, N kohdalle numero
ledN = 

# -----------------------------
# ledien koodi
# -----------------------------



# -----------------------------
# Moottorien pinnit + funktiot
# -----------------------------
moottoriA_pwm = PWM(Pin(16))
moottoriB_pwm = PWM(Pin(18))

moottoriA_ohjausA = Pin(15, Pin.OUT)
moottoriA_ohjausB = Pin(14, Pin.OUT)

moottoriB_ohjausA = Pin(13, Pin.OUT)
moottoriB_ohjausB = Pin(12, Pin.OUT)

moottoriA_pwm.freq(freq2)
moottoriB_pwm.freq(freq2)

def pysayta():
    moottoriA_ohjausA.low()
    moottoriA_ohjausB.low()
    moottoriB_ohjausA.low()
    moottoriB_ohjausB.low()
    moottoriA_pwm.duty_u16(0)
    moottoriB_pwm.duty_u16(0)

def eteen():
    moottoriA_ohjausA.high()
    moottoriA_ohjausB.low()
    moottoriB_ohjausA.high()
    moottoriB_ohjausB.low()
    moottoriA_pwm.duty_u16(freq1)
    moottoriB_pwm.duty_u16(freq1)

def taakse():
    moottoriA_ohjausA.low()
    moottoriA_ohjausB.high()
    moottoriB_ohjausA.low()
    moottoriB_ohjausB.high()
    moottoriA_pwm.duty_u16(freq1)
    moottoriB_pwm.duty_u16(freq1)

# -----------------------------
# looppaava koodi
# -----------------------------

async def ble_loop():
    while True:
        print("Odotetaan BLE-yhteyttä...")
        conn = await aioble.advertise(
            100_000,
            name="Ratikka",
            services=[BLE_SERVICE_UUID]
        )

        print("Yhdistetty!")
        await asyncio.sleep(lepo1)

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

            await asyncio.sleep(lepo2)

        print("Yhteys katkaistu")
        pysayta()

asyncio.run(ble_loop())

