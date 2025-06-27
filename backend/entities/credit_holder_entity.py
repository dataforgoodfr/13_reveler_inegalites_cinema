class CreditHolderEntity:
    def __init__(self, holder):
        self.holder = holder

    def full_name(self):
        if not self.holder:
            return None

        if self.is_company():
            return self.holder.legal_name.title() if self.holder.legal_name else None

        first_name = getattr(self.holder, "first_name", None)
        last_name = getattr(self.holder, "last_name", None)

        full = " ".join(filter(None, [first_name, last_name])).strip()
        return full.title() if full else None

    def is_company(self):
        return getattr(self.holder, "type", None) == "Company"
