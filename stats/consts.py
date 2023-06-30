SESSION_CURRENT_RACE_KEY = 'current-race'
SESSION_HIDE_FIRST_STINT_KEY = 'hide-first-stint'
SESSION_PIT_QUEUE_KEY = 'pit-queue'
SESSION_PIT_MODE_KEY = 'pit-mode'


SESSION_PIT_V2_QUEUE_KEY = 'pit-v2-queue'
SESSION_PIT_V2_HIGHLIGHT_KEY = 'pit-v2-highlight'


class PitModes:
    BEST_2 = 'best_2'
    BEST_LAST = 'best_last'
    BEST_NONSTART_LAST = 'best_nonstart_last'

    @classmethod
    def allowed(cls):
        return [cls.BEST_2, cls.BEST_LAST, cls.BEST_NONSTART_LAST]

    @classmethod
    def get(cls, value):
        # Provide default value
        # Enum is not used to simplify everything for now
        if value not in cls.allowed():
            return cls.BEST_LAST
        return value
