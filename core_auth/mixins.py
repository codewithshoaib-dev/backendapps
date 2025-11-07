from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='DoNothing')
class CSRFExemptMixin:

     def DoNothing(self):
          pass
