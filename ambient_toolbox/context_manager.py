class TempDisconnectSignal:
    """
    Context manager to temporarily disconnect a model from a signal.
    Attention: If your signal has a `dispatch_uid` set, you need to pass it to this class!
    Use with a "with" tag like this:
    ```
    with TempDisconnectSignal(**kwargs):
        obj.save()
    ```
    """

    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
        )

    def __exit__(self, type, value, traceback):  # noqa: A002
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
        )
