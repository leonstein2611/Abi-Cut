def ms_to_time(ms):

    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    milliseconds = ms % 1000

    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"


def time_to_ms(time_string):

    try:

        minutes_seconds, milliseconds = time_string.split(".")
        minutes, seconds = minutes_seconds.split(":")

        return (
            int(minutes) * 60000 +
            int(seconds) * 1000 +
            int(milliseconds)
        )

    except:
        return 0