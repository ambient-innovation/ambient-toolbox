from django.core import mail
from django.db.models import signals
from django.test import TestCase

from ambient_toolbox.context_manager import TempDisconnectSignal
from testapp.models import (
    MyMultipleSignalModel,
    MySingleSignalModel,
    increase_value_no_dispatch_uid,
    increase_value_with_dispatch_uid,
    send_email,
)


class TempDisconnectSignalTest(TestCase):
    def test_single_signal_executed_regular(self):
        obj = MySingleSignalModel.objects.create()
        self.assertEqual(obj.value, 1)

    def test_single_signal_not_executed(self):
        kwargs = {
            "signal": signals.pre_save,
            "receiver": increase_value_no_dispatch_uid,
            "sender": MySingleSignalModel,
        }

        with TempDisconnectSignal(**kwargs):
            obj = MySingleSignalModel.objects.create()

        self.assertEqual(obj.value, 0)

    def test_multiple_signals_not_executed(self):
        kwargs_pre = {
            "signal": signals.pre_save,
            "receiver": increase_value_with_dispatch_uid,
            "sender": MyMultipleSignalModel,
            "dispatch_uid": "test.mysinglesignalmodel.increase_value_with_uuid",
        }
        kwargs_post = {
            "signal": signals.post_save,
            "receiver": send_email,
            "sender": MyMultipleSignalModel,
        }

        with TempDisconnectSignal(**kwargs_pre):
            with TempDisconnectSignal(**kwargs_post):
                obj = MyMultipleSignalModel.objects.create()

        outbox = len(mail.outbox)

        self.assertEqual(obj.value, 0)
        self.assertEqual(outbox, 0)

    def test_multiple_signals_one_still_active(self):
        kwargs_pre = {
            "signal": signals.pre_save,
            "receiver": increase_value_with_dispatch_uid,
            "sender": MyMultipleSignalModel,
            "dispatch_uid": "test.mysinglesignalmodel.increase_value_with_uuid",
        }

        with TempDisconnectSignal(**kwargs_pre):
            obj = MyMultipleSignalModel.objects.create()

        outbox = len(mail.outbox)

        self.assertEqual(obj.value, 0)
        self.assertEqual(outbox, 1)
