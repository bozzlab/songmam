from songmam.models.webview import Context


def test_main():
    sample = """{
        "thread_type": "GROUP",
        "tid": "1411911565550430",
        "psid": "1293479104029354",
        "signed_request": "5f8i9XXH2hEaykXHKFvu-E5Nr6QRqN002JO7yl-w_9o.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTUwNDA0NjM4MCwicGFnZV9pZCI6NjgyNDk4MTcxOTQzMTY1LCJwc2lkIjoiMTI1NDQ1OTE1NDY4MjkxOSIsInRocmVhZF90eXBlIjoiVVNFUl9UT19QQUdFIiwidGlkIjoiMTI1NDQ1OTE1NDY4MjkxOSJ9"
        }
    """

    context = Context.parse_raw(sample)
    assert not context.verify("123")
    assert not context.verify("123")
