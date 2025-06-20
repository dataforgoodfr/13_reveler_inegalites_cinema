class FestivalAwardEntity:
    FALLBACK_LABEL = "Autre"

    def __init__(self, award):
        self.award = award

    def display_name(self):
        if not self.award:
            return None
        if self.award.french_label == self.FALLBACK_LABEL:
            return self.award.mubi_label
        return self.award.french_label
