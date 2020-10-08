from decouple import config

from songmam.models.webview import Context


def test_main():
    sample = """{
        "metadata": null,
        "thread_type": "USER_TO_PAGE",
        "tid": "3149159248537212",
        "psid": "3149159248537212",
        "signed_request": "kyYc0BUmhpqnlzGgf8_FgVMISpiAqo9TRs1Z3xSIX7w.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvbW11bml0eV9pZCI6bnVsbCwiaXNzdWVkX2F0IjoxNjAyMTM2OTE0LCJtZXRhZGF0YSI6bnVsbCwicGFnZV9pZCI6NTc0MTg1MzM2NTk1NjczLCJwc2lkIjoiMzE0OTE1OTI0ODUzNzIxMiIsInRocmVhZF9wYXJ0aWNpcGFudF9pZHMiOm51bGwsInRocmVhZF90eXBlIjoiVVNFUl9UT19QQUdFIiwidGlkIjoiMzE0OTE1OTI0ODUzNzIxMiJ9"
        }
    """

    context = Context.parse_raw(sample)
    assert not context.verify("123")
    assert context.verify("7edb841332147f98c53e42813c0d52d8")
