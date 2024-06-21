# Context manager

## TempDisconnectSignal

If you want to disable a signal from a django model temporarily, you can use this context manager. The great benefit
over disabling models the regular way is, that you cannot forget to enable the signal again. Secondly, you save one
line of code. Keep it DRY!

Image you have this setup:

````python
from django.db import models
from django.db.models.signals import pre_save

class MyModel(models.Model):
    value = models.IntegerField()
    factor = models.IntegerField()
    product = models.IntegerField()


@receiver(pre_save, sender=MyModel)
def calculate_product(sender, instance, created, **kwargs):
    instance.product = value * factor
````

Now you want to save an instance of ``MyModel`` without calling the signal, you have to define at first a dictionary
with all parameters describing your signal:

````python
from django.db.models import signals

signal_kwargs = {
    'signal': signals.pre_save,
    'receiver': calculate_product,
    'sender': MyModel,
}
````

With this information set, you can easily disable the signal like this:

````python
my_obj = MyModel(value=1, factor=2)
with TempDisconnectSignal(**signal_kwargs):
    my_obj.save()
````

Now the attribute ``product`` will be not set / calculated.

If you need to disable the signal on multiple locations throughout your code, it is convenient to declare a method in
your model which provides the dictionary:


````python
class MyModel(models.Model):
    ...

    @staticmethod
    def get_calculate_product_kwargs():
        return {
            'signal': signals.pre_save,
            'receiver': calculate_product,
            'sender': MyModel,
        }

...
with TempDisconnectSignal(**MyModel.get_calculate_product_kwargs()):
    my_obj.save()
````

Attention: If your signal has an explicit ``dispatch_uid``, you need to pass it to the context manager as well.

````python
@receiver(pre_save, sender=MyModel, dispatch_uid='mymodel.calculate_product')
def calculate_product(sender, instance, created, **kwargs):
    instance.product = value * factor

...

signal_kwargs = {
    'signal': signals.pre_save,
    'receiver': calculate_product,
    'sender': MyModel,
    'dispatch_uid: 'mymodel.calculate_product',
}

...
````
