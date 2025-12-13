serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    let command = serial.readUntil(serial.delimiters(Delimiters.NewLine)).trim()
    if (command == "VALID") {
        basic.showString("VALID")
        // green LED ON
        pins.digitalWritePin(DigitalPin.P1, 1)
        // red LED OFF
        pins.digitalWritePin(DigitalPin.P0, 0)
        // Servo at 90°
        pins.servoWritePin(AnalogPin.P2, 90)
        // sound
        music.playTone(440, music.beat(BeatFraction.Whole))
        // 5 sec. delay
        basic.pause(5000)
        // motor back
        pins.servoWritePin(AnalogPin.P2, 0)
        // green LED OFF
        pins.digitalWritePin(DigitalPin.P1, 0)
        // red LED ON 
        pins.digitalWritePin(DigitalPin.P0, 1)
    } else if (command == "INVALID") {
        basic.showString("INVALID")
        // red LED ON imideately
        pins.digitalWritePin(DigitalPin.P0, 1)
        // green LED OFF
        pins.digitalWritePin(DigitalPin.P1, 0)
        // Servo back
        pins.servoWritePin(AnalogPin.P2, 0)
        // 15 sec. alarm
        let start = control.millis()
        while (control.millis() - start < 15000) {
            music.playTone(880, music.beat(BeatFraction.Half))
            basic.pause(200)
            music.playTone(440, music.beat(BeatFraction.Half))
            basic.pause(200)
        }
        pins.digitalWritePin(DigitalPin.P0, 0)
    }
})


pins.digitalWritePin(DigitalPin.P0, 1)
