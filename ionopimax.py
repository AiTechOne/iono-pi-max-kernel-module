import logging
import time

#################################################
# logger object of this module
#################################################
logger = logging.getLogger(__name__)

class IonoPiMax:

    #######################################
    ## Digital Input/Output:

    def dio_mode(self, port:int, mode:str=None):
        if port in [1,2,3,4]:
            if mode:
                if mode in ['in', 'out']:
                    with open(f'/sys/class/ionopimax/digital_io/dt{port}_mode', 'w') as f:
                        f.write(mode)
                        logger.debug(f"Digital IO {port} -> {mode}")
                else:
                    logger.error(f'Mode={mode} not valid (only: "in" or "out")')
            else:
                with open(f'/sys/class/ionopimax/digital_io/dt{port}_mode', 'r') as f:
                    mode = f.read().strip()
                    logger.debug(f"Digital IO {port} = {mode}")
                    return mode
        else:
            logger.error(f"IO={port} does not exist")

    def dio_read(self, port:int):
        if port in [1,2,3,4]:
            with open(f'/sys/class/ionopimax/digital_io/dt{port}', 'r') as f:
                if f.read().strip() == "0":
                    logger.debug(f'Digital input {port} = LOW (inverted)')
                    return True
                else:
                    logger.debug(f'Digital input {port} = HIGH (inverted)')
                    return False
        else:
            logger.error(f"Digital input port={port} does not exist")
        return None

    def dio_write(self, port, value):
        value = str(value)
        if port in [1,2,3,4]:
            if value in ['0', '1']:
                with open(f'/sys/class/ionopimax/digital_io/dt{port}', 'w') as f:
                    f.write(value)
                    logger.debug(f"Digital IO {port} -> {value}")
            else:
                logger.error(f'Value={value} not valid')
        else:
            logger.error(f"Digital IO = {port} does not exist")

    #######################################
    ## Digital Input:

    def di_read(self, port:int):
        if port in [1,2,3,4]:
            with open(f'/sys/class/ionopimax/digital_in/di{port}', 'r') as f:
                if f.read().strip() == "1":
                    logger.debug(f'Digital input {port} = HIGH')
                    return True
                else:
                    logger.debug(f'Digital input {port} = LOW')
                    return False
        else:
            logger.error(f"Digital input port={port} does not exist")
        return None

    #######################################
    ## Analog voltage and current:

    def ai_read_v(self, port:int):
        voltage = None
        if port in [1,2,3,4]:
            with open(f'/sys/class/ionopimax/analog_in/av{port}', 'r') as f:
                try:
                    voltage = float(f.read().strip()) / 100
                    logger.debug(f'Voltage input {port} = {voltage} mV')
                except Exception as ex:
                    logger.error(ex)
                return voltage
        else:
            logger.error(f"Voltage input port={port} does not exist")
        return None

    def ai_read_i(self, port:int):
        current = None
        if port in [1,2,3,4]:
            with open(f'/sys/class/ionopimax/analog_in/ai{port}', 'r') as f:
                try:
                    current = float(f.read().strip()) / 100
                    logger.debug(f'Current input {port} = {current} mA')
                except Exception as ex:
                    logger.error(ex)
                return current
        else:
            logger.error(f"Analog input port={port} does not exist")
        return None

    #######################################
    ## Relays:

    def relay_status(self, relay:int):
        if relay in [1,2,3,4]:
            with open(f'/sys/class/ionopimax/digital_out/o{relay}', 'r') as f:
                if f.read().strip() == "1":
                    logger.debug(f'Relay {relay} = On')
                    return True
                else:
                    logger.debug(f'Relay {relay} = Off')
                    return False
        else:
            logger.error(f"Relay={relay} does not exist")
        return None

    def relay_on(self, relay):
        if relay in [1,2,3,4]:
            with open(f'/sys/class/ionopimax/digital_out/o{relay}', 'w') as f:
                f.write('1')
                logger.debug(f"Relay={relay} -> On")
        else:
            logger.error(f"Relay={relay} does not exist")

    def relay_off(self, relay):
        if relay in [1,2,3,4]:
            with open(f'/sys/class/ionopimax/digital_out/o{relay}', 'w') as f:
                f.write('0')
                logger.debug(f"Relay={relay} -> Off")
        else:
            logger.error(f"Relay={relay} does not exist")

    #######################################
    ## Open Collectors:
    # TODO

    #######################################
    ## Analog outputs
    # TODO

    #######################################
    ## IonoPiMax Generals:
    def buzzer(self, t_on:int, t_off:int, rep:int):
        if (type(t_on) == int) and (type(t_off) == int) and (type(rep) == int):
            if rep > 10:
                rep = 10
            with open(f'/sys/class/ionopimax/buzzer/beep', 'w') as f:
                f.write(f"{t_on*100} {t_off*100} {rep}")
        else:
            logger.error("All variables must be integers!")

    def fan_always_on(self):
        with open(f'/sys/class/ionopimax/fan/always_on', 'w') as f:
            f.write(1)

    def fan_auto(self):
        with open(f'/sys/class/ionopimax/fan/always_on', 'w') as f:
            f.write(0)

    def fan_is_on(self):
        with open(f'/sys/class/ionopimax/fan/status', 'r') as f:
            return f.read().strip()=='1'

    def power_supply_voltage(self):
        psv = None
        try:
            with open(f'/sys/class/ionopimax/power_in/mon_v', 'r') as f:
                psv = int(f.read().strip()) / 1000
                logger.debug(f'Power Supply Voltage = {psv} V')
        except:
            logger.error("Could not read power supply voltage")
        return psv

    def power_supply_current(self):
        psc = None
        try:
            with open(f'/sys/class/ionopimax/power_in/mon_i', 'r') as f:
                psc = int(f.read().strip()) / 1000
                logger.debug(f'Power Supply Current = {psc} A')
        except:
            logger.error("Could not read power supply current")
        return psc

    def usb_check(self, usb:int):
        with open(f'/sys/class/ionopimax/usb/usb{usb}_enabled', 'r') as f:
            return f.read().strip()

    def usb_check_fault(self, usb:int):
        with open(f'/sys/class/ionopimax/usb/usb{usb}_err', 'r') as f:
            return f.read().strip()

    def usb_enable(self, usb:int):
        with open(f'/sys/class/ionopimax/usb/usb{usb}_enabled', 'w') as f:
            f.write('1')

    def usb_disable(self, usb:int):
        with open(f'/sys/class/ionopimax/usb/usb{usb}_enabled', 'w') as f:
            f.write('0')

    def led_on(self, led:int):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                f.write('255')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_off(self, led:int):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                f.write('0')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_red(self, led:int, silent=False):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_r', 'w') as f:
                f.write('255')
            with open(f'/sys/class/ionopimax/led/l{led}_g', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_b', 'w') as f:
                f.write('0')
            if silent:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('0')
            else:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('255')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_green(self, led:int, silent=False):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_r', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_g', 'w') as f:
                f.write('255')
            with open(f'/sys/class/ionopimax/led/l{led}_b', 'w') as f:
                f.write('0')
            if silent:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('0')
            else:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('255')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_blue(self, led:int, silent=False):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_r', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_g', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_b', 'w') as f:
                f.write('255')
            if silent:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('0')
            else:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('255')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_purple(self, led:int, silent=False):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_r', 'w') as f:
                f.write('255')
            with open(f'/sys/class/ionopimax/led/l{led}_g', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_b', 'w') as f:
                f.write('255')
            if silent:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('0')
            else:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('255')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_yellow(self, led:int, silent=False):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_r', 'w') as f:
                f.write('255')
            with open(f'/sys/class/ionopimax/led/l{led}_g', 'w') as f:
                f.write('30')
            with open(f'/sys/class/ionopimax/led/l{led}_b', 'w') as f:
                f.write('0')
            if silent:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('0')
            else:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('255')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_light_blue(self, led:int, silent=False):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_r', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_g', 'w') as f:
                f.write('30')
            with open(f'/sys/class/ionopimax/led/l{led}_b', 'w') as f:
                f.write('255')
            if silent:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('0')
            else:
                with open(f'/sys/class/ionopimax/led/l{led}_br', 'w') as f:
                    f.write('255')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_reset_color(self, led):
        if led in [1,2,3,4,5]:
            with open(f'/sys/class/ionopimax/led/l{led}_r', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_g', 'w') as f:
                f.write('0')
            with open(f'/sys/class/ionopimax/led/l{led}_b', 'w') as f:
                f.write('0')
        else:
            logger.error(f"Led {led} does not exist!")

    def led_test(self):
        for i in range(1,6):
            self.led_off(led=i)
            self.led_reset_color(led=i)
        for i in range(1,6):
            self.led_on(led=i)
            time.sleep(0.5)
            self.led_red(led=i)
            time.sleep(0.5)
            self.led_blue(led=i)
            time.sleep(0.5)
            self.led_green(led=i)
            time.sleep(0.5)
            self.led_yellow(led=i)
            time.sleep(0.5)
            self.led_purple(led=i)
            time.sleep(0.5)
            self.led_light_blue(led=i)
            time.sleep(0.5)
            self.led_off(led=i)
            time.sleep(0.1)

    #######################################
    ## Watchdog

    def watchdog_manual_on(self):
        with open(f'/sys/class/ionopimax/watchdog/enabled', 'w') as f:
            f.write('1')

    def watchdog_manual_off(self):
        with open(f'/sys/class/ionopimax/watchdog/enabled', 'w') as f:
            f.write('0')

    def watchdog_expired(self):
        with open(f'/sys/class/ionopimax/watchdog/expired', 'r') as f:
            return f.read().strip()=='1'

    def watchdog_send_heartbeat(self):
        with open(f'/sys/class/ionopimax/watchdog/heartbeat', 'w') as f:
            f.write('F')

    def watchdog_get_mode(self):
        with open(f'/sys/class/ionopimax/watchdog/enable_mode', 'r') as f:
            mode = f.read().strip()
            if mode == '0':
                return "Normally disabled (default)"
            if mode == '1':
                return "Always enabled (ignore watchdog_manual_on/off)"

    def watchdog_set_mode_always(self):
        with open(f'/sys/class/ionopimax/watchdog/enable_mode', 'w') as f:
            f.write('A')
        self.save_config()

    def watchdog_set_mode_manual(self):
        with open(f'/sys/class/ionopimax/watchdog/enable_mode', 'w') as f:
            f.write('D')
        self.save_config()

    # TODO:
    def watchdog_set_timeout(self): pass
    def watchdog_set_down_delay(self): pass
    def watchdog_set_sd_switch(self, resets): pass

    #######################################
    ## UPS:
    # TODO
    def ups_enable(self): pass
    def ups_disable(self): pass
    def ups_status(self): pass
    def ups_state(self): pass

    #######################################
    ## Configuration :
    def save_config(self):
        with open(f'/sys/class/ionopimax/mcu', 'w') as f:
            f.write(f"S")

    def restore_config(self):
        with open(f'/sys/class/ionopimax/mcu', 'w') as f:
            f.write(f"R")