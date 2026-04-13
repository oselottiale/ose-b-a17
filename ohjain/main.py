import uasyncio as asyncio  #Vanha valkoinen ohjainsivu ei toimi. Vain v2 ohjain toimii! / Old white contorller page does not work. Only v2 controller works!
from machine import Pin, PWM
import aioble, bluetooth, time

BLE_SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
BLE_CHAR_UUID    = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

service = aioble.Service(BLE_SERVICE_UUID)
command_char = aioble.Characteristic(
    service, BLE_CHAR_UUID,
    read=True, write=True
)

aioble.register_services(service)

# Tehtävät / Tasks
task = None
led_t = None

# LED
led = Pin(0, Pin.OUT)

async def leds(s):
    led.value(s)

# Moottorit / Motors
motorA_pwm = PWM(Pin(16))
motorB_pwm = PWM(Pin(18))

motorA_controlA = Pin(15, Pin.OUT)
motorA_controlB = Pin(14, Pin.OUT)

motorB_controlA = Pin(13, Pin.OUT)
motorB_controlB = Pin(12, Pin.OUT)

motorA_pwm.freq(1000)
motorB_pwm.freq(1000)

def drive(aa, ab, ba, bb, freq):
    motorA_controlA.value(aa)
    motorA_controlB.value(ab)
    motorB_controlA.value(ba)
    motorB_controlB.value(bb)
    motorA_pwm.duty_u16(freq)
    motorB_pwm.duty_u16(freq)

def stop():
    aja(0,0,0,0,0)
    print("Pysäytetty / Stopped")

async def move_task(direction, freq, time):
    if direction == 1:
        drive(1,0,1,0,freq)
        print("Eteen / Forward")
    else:
        drive(0,1,0,1,freq)
        print("Taakse / Backward")

    if time != -1:
        try:
            await asyncio.sleep(time)
        except asyncio.CancelledError:
            return
        stop()

async def ble_loop():
    global task, led_t

    while True:
        print("Odotetaan BLE-yhteyttä... / Awaiting for BLE-connection...")
        conn = await aioble.advertise(
            100_000,
            name="Ratikka",
            services=[BLE_SERVICE_UUID]
        )

        print("Yhdistetty! / Connected!")
        await asyncio.sleep(0.2)

        while conn.is_connected():
            event = await command_char.written()

            data = command_char.read()
            command = data.decode().strip()
            print("Komento / Command:", command)

            if command == "stop()":
                if task:
                    task.cancel()
                    task = None
                stop()
                
            elif command.startswith("move(") and command.endswith(")"):
                try:
                    args = command[6:-1]
                    direction, freq, time = map(int, args.split(","))

                    if task:
                        task.cancel()

                    task = asyncio.create_task(move_task(direction, freq, time))

                except Exception as e:
                    print("Virhe liiku-komennossa / Error in move-command:", e)

            elif command.startswith("led(") and command.endswith(")"):
                try:
                    state = int(command[4:-1])

                    if led_t:
                        led_t.cancel()

                    led_t = asyncio.create_task(leds(state))

                except Exception as e:
                    print("Virhe led-komennossa / Error in led-command:", e)

            await asyncio.sleep(0.01)

        print("Yhteys katkaistu / Connection terminated")
        stop()

asyncio.run(ble_loop())

