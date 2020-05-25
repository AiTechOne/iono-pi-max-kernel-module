# Iono Pi Max driver kernel module

Raspberry Pi kernel module for using [Iono Pi Max](https://www.sferalabs.cc/iono-pi-max/) via sysfs.

## Compile and Install

If you don't have git installed:

    sudo apt-get install git-core

Clone this repo:

    git clone --depth 1 https://github.com/sfera-labs-dev/iono-pi-max-kernel-module.git
    
Install the Raspberry Pi kernel headers:

    sudo apt-get install raspberrypi-kernel-headers
    
Enable I2C:

    sudo raspi-config
    
Select: Interfacing Options -> I2C -> Yes

Make and install:

    cd iono-pi-max-kernel-module
    make
    sudo make install
    
Load the module:

    sudo insmod ionopimax.ko

Check that it was loaded correctly from the kernel log:

    sudo tail -f /var/log/kern.log

You will see something like:

    ...
    Sep  3 11:49:18 raspberrypi kernel: [   59.855723] ionopimax: - | init
    Sep  3 11:49:18 raspberrypi kernel: [   60.043024] ionopimax: - | ready
    ...

Optionally, to have the module automatically loaded at boot add `ionopimax` in `/etc/modules`.

E.g.:

    sudo sh -c "echo 'ionopimax' >> /etc/modules"

Optionally, to be able to use the `/sys/` files not as super user, create a new group "ionopimax" and set it as the module owner group by adding an udev rule:

    sudo groupadd ionopimax
    sudo cp 99-ionopimax.rules /etc/udev/rules.d/

and add your user to the group, e.g., for user "pi":

    sudo usermod -a -G ionopimax pi

then re-login to apply the group change and reload the module:

    su - $USER
    sudo rmmod ionopimax.ko
    sudo insmod ionopimax.ko

## Usage

After loading the module, you will find all the available devices under the directory `/sys/class/ionopimax/`.

The following paragraphs list all the possible devices (directories) and files coresponding to Iono Pi Max's features. 

You can read and/or write to these files to configure, monitor and control your Iono Pi Max.

The values of the configuration files marked with * can be permanently saved in the Iono Pi Max controller using the `/mcu/config` file.
If not permanently saved, the parameters will be reset to the original factory defaults, or to
the previously saved user configuration, after every power cycle of the Raspberry Pi.

### Buzzer - `/sys/class/ionopimax/buzzer/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|status|R/W|0|Buzzer off|
|status|R/W|1|Buzzer on|
|status|W|F|Flip buzzer's state|
|beep|W|&lt;t&gt;|Buzzer on for &lt;t&gt; ms|
|beep|W|&lt;t_on&gt; &lt;t_off&gt; &lt;rep&gt;|Buzzer beep &lt;rep&gt; times with &lt;t_on&gt;/&lt;t_off&gt; ms periods. E.g. "200 50 3"|

Examples:

    cat /sys/class/ionopimax/buzzer/status
    echo F > /sys/class/ionopimax/buzzer/status
    echo 200 50 3 > /sys/class/ionopimax/buzzer/beep

### Watchdog - `/sys/class/ionopimax/watchdog/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|enabled|R/W|0|Watchdog enabled|
|enabled|R/W|1|Watchdog disabled|
|enabled|W|F|Flip watchdog enabled state|
|expired|R|0|Watchdog timeout not expired|
|expired|R|1|Watchdog timeout expired|
|heartbeat|W|0|Set watchdog heartbeat line low|
|heartbeat|W|1|Set watchdog heartbeat line high|
|heartbeat|W|F|Flip watchdog heartbeat state|
|enable_mode*|R/W|D|MCU config XWED - Watchdog normally disabled (factory default)|
|enable_mode*|R/W|A|MCU config XWEA - Watchdog always enabled|
|timeout*|R/W|&lt;t&gt;|MCU config XWH&lt;t&gt; - Watchdog heartbeat timeout, in seconds (1 - 99999). Factory default: 60|
|down_delay*|R/W|&lt;t&gt;|MCU config XWW&lt;t&gt; - Forced shutdown delay from the moment the timeout is expired and the shutdown cycle has not been enabled, in seconds (1 - 99999). Factory default: 60|
|sd_switch|R/W|&lt;n&gt;|MCU config XWSD&lt;n&gt; (n &gt; 0) - Switch boot from SDA/SDB after &lt;n&gt; consecutive watchdog resets, if no heartbeat is detected. A value of n > 1 can be used with /enable_mode set to A only; if /enable_mode is set to D, then /sd_switch is set automatically to 1|
|sd_switch|R/W|0|MCU config XWSD0 - SD switch on watchdog reset disabled (factory default)|

### Power - `/sys/class/stratopi/power/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|down_enabled|R/W|0|Delayed shutdown cycle disabled|
|down_enabled|R/W|1|Delayed shutdown cycle enabled|
|down_delay*|R/W|&lt;t&gt;|MCU config XPW&lt;t&gt; - Shutdown delay from the moment it is enabled, in seconds (1 - 99999). Factory default: 60|
|off_time*|R/W|&lt;t&gt;|MCU config XPO&lt;t&gt; - Duration of power-off, in seconds (1 - 99999). Factory default: 5|
|up_delay*|R/W|&lt;t&gt;|MCU config XPU&lt;t&gt; - Power-up delay after main power is restored, in seconds (0 - 99999). Factory default: 0|
|down_enable_mode*|R/W|I|MCU config XPEI - Immediate (factory default): when shutdown is enabled, Strato Pi will immediately initiate the power-cycle, i.e. wait for the time specified in /down_delay and then power off the Pi board for the time specified in /off_time|
|down_enable_mode*|R/W|A|MCU config XPEA - Arm: enabling shutdown will arm the shutdown procedure, but will not start the power-cycle until the shutdown enable line goes low again (i.e. shutdown disabled or Raspberry Pi switched off). After the line goes low, Strato Pi will initiate the power-cycle|
|up_mode*|R/W|A|MCU config XPPA - Always: if shutdown is enabled when the main power is not present, only the Raspberry Pi is turned off, and the power is always restored after the power-off time, even if running on battery, with no main power present|
|up_mode*|R/W|M|MCU config XPPM - Main power (factory default): if shutdown is enabled when the main power is not present, the Raspberry Pi and the Strato Pi UPS board are powered down after the shutdown wait time, and powered up again only when the main power is restored|
|sd_switch|R/W|1|MCU config XPSD1 - Switch boot from SDA/SDB at every power-cycle|
|sd_switch|R/W|0|MCU config XPSD0 - SD switch at power-cycle disabled (factory default)|

### RS-485 Config - `/sys/class/stratopi/rs485/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|mode*|R/W|A|MCU config XSMA - Automatic (factory default): TX/RX switching is done automatically, based on speed and number of bits detection|
|mode*|R/W|P|MCU config XSMP - Passive: TX/RX switching is not actively controlled by Strato Pi|
|mode*|R/W|F|MCU config XSMF - Fixed: TX/RX switching is based on speed, number of bits, parity and number ofstop bits set in /params|
|params*|R/W|&lt;rbps&gt;|MCU config XSP&lt;rbps&gt; - Set RS-485 communication parameters: baud rate (r), number of bits (b), parity (p) and number of stop bits (s) for fixed mode, see below tables|

|Baud rate (r) value|Description|
|---------------|-----------|
|2|1200 bps|
|3|2400 bps|
|4|4800 bps|
|5|9600 bps (factory default)|
|6|19200 bps|
|7|38400 bps|
|8|57600 bps|
|9|115200 bps|

|Bits (b) value|Description|
|---------------|-----------|
|7|7 bit|
|8|8 bit (factory default)|


|Parity (p) value|Description|
|---------------|-----------|
|N|No parity (factory default)|
|E|Even parity|
|O|Odd parity|


|Stop bits (s) value|Description|
|---------------|-----------|
|1|1 stop bit (factory default)|
|2|2 stop bits|

### UPS - `/sys/class/stratopi/ups/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|battery|R|0|Running on main power|
|battery|R|1|Running on battery power|
|power_delay*|R/W|&lt;t&gt;|MCU config XUB&lt;t&gt; - UPS automatic power-cycle timeout, in seconds (0 - 99999). Strato Pi UPS will automatically initiate a delayed power-cycle (just like when /power/down_enabled is set to 1) if the main power source is not available for the number of seconds set. A value of 0 (factory default) disables the automatic power-cycle|

### Relay - `/sys/class/stratopi/relay/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|status|R/W|0|Relay open|
|status|R/W|1|Relay closed|
|status|W|F|Flip relay's state|

### LED - `/sys/class/stratopi/led/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|status|R/W|0|LED off|
|status|R/W|1|LED on|
|status|W|F|Flip LED's state|
|blink|W|&lt;t&gt;|LED on for &lt;t&gt; ms|
|blink|W|&lt;t_on&gt; &lt;t_off&gt; &lt;rep&gt;|LED blink &lt;rep&gt; times with &lt;t_on&gt;/&lt;t_off&gt; ms periods. E.g. "200 50 3"|

### Button - `/sys/class/stratopi/button/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|status|R|0|Button released|
|status|R|1|Button pressed|

### Expansion Bus - `/sys/class/stratopi/expbus/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|enabled|R/W|0|Expansion Bus enabled|
|enabled|R/W|1|Expansion Bus disabled|
|aux|R|0|Expansion Bus auxiliary line low|
|aux|R|1|Expansion Bus auxiliary line high|

### SD - `/sys/class/stratopi/sd/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|sdx_enabled*|R/W|1|MCU config XSD01 - SDX bus enabled (factory default)|
|sdx_enabled*|R/W|0|MCU config XSD00 - SDX bus disabled|
|sd1_enabled*|R/W|1|MCU config XSD11 - SD1 bus enabled|
|sd1_enabled*|R/W|0|MCU config XSD10 - SD1 bus disabled (factory default)|
|sdx_default|R/W|A|MCU config XSDPA - At power-up, SDX bus routed to SDA and SD1 bus to SDB by default (factory default)|
|sdx_default|R/W|B|MCU config XSDPB - At power-up, SDX bus routed to SDB and SD1 bus to SDA, by default|
|sdx_routing|R/W|A|MCU config XSDRA - SDX bus routed to SDA and SD1 bus to SDB (factory default)|
|sdx_routing|R/W|B|MCU config XSDRB - SDX bus routed to SDB and SD1 bus to SDA|

### USB 1 - `/sys/class/stratopi/usb1/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|disabled|R/W|0|USB 1 enabled|
|disabled|R/W|1|USB 1 disabled|
|ok|R|0|USB 1 fault|
|ok|R|1|USB 1 ok|

### USB 2 - `/sys/class/stratopi/usb2/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|disabled|R/W|0|USB 2 enabled|
|disabled|R/W|1|USB 2 disabled|
|ok|R|0|USB 2 fault|
|ok|R|1|USB 2 ok|

### MCU - `/sys/class/stratopi/mcu/`

|File|R/W|Value|Description|
|----|:---:|:-:|-----------|
|config|W|S|MCU command XCCS - Persist the current configuration in the controller to be retained across power cycles|
|config|W|R|MCU command XCCR - Restore the original factory configuration|
|fw_version|R|&lt;m&gt;.&lt;n&gt;/&lt;mc&gt;|MCU command XFW? - Read the firmware version, &lt;m&gt; is the major version number, &lt;n&gt; is the minor version number, &lt;mc&gt; is the model code. E.g. "4.0/07"|
|fw_install|W|<fw_file>|Set the MCU in boot-loader mode and upload the specified firmware HEX file|
|fw_install_progress|R|&lt;p&gt;|Progress of the current firmware upload process as percentage|

#### Firmware upload

The `/sys/class/stratopi/mcu/fw_install` sysfs file allows to upload a new firmware on Strato Pi's MCU. 

To this end, output the content of the firmaware HEX file to `/sys/class/stratopi/mcu/fw_install` and then monitor the progress reading from `/sys/class/stratopi/mcu/fw_install_progress`. 

The MCU will be set to boot-loader mode and the firware uploaded. When the progress reaches 100% you need to disable boot-loader mode by triggering a power-cycle, which is done by setting the shutdown line low (i.e. set `/sys/class/stratopi/power/down_enabled` to 0 or switch off the Raspberry Pi).

For troubleshooting or monitoring the firmware upload process check the kernel log in `/var/log/kern.log`.

Firmware upload axample:

    $ cat firmware.hex > /sys/class/stratopi/mcu/fw_install &
    [1] 14918
    $ cat /sys/class/stratopi/mcu/fw_install_progress
    0
    [...]
    $ cat /sys/class/stratopi/mcu/fw_install_progress
    100
    $ sudo shutdown now 
