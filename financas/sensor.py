class ContasAPagarSensor(Entity):
    """Sensor para contas a pagar."""
    def __init__(self, hass):
        self._hass = hass
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return "Contas a Pagar"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
