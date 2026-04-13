import uasyncio as asyncio  # V2 vanha valkoinen ohjain sivu ei toimi tämän kanssa vain v2 ohjain toimii!
from machine import Pin, PWM
import aioble, bluetooth, time

BLE_SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
BLE_CHAR_UUID    = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

palvelu = aioble.Service(BLE_SERVICE_UUID)
komento_char = aioble.Characteristic(
    palvelu, BLE_CHAR_UUID,
    read=True, write=True
)

aioble.register_services(palvelu)

# tehtävät
tehtava = None
led_t = None

# LED
led = Pin(0, Pin.OUT)

async def leds(s):
    led.value(s)

# Moottorit
moottoriA_pwm = PWM(Pin(16))
moottoriB_pwm = PWM(Pin(18))

moottoriA_ohjausA = Pin(15, Pin.OUT)
moottoriA_ohjausB = Pin(14, Pin.OUT)

moottoriB_ohjausA = Pin(13, Pin.OUT)
moottoriB_ohjausB = Pin(12, Pin.OUT)

moottoriA_pwm.freq(1000)
moottoriB_pwm.freq(1000)

def aja(aa, ab, ba, bb, freq):
    moottoriA_ohjausA.value(aa)
    moottoriA_ohjausB.value(ab)
    moottoriB_ohjausA.value(ba)
    moottoriB_ohjausB.value(bb)
    moottoriA_pwm.duty_u16(freq)
    moottoriB_pwm.duty_u16(freq)

def pysayta():
    aja(0,0,0,0,0)
    print("pysäytetty")

async def liiku_task(suunta, freq, aika):
    if suunta == 1:
        aja(1,0,1,0,freq)
        print("eteen")
    else:
        aja(0,1,0,1,freq)
        print("taakse")

    if aika != -1:
        try:
            await asyncio.sleep(aika)
        except asyncio.CancelledError:
            return
        pysayta()

async def ble_loop():
    global tehtava, led_t

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

            if komento == "pysayta()":
                if tehtava:
                    tehtava.cancel()
                    tehtava = None
                pysayta()
                
            elif komento.startswith("liiku(") and komento.endswith(")"):
                try:
                    args = komento[6:-1]
                    suunta, freq, aika = map(int, args.split(","))

                    if tehtava:
                        tehtava.cancel()

                    tehtava = asyncio.create_task(liiku_task(suunta, freq, aika))

                except Exception as e:
                    print("Virhe liiku-komennossa:", e)

            elif komento.startswith("led(") and komento.endswith(")"):
                try:
                    state = int(komento[4:-1])

                    if led_t:
                        led_t.cancel()

                    led_t = asyncio.create_task(leds(state))

                except Exception as e:
                    print("Virhe led-komennossa:", e)

            await asyncio.sleep(0.01)

        print("Yhteys katkaistu")
        pysayta()

asyncio.run(ble_loop())

