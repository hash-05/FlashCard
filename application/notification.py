class NService:
    M_DECK_CREATED = "Deck created successfully"
    M_DECK_RENAMED = "Deck renamed successfully"
    M_DECK_DELETED = "Deck deleted successfully"
    M_CARD_ADDED = "Card added successfully"
    M_CARD_EDITED = "Card edited successfully"
    M_CARD_DELETED = "Card deleted successfully"

    M_TO_BE_SHOWN = []

    def getMessage(self):
        if len(self.M_TO_BE_SHOWN) > 0:
            return self.M_TO_BE_SHOWN.pop(0)
        else:
            return ""
