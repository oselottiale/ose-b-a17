import uasyncio as asyncio
from machine import Pin, PWM
import aioble, bluetooth, time

# BLE UUIDs
BLE_SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
BLE_CHAR_UUID    = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

service = aioble.Service(BLE_SERVICE_UUID)
command_char = aioble.Characteristic(
    service, BLE_CHAR_UUID,
    read=True, write=True
)

aioble.register_services(service)

# Tasks
move_task_handle = None
led_task_handle = None

# LED
led = Pin(0, Pin.OUT)

async def toggle_led(_):
    led.value(1 - led.value())

# Motors
motorA_pwm = PWM(Pin(16))
motorB_pwm = PWM(Pin(18))

motorA_dirA = Pin(15, Pin.OUT)
motorA_dirB = Pin(14, Pin.OUT)

motorB_dirA = Pin(13, Pin.OUT)
motorB_dirB = Pin(12, Pin.OUT)

motorA_pwm.freq(1000)
motorB_pwm.freq(1000)

def drive(aa, ab, ba, bb, freq):
    motorA_dirA.value(aa)
    motorA_dirB.value(ab)
    motorB_dirA.value(ba)
    motorB_dirB.value(bb)
    motorA_pwm.duty_u16(freq)
    motorB_pwm.duty_u16(freq)

def stop():
    drive(0,0,0,0,0)
    print("Stopped")

async def move_task(direction, freq, duration_ms):
    if direction == 1:
        drive(1,0,1,0,freq)
        print("Forward")
    else:
        drive(0,1,0,1,freq)
        print("Backward")
        
    if duration_ms != -1:
        try:
            await asyncio.sleep(duration_ms / 1000)
        except asyncio.CancelledError:
            return
        stop()

async def ble_loop():
    global move_task_handle, led_task_handle

    while True:
        print("Waiting for BLE connection...")
        conn = await aioble.advertise(
            100_000,
            name="Ratikka",
            services=[BLE_SERVICE_UUID]
        )

        print("Connected!")
        await asyncio.sleep(0.2)

        while conn.is_connected():
            await command_char.written()

            data = command_char.read()
            command = data.decode().strip()
            print("Command:", command)

            if command == "pysayta()":
                if move_task_handle:
                    move_task_handle.cancel()
                    move_task_handle = None
                stop()

            elif command.startswith("liiku(") and command.endswith(")"):
                try:
                    args = command[6:-1]
                    direction, freq, duration_ms = map(int, args.split(","))

                    if move_task_handle:
                        move_task_handle.cancel()

                    move_task_handle = asyncio.create_task(
                        move_task(direction, freq, duration_ms)
                    )

                except Exception as e:
                    print("Error in liiku():", e)
                    
            elif command.startswith("led(") and command.endswith(")"):
                try:
                    if led_task_handle:
                        led_task_handle.cancel()

                    led_task_handle = asyncio.create_task(toggle_led(None))

                except Exception as e:
                    print("Error in led():", e)

            await asyncio.sleep(0.01)

        print("Connection lost")
        stop()

asyncio.run(ble_loop())
