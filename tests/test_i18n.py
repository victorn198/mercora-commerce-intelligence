from app.i18n import add_english_terms, dropdown_labels, language, options, translate


def test_language_falls_back_to_portuguese():
    assert language(None) == "pt"
    assert language("invalid") == "pt"
    assert language("en") == "en"


def test_filter_values_and_controls_are_localized():
    assert options(["credit_card", "delivered"], "en") == [
        {"label": "Credit card", "value": "credit_card"},
        {"label": "Delivered", "value": "delivered"},
    ]
    assert dropdown_labels("en")["deselect_all"] == "Clear selection"


def test_dataset_terms_can_be_registered_without_changing_filter_values():
    add_english_terms({"beleza_saude": "Health Beauty"})
    assert translate("beleza_saude", "en") == "Health Beauty"
    assert options(["beleza_saude"], "en") == [
        {"label": "Health Beauty", "value": "beleza_saude"}
    ]
