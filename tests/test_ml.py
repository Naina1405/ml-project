from models.baseline_classifier import BaselineIntentClassifier

def test_baseline_ml_classifier():
    clf = BaselineIntentClassifier()
    texts = ["remind me tomorrow", "search for python courses", "send an email to boss"]
    labels = ["create_reminder", "search_information", "send_email"]
    
    clf.train(texts, labels)
    intent, conf = clf.predict("search for ml courses")
    assert intent == "search_information"
    assert conf > 0.0
