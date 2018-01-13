# WebVTT plugin for Sublime Text 3

Syntax definitions and `Shift` command for WebVTT (`*.vtt`) format.

### Shift

Shift timestamps of selected or all cues.

Timestamp format is the same as the one used in WebVTT. All timestamp parts are optional. Timestamp can be negative.

Examples:

Rule | Time Interval
------------ | -------------
`01:02:03.004` | Canonical notation. 1 hour 2 min 3 sec 4 msec
`3` | 3 seconds
`.4` | 4 msec
`3.4` | 3004 msec
`3.004` | 3004 msec
`3.400` | 3400 msec
`2:` | 2 minutes
`2::` | 2 hours
`-3` | back by 3 seconds
