# Holiday Lights



## TODO

- [x] Make halloween less CPU intensive - try single update thread
- [x] fix supervisor fadecandy process 
- [ ] Convert halloween to generic twinkle behavior with color and timing parameters
- [ ] Twinkle better!
  - In zones,
  - When deciding wether to turn a new light on, count how many lights are currently on as those that are NOT OFF OR WAIT
  - when selecting what new light to turn on, 
    - consider only lights that are currently OFF
    - at least one neighboring light is not  in state UP
  - Start with every third light on
- [ ] Add Second light strand for inside!
  - [ ] Use wall power monitor to see how much power is being drawn by supply

